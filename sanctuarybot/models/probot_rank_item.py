import discord

class ProbotRankItem():

    def __init__(self, timestamp, embed_title, rank_line):
        self.timestamp = timestamp
        self.parse_rank_line(embed_title, rank_line)

    def parse_rank_line(self, title_string, line):
        title = title_string.replace("*", "").replace(":speech_balloon:", "")
        title = title.replace("SCORE", "").replace(" ", "")
        split1 = title.split("[")
        self.type = split1[0]
        self.part = split1[1].replace("]", "")
        
        split2 = line.split("I")
        self.rank = int(split2[0].replace("**", "").replace("#", "").strip())

        split3 = split2[1].split(" XP: ")
        self.member_id = split3[0].replace("<@!", "").replace(">", "").strip()
        xp = split3[1].replace("**", "").replace("`", "").strip()
        self.points = 0 if xp == "undefined" else int(xp)


