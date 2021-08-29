import argparse
import datetime
import sys

import sqlalchemy


def get_datetime(id: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(((id >> 22) + 1420070400000) / 1000)


class Formatter:
    def __init__(self, users: list):
        self.users = users
        self.title = "Rubbergoddess dump"

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
            f"<title>{self.title}</title>",
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
            + get_datetime(message.id).strftime("%Y-%m-%d %H:%M:%S")
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


class CSVFormatter(Formatter):
    def header(self):
        return "timestamp;author;message;attachments\n"

    def format_message(self, message):
        text = message.text
        text = text.replace("\n", "\\n")
        text = text.replace(";", ",")

        data = (
            get_datetime(message.id).strftime("%Y-%m-%dT%H:%M:%S"),
            self.get_user(message.author_id).name,
            text,
            message.attachments or "",
        )
        return ";".join(data) + "\n"

    def footer(self):
        return ""


def get_parser():
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
        choices=("html", "latex", "json", "csv"),
        default="html",
        help="Output format",
    )
    return parser


class Database:
    def __init__(self, dbfile: str):
        try:
            self.engine = sqlalchemy.create_engine("sqlite:///" + dbfile)
        except sqlalchemy.exc.SQLAlchemyError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

        self.connection = self.engine.connect()
        self.metadata = sqlalchemy.MetaData()

    def get_table(self, name: str, *, reverse: bool = False):
        table = sqlalchemy.Table(name, self.metadata, autoload=True, autoload_with=self.engine)
        if reverse:
            query = sqlalchemy.select([table]).order_by(table.c.id.asc())
        else:
            query = sqlalchemy.select([table])
        proxy = self.connection.execute(query)
        return proxy.fetchall()


def get_formatter(formatter: str, users):
    if formatter == "csv":
        return CSVFormatter(users)
    if formatter == "html":
        return HTMLFormatter(users)
    return ValueError("Formatter not supported.")


def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.fast != True:
        print("Only fast formatting is supported.")
        sys.exit(1)
    if args.format not in ("html", "csv"):
        print('The only supported format is "html" and "csv".')
        sys.exit(1)

    print("> Loading database...")
    database = Database(args.input)

    print("> Loading users...")
    users = database.get_table("users")

    print("> Loading messages...")
    messages = database.get_table("messages", reverse=True)

    print("> Loading formatter...")
    formatter = get_formatter(args.format, users)

    print("> Writing data...")
    with open(args.output, "w") as handle:
        handle.write(formatter.header())
        for message in messages:
            handle.write(formatter.format_message(message))
        handle.write(formatter.footer())

    print("> Done")


if __name__ == "__main__":
    main()
