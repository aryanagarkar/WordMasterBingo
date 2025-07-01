import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QTextOption
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtSvg import QSvgGenerator
import re
from utils import Utils
from word import Word

# File paths
WORDS_FILE = "../WordAndDefinitionGenerator/OpenAIIntegration/WordDefinitionsAndSynonyms.txt"

# Card dimensions (2.5x3.5 inches at 96 DPI)
CARD_WIDTH_PIXELS = 240
CARD_HEIGHT_PIXELS = 336

# Padding and margin constants
PADDING_HEIGHT = 5
PADDING_WIDTH = 10
BOTTOM_MARGIN = 10
WORD_BOX_MARGIN_SIDES = 10
DEFINITION_MARGIN_SIDES = 10
DEFINITION_MARGIN_TOP = 20

# Font sizes
DEFINITION_FONT_SIZE = 15
WORD_FONT_SIZE = 15

# Colors
YELLOW = QColor(251, 220, 106)
BLACK = Qt.black

# Layout constants
WORD_BOX_HEIGHT = 50
GAP_BETWEEN_WORD_BOXES = 5
BORDER_THICKNESS = 2
DEFINITION_HEIGHT_RATIO = 0.4
BORDER_INSET = 15  # How far borders are inset from the card edges
BORDER_EXTENSION = 10  # How far the border lines extend past the corners

# SVG settings
SVG_DPI = 96
SVG_WIDTH_INCHES = "2.5in"
SVG_HEIGHT_INCHES = "3.5in"

# Word box configuration
NUM_WORD_BOXES = 3


class WordCard(QMainWindow):
    """A word card widget that displays a word with its definition and synonyms."""
    
    def __init__(self, word):
        """Initialize the word card with the given word."""
        super().__init__()
        self.setWindowTitle("Word Card")
        
        self.word = word
        self.side = 'front'
        
        # Initialize card data
        self._setup_card_data()
        self._setup_dimensions()
        self._setup_fonts()
        self._setup_appearance()
        
        # Initialize offsets (will be set in resizeEvent)
        self.offset_x = 0
        self.offset_y = 0

    def _setup_card_data(self):
        """Extract word data for display."""
        self.definition = self.word.get_definitions()
        self.easy_synonym = self.word.get_easy_word()
        self.medium_synonym = self.word.get_word()
        self.hard_synonym = self.word.get_hard_word()

    def _setup_dimensions(self):
        """Setup card dimensions and geometry."""
        self.grid_width = CARD_WIDTH_PIXELS
        self.grid_height = CARD_HEIGHT_PIXELS
        self.setGeometry(100, 100, self.grid_width, self.grid_height)

    def _setup_fonts(self):
        """Setup fonts and text options."""
        self.definition_font = QFont('Arbutus Slab', DEFINITION_FONT_SIZE)
        self.word_font = QFont('Barlow', WORD_FONT_SIZE)
        self.word_font.setBold(True)
        
        # Text options for different sections
        self.top_section_text_option = QTextOption()
        self.top_section_text_option.setWrapMode(QTextOption.WordWrap)
        self.top_section_text_option.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        
        self.bottom_section_text_option = QTextOption()
        self.bottom_section_text_option.setWrapMode(QTextOption.WordWrap)
        self.bottom_section_text_option.setAlignment(Qt.AlignCenter)

    def _setup_appearance(self):
        """Setup window appearance."""
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        self.offset_x = (self.width() - self.grid_width) // 2
        self.offset_y = (self.height() - self.grid_height) // 2
        self.repaint()

    def paintEvent(self, event):
        """Handle paint events."""
        painter = QPainter(self)
        
        if self.side == 'front':
            self.draw_front_side(painter, ox=self.offset_x, oy=self.offset_y)
        else:
            self.draw_back_side(painter, ox=self.offset_x, oy=self.offset_y)

    def _get_border_rect(self, ox, oy):
        """Get the border rectangle coordinates."""
        left = ox + BORDER_INSET
        right = ox + self.grid_width - BORDER_INSET
        top = oy + BORDER_INSET
        bottom = oy + self.grid_height - BORDER_INSET
        return left, right, top, bottom

    def _draw_background(self, painter, ox, oy):
        """Draw the black background."""
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        painter.drawRect(ox, oy, self.grid_width, self.grid_height)

    def _draw_border(self, painter, ox, oy):
        """Draw the yellow border with corner extensions."""
        left, right, top, bottom = self._get_border_rect(ox, oy)
        
        # Main border rectangle
        painter.setPen(QPen(YELLOW, BORDER_THICKNESS))
        painter.drawRect(left, top, right - left, bottom - top)
        
        # Draw corner extensions
        self._draw_corner_extensions(painter, left, right, top, bottom)

    def _draw_corner_extensions(self, painter, left, right, top, bottom):
        """Draw the cross extensions at each corner."""
        # Top left
        painter.drawLine(left - BORDER_EXTENSION, top, left + BORDER_EXTENSION, top)
        painter.drawLine(left, top - BORDER_EXTENSION, left, top + BORDER_EXTENSION)
        
        # Top right
        painter.drawLine(right - BORDER_EXTENSION, top, right + BORDER_EXTENSION, top)
        painter.drawLine(right, top - BORDER_EXTENSION, right, top + BORDER_EXTENSION)
        
        # Bottom left
        painter.drawLine(left - BORDER_EXTENSION, bottom, left + BORDER_EXTENSION, bottom)
        painter.drawLine(left, bottom - BORDER_EXTENSION, left, bottom + BORDER_EXTENSION)
        
        # Bottom right
        painter.drawLine(right - BORDER_EXTENSION, bottom, right + BORDER_EXTENSION, bottom)
        painter.drawLine(right, bottom - BORDER_EXTENSION, right, bottom + BORDER_EXTENSION)

    def _draw_definition(self, painter, ox, oy):
        """Draw the definition text."""
        left, right, top, bottom = self._get_border_rect(ox, oy)
        
        # Calculate definition area
        definition_height = int((bottom - top) * DEFINITION_HEIGHT_RATIO)
        text_rect = QRect(
            left + DEFINITION_MARGIN_SIDES,
            top + DEFINITION_MARGIN_TOP,
            (right - left) - 2 * DEFINITION_MARGIN_SIDES,
            definition_height
        )
        
        # Draw definition text
        painter.setFont(self.definition_font)
        painter.setPen(YELLOW)
        painter.drawText(text_rect, Qt.AlignTop | Qt.AlignHCenter | Qt.TextWordWrap, self.definition)

    def _draw_word_boxes(self, painter, ox, oy):
        """Draw the word boxes with synonyms."""
        left, right, top, bottom = self._get_border_rect(ox, oy)
        
        # Calculate word box layout
        total_boxes_height = (NUM_WORD_BOXES * WORD_BOX_HEIGHT + 
                             (NUM_WORD_BOXES - 1) * GAP_BETWEEN_WORD_BOXES)
        first_box_y = bottom - BOTTOM_MARGIN - total_boxes_height
        box_width = (right - left) - 2 * WORD_BOX_MARGIN_SIDES
        
        # Word data
        words = [self.easy_synonym, self.medium_synonym, self.hard_synonym]
        
        # Draw each word box
        painter.setFont(self.word_font)
        painter.setPen(QPen(BLACK, BORDER_THICKNESS))
        painter.setBrush(QBrush(YELLOW))
        
        for i, word in enumerate(words):
            y = first_box_y + i * (WORD_BOX_HEIGHT + GAP_BETWEEN_WORD_BOXES)
            rect = QRect(left + WORD_BOX_MARGIN_SIDES, y, box_width, WORD_BOX_HEIGHT)
            
            # Draw box background
            painter.drawRect(rect)
            
            # Draw word text
            painter.setPen(QPen(Qt.black))
            painter.drawText(rect, Qt.AlignCenter, word)

    def draw_common_elements(self, painter, ox, oy):
        """Draw common elements (background, border, definition) for both sides."""
        painter.setRenderHint(QPainter.Antialiasing)
        
        self._draw_background(painter, ox, oy)
        self._draw_border(painter, ox, oy)
        self._draw_definition(painter, ox, oy)

    def draw_front_side(self, painter, ox=0, oy=0):
        """Draw the front side of the word card."""
        self.draw_common_elements(painter, ox, oy)

    def draw_back_side(self, painter, ox=0, oy=0):
        """Draw the back side of the word card with word boxes."""
        self.draw_common_elements(painter, ox, oy)
        self._draw_word_boxes(painter, ox, oy)

    def set_side(self, side):
        """Set which side of the card to display."""
        self.side = side
        self.repaint()

    def save_as_svg(self, filename, side='front'):
        """Save the card as an SVG file."""
        try:
            # Setup SVG generator
            generator = QSvgGenerator()
            generator.setFileName(filename)
            generator.setSize(QSize(self.grid_width, self.grid_height))
            generator.setViewBox(QRect(0, 0, self.grid_width, self.grid_height))
            generator.setResolution(SVG_DPI)
            generator.setTitle("Word Card")
            generator.setDescription("An SVG drawing created by WordMasterBingo.")
            
            # Create painter and draw
            painter = QPainter(generator)
            
            # Draw black background
            painter.setBrush(QBrush(Qt.black))
            painter.setPen(Qt.NoPen)
            painter.drawRect(0, 0, self.grid_width, self.grid_height)
            
            # Draw card content
            if side == 'front':
                self.draw_front_side(painter)
            else:
                self.draw_back_side(painter)
            
            painter.end()
            
            # Patch SVG with physical dimensions
            self._patch_svg_physical_size(filename)
            
        except Exception as e:
            print(f"Error saving SVG {filename}: {e}")

    def _patch_svg_physical_size(self, filename):
        """Add physical dimensions to the SVG file."""
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if "<svg" in line:
                    # Remove existing width/height attributes
                    line = re.sub(r'width="[^"]*"', '', line)
                    line = re.sub(r'height="[^"]*"', '', line)
                    
                    # Add correct width and height
                    line = line.replace("<svg", f'<svg width="{SVG_WIDTH_INCHES}" height="{SVG_HEIGHT_INCHES}"', 1)
                    lines[i] = line
                    break
            
            with open(filename, "w") as f:
                f.writelines(lines)
                
        except Exception as e:
            print(f"Error patching SVG {filename}: {e}")


def create_word_cards():
    """Create and save word cards for all words."""
    app = QApplication(sys.argv)
    Utils.initialize(WORDS_FILE)
    words = Utils.get_words()

    windows = []
    svg_files = []

    for i, word in enumerate(words):
        # Create back side
        word_card_back = WordCard(word)
        word_card_back.set_side('back')
        word_card_back.show()
        windows.append(word_card_back)
        
        back_svg_path = f"WordCards/word_card_{i}_back.svg"
        word_card_back.save_as_svg(back_svg_path, side='back')
        svg_files.append(back_svg_path)

        # Create front side
        word_card_front = WordCard(word)
        word_card_front.set_side('front')
        word_card_front.show()
        windows.append(word_card_front)
        
        front_svg_path = f"WordCards/word_card_{i}_front.svg"
        word_card_front.save_as_svg(front_svg_path, side='front')
        svg_files.append(front_svg_path)

    return app, windows, svg_files


if __name__ == "__main__":
    app, windows, svg_files = create_word_cards()
    sys.exit(app.exec())