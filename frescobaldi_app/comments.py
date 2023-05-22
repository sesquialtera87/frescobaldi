import re

from PyQt5.QtGui import QTextCursor, QTextBlock

import app
import cursortools
import documentinfo


def toggle_comments():
    print("UUUUU")
    doc = app.activeWindow().currentDocument()
    cursor = app.activeWindow().textCursor()
    mode = documentinfo.mode(doc)

    if not cursor.hasSelection():
        cursor.select(QTextCursor.LineUnderCursor)

    for block in cursortools.blocks(cursor):
        if cursortools.isblank(block):
            continue

        comment_span = is_commented(mode, block.text())

        if comment_span:
            uncomment_line(mode, cursor, block, comment_span)
        else:
            comment_line(mode, cursor, block)


def is_commented(mode, line: str):
    if mode == 'lilypond':
        return re.match(r'(^\s*%\s*)', line)
    elif mode == 'html':
        return re.match(r'(<!--).*(-->)', line)
    elif mode == 'scheme':
        for g in re.finditer(r'(^\s*;+\s*)', line):
            return g.span()


def uncomment_line(mode, cursor: QTextCursor, block: QTextBlock, match: re.Match):
    if mode == 'lilypond':
        cursor.setPosition(match.pos + block.position(), QTextCursor.MoveAnchor)
        cursor.setPosition(match.end() + block.position(), QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
    elif mode == 'html':
        cursor.beginEditBlock()
        cursor.setPosition(match.pos + block.position(), QTextCursor.MoveAnchor)
        cursor.setPosition(match.pos + len('<!--'), QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.setPosition(match.endpos - len('-->'), QTextCursor.MoveAnchor)
        cursor.setPosition(match.endpos + block.position(), QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.endEditBlock()


def comment_line(mode, cursor: QTextCursor, block: QTextBlock):
    if mode == 'lilypond':
        cursor.setPosition(block.position())
        cursor.insertText('% ')
    elif mode == 'html':
        cursor.beginEditBlock()
        cursor.setPosition(block.position())
        cursor.insertText('<!--')
        cursor.setPosition(block.position() + block.length() - 1)
        cursor.insertText('-->')
        cursor.endEditBlock()
    elif mode == 'scheme':
        for g in re.finditer(r'(^\s*;+\s*)', line):
            return g.span()
