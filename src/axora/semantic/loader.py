from pathlib import Path
import yaml
from pydantic import ValidationError
from axora.semantic.models import SemanticModel


def load_semantic_model_from_yaml(file_path: str | Path) -> SemanticModel:
    """Loads and validates a semantic model YAML file against the SemanticModel schema.

    Raises FileNotFoundError if the file does not exist.
    Raises ValueError if the YAML is malformed or violates the schema.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Semantic model file not found: {path.absolute()}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValueError(f"Malformed YAML content in '{path}': {exc}") from exc

    if not isinstance(raw_data, dict) or "model" not in raw_data:
        raise ValueError(f"Invalid semantic file structure in '{path}': missing top-level 'model' key.")

    try:
        model = SemanticModel.model_validate(raw_data["model"])
        return model
    except ValidationError as exc:
        raise ValueError(f"Semantic model validation failed for '{path}':\n{exc}") from exc
