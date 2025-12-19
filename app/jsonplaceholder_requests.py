import aiohttp
from typing import List, Dict, Any
import asyncio

USERS_DATA_URL = "https://jsonplaceholder.typicode.com/users"
POSTS_DATA_URL = "https://jsonplaceholder.typicode.com/posts"


async def fetch_json(session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
    """
    Базовая функция для выполнения GET-запроса и получения JSON-данных
    """
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


async def fetch_users_data() -> List[Dict[str, Any]]:
    """
    Получение данных о пользователях
    """
    async with aiohttp.ClientSession() as session:
        users_data = await fetch_json(session, USERS_DATA_URL)
        return users_data


async def fetch_posts_data() -> List[Dict[str, Any]]:
    """
    Получение данных о постах
    """
    async with aiohttp.ClientSession() as session:
        posts_data = await fetch_json(session, POSTS_DATA_URL)
        return posts_data


async def fetch_all_data() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Конкурентное получение данных о пользователях и постах
    """
    users_data, posts_data = await asyncio.gather(
        fetch_users_data(),
        fetch_posts_data(),
    )
    return users_data, posts_data
