from discord.ext.commands.view import StringView


class StringViewSpaces(StringView):

    def get_word(self):
        pos = 0
        nonSpace = 0
        while not self.eof:
            try:
                current = self.buffer[self.index + pos]
                if current.isspace():
                    if nonSpace > 0:
                        break
                else:
                    nonSpace += 1
                pos += 1
            except IndexError:
                break
        self.previous = self.index
        result = self.buffer[self.index:self.index + pos]
        self.index += pos
        return result