import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QImage
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCore import Qt, QRect
import random
from utils import Utils
from word import Word

# Color key
color_key = {
    'Noun': 'lightblue',
    'Verb': 'lightpink',
    'Adjective': 'lightgreen'
}

class GridWindow(QMainWindow):
    def __init__(self, words, grid_size=70, rows=6, cols=4):
        super().__init__()
        self.setWindowTitle("4x6 Grid Example")

        self.words = words
        self.grid_size = grid_size
        self.rows = rows
        self.cols = cols

        self.grid_width = self.cols * self.grid_size
        self.grid_height = self.rows * self.grid_size
        self.setGeometry(100, 100, self.grid_width, self.grid_height)

        pal = self.palette()
        pal.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        logo_size = 20
        key_size = 15
        word_size = 15

        painter = QPainter(self)
        
        # Set pen color and style for the grid lines
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))

        # Calculate offsets to center the grid within the window
        offset_x = (self.width() - self.grid_width) // 2
        offset_y = (self.height() - self.grid_height) // 2

        #print(f"selfWidth: {self.width()}, selfHieght: {self.height()}, gridWidth: {self.grid_width}, gridHeight: {self.grid_height}")

        for x in range(0, (self.cols + 1) * self.grid_size, self.grid_size):
            for y in range(0, (self.rows + 1) * self.grid_size, self.grid_size):
                if y == 0 or y > self.grid_size:
                    painter.drawLine(offset_x, offset_y + y, offset_x + self.grid_width, offset_y + y)
               # Draw vertical lines
                if x == 0 or x == (self.grid_width):  # Full lines at the borders
                    painter.drawLine(offset_x + x, offset_y, offset_x + x, offset_y + self.grid_height)
                elif y >= 2 * self.grid_size:  # Skip vertical lines in the merged area
                    painter.drawLine(offset_x + x, offset_y + 2 * self.grid_size, offset_x + x, offset_y + self.grid_height)

        # Calculate the width of the top section and space for the logo and color key
        top_section_rows = 2
        top_section_of_grid_height = self.grid_size * top_section_rows 
        section_width = self.grid_width // 2
        key_x = section_width + offset_x

        # Draw the logo placeholder text
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', logo_size))
        logo_rect = QRect(offset_x, offset_y, section_width, top_section_of_grid_height)
        painter.drawText(logo_rect, Qt.AlignCenter, 'Logo \n Placeholder')

        # Draw the color key
        painter.setFont(QFont('Arial', key_size))
        color_key_rect = QRect(key_x, offset_y, section_width, top_section_of_grid_height)

        total_items_height = len(color_key) * key_size
        start_y = color_key_rect.y() + (color_key_rect.height() - total_items_height) // 2

        # Draw the color key items
        for index, (part_of_speech, color) in enumerate(color_key.items()):
            # Calculate Y position for the current item
            item_y = start_y + index * 20

            # Draw the color rectangle
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRect(color_key_rect.x() + 10, item_y, 15, 15)

            # Draw the part of speech label
            painter.setPen(Qt.black)
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
                painter.drawRect(offset_x + col * self.grid_size, offset_y + (row + 2) * self.grid_size, self.grid_size, self.grid_size)
                
                # Draw the word in the cell
                painter.setPen(Qt.black)
                painter.setFont(QFont('Arial', word_size))
                text_rect = painter.boundingRect(offset_x + col * self.grid_size, offset_y + (row + 2) * self.grid_size, self.grid_size, self.grid_size, Qt.AlignCenter, word)
                painter.drawText(text_rect, Qt.AlignCenter, word)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    Utils.initialize("../WordAndDefinitionGenerator/OpenAIIntegration/WordDefinitionsAndSynonyms.txt")

    window = GridWindow(Utils.get_words())
    window.show()
    sys.exit(app.exec())