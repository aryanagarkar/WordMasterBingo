import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QTextOption, QPixmap
from PySide6.QtCore import Qt, QRect, QSize, QSizeF
from PySide6.QtSvg import QSvgGenerator, QSvgRenderer
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtGui import QPageSize
from utils import Utils
from word import Word
import re

WORDS_FILE = "../WordAndDefinitionGenerator/OpenAIIntegration/WordDefinitionsAndSynonyms.txt"

# Padding and margin constants.

PADDING_HEIGHT = 5
PADDING_WIDTH = 10
BOTTOM_MARGIN = 10
WORD_BOX_MARGIN_SIDES = 10
DEFINITION_MARGIN_SIDES = 10
DEFINITION_MARGIN_TOP = 20

# Font sizes.
DEFINITION_FONT_SIZE = 15
WORD_FONT_SIZE = 15

# Colors.
YELLOW = QColor(251, 220, 106)
BLACK = Qt.black

# Other constants.
WORD_BOX_HEIGHT = 50
GAP_BETWEEN_WORD_BOXES = 5
BORDER_THICKNESS = 2
DEFINITION_HEIGHT_RATIO = 0.4
BORDER_INSET = 15  # How far borders are inset from the card edges
BORDER_EXTENSION = 10  # How far the border lines extend past the corners (inside the card)


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
        """Draws the border and the definition text area on the card, with border lines extending slightly past the corners inside the card."""
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

        # Border rectangle (inset)
        left = ox + BORDER_INSET
        right = ox + self.grid_width - BORDER_INSET
        top = oy + BORDER_INSET
        bottom = oy + self.grid_height - BORDER_INSET
        painter.setPen(QPen(YELLOW, BORDER_THICKNESS))
        painter.drawRect(left, top, right - left, bottom - top)

        # Draw cross extensions at each corner (inside the card)
        # Top left
        painter.drawLine(left - BORDER_EXTENSION, top, left + BORDER_EXTENSION, top)  # horizontal
        painter.drawLine(left, top - BORDER_EXTENSION, left, top + BORDER_EXTENSION)  # vertical
        # Top right
        painter.drawLine(right - BORDER_EXTENSION, top, right + BORDER_EXTENSION, top)  # horizontal
        painter.drawLine(right, top - BORDER_EXTENSION, right, top + BORDER_EXTENSION)  # vertical
        # Bottom left
        painter.drawLine(left - BORDER_EXTENSION, bottom, left + BORDER_EXTENSION, bottom)  # horizontal
        painter.drawLine(left, bottom - BORDER_EXTENSION, left, bottom + BORDER_EXTENSION)  # vertical
        # Bottom right
        painter.drawLine(right - BORDER_EXTENSION, bottom, right + BORDER_EXTENSION, bottom)  # horizontal
        painter.drawLine(right, bottom - BORDER_EXTENSION, right, bottom + BORDER_EXTENSION)  # vertical

        # Definition text area (now relative to border)
        definition_height = int((bottom - top) * DEFINITION_HEIGHT_RATIO)
        text_rect = QRect(
            left + DEFINITION_MARGIN_SIDES,
            top + DEFINITION_MARGIN_TOP,
            (right - left) - 2 * DEFINITION_MARGIN_SIDES,
            definition_height
        )
        painter.setFont(self.definition_font)
        painter.setPen(YELLOW)
        painter.drawText(text_rect, Qt.AlignTop | Qt.AlignHCenter | Qt.TextWordWrap, f"{self.definition}")


    def draw_front_side(self, painter, for_svg=False, ox=0, oy=0):
        """Draws the front side of the word card, including an empty space for the image."""
        self.draw_common_elements(painter, ox, oy)


    def draw_back_side(self, painter, for_svg=False, ox=0, oy=0):
        """Draws the back side of the word card, including the definition and word boxes."""
        self.draw_common_elements(painter, ox, oy)

        # Border rectangle (inset)
        left = ox + BORDER_INSET
        right = ox + self.grid_width - BORDER_INSET
        top = oy + BORDER_INSET
        bottom = oy + self.grid_height - BORDER_INSET

        # Word box settings (relative to border)
        num_boxes = 3
        total_boxes_height = num_boxes * WORD_BOX_HEIGHT + (num_boxes - 1) * GAP_BETWEEN_WORD_BOXES
        first_box_y = bottom - BOTTOM_MARGIN - total_boxes_height
        box_width = (right - left) - 2 * WORD_BOX_MARGIN_SIDES

        painter.setFont(self.word_font)
        painter.setPen(QPen(BLACK, BORDER_THICKNESS))
        painter.setBrush(QBrush(YELLOW))

        words = [self.easy_synonym, self.medium_synonym, self.hard_synonym]
        for i, word in enumerate(words):
            y = first_box_y + i * (WORD_BOX_HEIGHT + GAP_BETWEEN_WORD_BOXES)
            rect = QRect(left + WORD_BOX_MARGIN_SIDES, y, box_width, WORD_BOX_HEIGHT)
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
        # SVG canvas size matches the actual card size (2.5" x 3.5")
        canvas_width = self.grid_width
        canvas_height = self.grid_height
        ox = 0  # Card starts at origin
        oy = 0  # Card starts at origin
        
        generator = QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(QSize(canvas_width, canvas_height))
        generator.setViewBox(QRect(0, 0, canvas_width, canvas_height))
        generator.setResolution(96)  # Ensure 96 DPI
        generator.setTitle("Word Card")
        generator.setDescription("An SVG drawing created by WordMasterBingo.")
        painter = QPainter(generator)
        
        # Draw a solid black background covering the entire canvas
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, canvas_width, canvas_height)
        
        if side == 'front':
            self.draw_front_side(painter, for_svg=True, ox=ox, oy=oy)
        else:
            self.draw_back_side(painter, for_svg=True, ox=ox, oy=oy)
        painter.end()


def patch_svg_physical_size(filename, width_in="2.5in", height_in="3.5in"):
    with open(filename, "r") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if "<svg" in line:
            # Remove any existing width/height attributes
            line = re.sub(r'width="[^"]*"', '', line)
            line = re.sub(r'height="[^"]*"', '', line)
            # Add the correct width and height
            line = line.replace("<svg", f'<svg width="{width_in}" height="{height_in}"', 1)
            lines[i] = line
            break
    with open(filename, "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    Utils.initialize(WORDS_FILE)
    words = Utils.get_words()

    windows = []  # Keep references to all windows
    svg_files = []  # List to store all SVG filenames

    for i, word in enumerate(words):
        # Create back side SVG
        word_card_back = GridWindow(word)
        word_card_back.set_side('back')  # Set side to 'back'
        word_card_back.show()
        windows.append(word_card_back)
        QApplication.processEvents()
        svg_back = f"WordCards/word_card_{i}_back.svg"
        word_card_back.save_as_svg(svg_back, side='back')
        patch_svg_physical_size(svg_back)
        svg_files.append(svg_back)

        # Create front side SVG
        word_card_front = GridWindow(word)
        word_card_front.set_side('front')
        word_card_front.show()
        windows.append(word_card_front)
        QApplication.processEvents()
        svg_front = f"WordCards/word_card_{i}_front.svg"
        word_card_front.save_as_svg(svg_front, side='front')
        patch_svg_physical_size(svg_front)
        svg_files.append(svg_front)

    sys.exit(app.exec())