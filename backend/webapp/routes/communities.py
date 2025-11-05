"""
API эндпоинты для сообществ/чатов
"""

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.database import get_session, Community

router = APIRouter()


# ========================================
# Схемы ответов
# ========================================
class CommunityResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    type: str  # city или profession
    city: Optional[str]
    category: Optional[str]
    telegram_link: str

    class Config:
        from_attributes = True


# ========================================
# Эндпоинты
# ========================================
@router.get("/", response_model=List[CommunityResponse])
async def get_communities(
    type: Optional[str] = None,  # Фильтр: city или profession
    city: Optional[str] = None,  # Фильтр по городу (если type=city)
    category: Optional[str] = None,  # Фильтр по категории (если type=profession)
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список всех сообществ/чатов
    
    Query параметры:
    - type: Фильтр по типу (city или profession)
    - city: Фильтр по городу
    - category: Фильтр по категории профессии
    """
    query = select(Community)
    
    if type:
        query = query.where(Community.type == type)
    
    if city:
        query = query.where(Community.city == city)
    
    if category:
        query = query.where(Community.category == category)
    
    result = await session.execute(query)
    communities = result.scalars().all()
    
    return communities


@router.get("/{community_id}", response_model=CommunityResponse)
async def get_community(
    community_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о конкретном сообществе
    """
    result = await session.execute(
        select(Community).where(Community.id == community_id)
    )
    community = result.scalar_one_or_none()
    
    if not community:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Community not found")
    
    return community

