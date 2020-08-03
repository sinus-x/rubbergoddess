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

    def addGroup(self, name: str, role_id: int) -> bool:
        if self.getGroup(name) is not None:
            return False
        session.add(ACL_group(name=name, role_id=role_id))
        session.commit()
        return True

    def deleteGroup(self, identifier: Union[int, str]) -> bool:
        if self.getGroup(identifier) is not None:
            return False
        if isinstance(identifier, int):
            session.query(ACL_group).filter(ACL_group.id == identifier).delete()
        else:
            session.query(ACL_group).filter(ACL_group.name == identifier).delete()
        return True

    ##
    ## Commands
    ##

    def getCommands(self) -> Optional[List[ACL_rule]]:
        return session.query(ACL_rule).all()

    def getCommand(self, command: str) -> Optional[ACL_rule]:
        return session.query(ACL_rule).filter(ACL_rule.command == command).one_or_none()

    def addCommand(self, command: str) -> bool:
        if self.get(command) is not None:
            return False

        session.add(ACL_rule(command=command))
        session.commit()
        return True

    def setCommandConstraint(self, command: str, *, constraint: str, id: int, allow: bool) -> bool:
        cmd = self.getCommand(command)
        if cmd is None:
            return False

        self.removeCommandConstraint(command, constraint=constraint, id=id)

        if constraint == "user":
            cmd.users.append(ACL_data(item_id=id, allow=allow))
        elif constraint == "channel":
            cmd.channels.append(ACL_data(item_id=id, allow=allow))
        elif constraint == "group":
            cmd.groups.append(ACL_data(item_id=id, allow=allow))
        else:
            return False

        session.commit()
        return True

    def removeCommandConstraint(self, command: str, *, constraint: str, id: int) -> bool:
        if self.getCommand(command) is None:
            return False

        session.query(ACL_data).filter(command=command, constraint=constraint, item_id=id).delete()
        return True
