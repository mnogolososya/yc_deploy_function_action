import time
from typing import Generator

import jwt
from httpx import Request, Response, Auth, AsyncClient

from yc_autodeploy.dynaconfig import settings


class YandexCloudAuth(Auth):
    requires_response_body = True

    def __init__(self, yc_auth_url: str, yc_account_id: str, yc_key_id: str, yc_private_key: str):
        self._iam_token: str = ''
        self._yc_auth_url = yc_auth_url
        self._yc_account_id = yc_account_id
        self._yc_key_id = yc_key_id
        self._yc_private_key = yc_private_key

    async def async_auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        response = None

        if self._iam_token:
            request.headers["Authorization"] = f'Bearer {self._iam_token}'
            response = yield request

        if not response or response.status_code in [401, 403]:
            refresh_response = await self.async_build_refresh_request()
            self.update_tokens(refresh_response)

            request.headers["Authorization"] = f'Bearer {self._iam_token}'
            yield request

    async def async_build_refresh_request(self):
        async with AsyncClient() as client:
            return await client.post(url=self._yc_auth_url, json={'jwt': self.get_jwt()})

    def get_jwt(self):
        now = int(time.time())

        payload = {
            'aud': self._yc_auth_url,
            'iss': self._yc_account_id,
            'iat': now,
            'exp': now + settings.JWT_LIFETIME
        }

        return jwt.encode(
            payload=payload,
            key=self._yc_private_key,
            algorithm='PS256',
            headers={'kid': self._yc_key_id}
        )

    def update_tokens(self, response):
        if response.status_code == 200:
            self._iam_token = response.json()['iamToken']