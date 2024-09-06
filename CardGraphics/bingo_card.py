import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QImage
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCore import Qt
import random
from utils import Utils
from word import Word

# Color key
color_key = {
    'Noun': 'lightblue',
    'Verb': 'lightpink',
    'Adjective': 'lightgreen'
}

# Global variable for words
words = []

def load_words(file_path):
        global words 
        words = Utils.parse_file(file_path)
        random.shuffle(words)

class GridWindow(QMainWindow):
    def __init__(self, grid_size=70, rows=6, cols=4):
        super().__init__()
        self.setWindowTitle("4x6 Grid Example")
        self.setGeometry(100, 100, cols * grid_size, rows * grid_size)
        self.grid_size = grid_size
        self.rows = rows
        self.cols = cols

        # Calculate the size of the window
        self.window_width = cols * grid_size
        self.window_height = rows * grid_size

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
        offset_x = (self.width() - (self.cols * self.grid_size)) // 2
        offset_y = (self.height() - (self.rows * self.grid_size)) // 2

        for x in range(0, (self.cols + 1) * self.grid_size, self.grid_size):
            for y in range(0, (self.rows + 1) * self.grid_size, self.grid_size):
                if y == 0 or y > self.grid_size:
                    painter.drawLine(offset_x, offset_y + y, offset_x + self.cols * self.grid_size, offset_y + y)
               # Draw vertical lines
                if x == 0 or x == (self.cols * self.grid_size):  # Full lines at the borders
                    painter.drawLine(offset_x + x, offset_y, offset_x + x, offset_y + self.rows * self.grid_size)
                elif y >= 2 * self.grid_size:  # Skip vertical lines in the merged area
                    painter.drawLine(offset_x + x, offset_y + 2 * self.grid_size, offset_x + x, offset_y + self.rows * self.grid_size)

        # Draw the logo placeholder text on the left side of the top merged row
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', logo_size))  # Set font and size
        logo_text = 'Logo Placeholder'
        logo_x = offset_x + 10
        logo_y = offset_y + self.grid_size // 2
        painter.drawText(logo_x, logo_y, logo_text)

        painter.setFont(QFont('Arial', key_size))
        color_key_x = offset_x + 200
        color_key_y = offset_y + self.grid_size // 2 - 10
        
       # Draw the color key
        for index, (part_of_speech, color) in enumerate(color_key.items()):
            # Draw color rectangles
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRect(color_key_x, color_key_y + index * 20, 15, 15)

            # Draw text labels
            painter.setPen(Qt.black)
            painter.drawText(color_key_x + 20, color_key_y + index * 20 + 12, part_of_speech)

        # Draw the words in the grid cells
        for row in range(self.rows - 2):  # 4 rows (excluding top merged rows)
            for col in range(self.cols):  # 4 columns
                index = row * 4 + col
                word_obj = words[index]
                
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
    
    load_words("../WordAndDefinitionGenerator/OpenAIIntegration/WordDefinitionsAndSynonyms.txt")

    window = GridWindow()
    window.show()
    sys.exit(app.exec())