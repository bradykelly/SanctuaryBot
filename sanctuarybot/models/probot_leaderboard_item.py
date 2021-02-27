class ProbotLeaderboardItem():

    def __init__(self, text_line):
        split1 = text_line.split("I")
        self.rank = int(split1[0].replace("**", "").replace("#", "").strip())
        split2 = split1.split(" XP: ")
        self.member_id = split2[0].replace("<@!", "").replace(">", "").strip()
        xp = split2[1].replace("**", "").replace("`", "").strip()
        self.points = 0 if xp == "undefined" else int(xp)