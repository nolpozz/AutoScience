"""
Run Codex to process data and execute the analysis pipeline for a project.
"""

import re
import subprocess
import sys
import threading
from pathlib import Path


ANSI_RE = re.compile(
    r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07|\x1b[@-Z\\-_]"
)


def clean_output(text: str) -> str:
    if not text:
        return ""
    text = ANSI_RE.sub("", text)
    text = re.sub(r".\x08", "", text)  # remove overprints
    return text


def run_codex(
    prompt: str,
    cwd: Path | None = None,
    timeout_seconds: int = 1800,
    stream: bool = True,
) -> tuple[str, str]:
    """
    Invoke codex exec with the given prompt.
    :param prompt: Instruction string for Codex.
    :param cwd: Working directory; default is current directory.
    :param timeout_seconds: Max run time.
    :param stream: If True (default), print stdout/stderr in real time.
    :return: (stdout, stderr) with ANSI codes stripped.
    """
    proc = subprocess.Popen(
        ["codex", "exec", "--skip-git-repo-check", prompt],
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    out_lines: list[str] = []
    err_lines: list[str] = []
    stream_output = stream

    def read_stream(pipe, lines: list[str], file_to_print: object):
        for line in iter(pipe.readline, ""):
            cleaned = clean_output(line)
            lines.append(cleaned)
            if stream_output and cleaned:
                print(cleaned, end="" if cleaned.endswith("\n") else "\n", file=file_to_print)
                sys.stdout.flush()
                sys.stderr.flush()

    t_out = threading.Thread(target=read_stream, args=(proc.stdout, out_lines, sys.stdout))
    t_err = threading.Thread(target=read_stream, args=(proc.stderr, err_lines, sys.stderr))
    t_out.daemon = True
    t_err.daemon = True
    t_out.start()
    t_err.start()

    try:
        proc.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        t_out.join(timeout=2)
        t_err.join(timeout=2)
        raise
    t_out.join(timeout=5)
    t_err.join(timeout=5)

    out = clean_output("".join(out_lines))
    err = clean_output("".join(err_lines))
    return out, err
