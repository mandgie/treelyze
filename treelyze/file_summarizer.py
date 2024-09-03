import yaml
import requests
import os
from pathlib import Path


def get_config_path():
    return str(Path.home() / ".treelyze/config.yaml")


def load_config():
    default_config = {
        "api_url": "http://localhost:11434/v1/chat/completions",
        "api_key": "your_api_key_here",
        "model": "llama3:8b-instruct-q5_1",
        "prompt": "You are a helpful assistant that summarizes file contents, including code files.",
    }

    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, "r") as config_file:
            user_config = yaml.safe_load(config_file)
            default_config.update(user_config)
    # Create the config directory if it doesn't exist
    else:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        save_config(default_config)
    return default_config


def save_config(config):
    config_path = get_config_path()
    with open(config_path, "w") as config_file:
        yaml.dump(config, config_file)


def summarize_file(file_path: str, model: str = None, prompt: str = None) -> str:
    config = load_config()

    # Override config with command-line arguments if provided
    if model:
        config["model"] = model
    if prompt:
        config["prompt"] = prompt

    api_url = config["api_url"]
    api_key = config["api_key"]
    model = config["model"]
    prompt = config["prompt"]

    try:
        with open(file_path, "r", errors="ignore") as file:
            content = file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"Summarize this file content in one short sentence. The file path is {file_path}:\n\n{content[:4000]}",
            },
        ],
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        summary = response.json()["choices"][0]["message"]["content"]
        return summary
    except Exception as e:
        return f"Error getting summary: {str(e)}"
