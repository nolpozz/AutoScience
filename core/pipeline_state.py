"""
Pipeline state for the orchestrator: read/write the current phase so agents
and the engine know where the project stands.
"""

from pathlib import Path

VALID_STATES = (
    "Parsing Data",
    "Running Analysis",
    "Visualizing",
    "Reporting",
    "Done",
)

STATE_FILE = "pipeline_state.txt"


def get_state_file(project_path: Path) -> Path:
    return Path(project_path) / STATE_FILE


def read_state(project_path: Path) -> str:
    """Return current pipeline state; default to first state if missing."""
    path = get_state_file(project_path)
    if not path.exists():
        return VALID_STATES[0]
    return path.read_text(encoding="utf-8").strip() or VALID_STATES[0]


def write_state(project_path: Path, state: str) -> None:
    """Write pipeline state; state should be one of VALID_STATES."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state: {state}. Must be one of {VALID_STATES}")
    get_state_file(project_path).write_text(state, encoding="utf-8")


def next_state(project_path: Path) -> str | None:
    """Advance to the next state; return new state or None if already Done."""
    current = read_state(project_path)
    try:
        i = VALID_STATES.index(current)
    except ValueError:
        return VALID_STATES[0]
    if i >= len(VALID_STATES) - 1:
        return None
    new_state = VALID_STATES[i + 1]
    write_state(project_path, new_state)
    return new_state
