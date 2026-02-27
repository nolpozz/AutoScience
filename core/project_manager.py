"""
Project manager: creates and validates the project-centric folder structure,
and provides helpers for managing project lifecycles.
"""

from pathlib import Path
from typing import Optional, Tuple
import shutil

from .codex_runner import run_codex
from .prompt_builder import build_codex_prompt

# Default root for projects (relative to this file's parent's parent)
DEFAULT_PROJECTS_ROOT = Path(__file__).resolve().parent.parent / "projects"

# Subfolders required for each project
PROJECT_SUBDIRS = (
    "data",
    "analysis_scripts",
    "visualization_scripts",
    "reporting",
)

# Project-level file
RESEARCH_QUESTION_FILE = "research_question.md"
PIPELINE_STATE_FILE = "pipeline_state.txt"


def get_project_path(project_name: str, projects_root: Optional[Path] = None) -> Path:
    """Return the absolute path to a project directory (may not exist yet)."""
    root = projects_root or DEFAULT_PROJECTS_ROOT
    # Normalize name: no path separators, no leading/trailing dots
    safe_name = project_name.strip().replace("/", "_").replace("\\", "_").strip(".")
    if not safe_name:
        raise ValueError("project_name must be non-empty after normalization")
    return root / safe_name


def ensure_projects_root(projects_root: Optional[Path] = None) -> Path:
    """Create the global projects root if it does not exist."""
    root = projects_root or DEFAULT_PROJECTS_ROOT
    root.mkdir(parents=True, exist_ok=True)
    return root


class ProjectManager:
    """
    Manages project-specific folder structure under /projects/[project_name]/.
    """

    def __init__(self, project_name: str, projects_root: Optional[Path] = None):
        self.project_name = project_name
        self.projects_root = projects_root or DEFAULT_PROJECTS_ROOT
        self.path = get_project_path(project_name, self.projects_root)

    def exists(self) -> bool:
        """Return True if the project directory already exists."""
        return self.path.is_dir()

    def create(self) -> Path:
        """
        Create the full project structure if it does not exist.
        Returns the project path.
        """
        ensure_projects_root(self.projects_root)
        self.path.mkdir(parents=True, exist_ok=True)
        for subdir in PROJECT_SUBDIRS:
            (self.path / subdir).mkdir(parents=True, exist_ok=True)
        research_question_path = self.path / RESEARCH_QUESTION_FILE
        if not research_question_path.exists():
            research_question_path.write_text(
                "# Research question\n\n"
                "<!-- Describe the goal and constraints of this research. -->\n",
                encoding="utf-8",
            )
        return self.path

    def ensure(self) -> Path:
        """Create project structure if missing; return project path."""
        return self.create()

    def get_research_question_path(self) -> Path:
        return self.path / RESEARCH_QUESTION_FILE

    def get_pipeline_state_path(self) -> Path:
        return self.path / PIPELINE_STATE_FILE

    def get_data_path(self) -> Path:
        return self.path / "data"

    def get_analysis_scripts_path(self) -> Path:
        return self.path / "analysis_scripts"

    def get_visualization_scripts_path(self) -> Path:
        return self.path / "visualization_scripts"

    def get_reporting_path(self) -> Path:
        return self.path / "reporting"


def clear_and_rerun_project(
    project_name: str,
    projects_root: Optional[Path] = None,
    timeout_seconds: int = 1800,
) -> Tuple[str, str]:
    """
    Clear generated artifacts for an existing project and rerun the Codex pipeline.

    This helper:
    - keeps the project folder, research_question.md, and data/ intact,
    - deletes contents of analysis_scripts/, visualization_scripts/, and reporting/,
      as well as pipeline_state.txt if present,
    - then invokes Codex with the same high-level prompt used by run_autoscience.py.

    :param project_name: Name of the project folder under projects/.
    :param projects_root: Optional custom projects root; defaults to DEFAULT_PROJECTS_ROOT.
    :param timeout_seconds: Max Codex run time in seconds.
    :return: (stdout, stderr) from the Codex run.
    """
    manager = ProjectManager(project_name, projects_root=projects_root)
    project_path = manager.ensure()

    # Preserve research question and data; clear generated artifacts.
    for subdir in ("analysis_scripts", "visualization_scripts", "reporting"):
        target_dir = project_path / subdir
        if not target_dir.exists():
            continue
        for child in target_dir.iterdir():
            if child.is_file() or child.is_symlink():
                # Python <3.8 does not support missing_ok; this codebase targets 3.12.
                child.unlink(missing_ok=True)  # type: ignore[arg-type]
            elif child.is_dir():
                shutil.rmtree(child)

    pipeline_state_path = project_path / PIPELINE_STATE_FILE
    if pipeline_state_path.exists():
        pipeline_state_path.unlink()

    # Build the same shared workflow prompt used by run_autoscience.py.
    repo_root = Path(__file__).resolve().parent.parent
    prompt = build_codex_prompt(
        project_name=project_name,
        project_path=project_path,
        repo_root=repo_root,
    )

    stdout, stderr = run_codex(
        prompt,
        cwd=project_path,
        timeout_seconds=timeout_seconds,
        stream=True,
    )
    return stdout, stderr

