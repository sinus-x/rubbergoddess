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

    def __repr__(self):
        return "{}^{}: {} ~ {}".format(self.id, self.parent_id, self.name, self.role_id)


class ACL_rule(database.base):
    __tablename__ = "acl_rules"

    # fmt: off
    command  = Column(String, primary_key=True)
    users    = relationship("ACL_data")
    groups   = relationship("ACL_data")
    channels = relationship("ACL_data")
    # fmt: on

    def __repr__(self):
        result = ["command " + self.command]
        result.append("users")
        for u in self.users:
            result.append(u)
        result.append("groups")
        for g in self.groups:
            result.append(g)
        result.append("channels")
        for c in self.channels:
            result.append(c)
        return "\n".join(result)


class ACL_data(database.base):
    __tablename__ = "acl_rules_data"

    # fmt: off
    id      = Column(Integer,    primary_key=True)
    command = Column(String,     ForeignKey('acl_rules.command', ondelete="CASCADE"))
    item_id = Column(BigInteger) #  discord_id or group ID
    allow   = Column(Boolean,    default=None)
    # fmt: on

    def __repr__(self):
        return "{}allow for ID {}".format("   " if self.allow else "dis", self.item_id)
