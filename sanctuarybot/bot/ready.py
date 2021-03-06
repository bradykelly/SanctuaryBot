import inspect


class Ready:
    def __init__(self, bot):
        self.bot = bot
        self.booted = False
        self.synced = False

        for cog in self.bot._cogs:
            setattr(self, cog, False)

    def up(self, cog):
        filename = inspect.getmodule(cog).__file__.split("\\")[-1].replace(".py", "")
        setattr(self, filename, True)
        print(f"{filename} cog ready.")

    @property
    def ok(self):
        return self.booted and all(getattr(self, cog) for cog in self.bot._cogs)

    @property
    def initialised_cogs(self):
        return [cog for cog in self.bot._cogs if getattr(self, cog)]

    def __str__(self):
        string = "Bot is booted." if self.booted else "Bot is not booted."
        string += f" {len(self.initialised_cogs)} of {len(self.bot._cogs)} cogs initialised."
        return string

    def __repr__(self):
        return f"<Ready booted={self.booted!r} ok={self.ok!r}>"

    def __int__(self):
        return len(self.initialised_cogs)

    def __bool__(self):
        return self.ok
