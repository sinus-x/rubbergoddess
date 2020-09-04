from typing import Union, Optional, List

from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.acl import ACL_rule, ACL_group, ACL_rule_user, ACL_rule_group


class ACLRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    ##
    ## Groups
    ##

    def getGroups(self) -> Optional[List[ACL_group]]:
        return session.query(ACL_group).all()

    def getGroup(self, identifier: Optional[Union[int, str]]) -> Optional[ACL_group]:
        if identifier is None:
            return None

        if type(identifier) == int:
            return session.query(ACL_group).filter(ACL_group.id == identifier).one_or_none()
        else:
            return session.query(ACL_group).filter(ACL_group.name == identifier).one_or_none()

    def getGroupByRole(self, role_id: int) -> Optional[ACL_group]:
        return session.query(ACL_group).filter(ACL_group.role_id == role_id).one_or_none()

    def addGroup(self, name: str, parent_id: int, role_id: int) -> ACL_group:
        if self.getGroup(parent_id) is None:
            raise Duplicate("parent_id", parent_id)
        if self.getGroup(name) is not None:
            raise Duplicate("group", name)
        session.add(ACL_group(name=name, parent_id=parent_id, role_id=role_id))
        session.commit()
        return self.getGroup(name)

    def editGroup(
        self, id: int, *, name: str = None, parent_id: int = None, role_id: int = None
    ) -> ACL_group:
        group = self.getGroup(id)
        if group is None:
            raise ACLException("id", id)

        if name is not None:
            group.name = name
        if parent_id is not None:
            if self.getGroup(parent_id) is None:
                raise ACLException("parent_id", parent_id)
            group.parent_id = parent_id
        if role_id is not None:
            group.role_id = role_id

        session.commit()
        return self.getGroup(id)

    def deleteGroup(self, identifier: Union[int, str]) -> bool:
        if self.getGroup(identifier) is None:
            raise ACLException("identifier", identifier)
        if isinstance(identifier, int):
            result = session.query(ACL_group).filter(ACL_group.id == identifier).delete()
        else:
            result = session.query(ACL_group).filter(ACL_group.name == identifier).delete()
        return result > 0

    ##
    ## Commands
    ##

    def getRules(self) -> Optional[List[ACL_rule]]:
        return session.query(ACL_rule).all()

    def getRule(self, command: str) -> Optional[ACL_rule]:
        return session.query(ACL_rule).filter(ACL_rule.command == command).one_or_none()

    def addRule(self, command: str, allow: bool = False) -> ACL_rule:
        if self.getRule(command) is not None:
            raise Duplicate("rule", command)

        session.add(ACL_rule(command=command, default=allow))
        session.commit()
        return self.getRule(command)

    def editRule(self, command: str, allow: bool) -> ACL_rule:
        cmd = self.getRule(command)
        if cmd is None:
            raise ACLException("command", command)
        cmd.default = allow
        session.commit()
        return cmd

    def deleteRule(self, command: str) -> bool:
        if self.getRule(command) is None:
            raise ACLException("command", command)
        result = session.query(ACL_rule).filter(ACL_rule.command == command).delete()
        session.commit()
        return result > 0

    def deleteAllRules(self) -> int:
        return session.query(ACL_rule).delete()

    ##
    ## Constraints
    ##

    def addGroupConstraint(self, command: str, identifier: Union[int, str], allow: bool) -> ACL_rule:
        cmd = self.getRule(command)
        if cmd is None:
            raise ACLException("command", command)

        group = self.getGroup(identifier)
        if group is None:
            raise ACLException("identifier", identifier)

        cmd.groups.append(ACL_rule_group(group_id=group.id, allow=allow))
        session.commit()
        return cmd

    def removeGroupConstraint(self, constraint_id: int) -> bool:
        result = session.query(ACL_rule_group).filter(ACL_rule_group.id == constraint_id).delete()
        session.commit()
        return result > 0

    def addUserConstraint(self, command: str, discord_id: int, allow: bool) -> ACL_rule:
        cmd = self.getRule(command)
        if cmd is None:
            raise ACLException("command", command)

        cmd.users.append(ACL_rule_user(discord_id=discord_id, allow=allow))
        session.commit()
        return cmd

    def removeUserConstraint(self, constraint_id: int) -> bool:
        result = session.query(ACL_rule_user).filter(ACL_rule_user.id == constraint_id).delete()
        session.commit()
        return result > 0


class ACLException(Exception):
    def __init__(self, parameter: str, value: Union[str, int]):
        self.parameter = parameter
        self.value = value

        super().__init__(f"Invalid parameter: {self.parameter} = {self.value}")

    def __repr__(self):
        return f"Invalid parameter: {self.parameter} = {self.value}"

    def __str__(self):
        return self.__repr__()


class Duplicate(Exception):
    def __init__(self, ACLtype: str, rule: str):
        self.type = ACLtype
        self.rule = rule
        super().__init__(f"Duplicate {self.type}: {self.rule}")

    def __repr__(self):
        return f"Duplicate {self.type}: {self.rule}"

    def __str__(self):
        return self.__repr__()
