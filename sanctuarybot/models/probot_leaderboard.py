from .probot_leaderboard_item import ProbotLeaderboardItem

class ProbotLeaderboard():

    def __init__(self, embed):
        self.time = embed.timestamp
        title = embed.title.replace("*", "").replace(":speech_balloon:", "")
        title = title.replace("SCORE", "").replace(" ", "")
        split1 = title.split("[")
        self.type = split1[0].split()
        self.part = split1[1].replace("]", "").split()
        self.items = []
        lines = embed.description.split("\n")
        for line in lines:
            self.items.append(ProbotLeaderboardItem(line))

