from repository.base_repository import BaseRepository
from repository.database import session
from repository.database.acl import ACL, ACL_data


class ACLRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def get(self, command: str):
        return session.query(ACL).filter(ACL.command == command).one_or_none()

    def addCommand(self, command: str):
        command = self.get(command)
        if command is not None:
            return

        session.add(ACL(command=command))
        session.commit()

    def addID(self, command: str, type: str, permission: str, discord_id: int):
        cmd = self.get(command)
        if cmd is None:
            raise Exception("Unknown command")

        obj = ACL_data(command=command, discord_id=discord_id)

        if type == "user" and permission == "allow":
            cmd.users_allowed.append(obj)
        elif type == "user" and permission == "deny":
            cmd.users_denied.append(obj)
        elif type == "role" and permission == "allow":
            cmd.roles_allowed.append(obj)
        elif type == "role" and permission == "deny":
            cmd.roles_denied.append(obj)
        elif type == "channel" and permission == "allow":
            cmd.channels_allowed.append(obj)
        elif type == "channel" and permission == "deny":
            cmd.channels_denied.append(obj)
        else:
            raise Exception("Invalid type or permission.")

        session.commit()
