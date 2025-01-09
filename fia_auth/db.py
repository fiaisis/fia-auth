"""DB Access moculde"""

import logging
import os

from sqlalchemy import Integer, NullPool, create_engine, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):

    """SQLAlchemy Base Model"""

    id: Mapped[int] = mapped_column(primary_key=True)


class Staff(Base):

    """Staff user"""

    __tablename__ = "staff"
    user_number: Mapped[int] = mapped_column(Integer())


DB_USERNAME = os.environ.get("DB_USERNAME", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_IP = os.environ.get("DB_IP", "localhost")

ENGINE = create_engine(
    f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}:5432/fia",
    poolclass=NullPool,
)

SESSION = sessionmaker(ENGINE)


def is_staff_user(user_number: int) -> bool:
    """
    Given a user_number, check if it is a staff
    :param user_number: The user number to check
    :return: boolean indicating if it is a staff
    """
    try:
        with SESSION() as session:
            session.execute(select(Staff.user_number).where(Staff.user_number == user_number)).one()
        return True
    except NoResultFound:
        return False
    except MultipleResultsFound:
        logger.warning(
            f"Multiple staff users found for user_number: {user_number}. This should not be possible. Check "
            f"integrity of the table"
        )
        return False
