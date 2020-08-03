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
        return "{}^{}: {} ~ {}".format(
            self.id, self.parent_id if self.parent_id >= 0 else "-", self.name, self.role_id
        )

    def __str__(self):
        return f"Group {self.name} ({self.id}) linked to role ID {self.role_id}"


class ACL_rule(database.base):
    __tablename__ = "acl_rules"

    # fmt: off
    id       = Column(Integer, primary_key=True, autoincrement=True)
    command  = Column(String)
    users    = relationship("ACL_data")
    groups   = relationship("ACL_data")
    channels = relationship("ACL_data")
    # fmt: on

    def __repr__(self):
        result = [self.command]
        result.append("users")
        for u in self.users:
            result.append(str(u))
        result.append("groups")
        for g in self.groups:
            result.append(str(g))
        result.append("channels")
        for c in self.channels:
            result.append(str(c))
        return "\n".join(result)

    def __str__(self):
        return self.__repr__()


class ACL_data(database.base):
    __tablename__ = "acl_rules_data"

    # fmt: off
    id      = Column(Integer,    primary_key=True)
    rule_id = Column(Integer,     ForeignKey('acl_rules.id', ondelete="CASCADE"))
    type    = Column(String)     # group, user, channel
    item_id = Column(BigInteger) #  discord_id or group ID
    allow   = Column(Boolean,    default=None)
    # fmt: on

    def __repr__(self):
        return f"{self.id:>3} of {self.type} for rule {self.rule_id}: "
        f"{self.item_id} set to {'' if self.allow else 'dis'}allow"

    def __str__(self):
        return "{}allow for ID {}".format("" if self.allow else "dis", self.item_id)
