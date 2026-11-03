from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from identity_service.domain.entities import User
from identity_service.domain.repositories import UserRepository
from identity_service.domain.value_objects import (
    DisplayName,
    EmailAddress,
    FamilyName,
    GivenName,
    PhoneNumber,
    UserId,
    UserMetadata,
    UserStatus,
    UserStatusValue,
    UserType,
)
from identity_service.infrastructure.persistence.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, user: User) -> None:
        model = await self.session.get(UserModel, str(user.user_id))
        if model is None:
            model = UserModel(user_id=str(user.user_id))
            self.session.add(model)
        model.tenant_id = user.tenant_id
        model.email = str(user.email)
        model.display_name = str(user.display_name)
        model.given_name = str(user.given_name)
        model.family_name = str(user.family_name)
        model.phone_number = str(user.phone_number)
        model.status = str(user.status)
        model.user_type = str(user.type)
        model.metadata_ = dict(user.metadata.values)
        model.created_at = user.created_at
        model.updated_at = user.updated_at
        await self.session.flush()

    async def get_by_id(self, tenant_id: str, user_id: UserId) -> User | None:
        model = await self.session.scalar(
            select(UserModel).where(
                UserModel.user_id == str(user_id), UserModel.tenant_id == tenant_id
            )
        )
        return self._read(model) if model else None

    async def get_by_email(self, tenant_id: str, email: EmailAddress) -> User | None:
        model = await self.session.scalar(
            select(UserModel).where(UserModel.tenant_id == tenant_id, UserModel.email == str(email))
        )
        return self._read(model) if model else None

    async def search(
        self,
        tenant_id: str,
        *,
        email: str | None = None,
        name: str | None = None,
        status: UserStatusValue | None = None,
        user_type: UserType | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[User]:
        clauses: list[ColumnElement[bool]] = [UserModel.tenant_id == tenant_id]
        if email:
            clauses.append(UserModel.email.ilike(f"%{email}%"))
        if name:
            clauses.append(UserModel.display_name.ilike(f"%{name}%"))
        if status:
            clauses.append(UserModel.status == str(status))
        if user_type:
            clauses.append(UserModel.user_type == str(user_type))
        result = await self.session.scalars(
            select(UserModel)
            .where(*clauses)
            .order_by(UserModel.created_at)
            .offset(offset)
            .limit(limit)
        )
        return tuple(self._read(model) for model in result if model.status != "DELETED")

    @staticmethod
    def _read(model: UserModel) -> User:
        return User(
            UserId(model.user_id),
            model.tenant_id,
            EmailAddress(model.email),
            DisplayName(model.display_name),
            GivenName(model.given_name),
            FamilyName(model.family_name),
            PhoneNumber(model.phone_number),
            UserStatus(UserStatusValue(model.status)),
            UserType(model.user_type),
            UserMetadata(cast(dict[str, str | int | float | bool | None], model.metadata_)),
            model.created_at,
            model.updated_at,
        )
