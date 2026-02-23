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
2. Prompts for your research question and saves it to:
   - `projects/[project_name]/research_question.md`
3. Waits for you to upload data into:
   - `projects/[project_name]/data/`
4. Launches Codex from that specific project directory.
5. Instructs agents to process only that project's files and produce outputs in that same project.

The generated notebook is required to be named:

- `projects/[project_name]/reporting/[project_name]_reproducable.ipynb`

And it must interleave markdown with code so each code section explains:

- what the code is doing,
- why that approach was chosen,
- and alternative choices that could have been made.

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
- `--no-codex`: create structure + question prompt, but skip Codex execution

## Walkthrough

1. Run:
   - `python run_autoscience.py --project my_experiment`
2. Enter your research question when prompted.
3. Put your files (CSV, PDF, etc.) into:
   - `projects/my_experiment/data/`
4. Press Enter to continue.
5. AutoScience runs Codex and streams output in your terminal.
6. Review outputs in:
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

Scaffold only (no Codex run):

```bash
python run_autoscience.py -p oncology_study --no-codex
```

## Notes And Troubleshooting

- If you see `codex command not found`, install Codex and ensure it is available on your `PATH`.
- If no research question is entered, you can edit `projects/[project_name]/research_question.md` manually and rerun.
- Rerunning the same project updates existing artifacts rather than creating a new project.

## How To Upload Data

When `run_autoscience.py` pauses and asks you to upload data, copy your files into:

- `projects/[project_name]/data/`

You can do this with either:

- a file explorer (drag and drop), or
- a terminal command.

Linux/macOS example:

```bash
cp /path/to/my_data.csv /path/to/AutoScience/projects/my_experiment/data/
cp /path/to/paper.pdf /path/to/AutoScience/projects/my_experiment/data/
```

Windows PowerShell example:

```powershell
Copy-Item "C:\path\to\my_data.csv" "C:\path\to\AutoScience\projects\my_experiment\data\"
Copy-Item "C:\path\to\paper.pdf" "C:\path\to\AutoScience\projects\my_experiment\data\"
```

After copying files, return to the script prompt and press Enter to continue.
