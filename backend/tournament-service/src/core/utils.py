from pathlib import Path


def find_root_env() -> Path:
    current_path = Path(__file__).resolve()
    for parent_path in current_path.parents:
        environment_file = parent_path / ".env"
        if environment_file.exists():
            return environment_file
    return Path(".env")
