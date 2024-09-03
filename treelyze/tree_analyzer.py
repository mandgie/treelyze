import os
import typer
from typing import List, Optional, Set
from .file_summarizer import summarize_file


def analyze_tree(
    startpath: str,
    max_depth: Optional[int],
    exclude: List[str],
    summarize: bool,
    output_file: Optional[typer.FileBinaryWrite],
    model: Optional[str] = None,
    prompt: Optional[str] = None,
):
    exclude_set: Set[str] = set(exclude)
    start_path = os.path.abspath(startpath)

    if not os.path.isdir(start_path):
        typer.echo(f"Error: {start_path} is not a valid directory", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Treelyze: Analyzing {start_path}")
    if output_file:
        output_file.write(f"Treelyze: Analysis of {start_path}\n".encode("utf-8"))

    print_tree(
        start_path, exclude_set, max_depth, summarize, output_file, model, prompt
    )

    if output_file:
        typer.echo(f"Analysis written to {output_file.name}")


def print_tree(
    startpath: str,
    exclude_dirs: Set[str],
    max_depth: Optional[int],
    summarize: bool,
    output_file: Optional[typer.FileBinaryWrite],
    model: Optional[str],
    prompt: Optional[str],
):
    def write_output(text: str):
        typer.echo(text)
        if output_file:
            output_file.write((text + "\n").encode("utf-8"))

    def print_directory_contents(path: str, prefix: str = ""):
        entries = sorted(
            os.scandir(path), key=lambda e: (not e.is_file(), e.name.lower())
        )
        for index, entry in enumerate(entries):
            is_last = index == len(entries) - 1
            connector = "└── " if is_last else "├── "
            write_output(f"{prefix}{connector}{entry.name}")

            if entry.is_file() and summarize:
                summary = summarize_file(entry.path, model, prompt)
                write_output(
                    f"{prefix}{'    ' if is_last else '│   '}Summary: {summary}"
                )

            if entry.is_dir():
                if entry.name in exclude_dirs:
                    write_output(f"{prefix}{'    ' if is_last else '│   '}...")
                elif max_depth is None or prefix.count("│   ") < max_depth:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    print_directory_contents(entry.path, next_prefix)

    write_output(f"{os.path.basename(startpath)}/")
    print_directory_contents(startpath, "    ")
