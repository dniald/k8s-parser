#!/usr/bin/env python3
import argparse
import os
import sys
import json
import re

def parse_simple_yaml(yaml_str):
    lines = yaml_str.splitlines()
    root = {}
    # Stack entries: (indent_level, container, last_key)
    stack = [(-1, root, None)]

    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue

        indent = len(line) - len(line.lstrip(' '))
        content = line.lstrip(' ')

        # Pop until correct parent frame
        while stack and indent <= stack[-1][0]:
            stack.pop()
        indent_parent, parent, last_key = stack[-1]

        # If parent is list and current is mapping, target last dict
        if isinstance(parent, list) and not content.startswith('- '):
            if not parent or not isinstance(parent[-1], dict):
                raise ValueError("Cannot nest mapping under non-dict list item")
            parent = parent[-1]
            last_key = None

        # Handle list items
        if content.startswith('- '):
            item_str = content[2:].strip()
            # If parent is dict and last_key exists, convert to list
            if isinstance(parent, dict) and last_key:
                lst = []  # new list for this key
                parent[last_key] = lst
                # Update stack frame
                stack[-1] = (indent_parent, lst, None)
                parent = lst

            if not isinstance(parent, list):
                raise ValueError("List item must follow a key or be under a list")

            # Parse item
            if ':' in item_str:
                k, v = [p.strip() for p in item_str.split(':', 1)]
                if v == '':
                    obj = {k: {}}
                    parent.append(obj)
                    stack.append((indent, obj[k], None))
                else:
                    parent.append({k: parse_value(v)})
            else:
                parent.append(parse_value(item_str))
            continue

        # Handle mapping entries
        if ':' in content:
            key, val = [p.strip() for p in content.split(':', 1)]
            if val == '':
                # nested dict
                parent[key] = {}
                stack[-1] = (stack[-1][0], parent, key)
                stack.append((indent, parent[key], None))
            else:
                parent[key] = parse_value(val)
                stack[-1] = (stack[-1][0], parent, key)
        else:
            # Fallback: treat as key with None
            parent[content] = None
            stack[-1] = (stack[-1][0], parent, content)

    return root


def parse_value(val):
    """Convert scalar YAML values to Python types."""
    lower = val.lower()
    if lower in ('null', 'none', '~'):
        return None
    if lower == 'true':
        return True
    if lower == 'false':
        return False
    if re.match(r'^-?\d+(\.\d+)?$', val):
        return int(val) if '.' not in val else float(val)
    return val.strip('"').strip("'")


def validate_k8s_resource(obj):
    """Basic validation for Kubernetes resources."""
    required = {'apiVersion', 'kind', 'metadata'}
    missing = required - obj.keys()
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

def yaml_to_json(yaml_str):
    obj = parse_simple_yaml(yaml_str)
    validate_k8s_resource(obj)
    return json.dumps(obj, indent=2)

# ——— CLI handling ———
def main():
    parser = argparse.ArgumentParser(description="K8s YAML → JSON converter")
    parser.add_argument(
        "source",
        nargs='?',  # make optional for stdin
        help="Path to .yaml file, raw YAML string, or omit to read from STDIN"
    )
    parser.add_argument(
        "-o", "--output",
        default="output.json",
        help="Output JSON file path"
    )
    args = parser.parse_args()

    # Determine YAML input source
    if args.source and os.path.isfile(args.source):
        yaml_content = open(args.source).read()
    elif args.source:
        yaml_content = args.source
    else:
        # No source: read from STDIN
        yaml_content = sys.stdin.read()

    try:
        json_out = yaml_to_json(yaml_content)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Print to stdout
    print(json_out)
    # Write to file
    with open(args.output, 'w') as f:
        f.write(json_out)
    print(f"\n➡️ JSON also saved to {args.output}", file=sys.stderr)

if __name__ == '__main__':
    main()
