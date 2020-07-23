import logging
from typing import List, Optional

import httpx
from ai_dungeon import config

_BASE_URL = "https://translate.api.cloud.yandex.net/translate/v2"


async def _make_request(path, payload=None) -> dict:
    """
    Wrapper function to make request conveniently 
    :param path: API endpoint
    :param payload: JSON data with request
    :return: API call result
    """
    async with httpx.AsyncClient() as client:
        return (await client.post(f"{_BASE_URL}/{path}", json={'folder_id': config.YANDEX_FOLDER_ID, **(payload or {})},
                                  headers={"Authorization": f"Bearer {config.YANDEX_IAM_TOKEN}"})).json()


async def translate(text: str, source_lang: Optional[str], target_lang: str) -> str:
    """
    Translates given text
    :param text: Text to translate
    :param source_lang: Input language or None, ISO 639-1 format
    :param target_lang: Language of the output, ISO 639-1 format
    :return: Text in target_lang
    """
    return (await _make_request("translate", {
        'texts': [text],
        'sourceLanguageCode': source_lang,
        'targetLanguageCode': target_lang,
    }))['translations'][0]['text']


async def languages() -> List[dict]:
    """
    :return: List of languages available in Yandex.Translator in format { "name": str, "code": str }
    """
    return (await _make_request("languages"))['languages']


async def detect_language(text: str) -> str:
    """
    :param text: Source text
    :return: Source text language in ISO 639-1 format.
    """
    return (await _make_request('detect', {'text': text}))['languageCode']
