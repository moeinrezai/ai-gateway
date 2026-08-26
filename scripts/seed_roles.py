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
        # 1. ایجاد یا دریافت Permissionها
        permissions = {}
        for perm_data in PERMISSIONS_DATA:
            stmt = select(Permission).where(Permission.codename == perm_data["codename"])
            result = await session.execute(stmt)
            perm = result.scalars().first()
            
            if not perm:
                perm = Permission(**perm_data)
                session.add(perm)
                await session.flush()  
                
            permissions[perm.codename] = perm


        for role_data in ROLES_DATA:
            stmt = select(Role).where(Role.name == role_data["name"])
            result = await session.execute(stmt)
            role = result.scalars().first()
            
            if not role:
       
                role_perms = []
                if role_data["name"] == "user":
                    role_perms = [permissions["ai:chat"]]
                elif role_data["name"] == "admin":
                    role_perms = list(permissions.values())
                
        
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    permissions=role_perms
                )
                session.add(role)
                await session.flush()
        
        await session.commit()
        print("✅ Roles and permissions seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_roles_and_permissions())