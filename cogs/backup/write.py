import argparse
import datetime
import sys

import sqlalchemy


parser = argparse.ArgumentParser(
    description="Data converter for Rubbergoddess dumps",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    allow_abbrev=False,
)
parser.add_argument(
    "--input",
    required=True,
    help="Input file path",
)
parser.add_argument(
    "--output",
    required=True,
    help="Output file path",
)
parser.add_argument(
    "--fast",
    action="store_true",
    help="Do not write emojis or avatars",
)
parser.add_argument(
    "--format",
    # TODO Add "guess from extension" option and make it default
    choices=("html", "latex", "json"),
    default="html",
    help="Output format",
)

args = parser.parse_args()
if args.fast != True:
    print("Only fast formatting is supported.")
    sys.exit(1)
if args.format != "html":
    print('The only supported format is "html".')
    sys.exit(1)

try:
    engine = sqlalchemy.create_engine("sqlite:///" + args.input)
except sqlalchemy.exc.SQLAlchemyError as exc:
    print(str(exc))
    sys.exit(1)


def get_datetime(id: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(((id >> 22) + 1420070400000) / 1000)


class Formatter:
    def __init__(self, users: list):
        self.users = users

    def get_user(self, user_id: int) -> object:
        for user in self.users:
            if user.id == user_id:
                return user

    def header(self) -> str:
        raise NotImplemented

    def format_message(self, message) -> str:
        raise NotImplemented

    def footer(self) -> str:
        raise NotImplemented


class HTMLFormatter(Formatter):
    def header(self):
        data = (
            "<DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            "<title>Rubbergoddess dump</title>",
            "<style>",
            "body {margin: 0;padding: 0;background: #36393F;color: #DCDDDE;font-family: Whitney,Helvetica Neue,Helvetica,Arial,sans-serif;}",
            ".message {padding: .3em .5em;}",
            ".author {display: inline-block; min-width: 5em;font-weight: bold;color: #DDC95E; padding-right: .5em}",
            "img {display: inline-block; max-height: 20em;}",
            "</style>",
            "</head>",
            "<body>",
        )
        return "\n".join(data) + "\n"

    def format_message(self, message):
        # DONE Hover to timestamp
        # TODO Embed formatter
        # TODO Link formatter
        # TODO Emoji formatter
        # TODO Tag formatter

        text = message.text
        text = text.replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace("\n", "<br>")

        attachments = []
        if message.attachments is not None:
            for attachment in message.attachments.split(" "):
                for extension in ("jpg", "jpeg", "gif", "png"):
                    if attachment.endswith(extension):
                        attachments.append(f"<img src='" + attachment + "' />")
                for extension in ("mp4", "webm"):
                    if attachment.endswith(extension):
                        attachments.append(f"<video src='" + attachment + "' />")

        data = (
            "<div class='message' title='"
            + get_datetime(message.id).strftime("%Y-%m-%d %H:%M:%S UTC")
            + "'>",
            "<span class='author'>" + self.get_user(message.author_id).name + "</span>",
            "<span class='text'>" + text + "</span>",
            # "<div class='attachments'>" + "\n".join(attachments) + "</div>",
            "</div>",
        )
        return "".join(data) + "\n"

    def footer(self):
        data = (
            "</body>",
            "</html>",
        )
        return "\n".join(data) + "\n"


connection = engine.connect()
metadata = sqlalchemy.MetaData()


def get_table(name: str, *, reverse: bool = False):
    table = sqlalchemy.Table(name, metadata, autoload=True, autoload_with=engine)
    if reverse:
        # reverse the order
        query = sqlalchemy.select([table]).order_by(table.c.id.asc())
    else:
        query = sqlalchemy.select([table])
    proxy = connection.execute(query)
    return proxy.fetchall()


users = get_table("users")
messages = get_table("messages", reverse=True)  # [:100]

formatter = HTMLFormatter(users)

with open(args.output, "w") as handle:
    handle.write(formatter.header())
    for message in messages:
        handle.write(formatter.format_message(message))
    handle.write(formatter.footer())
