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

from core.project_manager import ProjectManager, get_project_path
from core.codex_runner import run_codex


CODEX_PROMPT = """You are an AI research assistant for AutoScience. Your task is to analyze the user's dataset with respect to their research question.

You are running in the project directory. Follow this pipeline:

1. Read research_question.md for the goal and constraints.
2. Parse and document data in the data/ folder (PDFs, CSVs). Identify schema and write it under data/.
3. Write and run analysis scripts in analysis_scripts/. Fix errors until they run and produce valid results. Log stdout/stderr for the report.
4. Write and run visualization scripts in visualization_scripts/. Produce figures and save them (e.g. in reporting/figures/ or visualization_scripts/output/).
5. Write report.md and a reproducible .ipynb in reporting/, using the analysis logs and figures. The notebook must contain all successful code from the script folders.

Use the agent instructions in the repository's agents/ folder (orchestrator, data_architect, analyst_and_visualizer, scientific_writer) for detailed behavior.

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
            question = input("Enter your research question (goal and constraints):\n> ")
            if question.strip():
                rq_path.write_text(f"# Research question\n\n{question.strip()}\n", encoding="utf-8")
                print("Saved to research_question.md")
    else:
        question = input("Enter your research question (goal and constraints):\n> ")
        if question.strip():
            rq_path.write_text(f"# Research question\n\n{question.strip()}\n", encoding="utf-8")
            print("Saved to research_question.md")
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
    try:
        stdout, stderr = run_codex(CODEX_PROMPT, cwd=path)
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
