import hjson

import discord
from discord.ext import commands

from cogs.resource import CogText
from core import acl, rubbercog, utils, image_generator
from repository import subject_repo

repo_s = subject_repo.SubjectRepository()


class Semester(rubbercog.Rubbercog):
    """Prepare server for the next semester"""

    def __init__(self, bot):
        super().__init__(bot)

        self.text = CogText("semester")

    @commands.check(acl.check)
    @commands.group(name="semester")
    async def semester(self, ctx):
        """Prepare server for the next semester"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @semester.group(name="init")
    async def semester_init(self, ctx):
        """Initiate new semester"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @semester_init.command(name="subjects")
    async def semester_init_subjects(self, ctx, target: discord.TextChannel):
        """Send react-to-subject messages

        The channel has to have react-to-role function enabled. See Faceshifter.
        Channels and their descriptions are read from server channels.
        """
        counter_category = 0
        counter_subject = 0

        # get all subjects
        listing = {}
        for category in ctx.guild.categories:
            category_subjects = []
            for channel in category.text_channels:
                if repo_s.get(channel.name) is not None:
                    category_subjects.append(channel)
            if len(category_subjects):
                listing[category] = category_subjects

                counter_subject += len(category_subjects)
                counter_category += 1

        # send messages to channel
        for category, subjects in listing.items():

            header = image_generator.text_to_image(category.name.upper())
            await target.send(file=discord.File(fp=header, filename=f"{category.name}.png"))

            message = []
            for i, subject in enumerate(sorted(subjects, key=lambda s: s.name)):
                if i > 9 and i % 10 == 0:
                    await target.send("\n".join(message))
                    message = []

                num = utils.get_digit_emoji(i % 10)
                line = f"{num} #{subject.name}" + (f" **{subject.topic}**" if subject.topic else "")
                message.append(line)
            await target.send("\n".join(message))

        await ctx.send(
            self.text.get("init_subjects", subjects=counter_subject, category=counter_category)
        )

    @commands.check(acl.check)
    @semester_init.command(name="programmes")
    async def semester_init_programmes(
        self, ctx, target: discord.TextChannel, category: str, zeroes: bool = True
    ):
        """Send react-to-programe messages

        The channel has to have react-to-role function enabled. See Faceshifter.
        Programmes are read from data/semester/programmes.hjson file.

        target: Text channel
        category: bachelor | master
        zeroes: boolean, whether to include future first-years
        """
        # load file
        with open("data/semester/programmes.hjson", "r") as handle:
            data = hjson.loads(handle.read())

        def get_line(programme: dict, year: int) -> str:
            return (
                f"{utils.get_digit_emoji(year)} "
                f"{programme.get('code')}-{year} - "
                f"{self.text.get(programme.get('type'), str(year))}"
            )

        counter = 0
        for programme in data:
            if programme.get("type") != category:
                continue

            message = [f"**{programme.get('name')}**"]
            years = [i + 1 for i in range(programme.get("years"))]
            if zeroes:
                years = [0] + years
            for year in years:
                message.append(get_line(programme, year))
            await target.send("\n".join(message))
            counter += 1

        await ctx.send(self.text.get("init_programmes", counter=counter))

    @commands.check(acl.check)
    @semester.group(name="reset")
    async def semester_reset(self, ctx):
        """Remove roles and user overwrites"""
        await utils.send_help(ctx)

    @commands.check(acl.check)
    @semester_reset.command(name="subjects")
    async def semester_reset_subjects(self, ctx):
        """Remove overwrites from all subject channels"""
        for channel in ctx.guild.text_channels:
            counter = 0
            # only affect subject channels
            if repo_s.get(channel.name) is None:
                continue

            for target in channel.overwrites:
                # only affect members
                if type(target) != discord.Member:
                    continue

                # remove user overwrite
                await channel.set_permissions(target, overwrite=None)
                counter += 1

            if counter:
                await ctx.send(
                    self.text.get(
                        "reset_overwrite", counter=counter, channel=self.sanitise(channel.name)
                    )
                )

        await ctx.send(self.text.get("done"))

    @commands.check(acl.check)
    @semester_reset.command(name="overwrites")
    async def semester_reset_overwrites(self, ctx, channel: discord.TextChannel):
        """Remove overwrites from a single channel"""
        counter = 0
        for target in channel.overwrites:
            if type(target) != discord.Member:
                continue

            await channel.set_permissions(target, overwrite=None)
            counter += 1

        await ctx.send(
            self.text.get("reset_overwrite", counter=counter, channel=self.sanitise(channel.name))
        )

    @commands.check(acl.check)
    @semester_reset.command(name="programmes")
    async def semester_reset_programmes(self, ctx):
        """Remove all programme roles"""
        top_limit = "---PROGRAMMES"
        bottom_limit = "---INTERESTS"

        active = False
        for role in ctx.guild.roles[::-1]:
            counter = 0
            if role.name == top_limit:
                active = True
                continue
            if role.name == bottom_limit:
                active = False
                break

            if not active:
                continue

            # we're in programme roles area
            for member in role.members:
                await member.remove_roles(role)
                counter += 1

            if counter:
                await ctx.send(
                    self.text.get("reset_roles", role=self.sanitise(role.name), counter=counter)
                )

        await ctx.send(self.text.get("done"))
