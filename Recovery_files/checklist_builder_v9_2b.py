#!/usr/bin/env python3
"""
checklist_builder_v9_2b.py
Build: v9.2b_20260101_1700 (America/New_York)

Purpose
- Read a checklist spec Excel (Header + Steps)
- Inject SOP meta + steps JSON into a robust HTML template
- Supports dual entity codes:
    <Entity> = META_ENTITY_CODE (e.g., PALCO)
    <ENT>    = META_ENT_CODE (e.g., PPS)
- Supports Header suppression: if Header.suppress == "yes", hide that field in HTML UI.

Template markers (do not delete from template):
  __SOPINFO_JSON__
  __STEPS_JSON__
  __SUPPRESSED_KEYS_JSON__

Usage
  python checklist_builder_v9_2.py --spec SPEC.xlsx --template TEMPLATE.html --out-html OUT.html [--debug]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

MARK_SOPINFO = "__SOPINFO_JSON__"
MARK_STEPS = "__STEPS_JSON__"
MARK_SUPPRESS = "__SUPPRESSED_KEYS_JSON__"


def norm_yes(v: Any) -> bool:
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in {"y", "yes", "true", "1", "on"}


def read_header_kv(xlsx: Path, sheet: str = "Header") -> Tuple[Dict[str, str], List[str]]:
    df = pd.read_excel(xlsx, sheet_name=sheet, engine="openpyxl")
    cols = {c.lower().strip(): c for c in df.columns}

    field_col = cols.get("field") or cols.get("key") or cols.get("name")
    value_col = cols.get("value") or cols.get("val")
    suppress_col = cols.get("suppress")  # optional

    if not field_col or not value_col:
        raise ValueError(f"Header sheet must have Field and Value columns. Found: {list(df.columns)}")

    kv: Dict[str, str] = {}
    suppressed: List[str] = []

    for _, row in df.iterrows():
        k = str(row.get(field_col) or "").strip()
        if not k:
            continue
        raw_v = row.get(value_col)
        v = "" if raw_v is None or (isinstance(raw_v, float) and pd.isna(raw_v)) else str(raw_v)
        kv[k] = v

        if suppress_col and norm_yes(row.get(suppress_col)):
            suppressed.append(k)

    return kv, suppressed


def read_steps(xlsx: Path, sheet: str = "Steps") -> List[Dict[str, Any]]:
    df = pd.read_excel(xlsx, sheet_name=sheet, engine="openpyxl")
    cols = {c.lower().strip(): c for c in df.columns}

    def getcol(*names: str) -> str | None:
        for n in names:
            c = cols.get(n.lower())
            if c:
                return c
        return None

    c_order = getcol("StepOrder", "Order")
    c_id = getcol("StepID", "ID")
    c_title = getcol("Title")
    c_command = getcol("Command")
    c_input = getcol("InputNeeded", "Reminder")
    c_hints = getcol("Hints", "Notes")
    c_phase = getcol("Phase")

    missing = [n for n, c in [("StepOrder", c_order), ("StepID", c_id), ("Title", c_title)] if c is None]
    if missing:
        raise ValueError(f"Steps sheet missing required columns: {missing}. Found: {list(df.columns)}")

    def sget(row, c) -> str:
        if not c:
            return ""
        v = row.get(c)
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return ""
        return str(v)

    steps: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        sid = sget(row, c_id).strip()
        title = sget(row, c_title).strip()
        if not sid and not title:
            continue

        try:
            order_raw = sget(row, c_order)
            order_int = int(float(order_raw)) if order_raw else len(steps) + 1
        except Exception:
            order_int = len(steps) + 1

        steps.append({
            "id": sid or f"STEP_{order_int}",
            "order": order_int,
            "title": title or sid or f"Step {order_int}",
            "command": sget(row, c_command),
            "reminder": sget(row, c_input),
            "notes": sget(row, c_hints),
            "phase": sget(row, c_phase),
            "done": False,
            "runs": [],
        })

    steps.sort(key=lambda x: x.get("order", 0))
    return steps


def build_sopinfo(kv: Dict[str, str]) -> Dict[str, Any]:
    page_title = kv.get("APP_TITLE", "SOP Build Checklist").strip()
    header_visible = kv.get("APP_TITLE_VISIBLE", "SOP Build Checklist").strip()

    sop_id = kv.get("META_SOP_DEFAULT", "SOP").strip()
    sop_name = (kv.get("META_SOP_NAME_DEFAULT", "").strip() or header_visible)

    entity = kv.get("META_ENTITY", "").strip()
    run_label = kv.get("RUN_LABEL_DEFAULT", "").strip() or sop_id
    repo = kv.get("META_REPO", "").strip()
    webroot = kv.get("META_WEBROOT", "").strip()
    img_folder = kv.get("META_IMG_FOLDER_DEF", "").strip()
    template_tag = (kv.get("TEMPLATE_TAG", "").strip() or "v9.2")

    entity_code = kv.get("META_ENTITY_CODE", "").strip()
    ent_code = kv.get("META_ENT_CODE", "").strip()

    return {
        "pageTitle": page_title,
        "headerTitleVisible": header_visible,
        "name": sop_name,
        "id": sop_id,
        "entity": entity,
        "runLabel": run_label,
        "repo": repo,
        "webRoot": webroot,
        "imgFolder": img_folder,
        "templateTag": template_tag,
        "entityCode": entity_code,
        "entCode": ent_code,
        "faqLocation": (kv.get("FAQ_location", kv.get("FAQ_LOCATION", "")) or "").strip(),
        "quizLocation": (kv.get("Quiz_Location", kv.get("QUIZ_LOCATION", "")) or "").strip(),
    }


def inject(template_text: str, sopinfo: Dict[str, Any], steps: List[Dict[str, Any]], suppressed: List[str]) -> str:
    if MARK_SOPINFO not in template_text or MARK_STEPS not in template_text or MARK_SUPPRESS not in template_text:
        raise ValueError("Template is missing one or more injection markers.")
    out = template_text
    out = out.replace(MARK_SOPINFO, json.dumps(sopinfo, ensure_ascii=False))
    out = out.replace(MARK_STEPS, json.dumps(steps, ensure_ascii=False))
    out = out.replace(MARK_SUPPRESS, json.dumps(suppressed, ensure_ascii=False))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--template", required=True)
    ap.add_argument("--out-html", required=True)
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    spec = Path(args.spec)
    tmpl = Path(args.template)
    outp = Path(args.out_html)

    kv, suppressed = read_header_kv(spec, "Header")
    steps = read_steps(spec, "Steps")
    sopinfo = build_sopinfo(kv)

    if args.debug:
        print("[debug] Header sheet: Header")
        print("[debug] Steps sheet : Steps")
        print(f"[debug] header kv pairs read: {len(kv)}")
        print(f"[debug] header suppressed keys: {suppressed}")
        for k in sorted(kv.keys()):
            print(f"  {k} = {kv[k]}")
        print(f"[debug] steps read: {len(steps)}")
        if steps:
            print(f"[debug] first step id='{steps[0]['id']}' title='{steps[0]['title']}'")

    built = inject(tmpl.read_text(encoding="utf-8"), sopinfo, steps, suppressed)

    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(built, encoding="utf-8")

    if args.debug:
        print(f"[debug] Wrote HTML: {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
