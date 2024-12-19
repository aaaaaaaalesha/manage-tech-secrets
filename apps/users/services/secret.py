import hashlib
import secrets

from typing import TypeAlias

# Строка, представляющая собой открытое значение текста (или секрета).
PlainStr: TypeAlias = str
# Строка, представляющая собой хэш-значение некоторого открытого текста (или секрета).
HashStr: TypeAlias = str


def generate_secret_string(size: int = 32) -> PlainStr:
    """
    Генерирует секретную последовательность символов необходимого размера,
    состоящую из псевдослучайных URL-safe-символов.
    :param size: Длина необходимого секрета.
    """
    return secrets.token_urlsafe(nbytes=size)[:size]


def make_hash(plain_text: PlainStr, encoding="ascii", hash_func=hashlib.sha256) -> HashStr:
    """
    Вычисление хэша открытого текста.
    :param plain_text: Открытый текст.
    :param encoding: Кодировка для формирования хеша. По умолчанию используется ASCII, т.к. `secrets.token_urlsafe` использует её для генерации секрета.
    :param hash_func: Функция хеширования из модуля `hashlib`. По умолчанию используется `SHA-256`.
    :return: Строковое представление полученного хеша.
    """
    encoded_secret: bytes = plain_text.encode(encoding)
    return hash_func(encoded_secret).hexdigest()


def is_valid_hash(provided_plain_text: PlainStr, original_hash_value: HashStr, hash_func=hashlib.sha256) -> bool:
    """
    Проверка соответствия переданного открытого текста его хэш-значению.
    :param provided_plain_text: Представленный открытый текст для проверки.
    :param original_hash_value: Строковое значение исходного хэша. Может быть получено функцией `make_hash`.
    :param hash_func: Функция хеширования из модуля `hashlib`. По умолчанию используется `SHA-256`.
    :return: `True`, если вычисленный хэш открытого текста совпал с исходным, `False` - в противном случае.
    """
    return make_hash(provided_plain_text, hash_func=hash_func) == original_hash_value
