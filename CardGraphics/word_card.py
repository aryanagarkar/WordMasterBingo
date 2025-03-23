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

        self.offset_x = (self.width() - self.grid_width) // 2
        self.offset_y = (self.height() - self.grid_height) // 2
        self.font_size = 20
        self.paddingHeight = 5
        self.paddingWidth = 10
        self.border_thickness = 3
        self.top_section_rows = 2
        self.top_section_of_grid_height = self.grid_size * self.top_section_rows

        self.first_word = self.words[0]
        self.definition_first_word = self.first_word.get_definitions()
        self.pos_first_word = self.first_word.get_part_of_speech()
        self.easy_synonym = self.first_word.get_easy_word()
        self.medium_synonym = self.first_word.get_word()
        self.hard_synonym = self.first_word.get_hard_word()

        # QTextOptions for text wrapping and alignment
        self.top_section_text_option = QTextOption()
        self.top_section_text_option.setWrapMode(QTextOption.WordWrap)
        self.top_section_text_option.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.bottom_section_text_option = QTextOption()
        self.bottom_section_text_option.setWrapMode(QTextOption.WordWrap)
        self.bottom_section_text_option.setAlignment(Qt.AlignCenter)

        # Font
        self.font = QFont('Arial', self.font_size)
        self.font.setBold(True)  # Set the font to bold

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

    def draw_common_elements(self, painter):
        # Yellow color for border
        painter.setPen(QPen(QColor(251, 220, 106), self.border_thickness, Qt.SolidLine)) 

        for x in range(0, (self.rows + 1) * self.grid_size, self.grid_size):
            if x == 0 or x == (self.grid_width):  # Full lines at the borders
                    painter.drawLine(self.offset_x + x, self.offset_y, self.offset_x + x, self.offset_y + self.grid_height)

        # Draw horizontal borders (top and bottom)
        for y in range(0, self.grid_height + 1, self.grid_size):
            if y == 0 or y == self.grid_height:  # Full lines at the top and bottom
                painter.drawLine(self.offset_x, self.offset_y + y, self.offset_x + self.grid_width, self.offset_y + y)

        # Create rectangles for the part of speech and definition
        text_rect = QRect(self.offset_x + self.border_thickness + self.paddingHeight,
                    self.offset_y + self.border_thickness + self.paddingHeight, 
                    self.grid_width - 2 * (self.paddingHeight + self.border_thickness), 
                    self.top_section_of_grid_height - 2 * (self.paddingHeight + self.border_thickness))

        # Draw the word’s definition and part of speech in the top section
        painter.setFont(self.font)  

        # Combine part of speech and definition into a single string
        text = f"Definition: {self.definition_first_word}\nPart of Speech: {self.pos_first_word}"

        # Draw the combined text
        painter.drawText(text_rect, text, self.top_section_text_option)

    # Draws the front side of the card.
    def draw_front_side(self, painter):
        self.draw_common_elements(painter)

        painter.setPen(QPen(Qt.black))  # Black text
        painter.setBrush(QBrush(QColor(251, 220, 106)))  # Yellow background for the rectangle

        # Calculate the height for each of the remaining three sections
        remaining_sections_height = (self.grid_height - self.top_section_of_grid_height) // 3

        centered_x = self.offset_x + (self.grid_width - (self.grid_width - 2 * self.paddingWidth)) // 2

        centered_y_first = self.offset_y + self.top_section_of_grid_height + self.paddingHeight  # Just after the top section.   

        centered_y_second = centered_y_first + remaining_sections_height  # Just after the middle section.

        centered_y_third = centered_y_second + remaining_sections_height  # Just after the last section.

        easy_rect = QRect(centered_x, centered_y_first, 
        self.grid_width - 2 * self.paddingWidth, remaining_sections_height - 2 * self.paddingHeight)
        painter.drawRect(easy_rect)  
        painter.drawText(easy_rect, f"{self.easy_synonym}", self.bottom_section_text_option) 

        medium_rect = QRect(centered_x, centered_y_second,
        self.grid_width - 2 * self.paddingWidth, remaining_sections_height - 2 * self.paddingHeight)
        painter.drawRect(medium_rect)  
        painter.drawText(medium_rect, f"{self.medium_synonym}", self.bottom_section_text_option) 

        hard_rect = QRect(centered_x, centered_y_third, 
        self.grid_width - 2 * self.paddingWidth, remaining_sections_height - 2 * self.paddingHeight)
        painter.drawRect(hard_rect)  
        painter.drawText(hard_rect, f"{self.hard_synonym}", self.bottom_section_text_option) 

    # Draws the back side of the card
    def draw_back_side(self, painter):
        self.draw_common_elements(painter)

        # Create a rectangle for the image placeholder
        image_rect = QRect(self.offset_x + self.border_thickness + self.paddingHeight,
                        self.offset_y + self.border_thickness + self.top_section_of_grid_height + self.paddingHeight,
                        self.grid_width - 2 * (self.paddingHeight + self.border_thickness),
                        self.top_section_of_grid_height - 2 * (self.paddingHeight + self.border_thickness))

        # Draw the image placeholder rectangle
        painter.setPen(QPen(Qt.black))  # Black border for the image placeholder
        painter.setBrush(QBrush(QColor(200, 200, 200)))  # Light gray background for the placeholder
        painter.drawRect(image_rect)  # Draw the rectangle

        # Draw the placeholder text inside the rectangle
        painter.setPen(QPen(Qt.black))  # Black text for placeholder
        painter.drawText(image_rect, Qt.AlignCenter, "Image Placeholder")

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
    word_card_back = GridWindow(Utils.get_words())
    word_card_back.set_side('back')  # Set side to 'back'
    word_card_back.show()
    """

    sys.exit(app.exec())