from agent.infra.utils.filter import Filter

class DFAFilter(Filter):
    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add_word(self, word):
        if not isinstance(word, str):
            word = word.decode('utf-8')
        word = word.lower()
        chars = word.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def check(self, content, repl="*"):
        if not isinstance(content, str):
            content = content.decode('utf-8')
        content = content.lower()
        ret = []
        swords = []
        start = 0
        contained = False
        while start < len(content):
            level = self.keyword_chains
            step_ins = 0
            for char in content[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        contained = True
                        swords.append(content[start - 1:(start + step_ins - 1)])
                        break
                else:
                    ret.append(content[start])
                    break
            else:
                ret.append(content[start])
            start += 1
        return contained, ''.join(ret), swords


if __name__ == "__main__":
    filter = DFAFilter()
    #filter.add_word('恐怖')
    filter.load_words_from_file('/mnt/c/Workspace/cognitionX-workshop/test-data/sensitive-words.csv')
    print(filter.check('昨天发生了恐怖袭击，它非常的恐怖'))

