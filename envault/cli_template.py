"""CLI commands for envault template rendering."""

import sys
from envault.template import render_file, render_template, list_placeholders, template_summary


def cmd_template_render(args, vault):
    """Render a template file using values from the vault.

    args attributes expected:
        template_file (str): path to the template.
        output (str|None):   path to write output; if None, print to stdout.
        strict (bool):       fail on unresolved placeholders.
    """
    values = {k: vault.get(k) for k in vault.list() if vault.get(k) is not None}

    try:
        rendered = render_file(args.template_file, values, strict=getattr(args, "strict", False))
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: template file '{args.template_file}' not found.", file=sys.stderr)
        sys.exit(1)

    if getattr(args, "output", None):
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(rendered)
        print(f"Rendered template written to '{args.output}'.")
    else:
        print(rendered, end="")


def cmd_template_check(args, vault):
    """Check which placeholders in a template are resolved / missing.

    args attributes expected:
        template_file (str): path to the template.
    """
    values = {k: vault.get(k) for k in vault.list() if vault.get(k) is not None}

    try:
        with open(args.template_file, "r", encoding="utf-8") as fh:
            content = fh.read()
    except FileNotFoundError:
        print(f"Error: template file '{args.template_file}' not found.", file=sys.stderr)
        sys.exit(1)

    summary = template_summary(content, values)
    if summary["resolved"]:
        print("Resolved:")
        for name in summary["resolved"]:
            print(f"  ✓ {name}")
    if summary["missing"]:
        print("Missing:")
        for name in summary["missing"]:
            print(f"  ✗ {name}")
    if not summary["resolved"] and not summary["missing"]:
        print("No placeholders found in template.")


def register_template_commands(subparsers):
    """Attach template sub-commands to an argparse subparsers group."""
    p_render = subparsers.add_parser("template-render", help="Render a template with vault values")
    p_render.add_argument("template_file", help="Path to the template file")
    p_render.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p_render.add_argument("--strict", action="store_true", help="Fail on unresolved placeholders")
    p_render.set_defaults(func=cmd_template_render)

    p_check = subparsers.add_parser("template-check", help="Check template placeholder resolution")
    p_check.add_argument("template_file", help="Path to the template file")
    p_check.set_defaults(func=cmd_template_check)
