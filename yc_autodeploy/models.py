from dataclasses import dataclass


@dataclass
class FunctionParameters:
    function_name: str
    function_description: str
    runtime: str
    version_description: str
    function_entrypoint: str
    memory: int
    execution_timeout: int
    service_account_id: str
    source_dir: str
    folder_id: str
    environment: dict[str, str]


@dataclass
class AuthParameters:
    yc_auth_url: str
    yc_account_id: str
    yc_key_id: str
    yc_private_key: str
