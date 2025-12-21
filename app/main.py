
from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from app.database  import init_db, engine
from app.routers import users_posts


@asynccontextmanager
async def lifespan():
    """
       Контекстный менеджер для управления жизненным циклом приложения
       """
    # Инициализация при запуске
    try:
        print("Initializing database...")
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Если есть проблема с созданием таблиц, продолжаем без них
        # или пересоздаем
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database recreated successfully")
        except Exception as e2:
            print(f"❌ Failed to recreate database: {e2}")
    yield
    # Завершение при остановке
    print("Closing database connections...")
    await engine.dispose()
    print("✅ Database connections closed")


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