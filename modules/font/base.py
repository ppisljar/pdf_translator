from abc import ABC, abstractmethod

class FontBase(ABC):
    @abstractmethod
    def init(self, cfg: dict):
        pass


    @abstractmethod
    def get_font_info(self, image, line_cnt):
        """
        Translates a given string into another language.

        Parameters:
        - text (str): The text to be translated.

        Returns:
        - str: The translated text.

        This method needs to be implemented by subclasses.
        """
        pass


    @abstractmethod
    def get_all_fonts(self, layout):
        """
        Translates a given string into another language.

        Parameters:
        - text (str): The text to be translated.

        Returns:
        - str: The translated text.

        This method needs to be implemented by subclasses.
        """
        pass

