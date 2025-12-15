# Provenance: Developed collaboratively by Subi Rajagopalan and ChatGPT (GPT-5.1 Thinking)
# checklist_builder.py
# Version: v0.2.0
# Design notes: Builds task-type checklist HTML files from an Excel spec and an HTML template.
#               Also supports initializing new template files from a base template.
# Last updated: 2025-11-14

import argparse
import json
from pathlib import Path
from typing import Optional

import pandas as pd


REQUIRED_HEADER_FIELDS = [
    "APP_TITLE",
    "APP_TITLE_VISIBLE",
    "META_REPO",
    "META_ENTITY",
    "META_SOP_DEFAULT",
    "META_IMG_FOLDER_DEF",
    "RUN_LABEL_DEFAULT",
]

# Default base template used when creating new templates
DEFAULT_BASE_TEMPLATE = Path("templates/SOP_Build_Checklist_template_v3_3.html")


def load_header(sheet: pd.DataFrame) -> dict:
    """
    Convert Header sheet (Field/Value) into a dict.
    """
    header = {}
    for _, row in sheet.iterrows():
        field = str(row.get("Field", "")).strip()
        value = "" if pd.isna(row.get("Value")) else str(row.get("Value"))
        if field:
            header[field] = value

    # Ensure all expected keys exist (fill blanks if missing)
    for key in REQUIRED_HEADER_FIELDS:
        header.setdefault(key, "")

    return header


def load_steps(sheet: pd.DataFrame) -> list:
    """
    Convert Steps sheet into a list of step dicts suitable for embedding
    in the checklist HTML.
    """
    if sheet.empty:
        return []

    # Ensure StepOrder exists, otherwise create a default sequence
    if "StepOrder" not in sheet.columns:
        sheet["StepOrder"] = range(1, len(sheet) + 1)

    # Sort by StepOrder (numeric if possible)
    try:
        sheet["StepOrder_numeric"] = pd.to_numeric(sheet["StepOrder"])
        sheet = sheet.sort_values("StepOrder_numeric")
    except Exception:
        # Fallback: sort as strings
        sheet = sheet.sort_values("StepOrder", kind="stable")

    steps = []

    def s(val) -> str:
        return "" if pd.isna(val) else str(val)

    for _, row in sheet.iterrows():
        step_order = row.get("StepOrder", "")
        step_id = row.get("StepID", "")
        title = row.get("Title", "")
        input_needed = row.get("InputNeeded", "")
        program = row.get("Program", "")
        command = row.get("Command", "")
        variants = row.get("Variants", "")
        expected_file = row.get("ExpectedOutputFile", "")
        expected_folder = row.get("ExpectedOutputFolder", "")
        hints = row.get("Hints", "")
        phase = row.get("Phase", "")

        # Build a combined reminder text (multi-line) from the fields
        rem_lines = []
        if s(input_needed):
            rem_lines.append(f"Inputs needed: {s(input_needed)}")
        if s(program):
            rem_lines.append(f"Program: {s(program)}")
        if s(variants):
            rem_lines.append(f"Variants: {s(variants)}")
        if s(expected_file) or s(expected_folder):
            rem_lines.append(
                f"Expected output: {s(expected_file)} in {s(expected_folder)}".strip()
            )
        if s(hints):
            rem_lines.append(f"Hints: {s(hints)}")
        reminder_text = "\n".join(rem_lines)

        step_dict = {
            "id": f"step{step_order}" if s(step_order) else f"step{len(steps) + 1}",
            "order": s(step_order),
            "step_id": s(step_id),
            "title": s(title),
            "inputs": s(input_needed),
            "program": s(program),
            "command": s(command),
            "variants": s(variants),
            "expected_file": s(expected_file),
            "expected_folder": s(expected_folder),
            "hints": s(hints),
            "phase": s(phase),
            "reminder": reminder_text,
            # Interactive fields – start empty; UI will fill these
            "notes": "",
            "runs": [],
        }
        steps.append(step_dict)

    return steps


def embed_steps_json(html: str, steps: list) -> str:
    """
    Replace the {{STEPS_JSON}} placeholder with a JSON representation of `steps`.
    Also escape any closing </script> tags inside JSON.
    """
    steps_json = json.dumps(steps, indent=2)
    steps_json_safe = steps_json.replace("</script>", "<\\/script>")
    return html.replace("{{STEPS_JSON}}", steps_json_safe)


def embed_header_placeholders(html: str, header: dict) -> str:
    """
    Replace header placeholders in the template with values from header dict.
    """
    replacements = {
        "{{APP_TITLE}}": header.get("APP_TITLE", ""),
        "{{APP_TITLE_VISIBLE}}": header.get("APP_TITLE_VISIBLE", ""),
        "{{META_REPO}}": header.get("META_REPO", ""),
        "{{META_ENTITY}}": header.get("META_ENTITY", ""),
        "{{META_SOP_DEFAULT}}": header.get("META_SOP_DEFAULT", ""),
        "{{META_IMG_FOLDER_DEF}}": header.get("META_IMG_FOLDER_DEF", ""),
        "{{RUN_LABEL_DEFAULT}}": header.get("RUN_LABEL_DEFAULT", ""),
    }

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    return html


def slugify(value: str) -> str:
    """
    Simple slug: keep alphanumerics, underscores, and hyphens.
    Replace spaces with underscores.
    """
    value = value.strip().replace(" ", "_")
    cleaned = "".join(ch for ch in value if ch.isalnum() or ch in ("_", "-"))
    return cleaned or "Checklist"


def build_output_path(
    spec_path: Path, header: dict, out_html: Optional[str]
) -> Path:
    """
    Determine the output HTML path.

    Priority:
    1. If out_html is provided, use that.
    2. Else, use META_SOP_DEFAULT (slugified) if present.
    3. Else, use APP_TITLE_VISIBLE (slugified) if present.
    4. Else, fall back to <spec_stem>_Checklist.html.
    """
    if out_html:
        return Path(out_html)

    default_dir = Path("rep_checklists")
    default_dir.mkdir(parents=True, exist_ok=True)

    sop_default = (header.get("META_SOP_DEFAULT") or "").strip()
    if sop_default:
        filename = f"{slugify(sop_default)}_Checklist.html"
        return default_dir / filename

    app_title_vis = (header.get("APP_TITLE_VISIBLE") or "").strip()
    if app_title_vis:
        filename = f"{slugify(app_title_vis)}_Checklist.html"
        return default_dir / filename

    spec_stem = spec_path.stem
    filename = f"{spec_stem}_Checklist.html"
    return default_dir / filename


def init_template(new_template_path: Path, base_template_path: Optional[Path]) -> None:
    """
    Create a new template file by copying from a base template and stamping provenance.
    """
    base_path = base_template_path or DEFAULT_BASE_TEMPLATE

    if not base_path.is_file():
        raise FileNotFoundError(
            f"Base template not found: {base_path}\n"
            "Provide --base-template explicitly or ensure the default exists."
        )

    new_template_path.parent.mkdir(parents=True, exist_ok=True)

    base_html = base_path.read_text(encoding="utf-8")

    provenance_comment = (
        "<!--\n"
        "  Provenance: Developed collaboratively by Subi Rajagopalan and ChatGPT (GPT-5.1 Thinking)\n"
        f"  Template: {new_template_path.name}\n"
        f"  Created from base: {base_path.name}\n"
        "-->\n"
    )

    # Prepend the comment to the base template
    new_html = provenance_comment + base_html
    new_template_path.write_text(new_html, encoding="utf-8")

    print(f"New template created: {new_template_path}")
    print(f"  (Base template: {base_path})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a task-type interactive checklist HTML from an Excel spec and an HTML template,\n"
            "or initialize a new template from an existing base template."
        )
    )

    # Mode A: build checklist
    parser.add_argument(
        "--spec",
        required=False,
        help="Path to Excel spec file with 'Header' and 'Steps' sheets.",
    )
    parser.add_argument(
        "--template",
        required=False,
        help="Path to HTML template file (e.g., SOP_Build_Checklist_template_v3_3.html).",
    )
    parser.add_argument(
        "--out-html",
        required=False,
        help=(
            "Optional output HTML path. If omitted, the name is derived from the Header "
            "(META_SOP_DEFAULT or APP_TITLE_VISIBLE) or the spec filename."
        ),
    )

    # Mode B: init template
    parser.add_argument(
        "--init-template",
        required=False,
        help=(
            "Create a new template file at this path, copying from a base template. "
            "When using this, do NOT pass --spec/--template/--out-html."
        ),
    )
    parser.add_argument(
        "--base-template",
        required=False,
        help=(
            "Base HTML template to copy when using --init-template. "
            "If omitted, defaults to templates/SOP_Build_Checklist_template_v3_3.html."
        ),
    )

    args = parser.parse_args()

    # Mode B: Initialize a new template and exit
    if args.init_template:
        if args.spec or args.template or args.out_html:
            parser.error(
                "When using --init-template, do NOT pass --spec, --template, or --out-html."
            )
        new_template_path = Path(args.init_template)
        base_template_path = Path(args.base_template) if args.base_template else None
        init_template(new_template_path, base_template_path)
        return

    # Mode A: Build checklist
    if not args.spec or not args.template:
        parser.error(
            "To build a checklist, you must provide both --spec and --template "
            "(or use --init-template to create a new template)."
        )

    spec_path = Path(args.spec)
    template_path = Path(args.template)

    if not spec_path.is_file():
        raise FileNotFoundError(f"Spec Excel file not found: {spec_path}")

    if not template_path.is_file():
        raise FileNotFoundError(f"Template HTML file not found: {template_path}")

    # Load Excel sheets
    try:
        xls = pd.read_excel(spec_path, sheet_name=None)
    except Exception as e:
        raise RuntimeError(f"Failed to read spec Excel file: {e}") from e

    if "Header" not in xls:
        raise KeyError("Spec Excel must contain a 'Header' sheet.")
    if "Steps" not in xls:
        raise KeyError("Spec Excel must contain a 'Steps' sheet.")

    header_sheet = xls["Header"]
    steps_sheet = xls["Steps"]

    header = load_header(header_sheet)
    steps = load_steps(steps_sheet)

    # Read template HTML
    html_text = template_path.read_text(encoding="utf-8")

    # Embed header and steps
    html_text = embed_header_placeholders(html_text, header)
    html_text = embed_steps_json(html_text, steps)

    # Determine output path based on header or CLI override
    out_path = build_output_path(spec_path, header, args.out_html)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_text, encoding="utf-8")

    print(f"Checklist built successfully: {out_path}")


if __name__ == "__main__":
    main()
