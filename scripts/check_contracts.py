#!/usr/bin/env python3
"""Check tool names and flat list/filing examples against a pinned released catalog slice."""
import argparse
import datetime
import json
from pathlib import Path
import re
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "tests/fixtures/mcp-contract.json"


def refresh(source, revision):
    catalog = json.loads(Path(source).read_text())
    selected = {
        "clm_list_contracts", "clm_list_parties", "clm_list_folders", "clm_get_folder",
        "clm_create_folder", "clm_rename_folder", "clm_move_folder", "clm_move_contract",
        "clm_get_folder_access", "clm_get_contract_access",
    }
    snapshot = {
        "source": "Contracko released MCP catalog",
        "revision": revision,
        "tools": [
            {"name": tool["name"],
             "introducedInCapabilityPolicyVersion": tool["introducedInCapabilityPolicyVersion"],
             **({"inputSchema": tool["inputSchema"]} if tool["name"] in selected else {})}
            for tool in catalog["tools"]
        ],
    }
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(snapshot, indent=2) + "\n")


def validate_value(key, value, rule):
    if "anyOf" in rule:
        for alternative in rule["anyOf"]:
            try:
                validate_value(key, value, alternative)
                return
            except (ValueError, TypeError):
                pass
        raise ValueError(f"Invalid {key}")
    kind = rule.get("type")
    if kind == "null":
        if value is not None:
            raise ValueError(f"{key} must be null")
        return
    if kind not in ("string", "integer", "number"):
        raise ValueError(f"Unsupported example schema for {key}: {kind}")
    if kind == "string" and not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    if kind in ("integer", "number") and (isinstance(value, bool) or not isinstance(value, (int, float))):
        raise ValueError(f"{key} must be numeric")
    if kind == "integer" and int(value) != value:
        raise ValueError(f"{key} must be an integer")
    if isinstance(value, str):
        if len(value) < rule.get("minLength", 0) or len(value) > rule.get("maxLength", float("inf")):
            raise ValueError(f"Invalid length for {key}")
        if "pattern" in rule and not re.search(rule["pattern"], value):
            raise ValueError(f"Invalid pattern for {key}")
    if "enum" in rule and value not in rule["enum"]:
        raise ValueError(f"Invalid {key}")
    if "minimum" in rule and value < rule["minimum"]:
        raise ValueError(f"{key} below minimum")
    if "maximum" in rule and value > rule["maximum"]:
        raise ValueError(f"{key} above maximum")
    if rule.get("format") == "uuid":
        uuid.UUID(value)
    if rule.get("format") == "date":
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError(f"Invalid date {key}")
        datetime.date.fromisoformat(value)


def validate_call(name, args, tools):
    if name not in tools or "inputSchema" not in tools[name]:
        raise ValueError(f"No pinned example schema for {name}")
    schema = tools[name]["inputSchema"]
    if not isinstance(args, dict):
        raise ValueError("Arguments must be an object")
    properties = schema.get("properties", {})
    for key in schema.get("required", []):
        if key not in args:
            raise ValueError(f"Missing {key}")
    for key, value in args.items():
        if key not in properties:
            raise ValueError(f"Unknown argument {name}.{key}")
        validate_value(key, value, properties[key])
    for prefix in ("endDate", "noticeDate"):
        lower, upper = args.get(prefix + "From"), args.get(prefix + "To")
        if lower and upper and lower > upper:
            raise ValueError(f"Reversed {prefix} window")


def check(root):
    tools = {tool["name"]: tool for tool in json.loads(CATALOG.read_text())["tools"]}
    failures = []
    examples = 0
    paths = list((root / "skills").rglob("*.md"))
    paths += [path for path in (root / "README.md", root / "agent-setup/prompt.md") if path.exists()]
    for path in sorted(paths):
        text = path.read_text()
        for name in set(re.findall(r"\b(?:clm_|parser_)[a-z_]+\b|\bauth_validate\b", text)):
            if name not in tools:
                failures.append(f"{path.relative_to(root)}: unknown tool {name}")
        for name, body in re.findall(r"```json mcp:(\w+)\n(.*?)\n```", text, re.S):
            examples += 1
            try:
                validate_call(name, json.loads(body), tools)
            except (ValueError, TypeError) as error:
                failures.append(f"{path.relative_to(root)}: {error}")
        for stale in (
            "Metadata filters still do not exist", "Listing does not filter", "No server-side list filters",
            "the outcome is that nothing was written", "folderId` you can read and cannot set",
            "Creating folders and moving contracts is app work", "folderId` is readable, not settable",
            "You still create folders and move contracts in the Contracko app",
        ):
            if stale in text:
                failures.append(f"{path.relative_to(root)}: obsolete guidance: {stale}")
    if not examples:
        failures.append("No checked MCP call examples found")
    for failure in failures:
        print(failure, file=sys.stderr)
    print(f"Checked {len(tools)} tool names and {examples} list/filing examples")
    return bool(failures)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--refresh", help="Path to a reviewed, released MCP catalog JSON")
    parser.add_argument("--revision", help="Immutable app commit for the reviewed catalog")
    options = parser.parse_args()
    if options.refresh:
        if not re.fullmatch(r"[a-f0-9]{40}", options.revision or ""):
            parser.error("--refresh requires a full --revision SHA")
        refresh(options.refresh, options.revision)
    else:
        sys.exit(check(options.root))
