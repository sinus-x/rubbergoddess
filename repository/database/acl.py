from sqlalchemy import Column, ForeignKey, Integer, BigInteger, Boolean, String
from sqlalchemy.orm import relationship

from repository.database import database


class ACL_group(database.base):
    __tablename__ = "acl_groups"

    # fmt: off
    id       = Column(Integer, primary_key=True, autoincrement=True)
    name     = Column(String)
    parent   = Column(String, default=None)

    guild_id = Column(BigInteger)
    role_id  = Column(BigInteger, default=0)

    rules    = relationship("ACL_rule_group", back_populates="group")
    # fmt: on

    def __repr__(self):
        return (
            f"ACL group {self.name} (parent {self.parent}) "
            f"mapped to role {self.role_id} in guild {self.guild_id}. "
            f"Internal ID {self.id}."
        )

    def __str__(self):
        return f"ACL group {self.name} mapped to role {self.role_id} on server {self.guild_id}."

    def __eq__(self, obj):
        return type(self) == type(obj) and self.id == obj.id

    def __hash__(self):
        return hash((self.id))

    def mirror(self):
        return {
            "id": self.id,
            "name": self.name,
            "parent": self.parent,
            "guild_id": self.guild_id,
            "role_id": self.role_id,
        }


class ACL_rule(database.base):
    __tablename__ = "acl_rules"

    # fmt: off
    id       = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger)
    command  = Column(String)

    default  = Column(Boolean, default=False)
    users    = relationship("ACL_rule_user", back_populates="rule")
    groups   = relationship("ACL_rule_group", back_populates="rule")
    # fmt: on

    def __repr__(self):
        return f"R#{self.id}: {self.command} on {self.guild_id}: {self.allow}" f""

    def __str__(self):
        return (
            f"{self.command}: {self.allow} "
            f"{' '.join(str(rg) for rg in self.groups)} "
            f"{' '.join(str(ru) for ru in self.users)} (R#{self.id})."
        )

    def __eq__(self, obj):
        return type(self) == type(obj) and self.id == obj.id

    def mirror(self):
        return {
            "id": self.id,
            "guild_id": self.guild_id,
            "command": self.command,
            "default": self.default,
            "users": [user.mirror() for user in self.users],
            "groups": [group.mirror() for group in self.groups],
        }


class ACL_rule_user(database.base):
    __tablename__ = "acl_rule_users"

    # fmt: off
    id      = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey('acl_rules.id', ondelete="CASCADE"))
    rule    = relationship("ACL_rule", back_populates="users")
    user_id = Column(BigInteger)
    allow   = Column(Boolean)
    # fmt: on

    def __repr__(self):
        return f"RU#{self.id} for R#{self.rule_id}: {self.allow}."

    def __str__(self):
        return f"{self.user_id}: {self.allow} (RU#{self.id})."

    def __eq__(self, obj):
        return type(self) == type(obj) and self.id == obj.id

    def mirror(self):
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "guild_id": self.rule.guild_id,
            "command": self.rule.command,
            "user_id": self.user_id,
            "allow": self.allow,
        }


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
        return f"RG#{self.id} for R#{self.rule_id}: {self.allow}."

    def __str__(self):
        return f"{self.group.name}: {self.allow} (RG#{self.id})."

    def __eq__(self, obj):
        return type(self) == type(obj) and self.id == obj.id

    def mirror(self):
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "guild_id": self.rule.guild_id,
            "command": self.rule.command,
            "group_id": self.group_id,
            "group": self.group.name,
            "allow": self.allow,
        }
