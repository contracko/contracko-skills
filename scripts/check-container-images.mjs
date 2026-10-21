#!/usr/bin/env bun
// Source: contracko/agent-scripts/scripts/check-container-images.mjs at 45622a104b471eb2e7922d0d560f7c925481c879
import { YAML } from "bun";
import { execFileSync } from "node:child_process";
import { lstatSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
function protectedSearchText(text) {
    return (
        text.includes("." + "env") ||
        /docker-compose\.override\.ya?ml|op-run-service-account/.test(text)
    )
}


export function imageVerdict(reference, source = "") {
  if (!/@sha256:[a-f0-9]{64}$/.test(reference)) return "missing SHA-256 digest";
  const name = reference.split("@")[0];
  const tag = name.slice(name.lastIndexOf("/") + 1).split(":")[1];
  if (!tag)
    return /resolved-from:\s*\S+/.test(source)
      ? null
      : "digest-only image needs resolved-from provenance";
  const postgres =
    /(?:^|\/)postgres:/.test(name) &&
    /^\d+\.\d+(?:-alpine\d+\.\d+)?$/.test(tag);
  if (
    !postgres &&
    !/^(?:v?\d+\.\d+\.\d+(?:[._-][\w.-]+)?|\d{4}-\d{2}-\d{2}[\w.-]*|RELEASE\.\d{4}-\d{2}-\d{2}T[\w.-]+)$/.test(
      tag,
    )
  ) {
    return "tag must name a full version; use digest-only with resolved-from provenance when upstream has no full-version tag";
  }
  return null;
}

function words(source) {
  return [...source.matchAll(/"(?:\\.|[^"\\])*"|'[^']*'|[^\s]+/g)].map(
    (match) => match[0].replace(/^["']|["']$/g, ""),
  );
}

function commandImage(source) {
  const tokens = words(source);
  const valueFlags = new Set([
    "-e",
    "--env",
    "--env-file",
    "-v",
    "--volume",
    "--mount",
    "-p",
    "--publish",
    "--name",
    "--network",
    "--net",
    "--platform",
    "--entrypoint",
    "--user",
    "-u",
    "--workdir",
    "-w",
    "--label",
    "-l",
    "--hostname",
    "--add-host",
    "--memory",
    "--cpus",
    "--shm-size",
    "--pull",
    "--restart",
    "--cap-add",
    "--cap-drop",
    "--security-opt",
    "--device",
    "--tmpfs",
    "--ulimit",
    "--pid",
    "--ipc",
    "--cidfile",
  ]);
  for (let i = 0; i < tokens.length; i += 1) {
    const token = tokens[i];
    if (valueFlags.has(token)) {
      i += 1;
      continue;
    }
    if (token.startsWith("-")) continue;
    return token;
  }
  return "";
}

function launchImage(tokens) {
  const globalValues = new Set([
    "--config",
    "--context",
    "-c",
    "--host",
    "-H",
    "--log-level",
    "-l",
    "--tlscacert",
    "--tlscert",
    "--tlskey",
    "--connection",
    "--url",
    "--identity",
  ]);
  let index = 0;
  while (tokens[index]?.startsWith("-")) {
    index += globalValues.has(tokens[index]) ? 2 : 1;
  }
  if (tokens[index] === "container") index += 1;
  if (!["run", "pull", "create"].includes(tokens[index])) return null;
  return commandImage(
    tokens
      .slice(index + 1)
      .map((token) => JSON.stringify(token))
      .join(" "),
  );
}

function parseJsonc(source) {
  const withoutComments = source.replace(
    /("(?:\\.|[^"\\])*")|\/\/[^\r\n]*|\/\*[\s\S]*?\*\//g,
    (whole, string) => string ?? "",
  );
  return JSON.parse(
    withoutComments.replace(
      /("(?:\\.|[^"\\])*")|,\s*([}\]])/g,
      (whole, string, closing) => string ?? closing,
    ),
  );
}

export function scanImageSource(file, source) {
  const references = [];
  const dynamic = [];
  const stages = new Set(["scratch"]);
  const bindings = new Map();
  const lines = source.split(/\r?\n/);
  const dockerfile =
    /(?:^|\/)(?:Dockerfile[^/]*|[^/]*\.Dockerfile|Containerfile[^/]*)$/i.test(
      file,
    );
  const structured =
    /(?:\.github\/(?:workflows|actions)\/|compose[^/]*\.ya?ml$|docker-compose[^/]*\.ya?ml$|\.devcontainer(?:\/|\.json)|(?:k8s|kubernetes|helm|charts)\/|container-images\.json$|railway|dokploy)/i.test(
      file,
    ) ||
    (/\.ya?ml$/.test(file) &&
      /^\s*(?:apiVersion|services|jobs):/m.test(source));
  const helmTemplate =
    /(?:^|\/)(?:charts|helm)\//.test(file) &&
    /(?:^|\/)templates\//.test(file) &&
    source.includes("{{");
  const add = (reference, line, kind) => {
    if (typeof reference !== "string") return;
    const resolved = reference.replace(
      /\$\{([A-Za-z_]\w*)\}|\$([A-Za-z_]\w*)/g,
      (whole, a, b) => bindings.get(a ?? b) ?? whole,
    );
    if (stages.has(resolved.toLowerCase()) || /^\d+$/.test(resolved)) return;
    const row = { file, line, kind, reference: resolved };
    if (/[${}`]/.test(resolved)) {
      dynamic.push(row);
      return;
    }
    if (
      !references.some(
        (existing) => existing.line === line && existing.reference === resolved,
      )
    ) {
      references.push({
        ...row,
        error: imageVerdict(
          resolved,
          lines.slice(Math.max(0, line - 2), line + 1).join("\n"),
        ),
      });
    }
  };
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const binding = line.match(
      /^\s*(?:ARG\s+|(?:export\s+)?(?:const|let|var)\s+)?([A-Za-z_]\w*)\s*=\s*["']?([^\s"';]+)["']?\s*;?\s*$/,
    );
    if (binding) {
      bindings.set(binding[1], binding[2]);
      if (
        /(?:^|_)IMAGE$/.test(binding[1]) &&
        /[:/]/.test(binding[2]) &&
        !binding[2].startsWith("/")
      )
        add(binding[2], i + 1, "binding");
    }
    if (dockerfile) {
      const syntax = line.match(/^#\s*syntax=(\S+)/);
      if (syntax) add(syntax[1], i + 1, "frontend");
      const from = line.match(
        /^\s*FROM\s+(?:--platform=\S+\s+)?(\S+)(?:\s+AS\s+(\S+))?/i,
      );
      if (from) {
        add(from[1], i + 1, "base");
        if (from[2]) stages.add(from[2].toLowerCase());
      }
      for (const match of line.matchAll(/(?:COPY|RUN).*?--from=(\S+)/gi))
        add(match[1], i + 1, "copy");
      for (const mount of line.matchAll(/--mount=([^\s]+)/g)) {
        const from = mount[1]
          .split(",")
          .find((option) => option.startsWith("from="));
        if (from) add(from.slice(5), i + 1, "mount");
      }
    }
    if (/\.ya?ml$/.test(file))
      for (const match of line.matchAll(/docker:\/\/([^\s"'`]+)/g))
        add(match[1], i + 1, "action");
    for (const match of line.matchAll(
      /(?:new\s+\w*Container|DockerImageName\.parse|withDockerImage)\s*\(\s*["'`]([^"'`]+)["'`]/g,
    ))
      add(match[1], i + 1, "testcontainer");
    if (structured) {
      const assignment = line.match(
        /^\s*(?:-\s+)?(?:image|container|builder_container)\s*:\s*["']?([^\s"'#]+)["']?\s*(?:#.*)?$/,
      );
      if (assignment && !["|", ">", "false", "true"].includes(assignment[1]))
        add(assignment[1], i + 1, "config");
      if (helmTemplate && !assignment && /{{/.test(line)) {
        const image = line.match(/^\s*(?:-\s+)?image\s*:\s*(.+)$/);
        if (image) add(image[1].replace(/^["']|["']$/g, ""), i + 1, "helm");
      }
    }
    if (!/\.[cm]?[jt]sx?$/.test(file)) {
      const driver = line.match(/--driver-opt(?:=|\s+)["']?image=([^\s"',]+)/);
      if (driver) add(driver[1], i + 1, "builder");
    }
    if (!/\.[cm]?[jt]sx?$/.test(file) && /\b(?:docker|podman)\s+/.test(line)) {
      const start = i;
      let end = i;
      let command = line;
      while (/\\\s*$/.test(command) && end + 1 < lines.length)
        command = command.replace(/\\\s*$/, " ") + lines[++end].trim();
      for (const match of command.matchAll(/\b(?:docker|podman)\s+/g)) {
        const image = launchImage(
          words(command.slice(match.index + match[0].length)),
        );
        if (image !== null) {
          add(image, start + 1, "command");
          i = end;
          break;
        }
      }
    }
    if (
      !/\.[cm]?[jt]sx?$/.test(file) &&
      /\bbuildx\s+create\b/.test(line) &&
      /--driver(?:=|\s+)docker-container/.test(line) &&
      !/--driver-opt(?:=|\s+)["']?image=/.test(line)
    ) {
      references.push({
        file,
        line: i + 1,
        kind: "builder",
        reference: "moby/buildkit:buildx-stable-1",
        error:
          "docker-container builder needs explicit pinned --driver-opt image=",
      });
    }
  }
  if (/\.[cm]?[jt]sx?$/.test(file)) {
    const lineAt = (offset) => source.slice(0, offset).split("\n").length;
    for (const match of source.matchAll(
      /(?:const|let|var)\s+(\w*IMAGE)\s*=\s*["'`]([^"'`]+)["'`]/g,
    )) {
      bindings.set(match[1], match[2]);
      if (/[:/]/.test(match[2])) add(match[2], lineAt(match.index), "binding");
    }
    for (const match of source.matchAll(
      /(?:execFileSync|execFile|spawnSync|spawn|run)\s*\(\s*["'](?:docker|podman)["']\s*,\s*\[([\s\S]*?)\]/g,
    )) {
      const tokens = [
        ...match[1].matchAll(/"(?:\\.|[^"\\])*"|'[^']*'|`[^`]*`|[^,\s]+/g),
      ].map((token) =>
        /^["'`]/.test(token[0]) ? token[0].slice(1, -1) : "$" + token[0],
      );
      const image = launchImage(tokens);
      if (image !== null) add(image, lineAt(match.index), "command");
    }
    if (/["'](?:docker|podman)["']/.test(source)) {
      for (const definition of source.matchAll(
        /function\s+(\w+)\s*\(([^)]*)\)/g,
      )) {
        const imageIndex = definition[2]
          .split(",")
          .map((parameter) => parameter.trim())
          .indexOf("image");
        if (imageIndex < 0) continue;
        const calls = new RegExp(
          "\\b" + definition[1] + "\\s*\\(([^)]*)\\)",
          "g",
        );
        for (const call of source.matchAll(calls)) {
          const argument = call[1].split(",")[imageIndex]?.trim();
          const image = argument?.match(/^["'`]([^"'`]+)["'`]$/);
          if (image) add(image[1], lineAt(call.index), "command");
        }
      }
    }
  }
  if (
    (structured && !helmTemplate && /\.(?:ya?ml|jsonc?)$/.test(file)) ||
    /image-inputs\.lock\.json$/.test(file)
  ) {
    let document;
    try {
      document = /\.jsonc?$/.test(file)
        ? parseJsonc(source)
        : YAML.parse(source);
    } catch {
      return {
        references,
        dynamic,
        parseError: file + ": invalid image configuration",
      };
    }
    const inlineLines = lines.flatMap((text, index) =>
      /^\s*dockerfile_inline\s*:/.test(text) ? [index + 1] : [],
    );
    let inlineIndex = 0;
    const visit = (value, keys = []) => {
      if (!value || typeof value !== "object") return;
      for (const [key, child] of Object.entries(value)) {
        if (key === "dockerfile_inline" && typeof child === "string") {
          const nested = scanImageSource("Dockerfile", child);
          const offset = inlineLines[inlineIndex++] ?? 0;
          references.push(
            ...nested.references.map((row) => ({
              ...row,
              file,
              line: row.line + offset,
            })),
          );
          dynamic.push(
            ...nested.dynamic.map((row) => ({
              ...row,
              file,
              line: row.line + offset,
            })),
          );
        }
        if (
          ["image", "container", "builder_container", "dockerImage"].includes(
            key,
          ) &&
          typeof child === "string" &&
          !references.some((row) => row.reference === child) &&
          !dynamic.some((row) => row.reference === child)
        ) {
          const line = lines.findIndex((text) => text.includes(child)) + 1;
          add(child, Math.max(1, line), "config");
        }
        if (
          key === "image" &&
          child?.repository &&
          typeof child.repository === "string"
        ) {
          const reference =
            child.repository +
            (child.tag ? ":" + child.tag : "") +
            (child.digest ? "@" + child.digest : "");
          add(
            reference,
            lines.findIndex((text) => text.includes(child.repository)) + 1,
            "helm",
          );
        }
        if (
          key === "uses" &&
          typeof child === "string" &&
          child.startsWith("docker/setup-buildx-action@")
        ) {
          const options = value.with?.["driver-opts"] ?? "";
          const image = options.match(/(?:^|[\s,])image=([^\s,]+)/);
          if (image)
            add(
              image[1],
              lines.findIndex((text) => text.includes(image[1])) + 1,
              "builder",
            );
          if (!/image=\S+@sha256:[a-f0-9]{64}/.test(options))
            references.push({
              file,
              line: lines.findIndex((text) => text.includes(child)) + 1,
              kind: "builder",
              reference: "moby/buildkit:buildx-stable-1",
              error: "setup-buildx-action needs pinned image in driver-opts",
            });
        }
        visit(child, [...keys, key]);
      }
    };
    visit(document);
  }
  return { references, dynamic };
}

export function scanRepository(root) {
  const files = execFileSync("git", ["ls-files", "-z"], {
    cwd: root,
    encoding: "utf8",
    maxBuffer: 16 * 1024 * 1024,
  })
    .split("\0")
    .filter(Boolean);
  const result = { references: [], dynamic: [], parseErrors: [] };
  let provenance = [];
  if (files.includes("container-image-provenance.json")) {
    try {
      const absolute = path.join(root, "container-image-provenance.json");
      if (lstatSync(absolute).isSymbolicLink()) throw new Error("symlink");
      provenance = JSON.parse(readFileSync(absolute, "utf8"));
      if (
        !Array.isArray(provenance) ||
        provenance.some(
          (row) =>
            !row ||
            typeof row.file !== "string" ||
            !files.includes(row.file) ||
            typeof row.reference !== "string" ||
            !/^[^@]+@sha256:[a-f0-9]{64}$/.test(row.reference) ||
            !/^[^\s@]+:[^\s@]+$/.test(row.resolvedFrom ?? "") ||
            !files.includes(row.evidence) ||
            protectedSearchText(row.evidence),
        )
      )
        throw new Error("invalid provenance");
    } catch {
      result.parseErrors.push("invalid container-image-provenance.json");
    }
  }
  for (const file of files) {
    if (
      protectedSearchText(file) ||
      /(?:^|\/)(?:node_modules|vendor|dist|memory|knowledge)\//.test(file) ||
      /\.(?:md|mdx|txt|lock|jsonl|svg|html|csv)$/.test(file)
    )
      continue;
    const absolute = path.join(root, file);
    if (!lstatSync(absolute).isFile() || lstatSync(absolute).isSymbolicLink())
      continue;
    const buffer = readFileSync(absolute);
    if (buffer.includes(0)) continue;
    const scan = scanImageSource(file, buffer.toString("utf8"));
    for (const row of scan.references) {
      if (
        row.error === "digest-only image needs resolved-from provenance" &&
        provenance.some(
          (entry) =>
            entry.file === row.file && entry.reference === row.reference,
        )
      )
        row.error = null;
    }
    result.references.push(...scan.references);
    result.dynamic.push(...scan.dynamic);
    if (scan.parseError) result.parseErrors.push(scan.parseError);
  }
  return result;
}

if (
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  const root = path.resolve(process.argv[2] ?? ".");
  const result = scanRepository(root);
  for (const row of result.references.filter((row) => row.error))
    console.error(`${row.file}:${row.line}: ${row.reference}: ${row.error}`);
  for (const error of result.parseErrors) console.error(error);
  const failures =
    result.references.filter((row) => row.error).length +
    result.parseErrors.length;
  console.log(
    JSON.stringify({
      filesRoot: root,
      references: result.references.length,
      dynamicReferences: result.dynamic.length,
      failures,
    }),
  );
  process.exitCode = failures ? 1 : 0;
}
