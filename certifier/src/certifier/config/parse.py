from typing import Dict, Any

from pydantic import ValidationError

from certifier.config.models import Config


def parse_config(config: Dict[str, Any]) -> Config:
    try:
        return Config.parse_obj(config)
    except ValidationError as e:
        raise ValueError("Can't parse config") from e
