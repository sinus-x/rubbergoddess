from typing import Optional, List

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String
from sqlalchemy.orm import relationship

from repository.database import database


class ACL_group(database.base):
    __tablename__ = "acl_groups"

    # fmt: off
    id        = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, default=None)
    name      = Column(String)
    role_id   = Column(BigInteger, default=None)
    # fmt: on


class ACL_rule(database.base):
    __tablename__ = "acl_rules"

    # fmt: off
    command  = Column(String, primary_key=True)
    users    = relationship("ACL_data")
    groups   = relationship("ACL_group")
    channels = relationship("ACL_data")
    # fmt: on


class ACL_data(database.base):
    __tablename__ = "acl_rules_data"

    # fmt: off
    id      = Column(Integer,    primary_key=True)
    command = Column(String,     ForeignKey('acl.command', ondelete="CASCADE"))
    item_id = Column(BigInteger) #  discord_id or group ID
    allow   = Column(Boolean,    default=None)
    # fmt: on
