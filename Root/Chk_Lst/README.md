# Checklist Builder (Chk_Lst)

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

/workspaces/kya_baat_hai/Root/Chk_Lst/templates/SOP_Build_Checklist_v5_SLS_LineEnt.html

python /workspaces/kya_baat_hai/Root/Chk_Lst/src/checklist_builder_v4f.py \
      --spec "/workspaces/kya_baat_hai/Root/Chk_Lst/specs/Checklist_TaskType_ICSP_Desc3_251114_1052.xlsx" \
      --template "/workspaces/kya_baat_hai/Root/Chk_Lst/templates/SOP_Build_Checklist_v5_SLS_LineEnt.html" \
      --out-html /workspaces/kya_baat_hai/Root/Chk_Lst/rep_checklists/ICSP_Desc3_Checklist_V5.html