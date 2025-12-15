#!/usr/bin/env python3
"""
Provenance: Collaborative design between Subi Rajagopalan and ChatGPT (GPT-5.1/5.2 Thinking)
for Kya_Baat_Hai / Root/Chk_Lst generic checklist builder.

Collaboration note (2 lines):
- Subi defined the operational workflow + spec format (Header + Steps) and the required UI behaviors.
- ChatGPT implemented the Excel→JSON injection + template patching so one builder can emit many task checklists.

Version: v4f_v1a (2025-12-14)
Key fixes vs prior:
- Works with BOTH placeholder templates ({{STEPS_JSON}}, {{APP_TITLE}}…) and older “hard-coded” templates
  by regex-replacing the `let steps = [...]` block.
- Can also patch <title> and #headerTitle even when placeholders are missing.
- Default out filename tag corrected to v4f (was v4e).
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


def load_steps_from_excel(spec_path: Path):
    xls = pd.ExcelFile(spec_path)
    sheet_name = "Steps" if "Steps" in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=sheet_name)

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
        if all(pd.isna(v) for v in row.values):
            continue

        if col_order and not pd.isna(row.get(col_order)):
            try:
                order_val = int(row[col_order])
            except Exception:
                order_val = idx + 1
        else:
            order_val = idx + 1

        raw_id = ""
        if col_step_id and not pd.isna(row.get(col_step_id)):
            raw_id = str(row[col_step_id]).strip()
        if not raw_id:
            raw_id = f"step_{order_val}"

        title_val = raw_id
        if col_title and not pd.isna(row.get(col_title)):
            title_val = str(row[col_title]).strip()

        cmd_parts = []
        if col_cmd and not pd.isna(row.get(col_cmd)):
            cmd_parts.append(str(row[col_cmd]).rstrip())
        if col_program and not pd.isna(row.get(col_program)):
            cmd_parts.append(f"[Program] {str(row[col_program]).strip()}")
        if col_variants and not pd.isna(row.get(col_variants)):
            cmd_parts.append(f"[Variants] {str(row[col_variants]).strip()}")
        command_val = "\n\n".join([p for p in cmd_parts if p.strip()]).strip()

        reminder_parts = []
        if col_input and not pd.isna(row.get(col_input)):
            reminder_parts.append(f"Inputs: {row[col_input]}")
        if col_hints and not pd.isna(row.get(col_hints)):
            reminder_parts.append(f"Hints: {row[col_hints]}")
        if col_phase and not pd.isna(row.get(col_phase)):
            reminder_parts.append(f"Phase: {row[col_phase]}")
        reminder_val = " | ".join(str(p) for p in reminder_parts if str(p).strip())

        steps.append({
            "id": raw_id,
            "order": order_val,
            "title": title_val,
            "command": command_val,
            "reminder": reminder_val,
            "notes": "",
            "runs": []
        })

    steps.sort(key=lambda s: s.get("order", 0))
    return steps


def load_header_meta_from_excel(spec_path: Path):
    meta = {}
    xls = pd.ExcelFile(spec_path)
    if "Header" not in xls.sheet_names:
        return meta

    df = pd.read_excel(xls, sheet_name="Header")
    if df.shape[1] < 2:
        return meta

    for _, row in df.iterrows():
        key = "" if pd.isna(row.iloc[0]) else str(row.iloc[0]).strip()
        if not key:
            continue
        val = "" if pd.isna(row.iloc[1]) else str(row.iloc[1]).strip()
        meta[key] = val
    return meta


def build_default_meta(spec_path: Path, excel_meta: dict):
    stem = spec_path.stem

    app_title = excel_meta.get("APP_TITLE", "Checklist")
    app_title_visible = excel_meta.get("APP_TITLE_VISIBLE", app_title)

    meta_repo = excel_meta.get("META_REPO", "/workspaces/EdxBuild")
    meta_entity = excel_meta.get("META_ENTITY", "")
    meta_sop_default = excel_meta.get("META_SOP_DEFAULT", "")
    meta_img_folder = excel_meta.get("META_IMG_FOLDER_DEF", "")
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


def _replace_or_patch_title(html: str, title_text: str) -> str:
    # Placeholder first
    if "{{APP_TITLE}}" in html:
        return html.replace("{{APP_TITLE}}", title_text)

    # Otherwise patch the <title>...</title>
    return re.sub(r"(<title>)(.*?)(</title>)", rf"\1{title_text}\3", html, flags=re.I | re.S, count=1)


def _replace_or_patch_header_title(html: str, visible_text: str) -> str:
    # Placeholder first
    if "{{APP_TITLE_VISIBLE}}" in html:
        return html.replace("{{APP_TITLE_VISIBLE}}", visible_text)

    # Otherwise patch the default headerTitle content (id="headerTitle")
    return re.sub(
        r'(<div[^>]*\bid="headerTitle"[^>]*>)(.*?)(</div>)',
        rf"\1{visible_text}\3",
        html,
        flags=re.I | re.S,
        count=1
    )


def _inject_steps(html: str, steps_json: str) -> str:
    # Preferred placeholder path
    if "{{STEPS_JSON}}" in html:
        return html.replace("{{STEPS_JSON}}", steps_json)

    # Back-compat: replace `let steps = [ ... ];`
    # This will replace anything between `let steps =` and the next `];`
    pattern = r"(let\s+steps\s*=\s*)(\[[\s\S]*?\])(\s*;)"
    if re.search(pattern, html):
        return re.sub(pattern, rf"\1{steps_json}\3", html, count=1)

    # If we can’t find either, fail loudly (so we don’t ship wrong checklist silently)
    raise SystemExit("[ERROR] Template has no {{STEPS_JSON}} and no `let steps = [...]` block to replace.")


def apply_template(template_path: Path, out_path: Path, steps, meta_placeholders: dict):
    html = template_path.read_text(encoding="utf-8")

    steps_json = json.dumps(steps, indent=2, ensure_ascii=False)

    # Inject steps (placeholder or regex)
    html = _inject_steps(html, steps_json)

    # Patch title/header even if placeholders are missing
    html = _replace_or_patch_title(html, meta_placeholders.get("APP_TITLE", "Checklist"))
    html = _replace_or_patch_header_title(html, meta_placeholders.get("APP_TITLE_VISIBLE", meta_placeholders.get("APP_TITLE", "Checklist")))

    # Replace any other placeholders that DO exist
    for key, value in meta_placeholders.items():
        placeholder = "{{" + key + "}}"
        if placeholder in html:
            html = html.replace(placeholder, value)

    out_path.write_text(html, encoding="utf-8")
    print(f"[checklist_builder_v4f_v1a] Wrote checklist to: {out_path}")


def derive_default_out_path(spec_path: Path) -> Path:
    stem = spec_path.stem
    ts = datetime.now(tz=NY_TZ).strftime("%y%m%d_%H%M")  # YYMMDD_HHMM
    base_name = f"{stem}_checklist_v4f_{ts}.html"
    return spec_path.parent / base_name


def main():
    parser = argparse.ArgumentParser(
        description="Build a task-specific checklist HTML from Excel + HTML template."
    )
    parser.add_argument("--spec", required=True, help="Path to Excel spec file.")
    parser.add_argument("--template", required=True, help="Path to HTML template.")
    parser.add_argument("--out-html", help="Output HTML path.")

    args = parser.parse_args()

    spec_path = Path(args.spec).expanduser().resolve()
    template_path = Path(args.template).expanduser().resolve()
    out_path = Path(args.out_html).expanduser().resolve() if args.out_html else derive_default_out_path(spec_path)

    if not spec_path.exists():
        raise SystemExit(f"[ERROR] Spec not found: {spec_path}")
    if not template_path.exists():
        raise SystemExit(f"[ERROR] Template not found: {template_path}")

    print(f"[checklist_builder_v4f_v1a] Spec     : {spec_path}")
    print(f"[checklist_builder_v4f_v1a] Template : {template_path}")
    print(f"[checklist_builder_v4f_v1a] Output   : {out_path}")

    steps = load_steps_from_excel(spec_path)
    excel_meta = load_header_meta_from_excel(spec_path)
    meta_placeholders = build_default_meta(spec_path, excel_meta)

    apply_template(template_path, out_path, steps, meta_placeholders)


if __name__ == "__main__":
    main()
