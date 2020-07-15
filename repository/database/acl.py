from typing import Optional, List

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String
from sqlalchemy.orm import relationship

from repository.database import database


class ACL(database.base):
    __tablename__ = "acl"

    # fmt: off
    command          = Column(String, primary_key=True)
    users_allowed    = relationship("ACL_data")
    users_denied     = relationship("ACL_data")
    roles_allowed    = relationship("ACL_data")
    roles_denied     = relationship("ACL_data")
    channels_allowed = relationship("ACL_data")
    channels_denied  = relationship("ACL_data")
    # fmt: on


class ACL_data(database.base):
    __tablename__ = "acl_data"

    # fmt: off
    id         = Column(Integer,    primary_key=True)
    command    = Column(String,     ForeignKey('acl.command', ondelete="CASCADE"))
    discord_id = Column(BigInteger)
    # fmt: on
