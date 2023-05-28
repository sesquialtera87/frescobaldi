import time
import re
import os

from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget

path = r'G:\Il mio Drive\Frescobaldi Projects\Rusca\Missa A19-21'
file = os.path.join(path, 'credo.ly')
file = os.path.join(path, 'missa.ly')

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
            print(f'[{char}] -> {self.excess()}')
            return True
        elif self.end == char:
            self.end_count += 1
            print(f'[{char}] -> {self.excess()}')
            return True


class Matcher:
    def __init__(self, regex, start: str, end: str, name: str, leaf=False, capture=False):
        self.result = None
        self.rx = re.compile(regex)
        self.block = EnclosingBlock(start, end, name)
        self.leaf = leaf
        self.capture = capture

    def text(self):
        if self.capture and self.result:
            return self.result.group()
        else:
            return self.block.name

    def match(self, text, pos, endpos):
        self.result = self.rx.match(text, pos, endpos)
        return self.result


rx = {
    'paper': Matcher(r'\\paper\s*{', '{', '}', 'PAPER'),
    'header': Matcher(r'\\header\s*{', '{', '}', 'HEADER'),
    'layout': Matcher(r'\\layout\s*{', '{', '}', 'LAYOUT'),
    'book-part': Matcher(r'\\bookpart\s*{', '{', '}', 'BOOK-PART'),
    'context': Matcher(r'\\context\s*{', '{', '}', 'CONTEXT'),
    'score': Matcher(r'\\score\s*{', '{', '}', 'SCORE'),
    'variable': Matcher(r'[a-zA-Z]+\s*=', '', '', 'Variable', leaf=True, capture=True),

    # 'figure-mode': Matcher(r'\\figuremode\s*{', '{', '}', 'FigureMode'),
}


def structure(tree: QTreeWidget):
    t = time.time()
    L = len(text)
    i = 0
    updated = False
    queue = []
    items = [QTreeWidgetItem(tree)]

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
                    print("CLOSING " + last_block.name)
                if c:
                    break

            matcher: Matcher = rx[key]
            m = matcher.match(text, pos=i, endpos=L)
            if m:
                new_block = matcher.block.copy()
                it = QTreeWidgetItem()
                it.setText(0, matcher.text())
                items[-1].addChild(it)

                if not matcher.leaf:
                    queue.append(new_block)
                    items.append(it)

                i = m.end()
                updated = True
                print(m)
                break

        if not updated:
            i += 1
            updated = False

    print(time.time() - t)
    print(items)
