# From Solaris: https://github.com/parafoxia/Solaris/blob/master/solaris/utils/__init__.py

import os
from sanctuarybot import common
from pygount import SourceAnalysis
from sanctuarybot.utils import ROOT_DIR


class CodeCounter:
    def __init__(self):
        self.code = 0
        self.docs = 0
        self.empty = 0

    def count(self):
        for subdir, _, files in os.walk(ROOT_DIR / f"{common.BOT_NAME}"):
            for file in (f for f in files if f.endswith(".py")):
                analysis = SourceAnalysis.from_file(f"{subdir}/{file}", "pygount", encoding="utf=8")
                self.code += analysis.code_count
                self.docs += analysis.documentation_count
                self.empty += analysis.empty_count
