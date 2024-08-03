from abc import abstractmethod
import os


class Filter:
    def load_words_from_file(self, filter_dict_file_path):        
        if not os.path.isfile(filter_dict_file_path):
            return False
        for word in open(filter_dict_file_path):
            self.add_word(word)
        return True
    
    @abstractmethod
    def add_word(self, word):
        pass

    @abstractmethod
    def check(self, content):
        pass