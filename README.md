# Treelyze

Treelyze is a powerful CLI tool for analyzing directory structures and optionally summarizing file contents using Language Models (LLMs). It provides an easy-to-use interface for exploring and understanding complex directory hierarchies.

## Features

- Analyze directory structures with customizable depth
- Exclude specific directories from analysis
- Summarize file contents using LLMs (optional)
- Configurable settings for model and prompt customization
- Output results to file or console

## Installation

You can install Treelyze using pip:

```bash
pip install treelyze
```

## Usage

### Basic Usage

To analyze the current directory:

```bash
treelyze run
```

To analyze a specific directory:

```bash
treelyze run /path/to/directory
```

### Options

- `--max-depth, -d`: Set the maximum depth for directory traversal
- `--exclude, -e`: Specify directories to exclude (can be used multiple times)
- `--summarize, -s`: Enable file content summarization using LLM
- `--output, -o`: Specify an output file for the analysis results
- `--model`: Override the default language model for summarization
- `--prompt`: Override the default summarization prompt

### Examples

Analyze a directory with a maximum depth of 3, excluding 'node_modules':

```bash
treelyze run /path/to/directory --max-depth 3 --exclude node_modules
```

Analyze and summarize files, outputting results to a file:

```bash
treelyze run /path/to/directory --summarize --output results.txt
```

### Configuration

You can manage Treelyze configuration using the `config` subcommand:

```bash
# Show current configuration
treelyze config --show

# Set a configuration value
treelyze config --set model "gpt-3.5-turbo"
treelyze config --set prompt "Summarize this file concisely:"
```

**Note:** The configuration file is located at `~/.treelyze/config.yaml` in your home folder.

## Contributing

Contributions to Treelyze are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.