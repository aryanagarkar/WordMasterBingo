import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, QRect, QSize
import random
from utils import Utils
from word import Word
from PySide6.QtSvg import QSvgRenderer, QSvgGenerator
from difficulty_level import DifficultyLevel
import re
from pathlib import Path

# File paths
WORDS_FILE = "../WordAndDefinitionGenerator/OpenAIIntegration/WordDefinitionsAndSynonyms.txt"
LOGO_BASE_PATH = Path(__file__).parent

# Card dimensions (4x5 inches at 96 DPI)
CARD_WIDTH_PIXELS = 384
CARD_HEIGHT_PIXELS = 480
GRID_SIZE_PIXELS = 96
CELL_PADDING = 8

# Font sizes
TITLE_FONT_SIZE = 25
WORD_FONT_SIZE = 10

# Colors
GREEN = QColor(126, 217, 87)
YELLOW = QColor(251, 220, 106)
RED = QColor(255, 49, 49)

# Layout constants
BORDER_THICKNESS = 2
TOP_SECTION_ROWS = 1
GRID_ROWS = 5
GRID_COLS = 4
WORDS_PER_CARD = 16

# Logo sizing
FRONT_LOGO_SCALE_FACTOR = 2.8
BACK_LOGO_SCALE_FACTOR = 1.0
BACK_LOGO_HORIZONTAL_OFFSET = -30

# SVG settings
SVG_DPI = 96
SVG_WIDTH_INCHES = "4in"
SVG_HEIGHT_INCHES = "5in"


class BingoCard(QMainWindow):
    """A bingo card widget that can display front and back sides."""
    
    def __init__(self, words, difficulty=DifficultyLevel.MEDIUM):
        super().__init__()
        self.setWindowTitle("Bingo Card")
        
        # Normalize words list to exactly 16 items
        self.words = self._normalize_words_list(words)
        self.difficulty = difficulty
        self.side = 'front'
        
        # Initialize dimensions
        self._setup_dimensions()
        self._setup_logo_paths()
        self._setup_appearance()
        
        # Initialize offsets (will be set in resizeEvent)
        self.offset_x = 0
        self.offset_y = 0

    def _normalize_words_list(self, words):
        """Ensure exactly 16 words in the list."""
        if len(words) < WORDS_PER_CARD:
            return words + [Word() for _ in range(WORDS_PER_CARD - len(words))]
        elif len(words) > WORDS_PER_CARD:
            return words[:WORDS_PER_CARD]
        return words

    def _setup_dimensions(self):
        """Setup card dimensions and geometry."""
        self.grid_width = CARD_WIDTH_PIXELS
        self.grid_height = CARD_HEIGHT_PIXELS
        self.top_section_height = GRID_SIZE_PIXELS * TOP_SECTION_ROWS
        self.setGeometry(100, 100, self.grid_width, self.grid_height)

    def _setup_logo_paths(self):
        """Setup logo file paths."""
        self.logos = {
            'front': LOGO_BASE_PATH / "lingo_bingo_logo.svg",
            'easy': LOGO_BASE_PATH / "lingo_bingo_logo_green.svg",
            'medium': LOGO_BASE_PATH / "lingo_bingo_logo_yellow.svg",
            'hard': LOGO_BASE_PATH / "lingo_bingo_logo_red.svg"
        }

    def _setup_appearance(self):
        """Setup window appearance."""
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def get_difficulty_color(self):
        """Get the color associated with the current difficulty level."""
        color_map = {
            DifficultyLevel.EASY: GREEN,
            DifficultyLevel.MEDIUM: YELLOW,
            DifficultyLevel.HARD: RED
        }
        return color_map.get(self.difficulty, YELLOW)

    def get_word_by_difficulty(self, word_obj):
        """Get the appropriate word based on difficulty level."""
        method_map = {
            DifficultyLevel.EASY: word_obj.get_easy_word,
            DifficultyLevel.MEDIUM: word_obj.get_medium_word,
            DifficultyLevel.HARD: word_obj.get_hard_word
        }
        method = method_map.get(self.difficulty, word_obj.get_word)
        return method()

    def get_logo_path(self):
        """Get the appropriate logo path based on current side and difficulty."""
        if self.side == 'front':
            return self.logos['front']
        
        difficulty_map = {
            DifficultyLevel.EASY: 'easy',
            DifficultyLevel.MEDIUM: 'medium',
            DifficultyLevel.HARD: 'hard'
        }
        return self.logos[difficulty_map.get(self.difficulty, 'medium')]

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        self.offset_x = (self.width() - self.grid_width) // 2
        self.offset_y = (self.height() - self.grid_height) // 2
        self.repaint()

    def wrap_text(self, painter, text, max_width):
        """Split text into lines that fit within max_width."""
        words = text.split()
        if not words:
            return [""]
        
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + ' ' + word
            if painter.fontMetrics().horizontalAdvance(test_line) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        return lines

    def draw_svg_logo(self, painter, logo_path, x, y, width, height):
        """Draw an SVG logo at the specified position and size."""
        try:
            svg_renderer = QSvgRenderer(str(logo_path))
            if svg_renderer.isValid():
                svg_rect = QRect(x, y, width, height)
                svg_renderer.render(painter, svg_rect)
        except Exception as e:
            print(f"Error rendering logo {logo_path}: {e}")

    def draw_front_side(self, painter, ox=0, oy=0):
        """Draw the front side of the bingo card."""
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw black background
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        painter.drawRect(ox, oy, self.grid_width, self.grid_height)

        # Draw logo in top section
        self._draw_front_logo(painter, ox, oy)

        # Draw word grid
        self._draw_word_grid(painter, ox, oy)

        # Draw grid lines
        self._draw_grid_lines(painter, ox, oy)

    def _draw_front_logo(self, painter, ox, oy):
        """Draw the logo on the front side."""
        logo_path = self.get_logo_path()
        svg_renderer = QSvgRenderer(str(logo_path))
        
        # Calculate logo size
        svg_height = int(self.top_section_height * FRONT_LOGO_SCALE_FACTOR)
        svg_width = int(svg_height * (svg_renderer.defaultSize().width() / svg_renderer.defaultSize().height()))
        
        # Center the logo
        x = ox + (self.grid_width - svg_width) // 2
        y = oy + (self.top_section_height - svg_height) // 2
        
        self.draw_svg_logo(painter, logo_path, x, y, svg_width, svg_height)

    def _draw_word_grid(self, painter, ox, oy):
        """Draw the word grid cells."""
        for row in range(1, GRID_ROWS):  # Skip top row (logo section)
            for col in range(GRID_COLS):
                self._draw_word_cell(painter, ox, oy, row, col)

    def _draw_word_cell(self, painter, ox, oy, row, col):
        """Draw a single word cell."""
        index = (row - 1) * GRID_COLS + col
        word_obj = self.words[index]
        word = self.get_word_by_difficulty(word_obj)

        # Cell position and size
        cell_x = ox + col * GRID_SIZE_PIXELS
        cell_y = oy + row * GRID_SIZE_PIXELS

        # Draw cell background
        painter.setBrush(QBrush(Qt.black))
        painter.drawRect(cell_x, cell_y, GRID_SIZE_PIXELS, GRID_SIZE_PIXELS)

        # Draw word text
        self._draw_cell_text(painter, word, cell_x, cell_y)

    def _draw_cell_text(self, painter, word, cell_x, cell_y):
        """Draw text within a cell with wrapping."""
        painter.setPen(Qt.white)
        painter.setFont(QFont('Barlow', WORD_FONT_SIZE))
        
        # Calculate text layout
        max_text_width = GRID_SIZE_PIXELS - CELL_PADDING
        lines = self.wrap_text(painter, word, max_text_width)
        
        # Center text vertically and horizontally
        fm = painter.fontMetrics()
        total_text_height = len(lines) * fm.height()
        start_y = cell_y + (GRID_SIZE_PIXELS - total_text_height) // 2 + fm.ascent()
        
        for i, line in enumerate(lines):
            text_width = fm.horizontalAdvance(line)
            line_x = cell_x + (GRID_SIZE_PIXELS - text_width) // 2
            line_y = start_y + i * fm.height()
            painter.drawText(line_x, line_y, line)

    def _draw_grid_lines(self, painter, ox, oy):
        """Draw the grid lines."""
        color = self.get_difficulty_color()
        painter.setPen(QPen(color, BORDER_THICKNESS, Qt.SolidLine))
        
        # Draw horizontal lines
        for y in range(0, (GRID_ROWS + 1) * GRID_SIZE_PIXELS, GRID_SIZE_PIXELS):
            painter.drawLine(ox, oy + y, ox + self.grid_width, oy + y)
        
        # Draw vertical lines
        for x in range(0, (GRID_COLS + 1) * GRID_SIZE_PIXELS, GRID_SIZE_PIXELS):
            if x == 0 or x == self.grid_width:
                painter.drawLine(ox + x, oy, ox + x, oy + self.grid_height)
            else:
                painter.drawLine(ox + x, oy + self.top_section_height, ox + x, oy + self.grid_height)

    def draw_back_side(self, painter, ox=0, oy=0):
        """Draw the back side of the bingo card."""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw colored background
        color = self.get_difficulty_color()
        painter.setBrush(QBrush(color))
        painter.drawRect(ox, oy, self.grid_width, self.grid_height)

        # Draw logo
        self._draw_back_logo(painter, ox, oy)

    def _draw_back_logo(self, painter, ox, oy):
        """Draw the logo on the back side."""
        logo_path = self.get_logo_path()
        svg_renderer = QSvgRenderer(str(logo_path))
        
        # Calculate logo size
        svg_height = int(self.grid_height * BACK_LOGO_SCALE_FACTOR)
        svg_width = int(svg_height * (svg_renderer.defaultSize().width() / svg_renderer.defaultSize().height()))
        
        # Position logo with offset
        x = ox + (self.grid_width - svg_width) // 2 + BACK_LOGO_HORIZONTAL_OFFSET
        y = oy + (self.grid_height - svg_height) // 2
        
        self.draw_svg_logo(painter, logo_path, x, y, svg_width, svg_height)

    def paintEvent(self, event):
        """Handle paint events."""
        painter = QPainter(self)
        
        if self.side == 'front':
            self.draw_front_side(painter, ox=self.offset_x, oy=self.offset_y)
        else:
            self.draw_back_side(painter, ox=self.offset_x, oy=self.offset_y)

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
            generator.setTitle("Bingo Card")
            generator.setDescription("An SVG drawing created by WordMasterBingo.")
            
            # Create painter and draw
            painter = QPainter(generator)
            
            # Draw white background
            painter.setBrush(QBrush(Qt.white))
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


def get_words_by_difficulty(difficulty_enum):
    """Get Word objects filtered by difficulty level."""
    all_words = [
        w for w in Utils.get_words() 
        if getattr(w, f'get_{difficulty_enum.value}_word')() != '-'
    ]
    return all_words


def create_bingo_cards():
    """Create and save bingo cards for all difficulty levels."""
    app = QApplication(sys.argv)
    Utils.initialize(WORDS_FILE)

    windows = []
    num_cards_per_difficulty = 16
    svg_files = []

    for difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
        word_objs = get_words_by_difficulty(difficulty)
        
        for i in range(num_cards_per_difficulty):
            # Select words for this card
            if len(word_objs) >= WORDS_PER_CARD:
                selected_words = random.sample(word_objs, WORDS_PER_CARD)
            else:
                # Repeat words if not enough available
                selected_words = (word_objs * (WORDS_PER_CARD // len(word_objs)) + 
                                word_objs[:WORDS_PER_CARD % len(word_objs)])

            # Create back side
            card_back = BingoCard(selected_words, difficulty=difficulty)
            card_back.set_side('back')
            card_back.show()
            windows.append(card_back)
            
            back_svg_path = f"BingoCards/bingo_card_{difficulty.value}_{i}_back.svg"
            card_back.save_as_svg(back_svg_path, side='back')
            svg_files.append(back_svg_path)

            # Create front side
            card_front = BingoCard(selected_words, difficulty=difficulty)
            card_front.set_side('front')
            card_front.show()
            windows.append(card_front)
            
            front_svg_path = f"BingoCards/bingo_card_{difficulty.value}_{i}_front.svg"
            card_front.save_as_svg(front_svg_path, side='front')
            svg_files.append(front_svg_path)
    
    return app, windows, svg_files


if __name__ == "__main__":
    app, windows, svg_files = create_bingo_cards()
    sys.exit(app.exec())