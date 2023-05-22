import re

from PyQt5.QtGui import QTextCursor, QTextBlock

import app
import cursortools


def toggle_comments():
    from mainwindow import MainWindow
    from snippet.insert import state
    window: MainWindow = app.activeWindow()
    cursor: QTextCursor = window.textCursor()
    state = state(cursor)
    print(state)

    if not cursor.hasSelection():
        cursor.select(QTextCursor.LineUnderCursor)

    for block in cursortools.blocks(cursor):
        if cursortools.isblank(block):
            cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor)
            continue

        comment_span = is_commented(state, block.text())

        if comment_span:
            uncomment_line(state, cursor, block, comment_span)
        else:
            comment_line(state, cursor, block)
            cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor)

    window.setTextCursor(cursor)


def is_commented(state, line: str):
    mode = state[0]

    if mode == 'lilypond':
        if 'scheme' in state:
            return re.match(r'(^\s*;+)', line)
        else:
            return re.match(r'(^\s*%\s*)', line)
    elif mode == 'latex':
        return re.match(r'(^\s*%\s*)', line)
    elif mode == 'html':
        return re.match(r'(<!--).*(-->)', line)


def uncomment_line(state, cursor: QTextCursor, block: QTextBlock, match: re.Match):
    mode = state[0]

    if mode == 'lilypond' or mode == 'latex':
        cursor.setPosition(match.pos + block.position(), QTextCursor.MoveAnchor)
        cursor.setPosition(match.end() + block.position(), QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
    elif mode == 'html':
        with cursortools.compress_undo(cursor):
            cursor.setPosition(match.endpos + block.position() - len('-->'), QTextCursor.MoveAnchor)
            cursor.setPosition(match.endpos + block.position(), QTextCursor.KeepAnchor)
            cursor.removeSelectedText()

            cursor.setPosition(match.pos + block.position(), QTextCursor.MoveAnchor)
            cursor.setPosition(match.pos + block.position() + len('<!--'), QTextCursor.KeepAnchor)
            cursor.removeSelectedText()


def comment_line(state, cursor: QTextCursor, block: QTextBlock):
    mode = state[0]

    def left_line_comment(prefix: str):
        cursor.setPosition(block.position())
        cursor.insertText(prefix)

    if mode == 'lilypond':
        if 'scheme' in state:
            left_line_comment(';')
        else:
            left_line_comment('%')
    elif mode == 'latex':
        left_line_comment('%')
    elif mode == 'html':
        with cursortools.compress_undo(cursor):
            cursor.setPosition(block.position())
            cursor.insertText('<!--')
            cursor.setPosition(block.position() + block.length() - 1)
            cursor.insertText('-->')
