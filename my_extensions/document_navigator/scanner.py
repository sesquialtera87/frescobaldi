import time
import re
import os

from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget

path = r'G:\Il mio Drive\Frescobaldi Projects\Rusca\Missa A19-21'
file = os.path.join(path, 'credo.ly')
# file = os.path.join(path, 'missa.ly')

text = ''

with open(file, 'r', encoding='utf-8') as f:
    text = f.read()


class EnclosingBlock:
    def __init__(self, start, end, name):
        self.start = start
        self.end = end
        self.start_count = 1
        self.end_count = 0
        self.name = name

    def copy(self):
        return EnclosingBlock(self.start, self.end, self.name)

    def excess(self):
        return self.start_count - self.end_count

    def check(self, char):
        if self.start == char:
            self.start_count += 1
            # print(f'[{char}] -> {self.excess()}')
            return True
        elif self.end == char:
            self.end_count += 1
            # print(f'[{char}] -> {self.excess()}')
            return True


class Matcher:
    def __init__(self, regex, start: str, end: str, name: str, leaf=False, capture=False):
        self.result: re.Match
        self.rx = re.compile(regex, flags=re.MULTILINE)
        self.block = EnclosingBlock(start, end, name)
        self.leaf = leaf
        self.capture = capture

        if capture:
            matches = re.findall('\?P<\w+>', regex)
            if matches:
                self.group_name = matches[0][3:-1]
            else:
                self.group_name = None

    def text(self):
        if self.capture and self.result:
            if self.group_name:
                return self.result.group(self.group_name)
            else:
                return self.result.group()
        else:
            return self.block.name

    def match(self, text, pos, endpos):
        self.result = self.rx.match(text, pos, endpos)
        return self.result


def structure(root: QTreeWidget, text: str):
    t = time.time()
    L = len(text)
    i = 0
    updated = False
    queue = []
    items = []

    while i < L:
        char = text[i]
        updated = False

        for key in rx.keys():
            if queue:
                last_block = queue[-1]
                c = last_block.check(char)
                if last_block.excess() == 0:
                    queue.remove(last_block)
                    items.remove(items[-1])
                    # print("CLOSING " + last_block.name)
                if c:
                    break

            matcher: Matcher = rx[key]
            m = matcher.match(text, pos=i, endpos=L)
            if m:
                new_block = matcher.block.copy()
                it = QTreeWidgetItem()
                it.setText(0, matcher.text())

                if items:
                    items[-1].addChild(it)
                else:
                    root.addTopLevelItem(it)

                if not matcher.leaf:
                    queue.append(new_block)
                    items.append(it)

                i = m.end()
                updated = True
                break

        if not updated:
            i += 1
            updated = False

    print(time.time() - t)


rx = {
    'paper': Matcher(r'\\paper\s*{', '{', '}', 'PAPER'),
    'header': Matcher(r'\\header\s*{', '{', '}', 'HEADER'),
    'layout': Matcher(r'\\layout\s*{', '{', '}', 'Layout'),
    'book-part': Matcher(r'\\bookpart\s*{', '{', '}', 'BOOK-PART'),
    'book': Matcher(r'\\book\s*{', '{', '}', 'BOOK'),
    'context': Matcher(r'\\context\s*{', '{', '}', 'Context'),
    'score': Matcher(r'\\score\s*{', '{', '}', 'Score'),
    'variable': Matcher(r'^\s*(?P<name>[a-zA-Z]+)\s*=', '', '', 'Variable', leaf=True, capture=True),
    # 'line-comment': Matcher(r'%.*$', '', '', 'Comment', leaf=True),
    'include': Matcher(r'^\s*\\include \"[^\"]+\"', '', '', 'Include', leaf=True),
    'new': Matcher(r'\\new\s+(?P<name>[A-Z]\w+)', '', '', 'NEW', leaf=True, capture=True),

    # 'figure-mode': Matcher(r'\\figuremode\s*{', '{', '}', 'FigureMode'),
}
