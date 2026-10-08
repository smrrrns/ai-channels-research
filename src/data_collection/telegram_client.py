import logging
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError, PhoneNumberInvalidError,
    ApiIdInvalidError, FloodWaitError
)

class TelegramClientManager:
    """Контекстный менеджер для подключения к Telegram"""

    def __init__(self, api_id: int, api_hash: str, session_name: str = 'ai_research'):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = None
        self.logger = self._setup_logging()

    def _setup_logging(self):
        logger = logging.getLogger('TelegramClient')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    async def __aenter__(self):
        await self.connect()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        try:
            self.logger.info(f"Подключаемся к Telegram, сессия {self.session_name}")
            self.client = TelegramClient(
                self.session_name,
                self.api_id,
                self.api_hash
            )

            await self.client.start()
            me = await self.client.get_me()
            self.logger.info(f"Успешный вход как: {me.first_name}")

        except (ApiIdInvalidError, PhoneNumberInvalidError, SessionPasswordNeededError) as e:
            self.logger.error(f"Ошибка аутентификации: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Ошибка подключения: {e}")
            raise

    async def disconnect(self):
        if self.client and self.client.is_connected():
            await self.client.disconnect()
            self.logger.info("Отключились от Telegram")