from typing import Union, Optional, List

from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.acl import ACL_group, ACL_rule, ACL_data


class ACLRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    ##
    ## Groups
    ##

    def getGroups(self) -> Optional[List[ACL_group]]:
        return session.query(ACL_group).all()

    def getGroup(self, identifier: Union[int, str]) -> Optional[ACL_group]:
        if isinstance(identifier, int):
            return session.query(ACL_group).filter(ACL_group.id == identifier).one_or_none()
        else:
            return session.query(ACL_group).filter(ACL_group.name == identifier).one_or_none()

    def getGroupByRole(self, role_id: int) -> Optional[ACL_group]:
        return session.query(ACL_group).filter(ACL_group.role_id == role_id).one_or_none()

    def addGroup(self, name: str, parent_id: int, role_id: int) -> ACL_group:
        if parent_id != -1 and self.getGroup(parent_id) is None:
            raise ACLException("parent_id", parent_id)
        if self.getGroup(name) is not None:
            raise ACLException("name", name)
        session.add(ACL_group(name=name, parent_id=parent_id, role_id=role_id))
        session.commit()
        return self.getGroup(name)

    def deleteGroup(self, identifier: Union[int, str]) -> bool:
        if self.getGroup(identifier) is not None:
            raise ACLException("identifier", identifier)
        if isinstance(identifier, int):
            result = session.query(ACL_group).filter(ACL_group.id == identifier).delete()
        else:
            result = session.query(ACL_group).filter(ACL_group.name == identifier).delete()
        return result > 0

    ##
    ## Commands
    ##

    def getCommands(self) -> Optional[List[ACL_rule]]:
        return session.query(ACL_rule).all()

    def getCommand(self, command: str) -> Optional[ACL_rule]:
        return session.query(ACL_rule).filter(ACL_rule.command == command).one_or_none()

    def addCommand(self, command: str) -> ACL_rule:
        if self.getCommand(command) is not None:
            raise ACLException("command", command)

        session.add(ACL_rule(command=command))
        session.commit()
        return self.getCommand(command)

    def removeCommand(self, command: str) -> bool:
        if self.getCommand(command) is None:
            raise ACLException("command", command)
        result = session.query(ACL_rule).filter(ACL_rule.command == command).delete()
        session.commit()
        return result > 0

    def setCommandConstraint(
        self, command: str, *, constraint: str, id: int, allow: bool
    ) -> ACL_rule:
        cmd = self.getCommand(command)
        if cmd is None:
            raise ACLException("command", command)

        if constraint == "user":
            cmd.users.append(ACL_data(item_id=id, allow=allow))
        elif constraint == "channel":
            cmd.channels.append(ACL_data(item_id=id, allow=allow))
        elif constraint == "group":
            cmd.groups.append(ACL_data(item_id=id, allow=allow))
        else:
            raise ACLException("constraint", constraint)

        session.commit()
        return self.getCommand(command)

    def removeCommandConstraint(self, command: str, id: int) -> ACL_rule:
        if self.getCommand(command) is None:
            raise ACLException("command", command)

        session.query(ACL_data).filter(command=command, item_id=id).delete()
        session.commit()
        return self.getCommand(command)


class ACLException(Exception):
    def __init__(self, parameter: str, value: Union[str, int]):
        super().__init__("Invalid parameter")
        self.parameter = parameter
        self.value = value

    def __repr__(self):
        return f"Invalid parameter: {self.parameter} = {self.value}"
