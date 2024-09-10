import os
import tempfile
import pytest
from treelyze import file_summarizer


@pytest.fixture
def temp_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        original_get_config_path = file_summarizer.get_config_path
        file_summarizer.get_config_path = lambda: os.path.join(tmpdir, "config.yaml")
        yield
        file_summarizer.get_config_path = original_get_config_path


def test_load_and_save_config(temp_config):
    # Test default config
    config = file_summarizer.load_config()
    assert config["model"] == "llama3:8b-instruct-q5_1"
    assert config["exclude"] == ["node_modules", ".git", "env"]

    # Test saving and loading custom config
    config["model"] = "gpt-4"
    config["exclude"].append("dist")
    file_summarizer.save_config(config)

    new_config = file_summarizer.load_config()
    assert new_config["model"] == "gpt-4"
    assert "dist" in new_config["exclude"]


def test_should_exclude():
    exclude_list = ["node_modules", ".git", "env"]

    assert file_summarizer.should_exclude("/path/to/node_modules/file.js", exclude_list)
    assert file_summarizer.should_exclude("/path/to/.git/config", exclude_list)
    assert file_summarizer.should_exclude("/path/to/env/lib/python3.8", exclude_list)
    assert not file_summarizer.should_exclude("/path/to/src/main.py", exclude_list)


def test_summarize_file(temp_config, monkeypatch):
    # Mock the requests.post function
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("API error")

    def mock_post(*args, **kwargs):
        return MockResponse(
            {"choices": [{"message": {"content": "Mocked summary"}}]}, 200
        )

    monkeypatch.setattr("requests.post", mock_post)

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("This is a test file content.")
        temp_file_path = temp_file.name

    try:
        summary = file_summarizer.summarize_file(temp_file_path)
        assert summary == "Mocked summary"

        # Test exclusion
        config = file_summarizer.load_config()
        config["exclude"].append(os.path.basename(temp_file_path))
        file_summarizer.save_config(config)

        excluded_summary = file_summarizer.summarize_file(temp_file_path)
        assert "excluded" in excluded_summary.lower()
    finally:
        os.unlink(temp_file_path)
