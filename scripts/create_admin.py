#!/usr/bin/env python3
"""ASE Hub - 初始化管理员账号

用法:
  python scripts/create_admin.py <username> <password> [display_name]
  
示例:
  python scripts/create_admin.py admin MyP@ssw0rd "SA Admin"
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db, async_session
from app.models import User
from app.auth import hash_password
from sqlalchemy import select


async def create_admin(username: str, password: str, display_name: str = ""):
    await init_db()

    async with async_session() as db:
        # Check if user exists
        result = await db.execute(select(User).where(User.username == username))
        if result.scalars().first():
            print(f"❌ 用户 '{username}' 已存在")
            return

        user = User(
            username=username,
            password_hash=hash_password(password),
            display_name=display_name or username,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"✅ 管理员账号创建成功！")
        print(f"   ID:       {user.id}")
        print(f"   用户名:   {user.username}")
        print(f"   显示名:   {user.display_name}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    display_name = sys.argv[3] if len(sys.argv) > 3 else username

    asyncio.run(create_admin(username, password, display_name))
