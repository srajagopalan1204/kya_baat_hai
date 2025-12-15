# Provenance: Developed collaboratively by Subi Rajagopalan and ChatGPT (GPT-5.1 Thinking)
# init_chk_lst_scaffold.py
# Version: v0.1.0
# Design notes: Creates the folder and file scaffold for the Checklist builder under Root/Chk_Lst.
# Last updated: 2025-11-14

from pathlib import Path

BASE_DIR = Path("/workspaces/kya_baat_hai/Root/Chk_Lst")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def main() -> None:
    # Directories
    src_dir = BASE_DIR / "src"
    templates_dir = BASE_DIR / "templates"
    specs_dir = BASE_DIR / "specs"
    rep_dir = BASE_DIR / "rep_checklists"
    prev_dir = BASE_DIR / "Prev"
    docs_dir = BASE_DIR / "docs"

    for d in [BASE_DIR, src_dir, templates_dir, specs_dir, rep_dir, prev_dir, docs_dir]:
        ensure_dir(d)

    # README
    readme_content = """# Checklist Builder (Chk_Lst)

This folder contains the scaffold for the interactive checklist builder.

Structure:

- `src/checklist_builder.py`  
  Python script that builds task-type checklist HTML files from an Excel spec and an HTML template.

- `templates/`  
  Contains the generic HTML template (task-type engine), e.g. `SOP_Build_Checklist_template_v3_3.html`.

- `specs/`  
  Excel specifications for each Task Type (with `Header` and `Steps` sheets).

- `rep_checklists/`  
  Generated checklist HTML files (one per Task Type).

- `Prev/`  
  Your archive for older versions of scripts (with date/time in filenames).

- `docs/`  
  Any additional documentation.

Usage (planned):

1. Place your Task-Type Excel spec into `specs/`.
2. Ensure `templates/SOP_Build_Checklist_template_v3_3.html` contains the v3.3 interactive checklist with placeholders.
3. Run `python src/checklist_builder.py --spec specs/YourSpec.xlsx --template templates/SOP_Build_Checklist_template_v3_3.html --out-html rep_checklists/YourChecklist.html`
4. Download the generated HTML from `rep_checklists/` and open it in your browser on Windows.

"""

    write_file(BASE_DIR / "README.md", readme_content)

    # checklist_builder.py stub (you will paste full implementation later)
    checklist_builder_stub = """# Provenance: Developed collaboratively by Subi Rajagopalan and ChatGPT (GPT-5.1 Thinking)
# checklist_builder.py
# Version: v0.1.0
# Design notes: Builds task-type checklist HTML files from an Excel spec and an HTML template.
# Last updated: 2025-11-14

\"\"\"
This is a scaffold file.

Next steps:
- Replace this stub with the full `checklist_builder.py` implementation
  provided in our ChatGPT conversation.
- Keep the Provenance header at the top.
\"\"\"

import argparse
from pathlib import Path

import pandas as pd  # noqa: F401  # placeholder import, used in the real implementation


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Checklist builder (stub). Replace with full implementation."
    )
    parser.add_argument("--spec", required=False, help="Path to Excel spec file.")
    parser.add_argument("--template", required=False, help="Path to HTML template.")
    parser.add_argument("--out-html", required=False, help="Output HTML path.")
    args = parser.parse_args()

    print("This is a stub for checklist_builder.py.")
    print("Please paste the full implementation from ChatGPT into this file.")
    if args.spec:
        print(f"Spec argument received: {args.spec}")
    if args.template:
        print(f"Template argument received: {args.template}")
    if args.out_html:
        print(f"Out HTML argument received: {args.out_html}")


if __name__ == "__main__":
    main()
"""

    write_file(src_dir / "checklist_builder.py", checklist_builder_stub)

    # Template skeleton with placeholders
    template_skeleton = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{APP_TITLE}}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    /* Minimal styling placeholder. Replace with full v3.3 CSS. */
    body { font-family: sans-serif; margin: 1.5rem; }
    h1 { font-size: 1.4rem; margin-bottom: 0.5rem; }
    .tagver { font-size: 0.8rem; color: #555; margin-left: 0.5rem; }
    .step { border: 1px solid #ccc; padding: 0.75rem; margin-bottom: 0.5rem; }
    .step-title { font-weight: bold; margin-bottom: 0.25rem; }
    pre { background: #f7f7f7; padding: 0.5rem; overflow-x: auto; }
  </style>
</head>
<body>
  <h1 id="appTitle">
    {{APP_TITLE_VISIBLE}}
    <span class="tagver">(v3.3, multi-run)</span>
  </h1>

  <section id="meta">
    <h2>Run Header (placeholder)</h2>
    <div>
      <label>Repo:
        <input id="metaRepo" value="{{META_REPO}}">
      </label>
    </div>
    <div>
      <label>Entity / Function / SubEntity:
        <input id="metaEntity" value="{{META_ENTITY}}">
      </label>
    </div>
    <div>
      <label>SOP ID:
        <input id="metaSOP" value="{{META_SOP_DEFAULT}}">
      </label>
    </div>
    <div>
      <label>Image Folder:
        <input id="metaImgFolder" value="{{META_IMG_FOLDER_DEF}}">
      </label>
    </div>
    <div>
      <label>Run Label:
        <input id="metaRunLabel" value="{{RUN_LABEL_DEFAULT}}">
      </label>
    </div>
  </section>

  <hr>

  <section id="steps">
    <!-- Steps will be rendered by JavaScript from the embedded JSON. -->
  </section>

  <script>
    // This JSON is injected by checklist_builder.py
    let steps = {{STEPS_JSON}};

    function updateTitle() {
      const sop = document.getElementById("metaSOP")?.value || "";
      const runLabel = document.getElementById("metaRunLabel")?.value || "";
      const base = sop ? `${sop} – Interactive Checklist` : document.title;
      document.title = runLabel ? `${base} – [${runLabel}]` : base;
    }

    function renderSteps() {
      const container = document.getElementById("steps");
      container.innerHTML = "";

      steps.forEach((step) => {
        const div = document.createElement("div");
        div.className = "step";

        const title = document.createElement("div");
        title.className = "step-title";
        title.textContent = step.title || step.step_id || step.id;
        div.appendChild(title);

        if (step.command) {
          const pre = document.createElement("pre");
          pre.textContent = step.command;
          div.appendChild(pre);
        }

        if (step.hints) {
          const hints = document.createElement("div");
          hints.textContent = `Hints: ${step.hints}`;
          div.appendChild(hints);
        }

        container.appendChild(div);
      });
    }

    function wireHeaderEvents() {
      const fields = ["metaSOP", "metaRunLabel"];
      fields.forEach((id) => {
        const el = document.getElementById(id);
        if (el) {
          el.addEventListener("input", updateTitle);
        }
      });
    }

    document.addEventListener("DOMContentLoaded", () => {
      renderSteps();
      wireHeaderEvents();
      updateTitle();
    });
  </script>
</body>
</html>
"""

    write_file(templates_dir / "SOP_Build_Checklist_template_v3_3.html", template_skeleton)

    # .gitkeep placeholders
    for d in [specs_dir, rep_dir, prev_dir, docs_dir]:
        write_file(d / ".gitkeep", "", overwrite=False)

    print(f"Scaffold created under: {BASE_DIR}")


if __name__ == "__main__":
    main()
