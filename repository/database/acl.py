from typing import Optional, List

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String
from sqlalchemy.orm import relationship

from repository.database import database


class ACL_group(database.base):
    __tablename__ = "acl_groups"

    # fmt: off
    id        = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, default=-1)
    name      = Column(String)
    role_id   = Column(BigInteger, default=None)
    # fmt: on

    def __repr__(self):
        # 4^3: group verify ~ role 328875
        return (
            f"{self.id}^{self.parent_id if self.parent_id >= 0 else '-'}: "
            f"group {self.name} ~ role {self.role_id}"
        )

    def __str__(self):
        # Group verify (4) linked to role 328874
        return f"Group {self.name} ({self.id}) linked to role {self.role_id}"


class ACL_rule(database.base):
    __tablename__ = "acl_rules"

    # fmt: off
    id       = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger)
    command  = Column(String)
    users    = relationship("ACL_rule_user")
    groups   = relationship("ACL_rule_group")
    # fmt: on

    def __repr__(self):
        # hug
        # users
        # User 667155: disallow
        # groups
        # Group 4: allow
        result = [self.command]
        result.append("users")
        for u in self.users:
            result.append(u.__repr__())
        result.append("groups")
        for g in self.groups:
            result.append(g.__repr__())

        return "\n".join(result)

    def __str__(self):
        # Rule 4 for command hug: 1 user overrides, 1 group overrides
        return (
            f"Rule {self.id} for command {self.command}: "
            f"{len(self.users)} user overrides, {len(self.groups)} group overrides"
        )


class ACL_rule_user(database.base):
    __tablename__ = "acl_rule_users"

    # fmt: off
    id         = Column(Integer, primary_key=True, autoincrement=True)
    rule_id    = Column(Integer, ForeignKey('acl_rules.id', ondelete="CASCADE"))
    discord_id = Column(BigInteger)
    allow      = Column(Boolean)
    # fmt: on

    def __repr__(self):
        # Entry 56 for rule 32: User 667155: allow
        return (
            f"Entry {self.id} for rule {self.rule_id}: User {self.discord_id}: "
            + ("" if self.allow else "dis")
            + "allow"
        )

    def __str__(self):
        # User 667155: allow
        return f"User {self.discord_id}: " + ("" if self.allow else "dis") + "allow"


class ACL_rule_group(database.base):
    __tablename__ = "acl_rule_groups"

    # fmt: off
    id       = Column(Integer, primary_key=True, autoincrement=True)
    rule_id  = Column(Integer, ForeignKey("acl_rules.id", ondelete="CASCADE"))
    group_id = Column(Integer, ForeignKey("acl_groups.id", ondelete="CASCADE"))
    allow    = Column(Boolean, default=None)
    # fmt: on

    def __repr__(self):
        # Entry 78 for rule 15: group 4: disallow
        return (
            f"Entry {self.id} for rule {self.rule_id}: group {self.group_id}: "
            + ("" if self.allow else "dis")
            + "allow"
        )

    def __str__(self):
        # Group 4: disallow
        return f"Group {self.group_id}: " + ("" if self.allow else "dis") + "allow"
