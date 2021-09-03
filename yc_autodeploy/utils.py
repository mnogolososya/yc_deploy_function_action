import json
import os
from os.path import exists, join

from yc_autodeploy.dynaconfig import settings


def get_env_vars(source_dir: str) -> dict:
    deploy_config = join(source_dir, settings.DEPLOY_CONFIG_FILE_NAME)

    if exists(deploy_config):
        with open(deploy_config, 'rb') as f:
            env_var_names = [name.upper() for name in json.loads(f.read()).get('env')]
    else:
        env_var_names = []

    user_inputs = list(filter(lambda env: env[0].startswith('INPUT_'), os.environ.items()))

    return {
        key.replace('INPUT_', ''): value
        for key, value in user_inputs
        if key.replace('INPUT_', '') in env_var_names
    }
