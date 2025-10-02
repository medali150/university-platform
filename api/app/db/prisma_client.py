from prisma import Prisma
from contextlib import asynccontextmanager
from app.core.config import settings
from typing import Optional


class DatabaseManager:
    """Singleton database manager"""
    _instance: Optional['DatabaseManager'] = None
    _prisma: Optional[Prisma] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Connect to database"""
        if not self._prisma:
            self._prisma = Prisma()
            await self._prisma.connect()
            print(f"✅ Database connected: {settings.database_url}")
    
    async def disconnect(self):
        """Disconnect from database"""
        if self._prisma:
            await self._prisma.disconnect()
            self._prisma = None
            print("🔌 Database disconnected")
    
    @property
    def prisma(self) -> Prisma:
        """Get prisma client"""
        if not self._prisma:
            raise RuntimeError("Database not connected")
        return self._prisma


# Global database manager instance
db_manager = DatabaseManager()


async def get_prisma() -> Prisma:
    """Dependency to get prisma client"""
    if not db_manager._prisma:
        print("⚠️  Database not connected, attempting to connect...")
        await db_manager.connect()
    return db_manager.prisma


@asynccontextmanager
async def lifespan(app):
    """FastAPI lifespan context manager"""
    # Startup
    print("🚀 Starting University API...")
    try:
        await db_manager.connect()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await db_manager.disconnect()