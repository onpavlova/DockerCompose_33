
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import text
from typing import List


from app import schemas, models
from app.database import get_session
from app.jsonplaceholder_requests import fetch_all_data

router = APIRouter(prefix="/api", tags=["users & posts"])


@router.post("/load-data/", response_model=dict)
async def load_data_from_api(session: AsyncSession = Depends(get_session)):
    """
    Загрузка данных из JSONPlaceholder API
    """
    try:
        # Конкурентная загрузка данных
        users_data, posts_data = await fetch_all_data()

        # Создание пользователей
        users_dict = {}
        for user_data in users_data:
            user = models.User(
                id=user_data["id"],
                name=user_data["name"],
                username=user_data["username"],
                email=user_data["email"]
            )
            session.add(user)
            users_dict[user_data["id"]] = user

        await session.flush()

        # Создание постов
        for post_data in posts_data:
            post = models.Post(
                id=post_data["id"],
                user_id=post_data["userId"],
                title=post_data["title"],
                body=post_data["body"]
            )
            session.add(post)

        await session.commit()

        # Обновление счетчика последовательности
        if users_data:
            sequence_value = len(users_data)+1
            # Выполняем SQL-запрос для обновления последовательности
            await session.execute(
                text("SELECT setval('users_id_seq', :max_id, false)"), {"max_id": sequence_value}
            )
            await session.commit()

        # Обновление счетчика последовательности
        if posts_data:
            sequence_value = len(posts_data)+1
            # Выполняем SQL-запрос для обновления последовательности
            await session.execute(
                text("SELECT setval('posts_id_seq', :seq_val, false)"),
                {"seq_val": sequence_value}
            )
            await session.commit()


        return {
            "message": "Data loaded successfully",
            "users_loaded": len(users_data),
            "posts_loaded": len(posts_data)
        }

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/", response_model=schemas.UserBase)
async def create_user(
        user: schemas.UserCreate,
        session: AsyncSession = Depends(get_session)
):
    """
    Создание нового пользователя
    """
    try:
        db_user = models.User(**user.model_dump())
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/posts/", response_model=schemas.Post)
async def create_post(
        post: schemas.PostCreate,
        session: AsyncSession = Depends(get_session)
):
    """
    Создание нового поста
    """
    try:
        # Проверка существования пользователя
        result = await session.execute(
            select(models.User).where(models.User.id == post.user_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="User not found")

        db_post = models.Post(**post.dict())
        session.add(db_post)
        await session.commit()
        await session.refresh(db_post)
        return db_post
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/", response_model=List[schemas.User])
async def get_users(
        skip: int = 0,
        limit: int = 100,
        session: AsyncSession = Depends(get_session)
):
    """
    Получение списка пользователей с их постами
    """
    result = await session.execute(
        select(models.User)
        .offset(skip)
        .limit(limit)
        .options(selectinload(models.User.posts))
    )
    users = result.scalars().all()
    return users


@router.get("/posts/", response_model=List[schemas.Post])
async def get_posts(
        skip: int = 0,
        limit: int = 100,
        session: AsyncSession = Depends(get_session)
):
    """
    Получение списка постов
    """
    result = await session.execute(
        select(models.Post)
        .offset(skip)
        .limit(limit)
        .options(selectinload(models.Post.user))
    )
    posts = result.scalars().all()
    return posts


@router.get("/users/{user_id}", response_model=schemas.User)
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_session)
):
    """
    Получение пользователя по ID с его постами
    """
    result = await session.execute(
        select(models.User)
        .where(models.User.id == user_id)
        .options(selectinload(models.User.posts))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user