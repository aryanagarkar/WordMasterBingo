class Word:
    def __init__ (self, word='-', definition='-', easy='-', medium='-', hard='-'):
        self.__word = word
        self.__definition = definition
        self.__easy_word = easy
        self.__medium_word = medium
        self.__hard_word = hard

    def get_word(self):
        return self.__word
    
    def get_definitions(self):
        return self.__definition
    
    def get_easy_word(self):
        return self.__easy_word
    
    def get_medium_word(self):
        return self.__medium_word
    
    def get_hard_word(self):
        return self.__hard_word

    