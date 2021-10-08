import json
import os
from os.path import exists
from typing import Any


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


def get_function_deploy_parameters(config_file: str) -> dict[str, Any]:
    function_description = os.getenv('INPUT_FUNCTION_DESCRIPTION', '')
    function_name = os.getenv('INPUT_FUNCTION_NAME', 'new-function')
    runtime = os.getenv('INPUT_FUNCTION_RUNTIME', 'python37')
    version_description = os.getenv('INPUT_VERSION_DESCRIPTION', '')
    function_entrypoint = os.getenv('INPUT_FUNCTION_ENTRYPOINT', 'index.handler')
    memory = int(os.getenv('INPUT_MEMORY', 128))
    execution_timeout = int(os.getenv('INPUT_EXECUTION_TIMEOUT', 3))

    if not exists(config_file):
        return {
            'function_description': function_description,
            'function_name': function_name,
            'runtime': runtime,
            'version_description': version_description,
            'function_entrypoint': function_entrypoint,
            'memory': memory,
            'execution_timeout': execution_timeout
        }

    with open(config_file, 'rb') as f:
        json_parameters = json.loads(f.read())

    return {
        'function_description': json_parameters.get('function_description', function_description),
        'function_name': json_parameters.get('function_name', function_name),
        'runtime': json_parameters.get('runtime', runtime),
        'version_description': json_parameters.get('version_description', version_description),
        'function_entrypoint': json_parameters.get('function_entrypoint', function_entrypoint),
        'memory': int(json_parameters.get('memory', memory)),
        'execution_timeout': int(json_parameters.get('execution_timeout', execution_timeout))
    }
