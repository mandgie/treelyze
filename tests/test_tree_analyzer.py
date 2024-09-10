import os
import tempfile
import pytest
from typer.testing import CliRunner
from treelyze.main import app
from treelyze import tree_analyzer
import re


@pytest.fixture
def temp_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a sample directory structure
        os.makedirs(os.path.join(tmpdir, "src"))
        os.makedirs(os.path.join(tmpdir, "tests"))
        os.makedirs(os.path.join(tmpdir, "node_modules"))

        with open(os.path.join(tmpdir, "src", "main.py"), "w") as f:
            f.write("print('Hello, World!')")

        with open(os.path.join(tmpdir, "tests", "test_main.py"), "w") as f:
            f.write("def test_main():\n    assert True")

        with open(os.path.join(tmpdir, "node_modules", "package.json"), "w") as f:
            f.write('{"name": "test-package"}')

        yield tmpdir


def test_analyze_tree(temp_directory, monkeypatch, capfd):
    # Mock summarize_file to avoid actual API calls
    def mock_summarize_file(file_path, model, prompt):
        return f"Mocked summary for {os.path.basename(file_path)}"

    monkeypatch.setattr(tree_analyzer, "summarize_file", mock_summarize_file)

    # Test basic tree analysis
    tree_analyzer.analyze_tree(
        temp_directory,
        max_depth=None,
        exclude=["node_modules"],
        summarize=True,
        output_file=None,
    )

    captured = capfd.readouterr()
    assert "src" in captured.out
    assert "tests" in captured.out
    assert "node_modules" in captured.out
    assert "package.json" not in captured.out
    assert "main.py" in captured.out
    assert "test_main.py" in captured.out
    assert "Mocked summary for main.py" in captured.out
    assert "Mocked summary for test_main.py" in captured.out


def test_cli_run(temp_directory):
    runner = CliRunner()
    result = runner.invoke(app, ["run", temp_directory, "--summarize"])

    assert result.exit_code == 0
    assert "src" in result.output
    assert "tests" in result.output
    assert "node_modules" in result.output
    assert "package.json" not in result.output


def test_cli_config():
    runner = CliRunner()

    # Test showing config
    result = runner.invoke(app, ["config", "--show"])
    assert result.exit_code == 0
    assert "model:" in result.output
    assert "exclude:" in result.output

    # Test setting config
    result = runner.invoke(app, ["config", "--set", "model", "gpt-3.5-turbo"])
    assert (
        result.exit_code == 0
    ), f"Failed with exit code {result.exit_code}. Output: {result.output}"
    assert "Updated model in configuration" in result.output

    # Verify the change
    result = runner.invoke(app, ["config", "--show"])
    assert "model: gpt-3.5-turbo" in result.output
