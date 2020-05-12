import discord
from discord.ext import commands

class Paginator(commands.Paginator):
    def __init__(self):
        super().__init__()

    def add_line(self, line='', *, empty=False):
        super().add_line(line='> ' + line, empty=empty)


class Help(commands.MinimalHelpCommand):
    def __init__(self, **options):
        self.paginator = Paginator()

        super().__init__(no_category="\nNezařazeno", commands_heading="commands")

    def command_not_found(self, string):
        return f"Žádný příkaz jako `{string}` neexistuje."

    def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f"Příkaz `{command.qualified_name}` nemá podpříkaz `{string}`."
        return f"Příkaz `{command.qualified_name}` nemá žádný podpříkaz."

    def get_command_signature(self, command, quote = True):
        return f"**{command.qualified_name} {command.signature}**"

    def get_opening_note(self):
        return

    def get_ending_note(self):
        return " "

    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            cmds = []
            joined = ', '.join(c.name for c in commands)
            self.paginator.add_line(f"**{heading}**")
            self.paginator.add_line(joined)

    def add_aliases_formatting(self, aliases):
        return

    def add_command_formatting(self, command):
        if command.description:
            self.paginator.add_line(command.description)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(signature, empty=True)

        if command.help:
            try:
                self.paginator.add_line(command.help, empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

    def add_subcommand_formatting(self, command):
        fmt = f"\N{EN DASH} **{command.qualified_name}**"
        if command.short_doc:
            fmt += ": " + command.short_doc
        self.paginator.add_line(fmt)


    async def send_bot_help(self, mapping):
        self.paginator.add_line(">>> ")
        await super().send_bot_help(mapping)

    async def send_command_help(self, command):
        self.paginator.add_line(">>> ")
        await super().send_command_help(command)

    async def send_group_help(self, group):
        self.paginator.add_line(">>> ")
        await super().send_group_help(group)

    async def send_cog_help(self, cog):
        self.paginator.add_line(">>> ")
        await super().send_cog_help(cog)
