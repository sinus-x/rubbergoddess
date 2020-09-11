import discord
from discord.ext import commands

from cogs.resource import CogConfig, CogText
from core import rubbercog


class Sync(rubbercog.Rubbercog):
    """Guild synchronisation"""

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

        self.config = CogConfig("sync")
        self.text = CogText("sync")

        self.slave_guild_id = self.config.get("slave_guild_id")
        self.engineer_ids = self.config.get("roles", "master_engineer_ids")
        self.slave_verify_id = self.config.get("roles", "slave_verify_id")

        self.mapping_ids = self.config.get("roles", "mapping")
        self.mapping = {}

        self.slave_guild = None
        self.slave_verify = None

    def get_slave_guild(self):
        if self.slave_guild is None:
            self.slave_guild = self.bot.get_guild(self.slave_guild_id)
        return self.slave_guild

    def get_slave_verify(self) -> discord.Role:
        if self.slave_verify is None:
            self.slave_verify = self.get_slave_guild().get_role(self.slave_verify_id)
        return self.slave_verify

    def get_master_member(self, user_id: int) -> discord.Member:
        return self.getGuild().get_member(user_id)

    def get_slave_member(self, user_id: int) -> discord.Member:
        return self.get_slave_guild().get_member(user_id)

    def get_slave_role(self, master_role_id: int) -> discord.Role:
        key = str(master_role_id)
        if key not in self.mapping_ids:
            return None

        if key not in self.mapping.keys():
            self.mapping[key] = self.get_slave_guild().get_role(self.mapping_ids[key])
        return self.mapping[key]

    ##
    ## Commands
    ##

    ##
    ## Listeners
    ##

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Add member to slave guild if they add one of specified roles"""
        if before.roles == after.roles:
            return

        # roles are guild-specific, we do not need to check the guild ID
        before_ids = [role.id for role in before.roles]
        after_ids = [role.id for role in after.roles]

        for engineer_id in self.engineer_ids:
            if engineer_id not in before_ids and engineer_id in after_ids:
                await self.verify_member(after)
                return

            if engineer_id in before_ids and engineer_id not in after_ids:
                await self.unverify_member(after)
                return

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Verify user if they join slave server while having specified role on master"""
        if member.guild.id != self.slave_guild_id:
            return

        master_member = self.get_master_member(member.id)
        master_member_roles = [role.id for role in master_member.roles]

        for engineer_id in self.engineer_ids:
            if engineer_id in master_member_roles:
                await self.verify_member(member)
                return

    ##
    ## Logic
    ##

    async def verify_member(self, member: discord.Member):
        # get member object on slave guild
        slave_member = self.get_slave_member(member.id)
        if slave_member is not None:
            # map some of their roles to slave ones
            to_add = [self.get_slave_verify()]
            event_roles = []
            for role in member.roles:
                if str(role.id) in self.mapping_ids:
                    mapped = self.get_slave_role(role.id)
                    to_add.append(mapped)
                    event_roles.append(mapped.name)
            roles = ", ".join(f"**{self.sanitise(name)}**" for name in event_roles)

            # add the roles
            await slave_member.add_roles(*to_add, reason="Sync: verify")
            await self.event.user(slave_member, f"Verified on slave server with {roles}.")
        else:
            # send invitation
            await member.send(
                self.text.get("invite", invite_link=self.config.get("slave_invite_link"))
            )
            await self.event.user(member, "Not on slave server: invite sent.")

    async def unverify_member(self, member: discord.Member):
        # get member object on slave guild
        slave_member = self.get_slave_member(member.id)
        if slave_member is not None:
            roles = slave_member.roles[1:]  # the first is @everyone
            await slave_member.remove_roles(*roles, reason="Sync: unverify")
            await self.event.user(slave_member, "Unverified on slave server.")
        else:
            await self.event.user(member, "Not on slave server: skipping unverify.")
