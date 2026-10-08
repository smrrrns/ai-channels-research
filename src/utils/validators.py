import re
import logging

class TextValidator:
    """Валидатор и очиститель текста"""

    @staticmethod
    def clean_text_for_csv(text: str) -> str:
        """Склеивает переносы строк и экранирует кавычки"""
        if not text:
            return ""

        cleaned = re.sub(r'\s+', ' ', text.replace('\n', ' ').replace('\r', ' ')).strip()

        if '"' in cleaned:
            cleaned = cleaned.replace('"', '""')

        return cleaned

class ConfigValidator:
    """Валидатор конфигурации"""

    @staticmethod
    def validate_api_credentials(api_id: str, api_hash: str) -> list:
        errors = []

        if not api_id:
            errors.append("API_ID не найден в .env файле")
        elif not api_id.isdigit():
            errors.append("API_ID должен быть числом")

        if not api_hash:
            errors.append("API_HASH не найден в .env файле")
        elif len(api_hash) != 32:
            errors.append("API_HASH должен содержать 32 символа")

        return errors