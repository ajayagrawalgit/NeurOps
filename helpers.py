import yaml
import os

def load_configs():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config if config else {}
