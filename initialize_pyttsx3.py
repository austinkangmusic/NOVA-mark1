import pyttsx3

class Pyttsx3Initializer:
    _instance = None

    def __init__(self):
        if Pyttsx3Initializer._instance is None:
            # Initialize the pyttsx3 engine
            self.engine = pyttsx3.init()

            # Set properties for speech (you can adjust these values)
            self.engine.setProperty('rate', 150)    # Speed of speech
            self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

            Pyttsx3Initializer._instance = self

    @classmethod
    def get_instance(cls):
        """
        Returns the singleton instance of the Pyttsx3Initializer.
        """
        if cls._instance is None:
            cls._instance = Pyttsx3Initializer()
        return cls._instance

    def get_engine(self):
        """
        Returns the pyttsx3 engine instance.
        """
        return self.engine
