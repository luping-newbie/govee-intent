# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import os
import uuid
from collections.abc import AsyncIterator
from typing import Optional

from aiohttp import ClientSession, WSMsgType, WSServerHandshakeError

from rtclient.models import ServerMessageType, UserMessageType, create_message_from_dict
from rtclient.util.user_agent import get_user_agent


class ConnectionError(Exception):
    def __init__(self, message: str, headers=None):
        super().__init__(message)
        self.headers = headers

    pass


class RTLowLevelClient:
    def __init__(self):
        self._url = os.environ["AZURE_OPENAI_ENDPOINT"]
        self._api_key = os.environ["AZURE_OPENAI_API_KEY"]
        self._api_version = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_VERSION"]
        self._azure_deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]
        self._path = os.environ["AZURE_OPENAI_PATH"]

        self._session = ClientSession(base_url=self._url)
        self.request_id: Optional[uuid.UUID] = None

    async def _get_auth(self):
        # return {"api-key": self._key_credential.key}
        return {"api-key": self._api_key}

    async def connect(self):
        try:
            self.request_id = uuid.uuid4()

            auth_headers = await self._get_auth()
            headers = {
                "x-ms-client-request-id": str(self.request_id),
                "User-Agent": get_user_agent(),
                **auth_headers,
            }
            self.ws = await self._session.ws_connect(
                self._path,
                headers=headers,
                params={"deployment": self._azure_deployment, "api-version": self._api_version},
            )

        except WSServerHandshakeError as e:
            await self._session.close()
            error_message = f"Received status code {e.status} from the server"
            raise ConnectionError(error_message, e.headers) from e

    async def send(self, message: UserMessageType):
        message._is_azure = True
        message_json = message.model_dump_json(exclude_unset=True)
        # print(f"low level client send {message_json}")
        await self.ws.send_str(message_json)

    async def recv(self) -> ServerMessageType | None:
        if self.ws.closed:
            return None
        websocket_message = await self.ws.receive()
        print(f"websocket_message {websocket_message}")
        if websocket_message.type == WSMsgType.TEXT:
            data = json.loads(websocket_message.data)
            msg = create_message_from_dict(data)
            return msg
        else:
            return None

    def __aiter__(self) -> AsyncIterator[ServerMessageType | None]:
        return self

    async def __anext__(self):
        message = await self.recv()
        if message is None:
            raise StopAsyncIteration
        return message

    async def close(self):
        await self.ws.close()
        await self._session.close()

    @property
    def closed(self) -> bool:
        return self.ws.closed

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.close()
