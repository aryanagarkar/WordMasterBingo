import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QTextOption
from PySide6.QtCore import Qt, QRect
from utils import Utils
from word import Word

# Demo with first word.

words = []

class GridWindow(QMainWindow):
    def __init__(self, words, grid_size=70, rows=5, cols=4):
        super().__init__()
        self.setWindowTitle("Another Card with Two Sides")

        self.grid_size = grid_size
        self.words = words
        self.rows = rows
        self.cols = cols

        self.grid_width = self.cols * self.grid_size
        self.grid_height = self.rows * self.grid_size
        self.setGeometry(100, 100, self.grid_width, self.grid_height)

        pal = self.palette()
        pal.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        painter = QPainter(self)

        if hasattr(self, 'side') and self.side == 'back':
            self.draw_back_side(painter)
        else:
            self.draw_front_side(painter)

    # Draws the front side of the card.
    def draw_front_side(self, painter):
        size = 20
        padding = 5

        # Yellow color for border
        painter.setPen(QPen(QColor(251, 220, 106), 4, Qt.SolidLine)) 

        # Calculate offsets to center the grid within the window
        offset_x = (self.width() - self.grid_width) // 2
        offset_y = (self.height() - self.grid_height) // 2

        for x in range(0, (self.rows + 1) * self.grid_size, self.grid_size):
            if x == 0 or x == (self.grid_width):  # Full lines at the borders
                    painter.drawLine(offset_x + x, offset_y, offset_x + x, offset_y + self.grid_height)

        # Draw horizontal borders (top and bottom)
        for y in range(0, (self.cols + 1) * self.grid_size, self.grid_size):
            if y == 0 or y == (self.grid_height):  # Full lines at the top and bottom
                painter.drawLine(offset_x, offset_y + y, offset_x + self.grid_width, offset_y + y)

        # Top Section
        top_section_rows = 2
        top_section_of_grid_height = self.grid_size * top_section_rows
        section_width = self.grid_width // 2

        # Create a QTextOption for text wrapping and alignment
        top_section_text_option = QTextOption()
        top_section_text_option.setWrapMode(QTextOption.WordWrap)  # Enable word wrapping
        top_section_text_option.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Align to the top and center horizontally)  # Top-align text

        bottom_section_text_option = QTextOption()
        bottom_section_text_option.setWrapMode(QTextOption.WordWrap)  # Enable word wrapping
        bottom_section_text_option.setAlignment(Qt.AlignCenter)  # Center-align text

        # Create rectangles for the part of speech and definition
        text_rect = QRect(offset_x + 2 * padding, offset_y + 2 * padding, 
        self.grid_width - 2 * padding, top_section_of_grid_height - 2 * padding)

        # Draw the word’s definition and part of speech in the top section
        painter.setFont(QFont('Arial', size))  

        first_word = self.words[0]
        definition_first_word = first_word.get_definitions()  # Assuming `get_definition` is a method
        pos_first_word = first_word.get_part_of_speech()

        # Combine part of speech and definition into a single string
        text = f"Part of Speech: {pos_first_word}\nDefinition: {definition_first_word}"

        # Draw the combined text
        painter.drawText(text_rect, text, top_section_text_option)

        painter.setPen(QPen(Qt.black))  # Black text
        painter.setBrush(QBrush(QColor(251, 220, 106)))  # Yellow background for the rectangle

        # Calculate the height for each of the remaining three sections
        remaining_sections_height = (self.grid_height - top_section_of_grid_height) // 3

        # Define the synonyms (easy, medium, hard)
        easy_synonym = first_word.get_easy_word()
        medium_synonym = first_word.get_word()
        hard_synonym = first_word.get_hard_word()

        easy_rect = QRect(offset_x + padding, offset_y + top_section_of_grid_height + padding, 
        self.grid_width - 2 * padding, remaining_sections_height - 2 * padding)
        painter.drawRect(easy_rect)  
        painter.drawText(easy_rect, f"{easy_synonym}", bottom_section_text_option) 

        medium_rect = QRect(offset_x + padding, offset_y + top_section_of_grid_height + remaining_sections_height + padding,
        self.grid_width - 2 * padding, remaining_sections_height - 2 * padding)
        painter.drawRect(medium_rect)  
        painter.drawText(medium_rect, f"{medium_synonym}", bottom_section_text_option) 

        hard_rect = QRect(offset_x + padding, offset_y + top_section_of_grid_height + 2 * remaining_sections_height + padding, 
        self.grid_width - 2 * padding, remaining_sections_height - 2 * padding)
        painter.drawRect(hard_rect)  
        painter.drawText(hard_rect, f"{hard_synonym}", bottom_section_text_option) 

    # Draws the back side of the card
    def draw_back_side(self, painter):
        # Draw the back
        x = 5

    # Set the side to be drawn (either 'front' or 'back').
    def set_side(self, side):
        self.side = side
        self.repaint()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    Utils.initialize("../WordAndDefinitionGenerator/OpenAIIntegration/WordDefinitionsAndSynonyms.txt")

    # Create the front side of the card
    word_card_front = GridWindow(Utils.get_words())
    word_card_front.set_side('front')  # Set side to 'front'
    word_card_front.show()

    """
    # Create the back side of the card
    word_card_back = GridWindow()
    word_card_back.set_side('back')  # Set side to 'back'
    word_card_back.show()
    """

    sys.exit(app.exec())