from typing import Dict, Union

import discord
from discord.ext import commands

from cogs.resource import CogText
from core import acl, rubbercog, utils

from repository import (
    interaction_repo,
    karma_repo,
    points_repo,
    user_repo,
)

repo_interaction = interaction_repo.InteractionRepository()
repo_karma = karma_repo.KarmaRepository()
repo_points = points_repo.PointsRepository()
repo_user = user_repo.UserRepository()


class Mover(rubbercog.Rubbercog):
    """Move database objects"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("mover")

    ##
    ## Commands
    ##

    @commands.check(acl.check)
    @commands.group(name="move")
    async def move(self, ctx):
        """Move stuff"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @move.command(name="member")
    async def move_member(self, ctx, before: discord.Member, after: discord.Member):
        """Move old member data to new one

        Roles from the `before` member are moved to the `after` one.
        """
        async with ctx.typing():
            result = self.move_user_data(before.id, after.id)
            try:
                await self.move_member_roles(before, after)
            except Exception as e:
                await self.console.error(ctx, "Could not migrate member roles", e)
            embed = self.move_user_embed(ctx, after, result)
            await ctx.send(embed=embed)

    @commands.check(acl.check)
    @move.command(name="user")
    async def move_user(self, ctx, before: int, after: int):
        """Move old user data to new one

        This is useful when the member is not on the server anymore.
        """
        async with ctx.typing():
            result = self.move_user_data(before, after)
            embed = self.move_user_embed(ctx, after, result)
            await ctx.send(embed=embed)

    ##
    ## Logic
    ##

    def move_user_data(self, before_id: int, after_id: int) -> Dict[str, int]:
        """Move user data

        Arguments
        ---------
        before_id: `int` Old user ID
        after_id: `int` New user ID

        Returns
        -------
        `dict`: mapping from table name to change counter
        """
        result = {}
        result["interaction"] = repo_interaction.move_user(before_id, after_id)
        result["karma"] = repo_karma.move_user(before_id, after_id)
        result["points"] = repo_points.move_user(before_id, after_id)
        result["user"] = repo_user.move_user(before_id, after_id)

        return result

    async def move_member_roles(self, before: discord.Member, after: discord.Member):
        """Move roles from the before member to the after one."""
        roles = before.roles[1:]
        await after.add_roles(*roles, reason="Member migration")
        await before.remove_roles(*roles, reason="Member migration")

    ##
    ## Helper functions
    ##

    def move_user_embed(
        self,
        ctx,
        after: Union[discord.Member, int],
        result: Dict[str, int],
    ) -> discord.Embed:
        """Create embed for move_member and move_user

        Arguments
        ---------
        after: `Member` or `int` representing new user
        result: `Dict` mapping table - number of affected rows

        Returns
        -------
        `discord.Embed`
        """
        embed = self.embed(ctx=ctx, title=self.text.get("user", "move"), description=str(after))
        result_items = []
        for key, value in result.items():
            result_items.append(f"{key}: `{value}`")
        embed.add_field(
            name=self.text.get("user", "result"),
            value="\n".join(result_items),
        )
        return embed


def setup(bot):
    """Load cog"""
    bot.add_cog(Mover(bot))
