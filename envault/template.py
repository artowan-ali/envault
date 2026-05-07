"""Template rendering for envault — substitute vault values into text templates."""

import re
from typing import Optional

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_template(template: str, values: dict, strict: bool = False) -> str:
    """Replace {{KEY}} placeholders in *template* with values from *values*.

    Args:
        template: Raw template string containing ``{{KEY}}`` placeholders.
        values:   Mapping of variable names to their string values.
        strict:   If True, raise KeyError for any placeholder not found in
                  *values*.  If False, leave unresolved placeholders as-is.

    Returns:
        The rendered string.
    """
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key in values:
            return values[key]
        if strict:
            raise KeyError(f"Template placeholder '{{key}}' not found in vault")
        return match.group(0)  # leave unchanged

    return _PLACEHOLDER_RE.sub(replacer, template)


def render_file(src_path: str, values: dict, strict: bool = False) -> str:
    """Read a file and render it as a template.

    Args:
        src_path: Path to the template file.
        values:   Mapping of variable names to their string values.
        strict:   Passed through to :func:`render_template`.

    Returns:
        Rendered content as a string.
    """
    with open(src_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    return render_template(content, values, strict=strict)


def list_placeholders(template: str) -> list:
    """Return a sorted, deduplicated list of placeholder names in *template*."""
    return sorted(set(_PLACEHOLDER_RE.findall(template)))


def template_summary(template: str, values: dict) -> dict:
    """Return a summary dict describing placeholder resolution status.

    Returns:
        A dict with keys:
        - ``resolved``: list of placeholder names that were found in *values*.
        - ``missing``:  list of placeholder names not present in *values*.
    """
    placeholders = list_placeholders(template)
    resolved = [p for p in placeholders if p in values]
    missing = [p for p in placeholders if p not in values]
    return {"resolved": resolved, "missing": missing}
