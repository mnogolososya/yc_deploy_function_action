import asyncio
import logging
import os
from dataclasses import asdict

from dynaconfig import settings
from yc_autodeploy.auth import YandexCloudAuth
from yc_autodeploy.function_service import YandexCloudServerlessFunctionService
from yc_autodeploy.models import FunctionParameters, AuthParameters
from yc_autodeploy.utils import get_env_vars

logging.basicConfig(level=settings.LOGGING_LEVEL, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__file__)


async def main() -> None:
    try:
        source_dir = os.getenv('INPUT_SOURCE_DIR')

        if not os.path.exists(source_dir):
            raise Exception('Source directory not found!')

        function_params = FunctionParameters(
            function_name=os.getenv('INPUT_FUNCTION_NAME', None),
            function_description=os.getenv('INPUT_FUNCTION_DESCRIPTION', None),
            runtime=os.getenv('INPUT_RUNTIME', None),
            version_description=os.getenv('INPUT_VERSION_DESCRIPTION', None),
            function_entrypoint=os.getenv('INPUT_FUNCTION_ENTRYPOINT', None),
            memory=int(os.getenv('INPUT_MEMORY', 128)),
            execution_timeout=int(os.getenv('INPUT_EXECUTION_TIMEOUT', 3)),
            source_dir=source_dir,
            folder_id=os.getenv('INPUT_FOLDER_ID', None),
            environment=get_env_vars(source_dir)
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
            logger.error(f'Deploy failed due to following error:\n{response.text}')

    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
