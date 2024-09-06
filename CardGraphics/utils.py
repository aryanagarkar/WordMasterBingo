from word import Word

class Utils:
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