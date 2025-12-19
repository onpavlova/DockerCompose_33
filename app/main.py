from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from database  import init_db, engine
from routers import users_posts

#from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация при запуске
    await init_db()
    print("Database initialized")
    yield
    # Завершение при остановке
    await engine.dispose()
    print("Database connection closed")


app = FastAPI(
    title="JSONPlaceholder Data Loader",
    description="API для загрузки данных из JSONPlaceholder",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем роутеры
app.include_router(users_posts.router)

# Монтируем статические файлы и шаблоны
#app.mount("static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Главная страница с выводом данных
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


async def async_main():
    """
    Асинхронная главная функция для инициализации
    """
    await init_db()


def main():
    """
    Главная функция для запуска
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )


if __name__ == "__main__":
    main()