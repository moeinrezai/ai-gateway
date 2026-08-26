import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal
from app.models.permission import Permission
from app.models.role import Role

ROLES_DATA = [
    {"name": "user", "description": "Default user role"},
    {"name": "admin", "description": "Administrator role"},
]

PERMISSIONS_DATA = [
    {"codename": "ai:chat", "description": "Access AI chat endpoints"},
    {"codename": "users:read", "description": "Read user data"},
    {"codename": "admin:manage-users", "description": "Manage users and roles"},
]


async def seed_roles_and_permissions() -> None:
    async with AsyncSessionLocal() as session:

        permissions = {}
        for perm_data in PERMISSIONS_DATA:
            result = await session.execute(
                select(Permission).where(Permission.codename == perm_data["codename"])
            )
            perm = result.scalars().first()
            if not perm:
                perm = Permission(**perm_data)
                session.add(perm)
                await session.flush()
            permissions[perm.codename] = perm

   
        for role_data in ROLES_DATA:
            result = await session.execute(
                select(Role).where(Role.name == role_data["name"])
            )
            role = result.scalars().first()
            if not role:
                role = Role(**role_data)
                session.add(role)
                await session.flush()
            
                if role.name == "user":
                    role.permissions.append(permissions["ai:chat"])
     
                elif role.name == "admin":
                    role.permissions.extend(permissions.values())
        
        await session.commit()
        print("Roles and permissions seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_roles_and_permissions())