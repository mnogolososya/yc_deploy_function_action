import asyncio
import logging
import os
from dataclasses import asdict
from os.path import join

from dynaconfig import settings
from yc_autodeploy.auth import YandexCloudAuth
from yc_autodeploy.function_service import YandexCloudServerlessFunctionService
from yc_autodeploy.models import FunctionParameters, AuthParameters
from yc_autodeploy.utils import get_env_vars, get_function_deploy_parameters

logging.basicConfig(level=settings.LOGGING_LEVEL, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__file__)


async def main() -> None:
    source_dir = os.getenv('INPUT_SOURCE_DIR')
    logger.info(f'Source dir is set to {source_dir}')

    if not os.path.exists(source_dir):
        raise Exception('Source directory not found!')

    deploy_config = join(source_dir, settings.DEPLOY_CONFIG_FILE_NAME)
    deploy_parameters = get_function_deploy_parameters(deploy_config)

    function_params = FunctionParameters(
        function_name=deploy_parameters['function_name'],
        function_description=deploy_parameters['function_description'],
        runtime=deploy_parameters['runtime'],
        version_description=deploy_parameters['version_description'],
        function_entrypoint=deploy_parameters['function_entrypoint'],
        memory=deploy_parameters['memory'],
        execution_timeout=deploy_parameters['execution_timeout'],
        service_account_id=deploy_parameters['service_account_id'],
        source_dir=source_dir,
        folder_id=os.getenv('INPUT_FOLDER_ID', None),
        environment=get_env_vars(deploy_config)
    )

    auth_params = AuthParameters(
        yc_auth_url=settings.AUTH_URL,
        yc_account_id=os.getenv('INPUT_YC_ACCOUNT_ID'),
        yc_key_id=os.getenv('INPUT_YC_KEY_ID'),
        yc_private_key=os.getenv('INPUT_YC_PRIVATE_KEY').replace('\\n', '\n'),
    )

    function_service = YandexCloudServerlessFunctionService(auth=YandexCloudAuth(**asdict(auth_params)))

    response = await function_service.deploy_function(**asdict(function_params))

    if response.status_code == 200:
        logger.info(f'Successfully deployed function:\n{response.text}')
    else:
        raise Exception(f'Deploy failed due to following error:\n{response.text}')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
