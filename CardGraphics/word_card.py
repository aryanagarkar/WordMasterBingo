import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QTextOption, QPixmap
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtSvg import QSvgGenerator
from utils import Utils
from word import Word

WORDS_FILE = "../WordAndDefinitionGenerator/OpenAIIntegration/WordDefinitionsAndSynonyms.txt"

# Padding and margin constants.

PADDING_HEIGHT = 5
PADDING_WIDTH = 10
BOTTOM_MARGIN = 10
WORD_BOX_MARGIN_SIDES = 10
DEFINITION_MARGIN_SIDES = 10
DEFINITION_MARGIN_TOP = 20
IMAGE_MARGIN_SIDES = 10
IMAGE_MARGIN_BOTTOM = 10

# Font sizes.
DEFINITION_FONT_SIZE = 20
WORD_FONT_SIZE = 20
PLACEHOLDER_FONT_SIZE = 25

# Colors.
YELLOW = QColor(251, 220, 106)
BLACK = Qt.black

# Other constants.
WORD_BOX_HEIGHT = 50
GAP_BETWEEN_WORD_BOXES = 5
BORDER_THICKNESS = 2
DEFINITION_HEIGHT_RATIO = 0.4


# Demo with first word.

class GridWindow(QMainWindow):
    """A window that displays a word card with definition and synonyms."""
    
    def __init__(self, word, grid_size=70, rows=5, cols=4):
        """Initialize the word card window with the given word and layout settings."""
        
        super().__init__()
        self.setWindowTitle("Word Card")

        self.grid_size = grid_size
        self.word = word
        self.rows = rows
        self.cols = cols

        # Set fixed card size: 240x336 pixels (2.5x3.5 inches at 96 DPI)
        self.grid_width = 240
        self.grid_height = 336
        self.setGeometry(100, 100, self.grid_width, self.grid_height)
       
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

        self.definition_font = QFont('Arbutus Slab', DEFINITION_FONT_SIZE)  # Font for definition
        self.word_font = QFont('Barlow', WORD_FONT_SIZE)  # Font for words
        self.word_font.setBold(True)  # Make word font bold

        pal = self.palette()
        pal.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(pal)
        self.setAutoFillBackground(True)


    def paintEvent(self, event):
        """Handles the paint event and draws the front or back side of the card."""
        
        painter = QPainter(self)

        if hasattr(self, 'side') and self.side == 'front':
            self.draw_front_side(painter, ox=self.offset_x, oy=self.offset_y)
        else:
            self.draw_back_side(painter, ox=self.offset_x, oy=self.offset_y)


    def resizeEvent(self, event):
        """Recalculates offsets and repaints the window on resize."""
        
        self.offset_x = (self.width() - self.grid_width) // 2
        self.offset_y = (self.height() - self.grid_height) // 2
        self.repaint()


    def draw_common_elements(self, painter, ox, oy):
        """Draws the border and the definition text area on the card, with lines extending past the corners as in the provided image."""
        painter.setRenderHint(QPainter.Antialiasing)
        # Fill the background with black
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        painter.drawRect(
            ox,
            oy,
            self.grid_width,
            self.grid_height
        )

        # Definition text area
        definition_height = int(self.grid_height * DEFINITION_HEIGHT_RATIO)
        text_rect = QRect(
            ox + DEFINITION_MARGIN_SIDES,
            oy + DEFINITION_MARGIN_TOP,
            self.grid_width - 2 * DEFINITION_MARGIN_SIDES,
            definition_height
        )

        painter.setFont(self.definition_font)
        painter.setPen(YELLOW)
        painter.drawText(text_rect, Qt.AlignTop | Qt.AlignHCenter | Qt.TextWordWrap, f"{self.definition}")

        # Draw four border lines extending past the card's edges
        extension = 20  # How far lines extend past the card
        painter.setPen(QPen(YELLOW, BORDER_THICKNESS))
        # Top line
        painter.drawLine(
            ox - extension, oy, ox + self.grid_width + extension, oy
        )
        # Bottom line
        painter.drawLine(
            ox - extension, oy + self.grid_height, ox + self.grid_width + extension, oy + self.grid_height
        )
        # Left line
        painter.drawLine(
            ox, oy - extension, ox, oy + self.grid_height + extension
        )
        # Right line
        painter.drawLine(
            ox + self.grid_width, oy - extension, ox + self.grid_width, oy + self.grid_height + extension
        )


    def draw_front_side(self, painter, for_svg=False, ox=0, oy=0):
        """Draws the back side of the word card, including an empty space for the image."""
        self.draw_common_elements(painter, ox, oy)


    def draw_back_side(self, painter, for_svg=False, ox=0, oy=0):
        """Draws the front side of the word card, including the definition and word boxes."""
        self.draw_common_elements(painter, ox, oy)

        # Word box settings
        num_boxes = 3
        total_boxes_height = num_boxes * WORD_BOX_HEIGHT + (num_boxes - 1) * GAP_BETWEEN_WORD_BOXES
        first_box_y = oy + self.grid_height - BOTTOM_MARGIN - total_boxes_height
        box_width = self.grid_width - 2 * WORD_BOX_MARGIN_SIDES

        painter.setFont(self.word_font)
        painter.setPen(QPen(BLACK, BORDER_THICKNESS))
        painter.setBrush(QBrush(YELLOW))

        words = [self.easy_synonym, self.medium_synonym, self.hard_synonym]
        for i, word in enumerate(words):
            y = first_box_y + i * (WORD_BOX_HEIGHT + GAP_BETWEEN_WORD_BOXES)
            rect = QRect(ox + WORD_BOX_MARGIN_SIDES, y, box_width, WORD_BOX_HEIGHT)
            painter.setPen(QPen(BLACK, BORDER_THICKNESS))
            painter.setBrush(QBrush(YELLOW))
            painter.drawRect(rect)

            painter.setPen(QPen(Qt.black))
            painter.drawText(rect, Qt.AlignCenter, word)


    def set_side(self, side):
        """Sets which side of the card to display ('front' or 'back') and repaints."""
        
        self.side = side
        self.repaint()


    def save_as_image(self, filename):
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        return pixmap.save(filename)


    def save_as_svg(self, filename, side='front'):
        canvas_width, canvas_height = 400, 400
        ox = (canvas_width - self.grid_width) // 2
        oy = (canvas_height - self.grid_height) // 2
        generator = QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(QSize(canvas_width, canvas_height))
        generator.setViewBox(QRect(0, 0, canvas_width, canvas_height))
        generator.setTitle("Word Card")
        generator.setDescription("An SVG drawing created by WordMasterBingo.")
        painter = QPainter(generator)
        # Draw a solid black background covering the card and border extensions
        extension = 20  # Must match the border extension in draw_common_elements
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        painter.drawRect(ox - extension, oy - extension, self.grid_width + 2 * extension, self.grid_height + 2 * extension)
        if side == 'front':
            self.draw_front_side(painter, for_svg=True, ox=ox, oy=oy)
        else:
            self.draw_back_side(painter, for_svg=True, ox=ox, oy=oy)
        painter.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    Utils.initialize(WORDS_FILE)
    words = Utils.get_words()

    windows = []  # Keep references to all windows

    for i, word in enumerate(words):
        word_card_back = GridWindow(word)
        word_card_back.set_side('back')  # Set side to 'back'
        word_card_back.show()
        windows.append(word_card_back)
        QApplication.processEvents()
        word_card_back.save_as_svg(f"WordCards/word_card_{i}_back.svg", side='back')

        word_card_front = GridWindow(word)
        word_card_front.set_side('front')
        word_card_front.show()
        windows.append(word_card_front)
        QApplication.processEvents()
        word_card_front.save_as_svg(f"WordCards/word_card_{i}_front.svg", side='front')
            
    sys.exit(app.exec())