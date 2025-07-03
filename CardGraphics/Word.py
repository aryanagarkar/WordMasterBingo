class Word:
    """
    Represents a word with its definition and synonyms for different difficulty levels.
    Used for generating word and bingo cards with varying difficulty.
    """
    
    def __init__ (self, word='-', definition='-', easy='-', medium='-', hard='-'):
        """
        Initialize a Word object.
        Args:
            word (str): The main word.
            definition (str): The definition of the word.
            easy (str): Easy synonym.
            medium (str): Medium synonym.
            hard (str): Hard synonym.
            Default value for all of these is the placeholder '-' if a value is not found.
        """
        
        self.__word = word
        self.__definition = definition
        self.__easy_word = easy
        self.__medium_word = medium
        self.__hard_word = hard

    def get_word(self):
        """
        Return the main word.
        Returns:
            str: The main word.
        """
        
        return self.__word
    
    def get_definitions(self):
        """
        Return the definition of the word.
        Returns:
            str: The definition of the word.
        """

        return self.__definition
    
    def get_easy_word(self):
        """
        Return the easy synonym of the word.
        Returns:
            str: The easy synonym.
        """

        return self.__easy_word
    
    def get_medium_word(self):
        """
        Return the medium synonym of the word.
        Returns:
            str: The medium synonym.
        """

        return self.__medium_word
    
    def get_hard_word(self):
        """
        Return the hard synonym of the word.
        Returns:
            str: The hard synonym.
        """
        
        return self.__hard_word

    