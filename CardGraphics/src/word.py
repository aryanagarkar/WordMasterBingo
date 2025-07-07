from typing import Any

class Word:
    """
    Represents a word with its definition and synonyms for different difficulty levels.
    Used for generating word and bingo cards with varying difficulty.
    """
    
    def __init__(
        self,
        word: str = '-',
        definition: str = '-',
        easy: str = '-',
        medium: str = '-',
        hard: str = '-'
    ) -> None:
        
        """
        Initialize a Word object.

        Args:
            word (str): The main word.
            definition (str): The definition of the word.
            easy (str): Easy synonym.
            medium (str): Medium synonym.
            hard (str): Hard synonym.
        """
        
        self._word = word
        self._definition = definition
        self._easy_word = easy
        self._medium_word = medium
        self._hard_word = hard

    @property
    def word(self) -> str:
        """
        Get the main word.

        Returns:
            str: The main word.
        """

        return self._word
    
    @property
    def definition(self) -> str:
        """
        Get the definition of the word.

        Returns:
            str: The definition of the word.
        """

        return self._definition
    
    @property
    def easy_word(self) -> str:
        """
        Get the easy synonym of the word.

        Returns:
            str: The easy synonym.
        """

        return self._easy_word
    
    @property
    def medium_word(self) -> str:
        """
        Get the medium synonym of the word.

        Returns:
            str: The medium synonym.
        """

        return self._medium_word
    
    @property
    def hard_word(self) -> str:
        """
        Get the hard synonym of the word.

        Returns:
            str: The hard synonym.
        """

        return self._hard_word

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another Word object.

        Args:
            other (Any): The object to compare with.
        Returns:
            bool: True if all fields are equal, False otherwise.
        """

        if not isinstance(other, Word):
            return NotImplemented
        return (
            self.word == other.word and
            self.definition == other.definition and
            self.easy_word == other.easy_word and
            self.medium_word == other.medium_word and
            self.hard_word == other.hard_word
        )

    def __repr__(self) -> str:
        """
        Return a string representation of the Word object.

        Returns:
            str: String representation.
        """
        
        return (
            f"Word(word={self.word!r}, definition={self.definition!r}, "
            f"easy={self.easy_word!r}, medium={self.medium_word!r}, hard={self.hard_word!r})"
        )

    