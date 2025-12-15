#!/usr/bin/env python3
"""
Provenance: Collaborative design between Subi Rajagopalan and ChatGPT (GPT-5.2 Thinking)
for the Kya_Baat_Hai / Root/Chk_Lst generic checklist builder.

How we collaborated (short):
- Subi defined the SOPar workflow + Excel-driven spec structure; I implemented a resilient parser
  and template injector, then we iterated to match real-world sheets (Steps/Header) and UI needs.

Version: v4f1 (2025-12-14 America/New_York)
Fixes vs prior:
- Sanitize StepID into a DOM-safe slug (prevents UI breakage from spaces/parentheses).
- Include ExpectedOutputFile/ExpectedOutputFolder in the reminder line when present.
- Align defaults for v5 output naming (no more v4e/v4f stray labels).
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

NY_TZ = ZoneInfo("America/New_York")


def col_lookup(df, *candidates):
    """Return the actual column name found in df.columns (case-insensitive fallback)."""
    cols = {str(c).strip(): c for c in df.columns}
    for name in candidates:
        if name in cols:
            return cols[name]
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    for name in candidates:
        low = name.lower()
        if low in lower_map:
            return lower_map[low]
    return None


def slugify_step_id(s: str) -> str:
    """
    Convert an arbitrary StepID into something safe for HTML id / JS selectors.
    Keeps it readable, stable, and predictable.
    """
    s = (s or "").strip()
    if not s:
        return ""
    # Replace any run of non-alphanum with underscore
    s = re.sub(r"[^A-Za-z0-9]+", "_", s)
    s = s.strip("_")
    # HTML id cannot start with a digit in some selector contexts; prefix if needed
    if s and s[0].isdigit():
        s = f"step_{s}"
    return s.lower()


def ensure_unique_id(candidate: str, used: set) -> str:
    """Ensure step ids are unique (append _2, _3, ... if needed)."""
    if candidate not in used:
        used.add(candidate)
        return candidate
    i = 2
    while f"{candidate}_{i}" in used:
        i += 1
    final = f"{candidate}_{i}"
    used.add(final)
    return final


def load_steps_from_excel(spec_path: Path):
    """
    Load steps from the Excel 'Steps' sheet (or first sheet if not present).

    Flexible columns supported (common):
      StepOrder/Order/Seq, StepID/ID, Title, Command, InputNeeded, Hints,
      Program, Variants, Phase, ExpectedOutputFile, ExpectedOutputFolder
    """
    xls = pd.ExcelFile(spec_path)
    sheet_name = "Steps" if "Steps" in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=sheet_name)

    col_order     = col_lookup(df, "StepOrder", "Order", "Seq")
    col_step_id   = col_lookup(df, "StepID", "Step Id", "ID")
    col_title     = col_lookup(df, "Title", "StepTitle")
    col_cmd       = col_lookup(df, "Command", "Cmd")
    col_input     = col_lookup(df, "InputNeeded", "Inputs")
    col_hints     = col_lookup(df, "Hints", "Hint")
    col_program   = col_lookup(df, "Program")
    col_variants  = col_lookup(df, "Variants")
    col_phase     = col_lookup(df, "Phase")
    col_out_file  = col_lookup(df, "ExpectedOutputFile", "OutputFile", "Expected Output File")
    col_out_fold  = col_lookup(df, "ExpectedOutputFolder", "OutputFolder", "Expected Output Folder")

    steps = []
    used_ids = set()

    for idx, row in df.iterrows():
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

        # RAW ID (human)
        raw_step_id = ""
        if col_step_id and not pd.isna(row.get(col_step_id)):
            raw_step_id = str(row[col_step_id]).strip()

        # SAFE ID (machine)
        safe_id = slugify_step_id(raw_step_id) or f"step_{order_val}"
        safe_id = ensure_unique_id(safe_id, used_ids)

        # TITLE (human visible)
        if col_title and not pd.isna(row.get(col_title)):
            title_val = str(row[col_title]).strip()
        else:
            title_val = raw_step_id.strip() or safe_id

        # COMMAND (multi-part)
        cmd_parts = []
        if col_cmd and not pd.isna(row.get(col_cmd)):
            cmd_parts.append(str(row[col_cmd]).rstrip())
        if col_program and not pd.isna(row.get(col_program)):
            cmd_parts.append(f"[Program] {row[col_program]}")
        if col_variants and not pd.isna(row.get(col_variants)):
            cmd_parts.append(f"[Variants] {row[col_variants]}")
        command_val = "\n\n".join(cmd_parts).strip()

        # REMINDER (short line under title)
        reminder_parts = []
        if col_input and not pd.isna(row.get(col_input)):
            reminder_parts.append(f"Inputs: {row[col_input]}")
        if col_out_file and not pd.isna(row.get(col_out_file)):
            reminder_parts.append(f"OutFile: {row[col_out_file]}")
        if col_out_fold and not pd.isna(row.get(col_out_fold)):
            reminder_parts.append(f"OutFolder: {row[col_out_fold]}")
        if col_hints and not pd.isna(row.get(col_hints)):
            reminder_parts.append(f"Hints: {row[col_hints]}")
        if col_phase and not pd.isna(row.get(col_phase)):
            reminder_parts.append(f"Phase: {row[col_phase]}")

        reminder_val = " | ".join(str(p) for p in reminder_parts if str(p).strip())

        step_obj = {
            "id": safe_id,              # machine-safe
            "order": order_val,
            "title": title_val,         # human-visible
            "command": command_val,
            "reminder": reminder_val,
            "notes": "",
            "runs": []
        }
        steps.append(step_obj)

    steps.sort(key=lambda s: s.get("order", 0))
    return steps


def load_header_meta_from_excel(spec_path: Path):
    """Optionally load meta placeholders from a 'Header' sheet: key/value pairs in first two columns."""
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
        key = "" if pd.isna(row.iloc[0]) else str(row.iloc[0]).strip()
        if not key or key.lower() == "nan":
            continue
        val = "" if pd.isna(row.iloc[1]) else str(row.iloc[1]).strip()
        meta[key] = val

    return meta


def build_default_meta(spec_path: Path, excel_meta: dict):
    """Merge Header-sheet meta with sane defaults."""
    stem = spec_path.stem

    # Align with v5 templates (your current run)
    app_title = excel_meta.get("APP_TITLE", "SOP Build Checklist v5")
    app_title_visible = excel_meta.get("APP_TITLE_VISIBLE", app_title)

    meta_repo = excel_meta.get("META_REPO", "/workspaces/EdxBuild")
    meta_entity = excel_meta.get("META_ENTITY", "")
    meta_sop_default = excel_meta.get("META_SOP_DEFAULT", "")
    meta_img_folder = excel_meta.get("META_IMG_FOLDER_DEF", "SOP/images/SE/Distro/Quo2Ord")
    meta_webroot = excel_meta.get("META_WEBROOT", "")
    run_label_default = excel_meta.get("RUN_LABEL_DEFAULT", stem)

    return {
        "APP_TITLE": app_title,
        "APP_TITLE_VISIBLE": app_title_visible,
        "META_REPO": meta_repo,
        "META_ENTITY": meta_entity,
        "META_SOP_DEFAULT": meta_sop_default,
        "META_IMG_FOLDER_DEF": meta_img_folder,
        "META_WEBROOT": meta_webroot,
        "RUN_LABEL_DEFAULT": run_label_default,
    }


def apply_template(template_path: Path, out_path: Path, steps, meta_placeholders: dict):
    """Read template HTML, substitute placeholders, and write output HTML."""
    text = template_path.read_text(encoding="utf-8")

    steps_json = json.dumps(steps, indent=2, ensure_ascii=False)
    text = text.replace("{{STEPS_JSON}}", steps_json)

    for key, value in meta_placeholders.items():
        placeholder = "{{" + key + "}}"
        text = text.replace(placeholder, str(value))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"[checklist_builder_v4f1] Wrote checklist to: {out_path}")


def derive_default_out_path(spec_path: Path) -> Path:
    """Default output: <spec_stem>_checklist_v5_YYMMDD_HHMM.html in same folder as spec."""
    stem = spec_path.stem
    ts = datetime.now(tz=NY_TZ).strftime("%y%m%d_%H%M")
    return spec_path.parent / f"{stem}_checklist_v5_{ts}.html"


def main():
    parser = argparse.ArgumentParser(
        description="Build a task-specific checklist HTML from Excel + HTML template."
    )
    parser.add_argument("--spec", required=True, help="Path to Excel spec file.")
    parser.add_argument("--template", required=True, help="Path to HTML template.")
    parser.add_argument("--out-html", help="Output HTML path (optional).")

    args = parser.parse_args()

    spec_path = Path(args.spec).expanduser().resolve()
    template_path = Path(args.template).expanduser().resolve()
    out_path = Path(args.out_html).expanduser().resolve() if args.out_html else derive_default_out_path(spec_path)

    if not spec_path.exists():
        raise SystemExit(f"[ERROR] Spec not found: {spec_path}")
    if not template_path.exists():
        raise SystemExit(f"[ERROR] Template not found: {template_path}")

    print(f"[checklist_builder_v4f1] Spec     : {spec_path}")
    print(f"[checklist_builder_v4f1] Template : {template_path}")
    print(f"[checklist_builder_v4f1] Output   : {out_path}")

    steps = load_steps_from_excel(spec_path)
    excel_meta = load_header_meta_from_excel(spec_path)
    meta_placeholders = build_default_meta(spec_path, excel_meta)

    apply_template(template_path, out_path, steps, meta_placeholders)


if __name__ == "__main__":
    main()
