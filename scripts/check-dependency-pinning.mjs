import { readFileSync, readdirSync } from 'node:fs';

const manifests = ["packages/mcp/package.json"];
const exactVersion = /^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;
const failures = [];

for (const file of manifests) {
  const manifest = JSON.parse(readFileSync(new URL('../' + file, import.meta.url), 'utf8'));
  if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest)) throw new Error(file + ': manifest must be an object');
  for (const section of ['dependencies', 'devDependencies', 'optionalDependencies']) {
    const dependencies = manifest[section] ?? {};
    if (typeof dependencies !== 'object' || Array.isArray(dependencies)) throw new Error(file + ': invalid ' + section);
    for (const [name, value] of Object.entries(dependencies)) {
      if (typeof value === 'string' && /^(?:file|link|workspace):\S+$/.test(value)) continue;
      const version = typeof value === 'string' && value.startsWith('npm:') ? value.slice(value.lastIndexOf('@') + 1) : value;
      if (typeof version !== 'string' || !exactVersion.test(version)) failures.push(file + ': ' + section + '.' + name + ' must use an exact version');
    }
  }
}

const workflowFiles = readdirSync(new URL('../.github/workflows/', import.meta.url))
  .filter((name) => /\.ya?ml$/.test(name))
  .map((name) => '.github/workflows/' + name);
const commandFiles = ["README.md","DISTRIBUTION.md","packages/mcp/README.md","CHANGELOG.md"];
const findings = [];
const exceptions = JSON.parse(readFileSync(new URL('../.pinning-exceptions.json', import.meta.url), 'utf8'));
const today = new Date().toISOString().slice(0, 10);
for (const entry of exceptions) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(entry.expires) || entry.expires < today || !entry.reason) {
    failures.push('Invalid or expired pinning exception: ' + entry.match);
  }
}
function finding(rule, file, reference) {
  findings.push({ rule, match: file + ':' + reference });
}
for (const file of manifests) {
  const manifest = JSON.parse(readFileSync(new URL('../' + file, import.meta.url), 'utf8'));
  if (manifest.engines?.node && !exactVersion.test(manifest.engines.node)) {
    finding('node-version', file, 'engines.node=' + manifest.engines.node);
  }
}
for (const file of workflowFiles) {
  const source = readFileSync(new URL('../' + file, import.meta.url), 'utf8');
  for (const match of source.matchAll(/\buses:\s*["']?([^\s"'#]+)/g)) {
    if (!match[1].startsWith('./') && !/@[a-f0-9]{40}$/.test(match[1])) finding('action-sha', file, match[1]);
  }
  for (const match of source.matchAll(/\bnode-version:\s*["']?([^\s"'#]+)/g)) {
    if (!exactVersion.test(match[1])) finding('node-version', file, 'node-version=' + match[1]);
  }
}
for (const file of commandFiles) {
  const source = readFileSync(new URL('../' + file, import.meta.url), 'utf8');
  for (const match of source.matchAll(/(?:^|[\n`])\s*npx\s+(?:-y\s+)?((?:@[a-z0-9_.-]+\/)?[a-z0-9_.-]+(?:@[^\s`"'\)]+)?)/gi)) {
    const separator = match[1].lastIndexOf('@');
    if (separator <= 0 || !exactVersion.test(match[1].slice(separator + 1))) finding('tool-version', file, 'npx ' + match[1]);
  }
}
for (const row of findings) {
  if (!exceptions.some((entry) => entry.rule === row.rule && entry.match === row.match && entry.expires >= today)) failures.push(row.match + ' must be pinned');
}

if (failures.length) {
  console.error(failures.join('\n'));
  process.exitCode = 1;
} else {
  console.log('Dependency pinning checks passed.');
}
