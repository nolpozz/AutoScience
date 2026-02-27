# AutoScience

AutoScience is a project-centric research runner that helps you go from a research question + raw data to:

- working analysis scripts,
- generated visualizations,
- a written report,
- and a reproducable Jupyter notebook.

It creates a dedicated folder per project, keeps all artifacts scoped to that project, and runs a Codex-driven multi-agent workflow to complete the pipeline.

## What The Tool Does

When you run `run_autoscience.py` with a project name, AutoScience:

1. Creates or reuses `projects/[project_name]/` with standard subfolders.
2. Checks authentication in this order:
   - `OPENAI_API_KEY` in environment (loads `.env` if present),
   - existing `codex login` session,
   - prompt for key only if both are missing.
3. Prompts you to confirm or replace `research_question.md`.
4. Pauses so you can upload files into `data/`.
5. Validates that `research_question.md` is set and `data/` has files.
6. Launches Codex from that specific project directory.
7. Instructs agents to process only that project's files and produce outputs in that same project.

The generated notebook is required to be named:

- `projects/[project_name]/reporting/[project_name]_reproducable.ipynb`

And it must interleave markdown with code so each code section explains:

- what the code is doing,
- why that approach was chosen,
- and alternative choices that could have been made.

## Workflow Stages

The run is executed as a strict ordered pipeline:

1. Parse and document data in `data/` (including schema artifacts).
2. Select variables and write `analysis_scripts/selected_variables.md`.
3. Create focused dataset(s) in `data/` named `{dataset}_focused.csv` with only selected variables.
4. Run analysis scripts and logs in `analysis_scripts/`.
5. Run visualization scripts and generate figures in `visualization_scripts/` (or stable reporting paths).
6. Generate `reporting/report.md` and `reporting/[project_name]_reproducable.ipynb`.

Codex is instructed to finish all stages and required artifacts before marking the run complete.

## Project Layout

Each project lives under:

- `projects/[project_name]/`

With this structure:

- `research_question.md`: your goal + constraints
- `data/`: raw and processed datasets + schema docs
- `analysis_scripts/`: analysis code and logs
- `visualization_scripts/`: plotting code and figure outputs
- `reporting/`: final `report.md` + reproducable notebook

## Agent Roles

AutoScience uses prompt instructions in `agents/`:

- `orchestrator.md`: manages pipeline state and handoffs
- `data_architect.md`: parses/cleans data and writes schema artifacts
- `variable_selector.md`: selects relevant variables for the research question; writes `analysis_scripts/selected_variables.md`
- `analyst_and_visualizer.md`: runs/fixes analysis + visualization scripts using selected variables
- `scientific_writer.md`: assembles `report.md` and reproducable notebook

All agents are instructed to stay inside the same selected project root for a run.

## Quick Start

From the repository root:

```bash
python run_autoscience.py --project my_experiment
```

Short flag version:

```bash
python run_autoscience.py -p my_experiment
```

Optional flags:

- `--projects-root /path/to/projects`: choose a custom projects directory
- `--clear-and-run`: clear generated artifacts and rerun while keeping `data/` and `research_question.md`

## Codex API Key Setup

You need Codex authentication by either method:

- `OPENAI_API_KEY` in environment / `.env`, or
- an active `codex login` session

You also need the `codex` CLI installed and available on `PATH`.

Recommended project-local setup (without committing secrets):

1. Create a local env file:

```bash
cat > .env <<'EOF'
OPENAI_API_KEY=your_api_key_here
EOF
```

2. Ensure `.env` is gitignored (if you use git):

```bash
echo ".env" >> .gitignore
```

3. Load it in your current shell before running (helper command):

```bash
source scripts/load_env.sh
```

Manual equivalent:

```bash
set -a
source .env
set +a
```

4. Run AutoScience:

```bash
python run_autoscience.py -p my_experiment
```

If you skip shell setup, AutoScience checks `codex login status` first and only prompts for `OPENAI_API_KEY` when no key and no login session are found (with an option to save it to `.env`).

## Walkthrough

1. Run:
   - `python run_autoscience.py --project my_experiment`
2. At the prompt, keep or replace the research question.
3. Upload your files (CSV, PDF, etc.) into:
   - `projects/my_experiment/data/`
4. Return to the terminal and press Enter when upload is complete.
5. AutoScience runs Codex and streams output in your terminal.
6. Review outputs in:
   - `projects/my_experiment/data/*_focused.csv`
   - `projects/my_experiment/analysis_scripts/`
   - `projects/my_experiment/visualization_scripts/`
   - `projects/my_experiment/reporting/report.md`
   - `projects/my_experiment/reporting/my_experiment_reproducable.ipynb`

## Example Output Tree

After a typical run, your project may look like:

projects/
└── my_experiment/
    ├── research_question.md
    ├── pipeline_state.txt
    ├── data/
    │   ├── raw_data.csv
    │   ├── extracted_tables.csv
    │   ├── raw_data_focused.csv
    │   ├── schema.md
    │   └── cleaning_log.md
    ├── analysis_scripts/
    │   ├── selected_variables.md
    │   ├── 01_load_and_validate.py
    │   ├── 02_model_and_metrics.py
    │   └── run_log.txt
    ├── visualization_scripts/
    │   ├── 01_plots.py
    │   └── output/
    │       ├── figure_1.png
    │       └── figure_2.png
    └── reporting/
        ├── report.md
        ├── my_experiment_reproducable.ipynb
        └── figures/
            ├── figure_1.png
            └── figure_2.png
```

## Typical Command Variants

Use default projects folder:

```bash
python run_autoscience.py -p oncology_study
```

Use a custom projects root:

```bash
python run_autoscience.py -p oncology_study --projects-root /tmp/autoscience_projects
```

Clear generated artifacts and rerun:

```bash
python run_autoscience.py -p oncology_study --clear-and-run
```

## Notes And Troubleshooting

- If you see `codex command not found`, install Codex and ensure it is available on your `PATH`.
- If Codex authentication fails, confirm `OPENAI_API_KEY` is valid. You can load it with `source scripts/load_env.sh` or enter it when prompted at launch.
- If `research_question.md` is still template/empty, update it and rerun.
- If `data/` is empty when you continue past the upload prompt, the run will stop and ask you to add files.
- Rerunning the same project updates existing artifacts rather than creating a new project.
