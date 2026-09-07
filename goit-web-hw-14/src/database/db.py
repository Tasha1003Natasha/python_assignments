import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.conf.config import config


class DatabaseSessionManager:
    """Create and manage asynchronous SQLAlchemy database sessions."""

    def __init__(self, url: str):
        """Initialize the async engine and session factory.

        :param url: SQLAlchemy database connection URL.
        :type url: str
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        """Provide an async database session with rollback and close handling.

        :yield: An active asynchronous SQLAlchemy session.
        :rtype: AsyncSession
        :raises Exception: If the session factory is not initialized or the
            database operation fails.
        """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    """Yield a database session for FastAPI dependency injection.

    :yield: An active asynchronous SQLAlchemy session.
    :rtype: AsyncSession
    """
    async with sessionmanager.session() as session:
        yield session
