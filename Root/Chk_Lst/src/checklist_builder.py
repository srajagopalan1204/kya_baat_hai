#!/usr/bin/env python3
"""
Provenance: Collaborative design between Subi Rajagopalan and ChatGPT (GPT-5.1 Thinking)
for the Kya_Baat_Hai / Root/Chk_Lst generic checklist builder.

Description:
    - Reads an Excel spec that defines the steps for a checklist.
    - Reads an HTML template that contains placeholders such as {{STEPS_JSON}},
      {{APP_TITLE}}, etc.
    - Emits a task-specific HTML checklist where:
        * Steps come entirely from the Excel spec.
        * Header/meta fields are filled from an optional Header sheet
          (or sensible defaults).
        * The UI uses v4c features: header, multi-run, enhancements log,
          insert-step-during-run, etc.

Usage (example):
    python src/checklist_builder.py \
      --spec /workspaces/kya_baat_hai/Root/Chk_Lst/specs/Checklist_TaskType_ICSP_Desc3_251114_1052.xlsx \
      --template /workspaces/kya_baat_hai/Root/Chk_Lst/templates/SOP_Build_Checklist_template_v4e.html \
      --out-html /workspaces/kya_baat_hai/Root/Chk_Lst/rep_checklists/ICSP_Desc3_Checklist.html

If --out-html is omitted, a default name using YYMMDD_HHMM is created in the
same folder as the spec.
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd


NY_TZ = ZoneInfo("America/New_York")


def col_lookup(df, *candidates):
    """
    Given a DataFrame and a list of candidate column names, return the actual
    column name found in df.columns (case-sensitive) or None.
    """
    cols = {str(c).strip(): c for c in df.columns}
    for name in candidates:
        if name in cols:
            return cols[name]
    # also try case-insensitive
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    for name in candidates:
        low = name.lower()
        if low in lower_map:
            return lower_map[low]
    return None


def load_steps_from_excel(spec_path: Path):
    """
    Load steps from the Excel 'Steps' sheet (or first sheet if not present).

    Expected typical columns (flexible names):
        - StepOrder / Order / Seq
        - StepID / Step Id / ID
        - Title
        - Command
        - InputNeeded
        - Hints
        - Program
        - Variants
        - Phase

    Returns:
        A list of dicts, each of which will be injected into {{STEPS_JSON}}.
    """
    xls = pd.ExcelFile(spec_path)
    sheet_name = "Steps" if "Steps" in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=sheet_name)

    # Column mappings
    col_order    = col_lookup(df, "StepOrder", "Order", "Seq")
    col_step_id  = col_lookup(df, "StepID", "Step Id", "ID")
    col_title    = col_lookup(df, "Title", "StepTitle")
    col_cmd      = col_lookup(df, "Command", "Cmd")
    col_input    = col_lookup(df, "InputNeeded", "Inputs")
    col_hints    = col_lookup(df, "Hints", "Hint")
    col_program  = col_lookup(df, "Program")
    col_variants = col_lookup(df, "Variants")
    col_phase    = col_lookup(df, "Phase")

    steps = []
    for idx, row in df.iterrows():
        # Skip rows that are almost completely empty
        if all(pd.isna(v) for v in row.values):
            continue

        # ORDER
        if col_order and not pd.isna(row.get(col_order)):
            try:
                order_val = int(row[col_order])
            except Exception:
                order_val = idx + 1
        else:
            order_val = idx + 1

        # ID
        raw_id = None
        if col_step_id and not pd.isna(row.get(col_step_id)):
            raw_id = str(row[col_step_id]).strip()
        if not raw_id:
            raw_id = f"step_{order_val}"

        # TITLE
        title_val = ""
        if col_title and not pd.isna(row.get(col_title)):
            title_val = str(row[col_title]).strip()
        else:
            title_val = raw_id

        # COMMAND
        cmd_parts = []
        if col_cmd and not pd.isna(row.get(col_cmd)):
            cmd_parts.append(str(row[col_cmd]).rstrip())
        if col_program and not pd.isna(row.get(col_program)):
            cmd_parts.append(f"[Program] {row[col_program]}")
        if col_variants and not pd.isna(row.get(col_variants)):
            cmd_parts.append(f"[Variants] {row[col_variants]}")
        command_val = "\n\n".join(cmd_parts).strip()

        # REMINDER (short text visible under the title)
        reminder_parts = []
        if col_input and not pd.isna(row.get(col_input)):
            reminder_parts.append(f"Inputs: {row[col_input]}")
        if col_hints and not pd.isna(row.get(col_hints)):
            reminder_parts.append(f"Hints: {row[col_hints]}")
        if col_phase and not pd.isna(row.get(col_phase)):
            reminder_parts.append(f"Phase: {row[col_phase]}")
        reminder_val = " | ".join(str(p) for p in reminder_parts if str(p).strip())

        step_obj = {
            "id": raw_id,
            "order": order_val,
            "title": title_val,
            "command": command_val,
            "reminder": reminder_val,
            "notes": "",
            "runs": []
        }
        steps.append(step_obj)

    # Sort by order field
    steps.sort(key=lambda s: s.get("order", 0))
    return steps


def load_header_meta_from_excel(spec_path: Path):
    """
    Optionally load header/meta from a 'Header' sheet.

    Expected shape (loose):
        First column: key (e.g., APP_TITLE, APP_TITLE_VISIBLE, META_ENTITY, etc.)
        Second column: value.

    Returns:
        dict of key -> value (strings), used to fill template placeholders.
    """
    meta = {}
    try:
        xls = pd.ExcelFile(spec_path)
    except Exception:
        return meta

    if "Header" not in xls.sheet_names:
        return meta

    df = pd.read_excel(xls, sheet_name="Header")
    if df.shape[1] < 2:
        return meta

    for _, row in df.iterrows():
        key = str(row.iloc[0]).strip() if not pd.isna(row.iloc[0]) else ""
        if not key:
            continue
        val = "" if pd.isna(row.iloc[1]) else str(row.iloc[1]).strip()
        meta[key] = val

    return meta


def build_default_meta(spec_path: Path, excel_meta: dict):
    """
    Combine Excel meta (from Header sheet) with sensible defaults to generate
    the values that will replace the template placeholders.
    """
    stem = spec_path.stem  # e.g. Checklist_TaskType_ICSP_Desc3_251114_1052

    app_title = excel_meta.get("APP_TITLE", "SOP Build Checklist v4c")
    app_title_visible = excel_meta.get("APP_TITLE_VISIBLE", app_title)
    meta_repo = excel_meta.get("META_REPO", "Kya_Baat_Hai / Chk_Lst")
    meta_entity = excel_meta.get("META_ENTITY", "")
    meta_sop_default = excel_meta.get("META_SOP_DEFAULT", "")
    meta_img_folder = excel_meta.get("META_IMG_FOLDER_DEF", "SOP/images/SE/Distro/Quo2Ord")
    run_label_default = excel_meta.get("RUN_LABEL_DEFAULT", stem)

    return {
        "APP_TITLE": app_title,
        "APP_TITLE_VISIBLE": app_title_visible,
        "META_REPO": meta_repo,
        "META_ENTITY": meta_entity,
        "META_SOP_DEFAULT": meta_sop_default,
        "META_IMG_FOLDER_DEF": meta_img_folder,
        "RUN_LABEL_DEFAULT": run_label_default,
    }


def apply_template(template_path: Path, out_path: Path, steps, meta_placeholders: dict):
    """
    Read the HTML template, substitute placeholders, and write the final HTML.
    """
    text = template_path.read_text(encoding="utf-8")

    # 1) Steps JSON
    steps_json = json.dumps(steps, indent=2, ensure_ascii=False)
    text = text.replace("{{STEPS_JSON}}", steps_json)

    # 2) Meta placeholders
    for key, value in meta_placeholders.items():
        placeholder = "{{" + key + "}}"
        text = text.replace(placeholder, value)

    out_path.write_text(text, encoding="utf-8")
    print(f"[checklist_builder] Wrote checklist to: {out_path}")


def derive_default_out_path(spec_path: Path, template_path: Path) -> Path:
    """
    If --out-html is not provided, derive a reasonable default:
      <spec_stem>_checklist_v4e_YYMMDD_HHMM.html
    in the same directory as the spec.
    """
    stem = spec_path.stem
    ts = datetime.now(tz=NY_TZ).strftime("%y%m%d_%H%M")  # YYMMDD_HHMM
    base_name = f"{stem}_checklist_v4e_{ts}.html"
    return spec_path.parent / base_name


def main():
    parser = argparse.ArgumentParser(
        description="Build a task-specific checklist HTML from Excel + HTML template."
    )
    parser.add_argument(
        "--spec",
        required=True,
        help="Path to Excel spec file (with Steps sheet and optional Header sheet).",
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Path to HTML template (v4c/v4e style).",
    )
    parser.add_argument(
        "--out-html",
        help="Output HTML path. If omitted, a name with YYMMDD_HHMM is auto-created.",
    )

    args = parser.parse_args()

    spec_path = Path(args.spec).expanduser().resolve()
    template_path = Path(args.template).expanduser().resolve()

    if args.out_html:
        out_path = Path(args.out_html).expanduser().resolve()
    else:
        out_path = derive_default_out_path(spec_path, template_path)

    if not spec_path.exists():
        raise SystemExit(f"[ERROR] Spec not found: {spec_path}")
    if not template_path.exists():
        raise SystemExit(f"[ERROR] Template not found: {template_path}")

    print(f"[checklist_builder] Spec     : {spec_path}")
    print(f"[checklist_builder] Template : {template_path}")
    print(f"[checklist_builder] Output   : {out_path}")

    # Load steps and meta
    steps = load_steps_from_excel(spec_path)
    excel_meta = load_header_meta_from_excel(spec_path)
    meta_placeholders = build_default_meta(spec_path, excel_meta)

    apply_template(template_path, out_path, steps, meta_placeholders)


if __name__ == "__main__":
    main()
