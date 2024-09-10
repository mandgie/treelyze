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
        "exclude": ["node_modules", ".git", "env"],
    }

    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, "r") as config_file:
            user_config = yaml.safe_load(config_file)
            default_config.update(user_config)
    else:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        save_config(default_config)

    if not isinstance(default_config["exclude"], list):
        default_config["exclude"] = [str(default_config["exclude"])]

    return default_config


def save_config(config):
    config_path = get_config_path()
    with open(config_path, "w") as config_file:
        yaml.dump(config, config_file)


def should_exclude(file_path: str, exclude_list: list) -> bool:
    path = Path(file_path)
    return any(
        exclude == path.name
        or exclude in str(path)
        or Path(exclude) == path
        or any(Path(exclude) == parent for parent in path.parents)
        for exclude in exclude_list
    )


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
    exclude_list = config["exclude"]

    if should_exclude(file_path, exclude_list):
        return f"File {file_path} is excluded based on configuration."

    try:
        with open(file_path, "r", errors="ignore") as file:
            content = file.read()

        if not content:
            return f"File {file_path} is empty."

    except Exception as e:
        return f"Error processing file {file_path}: {str(e)}"

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
