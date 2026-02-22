#!/usr/bin/env python3
"""
AutoScience: project-centric entry point for automated scientific research.

Usage:
    python run_autoscience.py --project "my_experiment"
    python run_autoscience.py -p my_experiment

1. Creates the project folder structure.
2. Prompts for your research question and saves it to research_question.md.
3. Instructs you to upload data to the project's data/ folder.
4. After you confirm, calls Codex to process the data and run the analysis.
"""

import argparse
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.project_manager import ProjectManager
from core.codex_runner import run_codex


def build_codex_prompt(project_name: str, project_path: Path) -> str:
    agents_path = _ROOT / "agents"
    reporting_path = project_path / "reporting"
    notebook_name = f"{project_name}_reproducable.ipynb"
    return f"""You are an AI research assistant for AutoScience. Your task is to analyze the user's dataset with respect to their research question.

Run scope (must be used consistently for every agent and artifact):
- Project root: {project_path}
- Research question: {project_path / "research_question.md"}
- Data directory: {project_path / "data"}
- Analysis scripts directory: {project_path / "analysis_scripts"}
- Visualization scripts directory: {project_path / "visualization_scripts"}
- Reporting directory: {reporting_path}
- Agent instruction directory: {agents_path}

Before doing anything else:
1. Read {agents_path / "orchestrator.md"}.
2. Read {agents_path / "data_architect.md"}.
3. Read {agents_path / "analyst_and_visualizer.md"}.
4. Read {agents_path / "scientific_writer.md"}.
5. Read {project_path / "research_question.md"}.

Pipeline requirements:
1. Parse and document data in data/. Identify schema and write it under data/.
2. Write and run analysis scripts in analysis_scripts/. Fix errors until they run and produce valid results. Log stdout/stderr for the report.
3. Write and run visualization scripts in visualization_scripts/. Produce figures and save them in stable paths.
4. Write report.md in reporting/.
5. Create the reproducable notebook in reporting/ with this exact filename:
   - {notebook_name}
6. The notebook must include all successful code from analysis_scripts/ and visualization_scripts/.
7. Interleave markdown and code cells throughout the notebook: every section of code must have adjacent markdown that explains:
   - what the code is doing,
   - why this approach was chosen,
   - and alternative choices that could have been made.

Critical consistency rules:
- Every path used by every agent must stay under this project root: {project_path}
- Do not use artifacts from any other project.
- Keep outputs reproducible with relative paths from project root where possible.

When everything is complete, write <<DONE>>"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="AutoScience: run a research project from setup through Codex analysis.",
    )
    parser.add_argument(
        "--project",
        "-p",
        required=True,
        metavar="NAME",
        help="Project name (folder under projects/).",
    )
    parser.add_argument(
        "--projects-root",
        default=None,
        type=Path,
        help="Root directory for projects (default: AutoScience/projects).",
    )
    parser.add_argument(
        "--no-codex",
        action="store_true",
        help="Skip calling Codex (only create structure, prompt for question, and instruct upload).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        manager = ProjectManager(args.project, projects_root=args.projects_root)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    path = manager.ensure()
    project_name = path.name
    print(f"Project ready: {path}")
    print("  research_question.md")
    print("  data/")
    print("  analysis_scripts/")
    print("  visualization_scripts/")
    print("  reporting/")
    print()

    # Research question
    rq_path = manager.get_research_question_path()
    existing = rq_path.read_text(encoding="utf-8").strip()
    if existing and "Describe the goal" not in existing:
        print("Current research question (research_question.md):")
        print(existing[:500] + ("..." if len(existing) > 500 else ""))
        use = input("Replace with new question? [y/N]: ").strip().lower()
        if use != "y":
            print("Keeping existing research question.")
        else:
            question = input(f"Enter your research question for projects/{project_name} (goal and constraints):\n> ")
            if question.strip():
                rq_path.write_text(f"# Research question\n\n{question.strip()}\n", encoding="utf-8")
                print(f"Saved to projects/{project_name}/research_question.md")
    else:
        question = input(f"Enter your research question for projects/{project_name} (goal and constraints):\n> ")
        if question.strip():
            rq_path.write_text(f"# Research question\n\n{question.strip()}\n", encoding="utf-8")
            print(f"Saved to projects/{project_name}/research_question.md")
        else:
            print("No question entered; you can edit research_question.md later.")

    # Upload instructions
    data_path = manager.get_data_path()
    print()
    print("---")
    print("Next: upload your data into the project's data folder:")
    print(f"  {data_path}")
    print("  (PDFs, CSVs, or other files you want analyzed)")
    print("---")
    input("Press Enter when you have uploaded your data and want to run the analysis...")

    if args.no_codex:
        print("Skipping Codex (--no-codex). Run Codex manually with this project as context.")
        return

    # Run Codex from the project directory so it sees research_question.md and data/
    print("Calling Codex to process data and run the analysis...")
    print("(Output will stream below; this may take several minutes.)")
    print()
    codex_prompt = build_codex_prompt(project_name=project_name, project_path=path)
    try:
        stdout, stderr = run_codex(codex_prompt, cwd=path)
    except FileNotFoundError:
        print("Error: 'codex' command not found. Install Codex or ensure it is on your PATH.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Codex run timed out.", file=sys.stderr)
        sys.exit(1)

    print()
    print("Codex run finished.")


if __name__ == "__main__":
    main()
