import os
from dataclasses import fields

from yc_autodeploy.models import FunctionParameters, AuthParameters


def get_env_vars() -> dict:
    user_inputs = list(filter(lambda env: env[0].startswith('INPUT_'), os.environ.items()))
    base_inputs = [f.name.upper() for f in fields(FunctionParameters) + fields(AuthParameters)[1:]]

    return {
        key.replace('INPUT_', ''): value
        for key, value in user_inputs
        if key.replace('INPUT_', '') not in base_inputs
    }
