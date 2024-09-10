import os
import typer
from typing import List, Optional
from .file_summarizer import summarize_file, should_exclude


def analyze_tree(
    startpath: str,
    max_depth: Optional[int],
    exclude: List[str],
    summarize: bool,
    output_file: Optional[typer.FileBinaryWrite],
    model: Optional[str] = None,
    prompt: Optional[str] = None,
):
    start_path = os.path.abspath(startpath)

    if not os.path.isdir(start_path):
        typer.echo(f"Error: {start_path} is not a valid directory", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Treelyze: Analyzing {start_path}")
    if output_file:
        output_file.write(f"Treelyze: Analysis of {start_path}\n".encode("utf-8"))

    # Print the exclude list for debugging
    typer.echo(f"Exclude list: {exclude}")

    print_tree(start_path, exclude, max_depth, summarize, output_file, model, prompt)

    if output_file:
        typer.echo(f"Analysis written to {output_file.name}")


def print_tree(
    startpath: str,
    exclude: List[str],
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

    def print_directory_contents(path: str, prefix: str = "", current_depth: int = 0):
        if max_depth is not None and current_depth > max_depth:
            return

        entries = sorted(
            os.scandir(path), key=lambda e: (not e.is_file(), e.name.lower())
        )
        for index, entry in enumerate(entries):
            is_last = index == len(entries) - 1
            connector = "└── " if is_last else "├── "

            if should_exclude(entry.path, exclude):
                # write_output(f"{prefix}{connector}{entry.name} (excluded)")
                continue

            write_output(f"{prefix}{connector}{entry.name}")

            if entry.is_file() and summarize:
                summary = summarize_file(entry.path, model, prompt)
                write_output(
                    f"{prefix}{'    ' if is_last else '│   '}Summary: {summary}"
                )

            if entry.is_dir():
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_directory_contents(entry.path, next_prefix, current_depth + 1)

    write_output(f"{os.path.basename(startpath)}/")
    print_directory_contents(startpath, "    ")
