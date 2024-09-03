from treelyze.file_summarizer import load_config, save_config
import os
import tempfile


def test_load_and_save_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override the config path for testing
        import treelyze.file_summarizer

        treelyze.file_summarizer.get_config_path = lambda: os.path.join(
            tmpdir, "./treelyze/config.yaml"
        )

        # Test default config
        config = load_config()
        assert config["model"] == "llama3:8b-instruct-q5_1"

        # Test saving and loading custom config
        config["model"] = "gpt-4"
        save_config(config)

        new_config = load_config()
        assert new_config["model"] == "gpt-4"
