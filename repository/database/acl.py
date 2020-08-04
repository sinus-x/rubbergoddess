from typing import Optional, List

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String
from sqlalchemy.orm import relationship

from repository.database import database


class ACL_group(database.base):
    __tablename__ = "acl_groups"

    # fmt: off
    id        = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, default=-1)
    name      = Column(String,  unique=True)
    role_id   = Column(BigInteger, default=None)
    rules     = relationship("ACL_rule_group", back_populates="group")
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

    def __eq__(self, obj):
        return type(self) == type(obj) and self.id == obj.id


class ACL_rule(database.base):
    __tablename__ = "acl_rules"

    # fmt: off
    id       = Column(Integer, primary_key=True, autoincrement=True)
    command  = Column(String)
    default  = Column(Boolean, default=False)
    users    = relationship("ACL_rule_user", back_populates="rule")
    groups   = relationship("ACL_rule_group", back_populates="rule")
    # fmt: on

    def __repr__(self):
        # hug: allow
        # #4 User 667155: disallow
        # #8 Group 4: allow
        result = [self.command + f": {'' if self.allow else 'dis'}allow"]
        for u in self.users:
            result.append(str(u))
        for g in self.groups:
            result.append(str(g))

        return "\n".join(result)

    def __str__(self):
        # Rule 4 for command hug: False, 1 user overrides, 1 group overrides
        return (
            f"Rule {self.id} for command {self.command}: "
            f"{'' if self.allow else 'dis'}allow, "
            f"{len(self.users)} user overrides, {len(self.groups)} group overrides"
        )

    def __eq__(self, obj):
        return type(self) == type(obj) and self.id == obj.id


class ACL_rule_user(database.base):
    __tablename__ = "acl_rule_users"

    # fmt: off
    id         = Column(Integer, primary_key=True, autoincrement=True)
    rule_id    = Column(Integer, ForeignKey('acl_rules.id', ondelete="CASCADE"))
    rule       = relationship("ACL_rule", back_populates="users")
    discord_id = Column(BigInteger)
    allow      = Column(Boolean)
    # fmt: on

    def __repr__(self):
        # User override #56: User 667155: allow
        return (
            f"User override #{self.id}: User {self.discord_id}: "
            + ("" if self.allow else "dis")
            + "allow"
        )

    def __str__(self):
        # #56 User 667155: allow
        return f"#{self.id} User {self.discord_id}: " + ("" if self.allow else "dis") + "allow"

    def __eq__(self, obj):
        return type(self) == type(obj) and self.id == obj.id


class ACL_rule_group(database.base):
    __tablename__ = "acl_rule_groups"

    # fmt: off
    id       = Column(Integer, primary_key=True, autoincrement=True)
    rule_id  = Column(Integer, ForeignKey("acl_rules.id", ondelete="CASCADE"))
    rule     = relationship("ACL_rule", back_populates="groups")
    group_id = Column(Integer, ForeignKey("acl_groups.id", ondelete="CASCADE"))
    group    = relationship("ACL_group", back_populates="rules")
    allow    = Column(Boolean, default=None)
    # fmt: on

    def __repr__(self):
        # Entry 78 for rule 15: group 4: disallow
        allow = "undefined" if self.allow is None else "allow" if self.allow else "disallow"
        return f"Entry {self.id} for rule {self.rule_id}: group {self.group_id}: " + allow

    def __str__(self):
        # #78 Group 4: disallow
        return f"#{self.id} Group {self.group_id}: " + ("" if self.allow else "dis") + "allow"

    def __eq__(self, obj):
        return type(self) == type(obj) and self.id == obj.id
