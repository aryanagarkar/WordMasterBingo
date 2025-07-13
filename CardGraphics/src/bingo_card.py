import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, QRect, QSize
import random
from CardGraphics.src.utils import Utils
from CardGraphics.src.word import Word
from CardGraphics.src.difficulty_level import DifficultyLevel
from PySide6.QtSvg import QSvgRenderer, QSvgGenerator
import re
from pathlib import Path
from typing import List
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

# File paths.
WORDS_FILE = "/Users/aryanagarkar/Workspace/LingoBingo/OpenAIIntegration/Resources/WordDefinitionsAndSynonyms.txt"
LOGO_BASE_PATH = Path(__file__).parent.parent
BINGOCARDS_DIR = Path(__file__).parent.parent / "BingoCards"

# Card dimensions (4x5 inches at 96 DPI).
CARD_WIDTH_PIXELS = 384
CARD_HEIGHT_PIXELS = 480
GRID_SIZE_PIXELS = 96
CELL_PADDING = 8

# Font sizes.
TITLE_FONT_SIZE = 25
WORD_FONT_SIZE = 10

# Colors.
GREEN = QColor(126, 217, 87)
YELLOW = QColor(251, 220, 106)
RED = QColor(255, 49, 49)

# Layout constants.
BORDER_THICKNESS = 2
TOP_SECTION_ROWS = 1
GRID_ROWS = 5
GRID_COLS = 4
WORDS_PER_CARD = 16

# Logo sizing.
FRONT_LOGO_SCALE_FACTOR = 2.8
BACK_LOGO_SCALE_FACTOR = 1.0
BACK_LOGO_HORIZONTAL_OFFSET = -30

# SVG settings.
SVG_DPI = 96
SVG_WIDTH_INCHES = "4in"
SVG_HEIGHT_INCHES = "5in"

class BingoCardData:
    """
    Holds all data and logic needed to render a bingo card.
    This class is independent of any GUI and is fully unit-testable.
    """

    def __init__(self, words: List[Word], difficulty: DifficultyLevel = DifficultyLevel.MEDIUM):
        """
        Initialize the BingoCardData with a list of Word objects and a difficulty level.

        Args:
            words (List[Word]): List of Word objects to display on the card.
            difficulty (DifficultyLevel): The difficulty level for the card.
        """

        self.words = self._normalize_words_list(words)
        self.difficulty = difficulty

    def _normalize_words_list(self, words: List[Word]) -> List[Word]:
        """
        Ensure the words list has exactly WORDS_PER_CARD items.
        If there are fewer, pad with empty Word objects; if more, truncate.

        Args:
            words (List[Word]): List of Word objects.
        Returns:
            List[Word]: List of exactly WORDS_PER_CARD Word objects.
        """

        if len(words) < WORDS_PER_CARD:
            return words + [Word() for _ in range(WORDS_PER_CARD - len(words))]
        elif len(words) > WORDS_PER_CARD:
            return words[:WORDS_PER_CARD]
        return words

    def get_words_for_grid(self) -> List[str]:
        """
        Get the list of words for the bingo grid based on the current difficulty.

        Returns:
            List[str]: List of words for the grid.
        """

        result = []
        for word_obj in self.words:
            if self.difficulty == DifficultyLevel.EASY:
                result.append(word_obj.easy_word)
            elif self.difficulty == DifficultyLevel.MEDIUM:
                result.append(word_obj.medium_word)
            elif self.difficulty == DifficultyLevel.HARD:
                result.append(word_obj.hard_word)
            else:
                result.append(word_obj.word)
        return result

    def as_dict(self) -> dict:
        """
        Return the card data as a dictionary (for testing or serialization).

        Returns:
            dict: Dictionary representation of the card data.
        """

        return {
            'words': [w.word for w in self.words],
            'difficulty': self.difficulty.name
        }

class BingoCard(QMainWindow):
    """
    A bingo card widget that can display front and back sides with a grid of words.
    Used for 'lingo bingo' - an educational vocabulary game using words, definitions, and synonyms.
    """

    def __init__(self, card_data: BingoCardData):
        """
        Initialize the bingo card with a BingoCardData instance.

        Args:
            card_data (BingoCardData): The data to display on the card.
        """

        super().__init__()
        self.setWindowTitle("Bingo Card")
        self.card_data = card_data
        self.side = 'front'
        self._setup_dimensions()
        self._setup_logo_paths()
        self._setup_appearance()
        self.offset_x = 0
        self.offset_y = 0

    def _setup_dimensions(self) -> None:
        """
        Setup card dimensions and geometry for the bingo card window.
        Sets grid width, height, and top section height.
        """

        self.grid_width = CARD_WIDTH_PIXELS
        self.grid_height = CARD_HEIGHT_PIXELS
        self.top_section_height = GRID_SIZE_PIXELS * TOP_SECTION_ROWS
        self.setGeometry(100, 100, self.grid_width, self.grid_height)

    def _setup_logo_paths(self) -> None:
        """
        Setup logo file paths for different card sides and difficulties.
        """

        self.logos = {
            'front': LOGO_BASE_PATH / "lingo_bingo_logo.svg",
            'easy': LOGO_BASE_PATH / "lingo_bingo_logo_green.svg",
            'medium': LOGO_BASE_PATH / "lingo_bingo_logo_yellow.svg",
            'hard': LOGO_BASE_PATH / "lingo_bingo_logo_red.svg"
        }

    def _setup_appearance(self) -> None:
        """
        Setup window appearance, including background color.
        """

        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def get_difficulty_color(self):
        """
        Get the color associated with the current difficulty level.

        Returns:
            QColor: The color for the current difficulty (green, yellow, or red).
        """

        color_map = {
            DifficultyLevel.EASY: GREEN,
            DifficultyLevel.MEDIUM: YELLOW,
            DifficultyLevel.HARD: RED
        }
        return color_map.get(self.card_data.difficulty, YELLOW)

    def get_logo_path(self):
        """
        Get the appropriate logo path based on the current card side and difficulty.

        Returns:
            Path: Path to the SVG logo file.
        """

        if self.side == 'front':
            return self.logos['front']
        difficulty_map = {
            DifficultyLevel.EASY: 'easy',
            DifficultyLevel.MEDIUM: 'medium',
            DifficultyLevel.HARD: 'hard'
        }
        return self.logos[difficulty_map.get(self.card_data.difficulty, 'medium')]

    def resizeEvent(self, event):
        """
        Handle window resize events to keep the card consistently centered.

        Args:
            event (QResizeEvent): The resize event object.
        """

        super().resizeEvent(event)
        self.offset_x = (self.width() - self.grid_width) // 2
        self.offset_y = (self.height() - self.grid_height) // 2
        self.repaint()

    def wrap_text(self, painter, text, max_width):
        """
        Split text into lines that fit within max_width.
        Args:
            painter (QPainter): The painter object.
            text (str): The text to wrap.
            max_width (int): Maximum width in pixels for each line.
        Returns:
            list: List of text lines.
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

    def draw_svg_logo(self, painter, logo_path, x, y, width, height):
        """
        Draw an SVG logo at the specified position and size.
        Args:
            painter (QPainter): The painter object.
            logo_path (Path): Path to the SVG logo file.
            x (int): X position.
            y (int): Y position.
            width (int): Width to draw.
            height (int): Height to draw.
        """

        try:
            svg_renderer = QSvgRenderer(str(logo_path))
            if svg_renderer.isValid():
                svg_rect = QRect(x, y, width, height)
                svg_renderer.render(painter, svg_rect)
        except Exception as e:
            print(f"Error rendering logo {logo_path}: {e}")

    def draw_front_side(self, painter, ox=0, oy=0):
        """
        Draw the front side of the bingo card.
        Args:
            painter (QPainter): The painter object.
            ox (int): X offset.
            oy (int): Y offset.
        """
        
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw black background.
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        painter.drawRect(ox, oy, self.grid_width, self.grid_height)

        # Draw logo in top section.
        self._draw_front_logo(painter, ox, oy)

        # Draw word grid.
        self._draw_word_grid(painter, ox, oy)

        # Draw grid lines.
        self._draw_grid_lines(painter, ox, oy)

    def _draw_front_logo(self, painter, ox, oy):
        """
        Draw the logo on the front side.
        Args:
            painter (QPainter): The painter object.
            ox (int): X offset.
            oy (int): Y offset.
        """
        
        logo_path = self.get_logo_path()
        svg_renderer = QSvgRenderer(str(logo_path))
        
        # Calculate logo size.
        svg_height = int(self.top_section_height * FRONT_LOGO_SCALE_FACTOR)
        svg_width = int(svg_height * (svg_renderer.defaultSize().width() / svg_renderer.defaultSize().height()))
        
        # Center the logo.
        x = ox + (self.grid_width - svg_width) // 2
        y = oy + (self.top_section_height - svg_height) // 2
        
        self.draw_svg_logo(painter, logo_path, x, y, svg_width, svg_height)

    def _draw_word_grid(self, painter, ox, oy):
        """
        Draw the word grid cells.
        Args:
            painter (QPainter): The painter object.
            ox (int): X offset.
            oy (int): Y offset.
        """

        for row in range(1, GRID_ROWS):  # Skip top row (logo section).
            for col in range(GRID_COLS):
                self._draw_word_cell(painter, ox, oy, row, col)

    def _draw_word_cell(self, painter, ox, oy, row, col):
        """
        Draw a single word cell.
        Args:
            painter (QPainter): The painter object.
            ox (int): X offset.
            oy (int): Y offset.
            row (int): Row index.
            col (int): Column index.
        """
        
        index = (row - 1) * GRID_COLS + col
        word_obj = self.card_data.words[index]
        word = self.card_data.get_words_for_grid()[index]

        # Cell position and size.
        cell_x = ox + col * GRID_SIZE_PIXELS
        cell_y = oy + row * GRID_SIZE_PIXELS

        # Draw cell background.
        painter.setBrush(QBrush(Qt.black))
        painter.drawRect(cell_x, cell_y, GRID_SIZE_PIXELS, GRID_SIZE_PIXELS)

        # Draw word text.
        self._draw_cell_text(painter, word, cell_x, cell_y)

    def _draw_cell_text(self, painter, word, cell_x, cell_y):
        """
        Draw text within a cell with wrapping.
        Args:
            painter (QPainter): The painter object.
            word (str): The word to draw.
            cell_x (int): X position of the cell.
            cell_y (int): Y position of the cell.
        """
        
        painter.setPen(Qt.white)
        painter.setFont(QFont('Barlow', WORD_FONT_SIZE))
        
        # Calculate text layout.
        max_text_width = GRID_SIZE_PIXELS - CELL_PADDING
        lines = self.wrap_text(painter, word, max_text_width)
        
        # Center text vertically and horizontally.
        fm = painter.fontMetrics()
        total_text_height = len(lines) * fm.height()
        start_y = cell_y + (GRID_SIZE_PIXELS - total_text_height) // 2 + fm.ascent()
        
        for i, line in enumerate(lines):
            text_width = fm.horizontalAdvance(line)
            line_x = cell_x + (GRID_SIZE_PIXELS - text_width) // 2
            line_y = start_y + i * fm.height()
            painter.drawText(line_x, line_y, line)

    def _draw_grid_lines(self, painter, ox, oy):
        """
        Draw the grid lines.
        Args:
            painter (QPainter): The painter object.
            ox (int): X offset.
            oy (int): Y offset.
        """
        
        color = self.get_difficulty_color()
        painter.setPen(QPen(color, BORDER_THICKNESS, Qt.SolidLine))
        
        # Draw horizontal lines.
        for y in range(0, (GRID_ROWS + 1) * GRID_SIZE_PIXELS, GRID_SIZE_PIXELS):
            painter.drawLine(ox, oy + y, ox + self.grid_width, oy + y)
        
        # Draw vertical lines.
        for x in range(0, (GRID_COLS + 1) * GRID_SIZE_PIXELS, GRID_SIZE_PIXELS):
            if x == 0 or x == self.grid_width:
                painter.drawLine(ox + x, oy, ox + x, oy + self.grid_height)
            else:
                painter.drawLine(ox + x, oy + self.top_section_height, ox + x, oy + self.grid_height)

    def draw_back_side(self, painter, ox=0, oy=0):
        """
        Draw the back side of the bingo card.
        Args:
            painter (QPainter): The painter object.
            ox (int): X offset.
            oy (int): Y offset.
        """
        
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw colored background.
        color = self.get_difficulty_color()
        painter.setBrush(QBrush(color))
        painter.drawRect(ox, oy, self.grid_width, self.grid_height)

        # Draw logo.
        self._draw_back_logo(painter, ox, oy)

    def _draw_back_logo(self, painter, ox, oy):
        """
        Draw the logo on the back side.
        Args:
            painter (QPainter): The painter object.
            ox (int): X offset.
            oy (int): Y offset.
        """
        
        logo_path = self.get_logo_path()
        svg_renderer = QSvgRenderer(str(logo_path))
        
        # Calculate logo size.
        svg_height = int(self.grid_height * BACK_LOGO_SCALE_FACTOR)
        svg_width = int(svg_height * (svg_renderer.defaultSize().width() / svg_renderer.defaultSize().height()))
        
        # Position logo with offset.
        x = ox + (self.grid_width - svg_width) // 2 + BACK_LOGO_HORIZONTAL_OFFSET
        y = oy + (self.grid_height - svg_height) // 2
        
        self.draw_svg_logo(painter, logo_path, x, y, svg_width, svg_height)

    def paintEvent(self, event):
        """
        Handle paint events to draw the card's front or back side.
        Args:
            event (QPaintEvent): The paint event object.
        """

        painter = QPainter(self)
        
        # Draw the appropriate side of the card.
        if self.side == 'front':
            self.draw_front_side(painter, ox=self.offset_x, oy=self.offset_y)
        else:
            self.draw_back_side(painter, ox=self.offset_x, oy=self.offset_y)

    def set_side(self, side):
        """
        Set which side of the card to display ('front' or 'back').
        Args:
            side (str): 'front' or 'back'.
        """
        
        self.side = side
        self.repaint()

    def save_as_svg(self, filename, side='front'):
        """
        Save the card as an SVG file.
        Args:
            filename (str): The output SVG file path.
            side (str): Which side to save ('front' or 'back').
        """

        try:
            # Setup SVG generator.
            generator = QSvgGenerator()
            generator.setFileName(filename)
            generator.setSize(QSize(self.grid_width, self.grid_height))
            generator.setViewBox(QRect(0, 0, self.grid_width, self.grid_height))
            generator.setResolution(SVG_DPI)
            generator.setTitle("Bingo Card")
            generator.setDescription("An SVG drawing created by WordMasterBingo.")
            
            # Create painter and draw.
            painter = QPainter(generator)
            
            # Draw white background.
            painter.setBrush(QBrush(Qt.white))
            painter.setPen(Qt.NoPen)
            painter.drawRect(0, 0, self.grid_width, self.grid_height)
            
            # Draw card content.
            if side == 'front':
                self.draw_front_side(painter)
            else:
                self.draw_back_side(painter)
            
            painter.end()
            
            # Patch SVG with physical dimensions.
            self._patch_svg_physical_size(filename)
            
        except Exception as e:
            # Print error if SVG saving fails.
            print(f"Error saving SVG {filename}: {e}")

    def _patch_svg_physical_size(self, filename):
        """
        Add physical dimensions to the SVG file.
        Args:
            filename (str): The SVG file path.
        """
        
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if "<svg" in line:
                    # Remove existing width/height attributes.
                    line = re.sub(r'width="[^"]*"', '', line)
                    line = re.sub(r'height="[^"]*"', '', line)
                    
                    # Add correct width and height.
                    line = line.replace("<svg", f'<svg width="{SVG_WIDTH_INCHES}" height="{SVG_HEIGHT_INCHES}"', 1)
                    lines[i] = line
                    break
            
            with open(filename, "w") as f:
                f.writelines(lines)
                
        except Exception as e:
            # Print error if patching fails.
            print(f"Error patching SVG {filename}: {e}")

    @staticmethod
    def generate_printable_pdf(svg_folder, output_pdf):
        """
        Generate a double-sided printable PDF from all SVGs in the given folder using CairoSVG and PyPDF2.
        Page 1: all fronts in grid order.
        Page 2: all backs, mirrored horizontally in each row for double-sided alignment.
        Args:
            svg_folder (str or Path): Folder containing SVG files.
            output_pdf (str or Path): Output PDF file path.
        """
        import tempfile
        import cairosvg
        from PyPDF2 import PdfWriter, PdfReader
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from pathlib import Path
        import re

        svg_folder = Path(svg_folder)
        svg_files = sorted([f for f in svg_folder.iterdir() if f.suffix.lower() == '.svg'])
        front_svgs = [f for f in svg_files if '_front' in f.stem]
        back_svgs = [f for f in svg_files if '_back' in f.stem]
        def extract_index(f):
            m = re.search(r'_(\d+)_', f.stem)
            return int(m.group(1)) if m else -1
        front_svgs.sort(key=extract_index)
        back_svgs.sort(key=extract_index)
        card_w_in, card_h_in = 4, 5
        page_w, page_h = letter
        cards_per_row = 2
        cards_per_col = 2
        x_margin = (page_w - cards_per_row * card_w_in * 72) / 2
        y_margin = (page_h - cards_per_col * card_h_in * 72) / 2
        card_w = card_w_in * 72
        card_h = card_h_in * 72

        def make_page(card_svgs, mirrored=False):
            # Create a blank PDF page
            temp_page = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            c = canvas.Canvas(temp_page.name, pagesize=letter)
            for i, svg_path in enumerate(card_svgs):
                if i >= cards_per_row * cards_per_col:
                    break
                row = (i % 4) // 2
                col = (i % 4) % 2
                if mirrored:
                    col = cards_per_row - 1 - col
                x = x_margin + col * card_w
                y = page_h - y_margin - (row + 1) * card_h
                # Convert SVG to PDF (single card)
                temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                cairosvg.svg2pdf(url=str(svg_path), write_to=temp_pdf.name, output_width=int(card_w), output_height=int(card_h))
                temp_pdf.close()
                # Overlay the card PDF onto the page
                card_pdf = PdfReader(temp_pdf.name)
                c.saveState()
                c.doForm(c.beginFormXObject(x, y, card_w, card_h))
                c.restoreState()
                c.showPage()  # This is needed to flush the form, but we'll merge with PyPDF2 below
                # Instead, merge with PyPDF2 after saving all cards
            c.save()
            return temp_page.name

        # Create front and back pages as PDFs
        front_page_pdf = make_page(front_svgs, mirrored=False)
        back_page_pdf = make_page(back_svgs, mirrored=True)

        # Merge the single-card PDFs onto the blank pages using PyPDF2
        writer = PdfWriter()
        for page_pdf in [front_page_pdf, back_page_pdf]:
            page_reader = PdfReader(page_pdf)
            for page in page_reader.pages:
                writer.add_page(page)
        with open(output_pdf, 'wb') as f_out:
            writer.write(f_out)


def get_words_by_difficulty(difficulty_enum):
    """
    Get Word objects filtered by difficulty level.
    Args:
        difficulty_enum (DifficultyLevel): The difficulty level to filter words by.
    Returns:
        list: List of Word objects that have a valid word for the given difficulty.
    """
    # Filter all words to only those that have a valid word for the given difficulty.
    all_words = [
        w for w in Utils.get_words() 
        if getattr(w, f'{difficulty_enum.value}_word') != '-'
    ]
    return all_words


def create_bingo_cards():
    """
    Create and save bingo cards for all difficulty levels.
    Returns:
        tuple: (QApplication, list of BingoCard windows, list of SVG file paths)
    """
    
    app = QApplication(sys.argv)
    Utils.initialize(WORDS_FILE)

    windows = []
    num_cards_per_difficulty = 16
    svg_files = []

    # Original code:
    # for difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
    #     word_objs = get_words_by_difficulty(difficulty)
    #     for i in range(num_cards_per_difficulty):
    #         # Select words for this card.
    #         if len(word_objs) >= WORDS_PER_CARD:
    #             selected_words = random.sample(word_objs, WORDS_PER_CARD)
    #         else:
    #             # Repeat words if not enough available.
    #             selected_words = (word_objs * (WORDS_PER_CARD // len(word_objs)) + 
    #                             word_objs[:WORDS_PER_CARD % len(word_objs)])
    #
    #         # Create back side.
    #         card_back = BingoCard(BingoCardData(selected_words, difficulty=difficulty))
    #         card_back.set_side('back')
    #         card_back.show()
    #         windows.append(card_back)
    #         back_svg_path = str(BINGOCARDS_DIR / f"bingo_card_{difficulty.value}_{i}_back.svg")
    #         card_back.save_as_svg(back_svg_path, side='back')
    #         svg_files.append(back_svg_path)
    #
    #         # Create front side.
    #         card_front = BingoCard(BingoCardData(selected_words, difficulty=difficulty))
    #         card_front.set_side('front')
    #         card_front.show()
    #         windows.append(card_front)
    #         front_svg_path = str(BINGOCARDS_DIR / f"bingo_card_{difficulty.value}_{i}_front.svg")
    #         card_front.save_as_svg(front_svg_path, side='front')
    #         svg_files.append(front_svg_path)

    # Test version: Only generate 4 cards for MEDIUM difficulty
    difficulty = DifficultyLevel.MEDIUM
    word_objs = get_words_by_difficulty(difficulty)
    for i in range(4):  # Only generate 4 cards for testing
        # Select words for this card.
        if len(word_objs) >= WORDS_PER_CARD:
            selected_words = random.sample(word_objs, WORDS_PER_CARD)
        else:
            # Repeat words if not enough available.
            selected_words = (word_objs * (WORDS_PER_CARD // len(word_objs)) + 
                            word_objs[:WORDS_PER_CARD % len(word_objs)])

        # Create back side.
        card_back = BingoCard(BingoCardData(selected_words, difficulty=difficulty))
        card_back.set_side('back')
        card_back.show()
        windows.append(card_back)
        back_svg_path = str(BINGOCARDS_DIR / f"bingo_card_{difficulty.value}_{i}_back.svg")
        card_back.save_as_svg(back_svg_path, side='back')
        svg_files.append(back_svg_path)

        # Create front side.
        card_front = BingoCard(BingoCardData(selected_words, difficulty=difficulty))
        card_front.set_side('front')
        card_front.show()
        windows.append(card_front)
        front_svg_path = str(BINGOCARDS_DIR / f"bingo_card_{difficulty.value}_{i}_front.svg")
        card_front.save_as_svg(front_svg_path, side='front')
        svg_files.append(front_svg_path)

    # Generate the printable PDF after SVGs are created
    BingoCard.generate_printable_pdf(BINGOCARDS_DIR, "CardGraphics/bingo_cards_printable.pdf")

    return app, windows, svg_files

if __name__ == "__main__":
    app, windows, svg_files = create_bingo_cards()
    sys.exit(app.exec())