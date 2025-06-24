import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QImage, QPixmap, QPageSize, QPdfWriter
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCore import Qt, QRect, QRectF, QSizeF, QSize
import random
from utils import Utils
from word import Word
from PySide6.QtSvg import QSvgRenderer, QSvgGenerator
from difficulty_level import DifficultyLevel
import re

WORDS_FILE = "../WordAndDefinitionGenerator/OpenAIIntegration/WordDefinitionsAndSynonyms.txt"

# Font sizes.
TITLE_FONT_SIZE = 25
WORD_FONT_SIZE = 12

# Colors.
GREEN = QColor(126, 217, 87)
YELLOW = QColor(251, 220, 106)
RED = QColor(255, 49, 49)
BLACK = Qt.black

# Other constants.
BORDER_THICKNESS = 2
TOP_SECTION_ROWS = 1

# Demo for medium words:

class GridWindow(QMainWindow):
    def __init__(self, words, difficulty=DifficultyLevel.MEDIUM, grid_size=96, rows=5, cols=4):
        super().__init__()
        self.setWindowTitle("4x4 Bingo Card Grid")

        self.words = words
        # Ensure self.words is exactly 16 items
        if len(self.words) < 16:
            self.words += [Word() for _ in range(16 - len(self.words))]
        elif len(self.words) > 16:
            self.words = self.words[:16]

        self.difficulty = difficulty
        self.grid_size = grid_size
        self.rows = rows
        self.cols = cols

        # Set exact card size: 4x5 inches at 96 DPI
        self.grid_width = 384
        self.grid_height = 480
        self.setGeometry(100, 100, self.grid_width, self.grid_height)

        # Calculate offsets to center the grid within the window
        self.top_section_of_grid_height = self.grid_size * TOP_SECTION_ROWS
        self.section_width = self.grid_width // 2

        self.white_logo = "word_wizards_logo_white.svg"
        self.black_logo = "word_wizards_logo_black.svg"

        pal = self.palette()
        pal.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(pal)
        self.setAutoFillBackground(True)


    def get_color(self):
        if self.difficulty == DifficultyLevel.EASY:
            return GREEN
        elif self.difficulty == DifficultyLevel.MEDIUM:
            return YELLOW
        elif self.difficulty == DifficultyLevel.HARD:
            return RED


    def resizeEvent(self, event):
        self.offset_x = (self.width() - self.grid_width) // 2
        self.offset_y = (self.height() - self.grid_height) // 2
        self.repaint()

    def wrap_text(self, painter, text, max_width):
        """
        Splits text into lines so that each line fits within max_width using the current font.
        Returns a list of lines.
        """
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

    def draw_front_side(self, painter, ox=0, oy=0):
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill the entire card background with black
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        painter.drawRect(ox, oy, self.grid_width, self.grid_height)

        color = self.get_color()

        # Draw the logo on the top of the card.
        svg_renderer = QSvgRenderer(self.white_logo)
        svg_natural_width = svg_renderer.defaultSize().width()
        svg_natural_height = svg_renderer.defaultSize().height()
        svg_height = int(self.top_section_of_grid_height * 3.5)
        svg_width = int(svg_height * (svg_natural_width / svg_natural_height))
        if svg_width > self.grid_width:
            svg_width = self.grid_width
            svg_height = int(svg_width * (svg_natural_height / svg_natural_width))
        x = ox + (self.grid_width - svg_width) // 2
        y = oy + (self.top_section_of_grid_height - svg_height) // 2
        svg_rect = QRect(x, y, svg_width, svg_height)
        svg_renderer.render(painter, svg_rect)

        # Draw the words in the grid cells (rows 1-4)
        for row in range(1, 5):  # rows 1 to 4
            for col in range(self.cols):  # 4 columns
                index = (row - 1) * 4 + col
                word_obj = self.words[index]
                # Select the correct synonym based on difficulty
                if self.difficulty == DifficultyLevel.EASY:
                    word = word_obj.get_easy_word()
                elif self.difficulty == DifficultyLevel.MEDIUM:
                    word = word_obj.get_medium_word()
                elif self.difficulty == DifficultyLevel.HARD:
                    word = word_obj.get_hard_word()
                else:
                    word = word_obj.get_word()

                painter.setBrush(QBrush(Qt.black))
                painter.drawRect(ox + col * self.grid_size, oy + row * self.grid_size, self.grid_size, self.grid_size)

                # Draw the word in the cell, wrapped if needed
                painter.setPen(Qt.white)
                painter.setFont(QFont('Barlow', WORD_FONT_SIZE))
                cell_x = ox + col * self.grid_size
                cell_y = oy + row * self.grid_size
                cell_w = self.grid_size
                cell_h = self.grid_size
                lines = self.wrap_text(painter, word, cell_w - 8)  # 8px padding
                fm = painter.fontMetrics()
                total_text_height = len(lines) * fm.height()
                start_y = cell_y + (cell_h - total_text_height) // 2 + fm.ascent()
                for i, line in enumerate(lines):
                    text_width = fm.horizontalAdvance(line)
                    line_x = cell_x + (cell_w - text_width) // 2
                    line_y = start_y + i * fm.height()
                    painter.drawText(line_x, line_y, line)

        # Draw horizontal and vertical grid lines
        painter.setPen(QPen(color, BORDER_THICKNESS, Qt.SolidLine))
        for x in range(0, (self.cols + 1) * self.grid_size, self.grid_size):
            for y in range(0, (self.rows + 1) * self.grid_size, self.grid_size):
                painter.drawLine(ox, oy + y, ox + self.grid_width, oy + y)
                if x == 0 or x == (self.grid_width):
                    painter.drawLine(ox + x, oy, ox + x, oy + self.grid_height)
                else:
                    painter.drawLine(ox + x, oy + self.top_section_of_grid_height, ox + x, oy + self.grid_height)


    def draw_back_side(self, painter, ox=0, oy=0):
        """Draws the back side of the card."""
        painter.setRenderHint(QPainter.Antialiasing)

        color = self.get_color()

        # Fill the entire background with the color.
        painter.setBrush(QBrush(color))
        painter.drawRect(ox, oy, self.grid_width, self.grid_height)

        # Draw the logo centered in the card.
        svg_renderer = QSvgRenderer(self.black_logo)
        svg_width = int(self.grid_width * 0.8)
        svg_height = int(self.grid_height * 0.8)
        x = ox + (self.grid_width - svg_width) // 2
        y = oy + (self.grid_height - svg_height) // 2
        svg_rect = QRect(x, y, svg_width, svg_height)
        svg_renderer.render(painter, svg_rect)

    def paintEvent(self, event):
        painter = QPainter(self)

        if hasattr(self, 'side') and self.side == 'front':
            self.draw_front_side(painter, ox=self.offset_x, oy=self.offset_y)
        else:
            self.draw_back_side(painter, ox=self.offset_x, oy=self.offset_y)

   
    def set_side(self, side):
        self.side = side
        self.repaint()

    def save_as_svg(self, filename, side='front'):
        # SVG canvas size matches the actual card size (4" x 5")
        canvas_width = self.grid_width
        canvas_height = self.grid_height
        ox = 0  # Card starts at origin
        oy = 0  # Card starts at origin
        generator = QSvgGenerator()
        generator.setFileName(filename)
        generator.setSize(QSize(canvas_width, canvas_height))
        generator.setViewBox(QRect(0, 0, canvas_width, canvas_height))
        generator.setResolution(96)  # Ensure 96 DPI
        generator.setTitle("Bingo Card")
        generator.setDescription("An SVG drawing created by WordMasterBingo.")
        painter = QPainter(generator)
        # Draw a white background for the SVG canvas
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, canvas_width, canvas_height)
        if side == 'front':
            self.draw_front_side(painter, ox=ox, oy=oy)
        else:
            self.draw_back_side(painter, ox=ox, oy=oy)
        painter.end()
        patch_svg_physical_size(filename)

def patch_svg_physical_size(filename, width_in="4in", height_in="5in"):
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

    windows = []
    num_cards_per_difficulty = 6
    num_words_per_card = 16
    svg_files = []  # Store all SVG file paths

    # Helper to get Word objects by difficulty.
    def get_word_objs_by_difficulty(difficulty_enum):
        all_words = [w for w in Utils.get_words() if getattr(w, f'get_{difficulty_enum.value}_word')() != '-']
        return all_words

    for difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
        word_objs = get_word_objs_by_difficulty(difficulty)
        for i in range(num_cards_per_difficulty):
            if len(word_objs) >= num_words_per_card:
                selected_words = random.sample(word_objs, num_words_per_card)
            else:
                selected_words = word_objs * (num_words_per_card // len(word_objs)) + word_objs[:num_words_per_card % len(word_objs)]
            card_back = GridWindow(selected_words, difficulty=difficulty)
            card_back.set_side('back')
            card_back.show()
            windows.append(card_back)
            back_svg_path = f"BingoCards/bingo_card_{difficulty.value}_{i}_back.svg"
            card_back.save_as_svg(back_svg_path, side='back')
            svg_files.append(back_svg_path)

            card_front = GridWindow(selected_words, difficulty=difficulty)
            card_front.set_side('front')
            card_front.show()
            windows.append(card_front)
            front_svg_path = f"BingoCards/bingo_card_{difficulty.value}_{i}_front.svg"
            card_front.save_as_svg(front_svg_path, side='front')
            svg_files.append(front_svg_path)
    
    sys.exit(app.exec())