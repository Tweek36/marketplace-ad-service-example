from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repositories import AdRepository
from src.domain.entities import Ad, AdStatus
from src.infrastructure.persistence.models import AdModel


class SQLAlchemyAdRepository(AdRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        title: str,
        description: str,
        price: int,
        category: str,
        city: str,
        user_id: int,
    ) -> Ad:
        model = AdModel(
            title=title,
            description=description,
            price=price,
            category=category,
            city=city,
            user_id=user_id,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

    async def save(self, ad: Ad) -> None:
        await self._session.execute(
            update(AdModel)
            .where(AdModel.id == ad.id)
            .values(
                title=ad.title,
                description=ad.description,
                price=ad.price,
                category=ad.category,
                city=ad.city,
                user_id=ad.user_id,
                status=ad.status.value,
                updated_at=ad.updated_at,
            )
        )
        await self._session.flush()

    async def get_by_id(self, ad_id: int) -> Ad | None:
        result = await self._session.execute(select(AdModel).where(AdModel.id == ad_id))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return _to_entity(model)

    async def get_by_user_id(self, user_id: int) -> list[Ad]:
        result = await self._session.execute(
            select(AdModel).where(AdModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [_to_entity(model) for model in models]

    async def list(self, limit: int, offset: int) -> list[Ad]:
        result = await self._session.execute(
            select(AdModel).limit(limit).offset(offset)
        )
        models = result.scalars().all()
        return [_to_entity(model) for model in models]

    async def update(self, ad_id: int, **kwargs) -> Ad | None:
        result = await self._session.execute(select(AdModel).where(AdModel.id == ad_id))
        model = result.scalar_one_or_none()
        if model is None:
            return None

        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)

        await self._session.flush()
        return _to_entity(model)

    async def delete(self, ad_id: int) -> bool:
        result = await self._session.execute(select(AdModel).where(AdModel.id == ad_id))
        model = result.scalar_one_or_none()
        if model is None:
            return False

        model.status = AdStatus.ARCHIVED.value
        await self._session.flush()
        return True

    async def count(self) -> int:
        result = await self._session.execute(select(AdModel))
        return len(result.scalars().all())


def _to_entity(model: AdModel) -> Ad:
    return Ad(
        id=model.id,
        title=model.title,
        description=model.description,
        price=model.price,
        category=model.category,
        city=model.city,
        user_id=model.user_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        status=AdStatus(model.status),
        views=model.views,
    )
