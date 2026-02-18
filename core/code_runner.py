"""
Code Runner: executes Python scripts in project subfolders and captures stdout/stderr
for agents to review.
"""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RunResult:
    """Result of running a single script."""

    script_path: Path
    returncode: int
    stdout: str
    stderr: str
    success: bool

    def summary(self) -> str:
        lines = [
            f"Script: {self.script_path}",
            f"Return code: {self.returncode}",
            f"Success: {self.success}",
        ]
        if self.stdout:
            lines.append("STDOUT:")
            lines.append(self.stdout)
        if self.stderr:
            lines.append("STDERR:")
            lines.append(self.stderr)
        return "\n".join(lines)


class CodeRunner:
    """
    Executes Python scripts found in project subfolders (e.g. analysis_scripts,
    visualization_scripts) and captures stdout/stderr for agent review.
    """

    def __init__(
        self,
        project_path: Path,
        timeout_seconds: Optional[int] = 300,
        python_executable: Optional[str] = None,
    ):
        """
        :param project_path: Path to the project root (e.g. projects/my_experiment).
        :param timeout_seconds: Max run time per script; None for no limit.
        :param python_executable: Python to use; defaults to sys.executable.
        """
        self.project_path = Path(project_path)
        self.timeout_seconds = timeout_seconds
        self.python_executable = python_executable or sys.executable

    def run_script(
        self,
        script_path: Path,
        cwd: Optional[Path] = None,
        env: Optional[dict] = None,
    ) -> RunResult:
        """
        Run a single Python script and return a RunResult.

        :param script_path: Path to the .py file (can be absolute or relative to project_path).
        :param cwd: Working directory during execution; defaults to script's parent.
        :param env: Optional env overlay; base is current process env.
        """
        path = Path(script_path)
        if not path.is_absolute():
            path = self.project_path / path
        if not path.exists():
            return RunResult(
                script_path=path,
                returncode=-1,
                stdout="",
                stderr=f"Script not found: {path}",
                success=False,
            )
        if cwd is None:
            cwd = path.parent
        else:
            cwd = Path(cwd)
        if not cwd.is_absolute():
            cwd = self.project_path / cwd

        try:
            proc = subprocess.run(
                [self.python_executable, str(path)],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                env={**(env or {})} if env else None,
            )
            return RunResult(
                script_path=path,
                returncode=proc.returncode,
                stdout=proc.stdout or "",
                stderr=proc.stderr or "",
                success=proc.returncode == 0,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                script_path=path,
                returncode=-1,
                stdout="",
                stderr=f"Script timed out after {self.timeout_seconds} seconds",
                success=False,
            )
        except Exception as e:
            return RunResult(
                script_path=path,
                returncode=-1,
                stdout="",
                stderr=str(e),
                success=False,
            )

    def run_scripts_in_folder(
        self,
        folder_name: str,
        pattern: str = "*.py",
    ) -> list[RunResult]:
        """
        Run all Python scripts in a project subfolder (e.g. 'analysis_scripts').
        Returns a list of RunResult in arbitrary order.
        """
        folder = self.project_path / folder_name
        if not folder.is_dir():
            return []
        results = []
        for script in sorted(folder.glob(pattern)):
            if script.is_file():
                results.append(self.run_script(script))
        return results
