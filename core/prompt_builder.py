"""
Prompt builder for AutoScience Codex runs.

This module centralizes prompt construction so normal runs and clear/reruns
always use the same workflow instructions.
"""

from pathlib import Path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_codex_prompt(project_name: str, project_path: Path, repo_root: Path) -> str:
    agents_path = repo_root / "agents"
    reporting_path = project_path / "reporting"
    notebook_name = f"{project_name}_reproducable.ipynb"

    orchestrator_prompt = _read(agents_path / "orchestrator.md")
    data_architect_prompt = _read(agents_path / "data_architect.md")
    variable_selector_prompt = _read(agents_path / "variable_selector.md")
    analyst_visualizer_prompt = _read(agents_path / "analyst_and_visualizer.md")
    scientific_writer_prompt = _read(agents_path / "scientific_writer.md")

    return f"""You are an AI research assistant running the AutoScience multi-agent workflow for this project.

Run scope (must be used consistently for every agent and artifact):
- Project root: {project_path}
- Research question: {project_path / "research_question.md"}
- Data directory: {project_path / "data"}
- Analysis scripts directory: {project_path / "analysis_scripts"}
- Visualization scripts directory: {project_path / "visualization_scripts"}
- Reporting directory: {reporting_path}
- Agent instruction directory: {agents_path}

Workflow contract:
- Use the agent prompts below as the authoritative, exact instructions for each role.
- Orchestrate the pipeline by following the Orchestrator prompt state machine.
- Keep all paths and artifacts under this project root.
- Do not use artifacts from any other project.
- Execute all pipeline stages in order; do not skip any stage.

Required stage-by-stage execution checklist (must complete in order):
1) Parsing Data
   - Ensure data parsing/inspection artifacts and schema docs exist in data/.
2) Selecting Variables
   - Write analysis_scripts/selected_variables.md from the research question + schema.
3) Build Focused Dataset
   - Create a focused CSV containing only selected variables.
   - Name it [dataset_name]_focused.csv (dataset stem + "_focused.csv"), under data/.
4) Running Analysis
   - Write and execute analysis scripts in analysis_scripts/.
   - Produce analysis outputs and run logs (stdout/stderr).
5) Visualizing
   - Write and execute visualization scripts in visualization_scripts/.
   - Produce figure outputs in stable paths plus run logs.
6) Reporting
   - Write reporting/report.md.
   - Write reporting/{notebook_name}.
   - Notebook must include successful analysis/visualization code with required commentary coverage.

Completion rule:
- You may output <<DONE>> only after all checklist items are complete and artifacts are present on disk.

Notebook filename requirement:
- {notebook_name}

Global quality gate (must pass before writing <<DONE>>):
- The notebook must provide commentary coverage for logical analysis units:
  - every non-trivial function has commentary,
  - complex functions are split into commentary across smaller logical steps,
  - basic/obvious helper functions may omit commentary.
- If any required commentary coverage is missing, do not finish; fix the notebook first.

=== AGENT PROMPT: ORCHESTRATOR ===
{orchestrator_prompt}

=== AGENT PROMPT: DATA ARCHITECT ===
{data_architect_prompt}

=== AGENT PROMPT: VARIABLE SELECTOR ===
{variable_selector_prompt}

=== AGENT PROMPT: ANALYST AND VISUALIZER ===
{analyst_visualizer_prompt}

=== AGENT PROMPT: SCIENTIFIC WRITER ===
{scientific_writer_prompt}

When everything is complete, write <<DONE>>"""
