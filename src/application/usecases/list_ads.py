import asyncio

from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import AdView, ListAdsPort
from src.application.ports.user_profile import UserProfileService


class ListAds(ListAdsPort):
    def __init__(self, uow: UnitOfWork, user_profile: UserProfileService) -> None:
        self._uow = uow
        self._user_profile = user_profile

    async def execute(
        self,
        user_id: int | None,
        limit: int,
        offset: int,
    ) -> tuple[list[AdView], int]:
        async with self._uow:
            ads, total = await self._uow.ads.list(
                user_id=user_id,
                limit=limit,
                offset=offset,
            )

        unique_ids = list({ad.user_id for ad in ads})
        users = await asyncio.gather(
            *(self._user_profile.user(uid) for uid in unique_ids)
        )
        name_map = {uid: u.name for uid, u in zip(unique_ids, users) if u is not None}
        views = [AdView(ad=ad, user_name=name_map.get(ad.user_id)) for ad in ads]
        return views, total
