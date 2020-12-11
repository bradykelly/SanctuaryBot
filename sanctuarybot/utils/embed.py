# From Solaris: https://github.com/parafoxia/Solaris/blob/master/solaris/utils/embed.py
from datetime import datetime
from discord import Embed
from sanctuarybot.utils import DEFAULT_EMBED_COLOUR
from sanctuarybot.config import Config


class EmbedConstructor:
    def __init__(self, bot):
        self.bot = bot

    def build(self, **kwargs):
        ctx = kwargs.get("ctx")

        embed = Embed(
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            colour=(
                kwargs.get("colour")
                or (ctx.author.colour if ctx and ctx.author.colour.value else None)
                or DEFAULT_EMBED_COLOUR
            ),
            timestamp=datetime.utcnow(),
        )

        embed.set_author(name=kwargs.get("author", f"{Config.BOT_NAME}"), url=kwargs.get("author_url"))
        embed.set_footer(
            text=kwargs.get("footer_text", f"Invoked by {ctx.author.display_name}" if ctx else r"\o/"),
            icon_url= kwargs.get("footer_icon_url", ctx.author.avatar_url if ctx else self.bot.user.avatar_url)
        )

        if thumbnail := kwargs.get("thumbnail"):
            embed.set_thumbnail(url=thumbnail)

        if image := kwargs.get("image"):
            embed.set_image(url=image)

        fields = kwargs.get("fields", ())
        for name, value, inline in kwargs.get("fields", ()):
            embed.add_field(name=name, value=value, inline=inline)

        return embed

    def build_birthday_message(self):
        self.build(
            title="Happy Birthday!", 
            description="The Sanctuary community wishes you a very happy birthday",
            url="http://sancturaybot.co.za/help?command=birthday",
            author=Config.BOT_NAME,
            author_url="http://sancturaybot.co.za",
            image="file://D:/Personal/Python+Projects/SanctuaryBot/images/bday1.jpg"
        )

      