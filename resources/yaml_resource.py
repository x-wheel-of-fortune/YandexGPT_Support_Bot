from functools import cache


@cache
def load_yaml_resource(yaml_file_path: str):
    with open(yaml_file_path, encoding="utf8") as file:
        return yaml.safe_load(file)
