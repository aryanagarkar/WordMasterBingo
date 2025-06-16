import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QTextOption
from PySide6.QtCore import Qt, QRect
from utils import Utils
from word import Word

# Demo with first word.

class GridWindow(QMainWindow):
    def __init__(self, word, grid_size=60, rows=6, cols=4):
        super().__init__()
        self.setWindowTitle("Word Card")

        self.grid_size = grid_size
        self.word = word
        self.rows = rows
        self.cols = cols

        self.grid_width = self.cols * self.grid_size
        self.grid_height = self.rows * self.grid_size
        self.setGeometry(100, 100, self.grid_width, self.grid_height)
       
        self.definition_font_size = 25
        self.word_font_size = 20
        self.padding_height = 5
        self.padding_width = 10
        self.border_thickness = 2
        self.definition_margin_top = 20

        self.definition = self.word.get_definitions()
        self.easy_synonym = self.word.get_easy_word()
        self.medium_synonym = self.word.get_word()
        self.hard_synonym = self.word.get_hard_word()

        self.top_section_text_option = QTextOption()
        self.top_section_text_option.setWrapMode(QTextOption.WordWrap)
        self.top_section_text_option.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.bottom_section_text_option = QTextOption()
        self.bottom_section_text_option.setWrapMode(QTextOption.WordWrap)
        self.bottom_section_text_option.setAlignment(Qt.AlignCenter)

        self.definition_font = QFont('Arbutus Slab', self.definition_font_size)  # Font for definition
        self.word_font = QFont('Barlow', self.word_font_size)  # Font for words
        self.word_font.setBold(True)  # Make word font bold

        pal = self.palette()
        pal.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        painter = QPainter(self)

        if hasattr(self, 'side') and self.side == 'front':
            self.draw_front_side(painter)
        else:
            self.draw_back_side(painter)

    def resizeEvent(self, event):
        self.offset_x = (self.width() - self.grid_width) // 2
        self.offset_y = (self.height() - self.grid_height) // 2
        self.repaint()

    def draw_common_elements(self, painter):
        painter.setRenderHint(QPainter.Antialiasing)

        border_color = QColor(251, 220, 106)
        border_thickness = self.border_thickness
        extension = 20  

        # Draw borders
        painter.setPen(QPen(border_color, border_thickness))
        painter.drawLine(self.offset_x - extension, self.offset_y, self.offset_x + self.grid_width + extension, self.offset_y)
        painter.drawLine(self.offset_x - extension, self.offset_y + self.grid_height, self.offset_x + self.grid_width + extension, self.offset_y + self.grid_height)
        painter.drawLine(self.offset_x, self.offset_y - extension, self.offset_x, self.offset_y + self.grid_height + extension)
        painter.drawLine(self.offset_x + self.grid_width, self.offset_y - extension, self.offset_x + self.grid_width, self.offset_y + self.grid_height + extension)

        # Definition text area
        definition_margin_sides = 10
        definition_height = int(self.grid_height * 0.35)
        text_rect = QRect(
            self.offset_x + definition_margin_sides,
            self.offset_y + self.definition_margin_top,
            self.grid_width - 2 * definition_margin_sides,
            definition_height
        )

        painter.setFont(self.definition_font)
        painter.setPen(border_color)
        painter.drawText(text_rect, Qt.AlignTop | Qt.AlignHCenter | Qt.TextWordWrap, f"{self.definition}")

    def draw_front_side(self, painter):
        self.draw_common_elements(painter)

        # Word box settings
        box_color = QColor(251, 220, 106)
        box_border_color = QColor(0, 0, 0)
        box_border_thickness = 2
        box_margin_sides = 10
        box_height = 60 
        box_gap = 5      # Gap between word boxes
        num_boxes = 3
        bottom_margin = 10

        total_boxes_height = num_boxes * box_height + (num_boxes - 1) * box_gap
        first_box_y = self.offset_y + self.grid_height - bottom_margin - total_boxes_height
        box_width = self.grid_width - 2 * box_margin_sides

        painter.setFont(self.word_font)
        painter.setPen(QPen(box_border_color, box_border_thickness))
        painter.setBrush(QBrush(box_color))

        words = [self.easy_synonym, self.medium_synonym, self.hard_synonym]
        for i, word in enumerate(words):
            y = first_box_y + i * (box_height + box_gap)
            rect = QRect(self.offset_x + box_margin_sides, y, box_width, box_height)
            painter.setPen(QPen(box_border_color, box_border_thickness))
            painter.setBrush(QBrush(box_color))
            painter.drawRect(rect)

            painter.setPen(QPen(Qt.black))
            painter.drawText(rect, Qt.AlignCenter, word)

    def draw_back_side(self, painter):
        self.draw_common_elements(painter)

        # Image placeholder settings
        definition_margin_sides = 10
        definition_height = int(self.grid_height * 0.35)
        image_margin_top = self.offset_y + self.definition_margin_top + definition_height
        image_margin_sides = 10
        image_margin_bottom = 10

        image_rect = QRect(
            self.offset_x + image_margin_sides,
            image_margin_top,
            self.grid_width - 2 * image_margin_sides,
            self.grid_height - (image_margin_top - self.offset_y) - image_margin_bottom
        )

        painter.setPen(QPen(Qt.black))  # Black border for the image placeholder
        painter.setBrush(QBrush(QColor(200, 200, 200)))  # Light gray background for the placeholder
        painter.drawRect(image_rect)  # Draw the rectangle

        # Draw the placeholder text inside the rectangle
        placeholder_font = QFont('Barlow', 25)
        placeholder_font.setBold(True)
        painter.setFont(placeholder_font)
        painter.setPen(QPen(Qt.black))  # Black text for placeholder
        painter.drawText(image_rect, Qt.AlignCenter, "Image Placeholder")

    def set_side(self, side):
        self.side = side
        self.repaint()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    Utils.initialize("../WordAndDefinitionGenerator/OpenAIIntegration/WordDefinitionsAndSynonyms.txt")

    words = Utils.get_words()

    for i, word in enumerate(words):
        if(i == 1):
            word_card_front = GridWindow(word)
            word_card_front.set_side('front')
            word_card_front.show()

            word_card_back = GridWindow(word)
            word_card_back.set_side('back')  # Set side to 'back'
            word_card_back.show()

        # Show the back after a delay
        # QTimer.singleShot(i * 1000 + 500, lambda back=word_card_back: back.show())  

    sys.exit(app.exec())