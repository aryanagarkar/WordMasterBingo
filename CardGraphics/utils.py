import random
from word import Word

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
    def parse_file(file_path):
        words = []

        with open(file_path, 'r') as file:
            for line in file:
                word_part, remaining_attributes = line.split(':', 1)

                main_word = word_part.strip()

                attributes = remaining_attributes.split(',')
                part_of_speech = attributes[0].strip()
                definition = attributes[1].strip()
                easy = attributes[2].strip()
                medium = attributes[3].strip()
                hard = attributes[4].strip()

                word_obj = Word(main_word, part_of_speech, definition, easy, medium, hard)
                words.append(word_obj)

        return words