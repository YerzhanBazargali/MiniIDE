import sys
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QPainter, QTextFormat
from PyQt6.QtCore import Qt, QRect, QSize
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name

class PygmentsHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.lexer = PythonLexer()
        self.formats = {}

        # Цвета в стиле Programiz
        self.colors = {
            'Token.Keyword': '#FF7B16',          # if, def, return
            'Token.Keyword.Namespace': '#FF7B16',# import, from
            'Token.Name.Namespace': '#39B3BC',   # названия библиотек (pygame, sys)
            'Token.Name.Builtin': '#39B3BC',     # print, len
            'Token.Name.Function': '#39B3BC',    # названия функций
            'Token.Literal.String': '#41B35D',   # 'строки'
            'Token.Literal.Number': '#D63384',   # 123
            'Token.Comment': '#6A737D',          # # комментарии
            'Token.Operator': '#FF7B16',         # +, -, =
            'Token.Punctuation': '#d4d4d4',      # (), [], {} (светло-серый)
            'Token.Name.Class': '#39B3BC',       # классы
            'Token.Name.Decorator': '#D63384',   # @decorator
        }

    def highlightBlock(self, text):
        for index, token, value in self.lexer.get_tokens_unprocessed(text):
            # Проходим по иерархии токенов (например, Token.Keyword.Constant -> Token.Keyword)
            style_key = str(token)
            
            # Ищем самый близкий ключ в нашем словаре цветов
            color = None
            curr_token = token
            while curr_token:
                if str(curr_token) in self.colors:
                    color = self.colors[str(curr_token)]
                    break
                curr_token = curr_token.parent

            if color:
                fmt = QTextCharFormat()
                fmt.setForeground(QColor(color))
                self.setFormat(index, len(value), fmt)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class QCodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.highlighter = PygmentsHighlighter(self.document())

        # Стили редактора (VS Code Dark)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                border: none;
            }
        """)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

    def keyPressEvent(self, event):
        # Проверяем, нажата ли клавиша Enter (Return)
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            line_text = cursor.block().text() # Текст текущей строки
            
            # Считаем количество пробелов в начале строки
            indent = ""
            for char in line_text:
                if char.isspace():
                    indent += char
                else:
                    break
            
            # Если строка заканчивается на ':', добавляем +4 пробела
            if line_text.strip().endswith(':'):
                indent += "    "
            
            # Вставляем перевод строки и вычисленный отступ
            cursor.insertText("\n" + indent)
            self.ensureCursorVisible()
            return # Прерываем стандартную обработку Enter

        # Для всех остальных клавиш используем стандартное поведение
        super().keyPressEvent(event)

    
    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = QCodeEditor()
    editor.setPlainText("import pygame\n\ndef main():\n    print('Hello World')\n\nif __name__ == '__main__':\n    main()")
    editor.show()
    sys.exit(app.exec())
