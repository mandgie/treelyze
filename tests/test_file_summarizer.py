import os
import tempfile
from treelyze import file_summarizer


def test_load_and_save_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override the config path for testing
        original_get_config_path = file_summarizer.get_config_path
        file_summarizer.get_config_path = lambda: os.path.join(
            tmpdir, ".treelyze_config.yaml"
        )

        try:
            # Test default config
            config = file_summarizer.load_config()
            assert config["model"] == "llama3:8b-instruct-q5_1"

            # Test saving and loading custom config
            config["model"] = "gpt-4"
            file_summarizer.save_config(config)

            new_config = file_summarizer.load_config()
            assert new_config["model"] == "gpt-4"

        finally:
            # Restore the original get_config_path function
            file_summarizer.get_config_path = original_get_config_path
