from typing import Union, List

import discord
from discord.ext import commands

from core import acl, rubbercog, utils
from cogs.resource import CogText
from repository.database.comment import Comment


class Comments(rubbercog.Rubbercog):
    """Manage user information"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("comments")

    @commands.guild_only()
    @commands.check(acl.check)
    @commands.group(name="comment")
    async def comments(self, ctx):
        """Manage comments on guild users"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @comments.command(name="list")
    async def comments_list(self, ctx, user: Union[discord.Member, discord.User]):
        comments: List[Comment] = Comment.get(ctx.guild.id, user.id)
        if not len(comments):
            return await ctx.reply(self.text.get("list", "none"))

        def format_comment(comment: Comment) -> str:
            timestamp: str = comment.timestamp.strftime("%Y-%m-%d %H:%M")
            author: discord.Member = ctx.guild.get_member(comment.author_id)
            author_name: str = (
                f"{comment.author_id}"
                if author is None
                else discord.utils.escape_markdown(author.display_name)
            )
            text: str = "\n".join([f"> {line}" for line in comment.text.split("\n")])
            return f"**{author_name}**, {timestamp} (ID {comment.id}):\n{text}"

        response: str = "\n".join([format_comment(comment) for comment in comments])
        stubs: List[str] = utils.paginate(response)
        await ctx.reply(stubs[0])
        if len(stubs) > 1:
            for stub in utils.paginate(response):
                await ctx.send(stub)

    @commands.check(acl.check)
    @comments.command(name="add")
    async def comments_add(self, ctx, user: Union[discord.Member, discord.User, int], *, text: str):
        Comment.add(
            guild_id=ctx.guild.id,
            author_id=ctx.author.id,
            user_id=user.id,
            text=text,
        )
        await ctx.reply(self.text.get("add", "ok"))
        await self.event.sudo(ctx, f"Comment added on {user}.")

    @commands.check(acl.check)
    @comments.command(name="remove")
    async def comments_remove(self, ctx, id: int):
        success = Comment.remove(guild_id=ctx.guild.id, id=id)
        if not success:
            return await ctx.reply("remove", "none")
        await ctx.reply(self.text.get("remove", "ok"))
        await self.event.sudo(ctx, f"Comment with ID {id} removed.")


def setup(bot):
    bot.add_cog(Comments(bot))
