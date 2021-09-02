import asyncio
import base64
import logging
import pathlib
import zipfile
from io import BytesIO
from typing import Optional

from httpx import AsyncClient

from yc_autodeploy.dynaconfig import settings

logger = logging.getLogger(__file__)


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
            folder_id: str,
            environment: Optional[dict[str, str]] = None
    ) -> None:
        function = await self.get_function_by_name(folder_id=folder_id, name=function_name)
        function_id = function['id'] if function else None

        if not function_id:
            logger.info(f'function with name {function_name} not found, creating a new one...')
            function_id = await self.create_function(
                folder_id=folder_id,
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
            for file in pathlib.Path(source_dir).rglob('*'):
                zf.write(file, file.name)

        return buffer.getvalue()
