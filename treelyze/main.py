import typer
from typing import List, Optional
from .tree_analyzer import analyze_tree
from .file_summarizer import load_config, save_config

app = typer.Typer(
    name="Treelyze",
    help="A CLI tool for analyzing directory structures and summarizing files.",
)


@app.command()
def run(
    path: str = typer.Argument(
        ".", help="Path to the directory (default: current directory)"
    ),
    max_depth: Optional[int] = typer.Option(
        None, "--max-depth", "-d", help="Maximum depth to explore"
    ),
    exclude: List[str] = typer.Option(
        ["node_modules", ".git", "env"],
        "--exclude",
        "-e",
        help="Directories to exclude",
    ),
    summarize: bool = typer.Option(
        False, "--summarize", "-s", help="Summarize file contents using LLM"
    ),
    output: Optional[typer.FileBinaryWrite] = typer.Option(
        None, "--output", "-o", help="Output file to write the analysis"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", help="Override the default language model"
    ),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Override the default summarization prompt"
    ),
):
    """
    Analyze a directory structure and optionally summarize files.
    """
    analyze_tree(path, max_depth, exclude, summarize, output, model, prompt)


@app.command()
def config(
    set_key: Optional[str] = typer.Option(
        None, "--set", help="Set a configuration key (e.g., 'model' or 'prompt')"
    ),
    set_value: Optional[str] = typer.Option(
        None, help="Value for the configuration key"
    ),
    show: bool = typer.Option(False, "--show", help="Show the current configuration"),
):
    """
    Manage Treelyze configuration.
    """
    config = load_config()

    if set_key and set_value:
        config[set_key] = set_value
        save_config(config)
        typer.echo(f"Updated {set_key} in configuration.")
    elif show:
        for key, value in config.items():
            typer.echo(f"{key}: {value}")
    else:
        typer.echo(
            "Use --set KEY VALUE to update configuration or --show to display current settings."
        )


if __name__ == "__main__":
    app()
