import asyncio
import base64
import logging
import os
import zipfile
from io import BytesIO
from os.path import join
from typing import Generator, Optional

from httpx import Auth, AsyncClient, Request, Response

from dynaconfig import settings

logging.basicConfig(level=settings.LOGGING_LEVEL, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__file__)


class YandexCloudAuth(Auth):
    requires_response_body = True

    def __init__(self, auth_url: str, credentials: dict, session: Optional[AsyncClient] = None):
        self._token: str = ''
        self._auth_url = auth_url
        self._credentials = credentials
        self._session = session

    async def async_auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        response = None

        if self._token:
            request.headers["Authorization"] = f'Bearer {self._token}'
            response = yield request

        if not response or response.status_code in [401, 403]:
            refresh_response = await self.async_build_refresh_request()
            self.update_tokens(refresh_response)

            request.headers["Authorization"] = f'Bearer {self._token}'
            yield request

    async def async_build_refresh_request(self):
        if self._session:
            response = await self._session.post(url=self._auth_url, json=self._credentials)
        else:
            async with AsyncClient() as client:
                response = await client.post(url=self._auth_url, json=self._credentials)
        return response

    def update_tokens(self, response):
        if response.status_code == 200:
            self._token = response.json()['iamToken']


class YandexCloudServerlessFunctionService:
    def __init__(self, auth):
        self._auth = auth

    async def deploy_function(
            self,
            function_name: str,
            function_description: str,
            runtime: str,
            version_description: str,
            function_entrypoint: str,
            memory: int,
            execution_timeout: int,
            source_dir: str,
            environment: Optional[dict[str, str]] = None
    ) -> None:
        function = await self.get_function_by_name(folder_id=settings.FOLDER_ID, name=function_name)
        function_id = function['id'] if function else None

        if not function_id:
            logger.info(f'function with name {function_name} not found, creating a new one...')
            function_id = await self.create_function(
                folder_id=settings.FOLDER_ID,
                name=function_name,
                description=function_description
            )
            await asyncio.sleep(settings.CREATE_FUNCTION_TIMEOUT)

        logger.info('creating new function version...')
        await self.create_function_version(
            function_id=function_id,
            runtime=runtime,
            description=version_description,
            function_entrypoint=function_entrypoint,
            memory=memory,
            execution_timeout=execution_timeout,
            source_dir=source_dir,
            environment=environment
        )
        logger.info('done!')

    async def get_function_by_name(self, folder_id: str, name: str) -> Optional[dict]:
        params = {
            'folder_id': folder_id,
            'filter': f'name="{name}"'
        }

        async with AsyncClient() as client:
            response = await client.get(url=f'{settings.BASE_URL}/functions', params=params, auth=self._auth)

        functions = response.json().get('functions', None)

        return functions[0] if functions else None

    async def create_function(self, folder_id: str, name: str, description: str) -> str:
        data = {
            'folderId': folder_id,
            'name': name,
            'description': description
        }

        async with AsyncClient() as client:
            response = await client.post(url=f'{settings.BASE_URL}/functions', json=data, auth=self._auth)
            logger.debug(response.text)

        return response.json()['metadata']['functionId']

    async def create_function_version(
            self,
            function_id: str,
            runtime: str,
            description: str,
            function_entrypoint: str,
            memory: int,
            execution_timeout: int,
            source_dir: str,
            environment: Optional[dict[str, str]] = None
    ) -> None:
        data = {
            'function_id': function_id,
            'runtime': runtime,
            'description': description,
            'entrypoint': function_entrypoint,
            'resources': {'memory': memory * 1024 * 1024},
            'execution_timeout': {'seconds': execution_timeout},
            'content': base64.b64encode(self._generate_zip(source_dir)).decode('ascii')
        }

        if environment:
            data.update({'environment': environment})

        async with AsyncClient() as client:
            response = await client.post(url=f'{settings.BASE_URL}/versions', json=data, auth=self._auth)
            logger.debug(response.text)

    @staticmethod
    def _generate_zip(source_dir):
        buffer = BytesIO()

        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path, _, files in os.walk(source_dir):
                for file in files:
                    zf.write(join(path, file))

        return buffer.getvalue()


def get_env_vars(env_str: str) -> dict:
    return {key: value for key, value in [item.split('=') for item in env_str.split(',')]}


async def main():
    # TODO:
    #  - написать обертку для гитхаб экшна
    #  - добавить ретраи для создания версии
    auth = YandexCloudAuth(
        auth_url=settings.AUTH_URL,
        credentials={"yandexPassportOauthToken": settings.OAUTH_TOKEN},
    )
    function_service = YandexCloudServerlessFunctionService(auth=auth)

    await function_service.deploy_function(
        function_name=os.getenv('function_name'),
        function_description=os.getenv('function_description'),
        runtime=os.getenv('runtime'),
        version_description=os.getenv('version_description'),
        function_entrypoint=os.getenv('function_entrypoint'),
        memory=int(os.getenv('memory', 128)),
        execution_timeout=int(os.getenv('execution_timeout', 3)),
        source_dir=os.getenv('source_dir'),
        environment=get_env_vars(os.getenv('environment'))
    )


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
