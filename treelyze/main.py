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
    exclude: Optional[List[str]] = typer.Option(
        None,
        "--exclude",
        "-e",
        help="Directories or files to exclude (can be used multiple times)",
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
    config = load_config()

    # Use config exclude if not provided in command line
    if exclude is None:
        exclude_list = config.get("exclude", [])
    else:
        exclude_list = exclude  # exclude is already a list of strings

    # Print the exclude list for debugging
    typer.echo(f"Exclude list: {exclude_list}")

    analyze_tree(path, max_depth, exclude_list, summarize, output, model, prompt)


@app.command()
def config(
    set_key: Optional[str] = typer.Option(
        None,
        "--set",
        help="Set a configuration key (e.g., 'model', 'prompt', or 'exclude')",
    ),
    set_value: Optional[str] = typer.Argument(
        None, help="Value for the configuration key"
    ),
    show: bool = typer.Option(False, "--show", help="Show the current configuration"),
):
    """
    Manage Treelyze configuration.
    """
    config = load_config()

    if set_key and set_value:
        if set_key == "exclude":
            # Convert comma-separated string to list
            config[set_key] = [item.strip() for item in set_value.split(",")]
        else:
            config[set_key] = set_value
        save_config(config)
        typer.echo(f"Updated {set_key} in configuration.")
    elif show:
        for key, value in config.items():
            if key == "exclude":
                typer.echo(f"{key}: {', '.join(value)}")
            else:
                typer.echo(f"{key}: {value}")
    else:
        typer.echo(
            "Use --set KEY VALUE to update configuration or --show to display current settings."
        )


if __name__ == "__main__":
    app()
