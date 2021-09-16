import json
import os
from os.path import exists


def get_env_vars(config_file: str) -> dict:
    env_var_names = []

    if exists(config_file):
        with open(config_file, 'rb') as f:
            env_var_names = [name.upper() for name in json.loads(f.read()).get('env', [])]

    user_inputs = list(filter(lambda env: env[0].startswith('INPUT_'), os.environ.items()))

    return {
        key.replace('INPUT_', ''): value
        for key, value in user_inputs
        if key.replace('INPUT_', '') in env_var_names
    }


def get_function_description(config_file: str) -> str:
    description = os.getenv('INPUT_FUNCTION_DESCRIPTION', '')

    if not description and exists(config_file):
        with open(config_file, 'rb') as f:
            description = json.loads(f.read()).get('description', '')

    return description
