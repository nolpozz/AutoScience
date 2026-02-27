#!/usr/bin/env python3
"""
AutoScience: project-centric entry point for automated scientific research.

Usage:
    python run_autoscience.py --project "my_experiment"
    python run_autoscience.py -p my_experiment

1. Creates the project folder structure.
2. Prompts for your research question and saves it to research_question.md.
3. Instructs you to upload data to the project's data/ folder.
4. After you confirm, calls Codex to process data, run analysis, and generate reporting artifacts.
"""

import argparse
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.project_manager import ProjectManager, clear_and_rerun_project
from core.prompt_builder import build_codex_prompt
from core.codex_runner import run_codex


def _validate_ready_for_run(manager: ProjectManager) -> None:
    rq_path = manager.get_research_question_path()
    data_path = manager.get_data_path()

    if not rq_path.exists():
        raise ValueError(f"Missing research question file: {rq_path}")

    rq_text = rq_path.read_text(encoding="utf-8").strip()
    if not rq_text or "Describe the goal" in rq_text:
        raise ValueError(
            "research_question.md is empty or still a template. "
            "Please set your research question before running Codex."
        )

    if not data_path.exists():
        raise ValueError(f"Missing data directory: {data_path}")

    has_data_files = any(path.is_file() for path in data_path.iterdir())
    if not has_data_files:
        raise ValueError(
            f"No files found in {data_path}. Add dataset files before running Codex."
        )


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
        "--clear-and-run",
        action="store_true",
        help=(
            "Clear generated artifacts (analysis/visualization/reporting + pipeline state) "
            "while keeping data and research_question.md, then rerun Codex."
        ),
    )
    parser.add_argument(
        "--clear-and-rerun",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    clear_and_run = args.clear_and_run or args.clear_and_rerun

    if clear_and_run:
        try:
            print(f"Clearing generated artifacts and rerunning project: {args.project}")
            clear_and_rerun_project(
                project_name=args.project,
                projects_root=args.projects_root,
            )
            print("Clear-and-rerun completed.")
        except FileNotFoundError:
            print("Error: 'codex' command not found. Install Codex or ensure it is on your PATH.", file=sys.stderr)
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print("Codex run timed out.", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

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
                print("No question entered; keeping existing research question.")
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

    _validate_ready_for_run(manager)

    # Run Codex from the project directory so it sees research_question.md and data/
    print("Calling Codex to parse data, select variables, run analysis, generate visualizations, and write reporting artifacts...")
    print("(Output will stream below; this may take several minutes.)")
    print()
    codex_prompt = build_codex_prompt(project_name=project_name, project_path=path, repo_root=_ROOT)
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
