import random
from word import Word
from difficulty_level import DifficultyLevel

class Utils:
    words = []
    _initialized = False

    @staticmethod
    def initialize(file_path):
        """
        Initialize the static `words` array by loading and shuffling words from the given file.
        This method should be called once at the start.
        """
        if Utils._initialized:
            raise RuntimeError("Utils has already been initialized. Cannot initialize again.")
        
        if(Utils._initialized == False):
            Utils.words = Utils.parse_file(file_path)
            random.shuffle(Utils.words)
            Utils._initialized = True

    @staticmethod
    def get_words():
        return Utils.words

    @staticmethod
    def get_words_by_difficulty(difficulty: DifficultyLevel):
        """Returns a list of words for the specified difficulty level."""
        
        words = []
        for word_obj in Utils.words:
            if difficulty == DifficultyLevel.EASY:
                word = word_obj.get_easy_word()
            elif difficulty == DifficultyLevel.MEDIUM:
                word = word_obj.get_medium_word()
            elif difficulty == DifficultyLevel.HARD:
                word = word_obj.get_hard_word()
            
            if word != '-':
                words.append(word)
        return words

    @staticmethod
    def parse_file(file_path):
        words = []

        with open(file_path, 'r') as file:
            for line in file:
                word_part, remaining_attributes = line.split(':', 1)

                main_word = word_part.strip()

                attributes = remaining_attributes.split(',')
                definition = attributes[0].strip()
                easy = attributes[1].strip()
                medium = attributes[2].strip()
                hard = attributes[3].strip()

                word_obj = Word(main_word, definition, easy, medium, hard)
                words.append(word_obj)

        return words

    @staticmethod
    def clear():
        """Clears the words list and resets the initialization flag, allowing re-initialization."""
        Utils.words = []
        Utils._initialized = False