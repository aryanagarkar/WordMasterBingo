import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QImage
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCore import Qt, QRect
import random
from utils import Utils
from word import Word

# Level key
level_key = {
    'Easy': 'green',
    'Medium': 'yellow',
    'Hard': 'red'
}

# Color key
color_key = {
    'Noun': 'lightblue',
    'Verb': 'pink',
    'Adjective': 'orange'
}

# Demo for medium words:

class GridWindow(QMainWindow):
    def __init__(self, words, grid_size=70, rows=6, cols=4):
        super().__init__()
        self.setWindowTitle("4x6 Bingo Card Grid")

        self.words = words
        self.grid_size = grid_size
        self.rows = rows
        self.cols = cols

        self.grid_width = self.cols * self.grid_size
        self.grid_height = self.rows * self.grid_size
        self.setGeometry(100, 100, self.grid_width, self.grid_height)

        self.logo_size = 20
        self.key_size = 15
        self.word_size = 15

        # Calculate offsets to center the grid within the window
        self.top_section_rows = 2
        self.top_section_of_grid_height = self.grid_size * self.top_section_rows
        self.section_width = self.grid_width // 2

        pal = self.palette()
        pal.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

    def resizeEvent(self, event):
        self.offset_x = (self.width() - self.grid_width) // 2
        self.offset_y = (self.height() - self.grid_height) // 2
        self.repaint()

    # Draws the front side of the card.
    def draw_front_side(self, painter):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        key_x = self.section_width + self.offset_x

        # Draw the logo placeholder text
        painter.setPen(Qt.white)
        painter.setFont(QFont('Arial', self.logo_size))
        logo_rect = QRect(self.offset_x, self.offset_y, self.section_width, self.top_section_of_grid_height)
        painter.drawText(logo_rect, Qt.AlignCenter, 'Logo \n Placeholder')

        # Draw the color key
        painter.setFont(QFont('Arial', self.key_size))
        color_key_rect = QRect(key_x, self.offset_y, self.section_width, self.top_section_of_grid_height)

        total_items_height = len(color_key) * self.key_size
        start_y = color_key_rect.y() + (color_key_rect.height() - total_items_height) // 2

        # Draw the color key items
        for index, (part_of_speech, color) in enumerate(color_key.items()):
            # Calculate Y position for the current item
            item_y = start_y + index * 20

            # Draw the color rectangle
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRect(color_key_rect.x() + 10, item_y, 15, 15)

            # Draw the part of speech label
            painter.setPen(Qt.white)
            painter.drawText(color_key_rect.x() + 30, item_y + 12, part_of_speech)
            
        # Draw the words in the grid cells
        for row in range(self.rows - 2):  # 4 rows (excluding top merged rows)
            for col in range(self.cols):  # 4 columns
                index = row * 4 + col
                word_obj = self.words[index]
                
                word = word_obj.get_word()
                pos = word_obj.get_part_of_speech()
                
                # Set brush color based on the part of speech
                color = color_key[pos]
                painter.setBrush(QBrush(QColor(color)))
                painter.drawRect(self.offset_x + col * self.grid_size, self.offset_y + (row + 2) * self.grid_size, self.grid_size, self.grid_size)
                
                # Draw the word in the cell
                painter.setPen(Qt.black)
                painter.setFont(QFont('Arial', self.word_size))
                text_rect = painter.boundingRect(self.offset_x + col * self.grid_size, self.offset_y + (row + 2) * self.grid_size, self.grid_size, self.grid_size, Qt.AlignCenter, word)
                painter.drawText(text_rect, Qt.AlignCenter, word)

        # Draw horizontal and vertical grid lines (yellow) FIRST:
        painter.setPen(QPen(QColor(251, 220, 106), 3, Qt.SolidLine))

        # Draw grid lines:
        for x in range(0, (self.cols + 1) * self.grid_size, self.grid_size):
            for y in range(0, (self.rows + 1) * self.grid_size, self.grid_size):
                if y == 0 or y > self.grid_size:
                    painter.drawLine(self.offset_x, self.offset_y + y, self.offset_x + self.grid_width, self.offset_y + y)
               # Draw vertical lines:
                if x == 0 or x == (self.grid_width):  # Full lines at the borders.
                    painter.drawLine(self.offset_x + x, self.offset_y, self.offset_x + x, self.offset_y + self.grid_height)
                elif y >= 2 * self.grid_size:  # Skip vertical lines in the merged area.
                    painter.drawLine(self.offset_x + x, self.offset_y + 2 * self.grid_size, self.offset_x + x, self.offset_y + self.grid_height)

    # Draws the back side of the card
    def draw_back_side(self, painter):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        # Fill background color
        painter.setBrush(QBrush(QColor(251, 220, 106)))
        painter.drawRect(self.offset_x, self.offset_y, self.grid_width, self.grid_height)

        # Draw only the outer borders of the grid
        painter.setPen(QPen(QColor(251, 220, 106), 3, Qt.SolidLine))

         # Top border
        painter.drawLine(self.offset_x, self.offset_y, self.offset_x + self.grid_width, self.offset_y)
        # Bottom border
        painter.drawLine(self.offset_x, self.offset_y + self.grid_height, self.offset_x + self.grid_width, self.offset_y + self.grid_height)
        # Left border
        painter.drawLine(self.offset_x, self.offset_y, self.offset_x, self.offset_y + self.grid_height)
        # Right border
        painter.drawLine(self.offset_x + self.grid_width, self.offset_y, self.offset_x + self.grid_width, self.offset_y + self.grid_height)
        
        # Draw the logo placeholder in the center
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', 20))
        logo_rect = QRect(self.offset_x, self.offset_y, self.grid_width, self.grid_height)
        painter.drawText(logo_rect, Qt.AlignCenter, "Logo \n Placeholder")

    def paintEvent(self, event):
        painter = QPainter(self)

        if hasattr(self, 'side') and self.side == 'front':
            self.draw_front_side(painter)
        else:
            self.draw_back_side(painter)

    # Set the side to be drawn (either 'front' or 'back').
    def set_side(self, side):
        self.side = side
        self.repaint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    Utils.initialize("../WordAndDefinitionGenerator/OpenAIIntegration/WordDefinitionsAndSynonyms.txt")

    # Create the front side of the card
    bingo_card_front = GridWindow(Utils.get_words())
    bingo_card_front.set_side('front')  # Set side to 'front'
    bingo_card_front.show()


    # Create the back side of the card
    bingo_card_back = GridWindow(Utils.get_words())
    bingo_card_back.set_side('back')  # Set side to 'back'
    bingo_card_back.show()

    sys.exit(app.exec())