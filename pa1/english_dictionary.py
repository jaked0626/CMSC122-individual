# CS122: Auto-completing keyboard using Tries
# Distribution
#
# Matthew Wachs
# Autumn 2014
#
# Revised: August 2015, AMR
#   December 2017, AMR
#
# YOUR NAME HERE

import os
import sys
from sys import exit

import autocorrect_shell


class EnglishDictionary(object):
    def __init__(self, wordfile):
        '''
        Constructor

        Inputs:
          wordfile (string): name of the file with the words.
        '''
        self.words = TrieNode()

        with open(wordfile) as f:
            for w in f:
                w = w.strip()
                if w != "" and not self.is_word(w):
                    self.words.add_word(w)

    def is_word(self, w):
        '''
        Is the string a word?

        Inputs:
           w (string): the word to check

        Returns: boolean
        '''
        # ADD YOUR CODE HERE AND REPLACE THE False
        # IN THE RETURN WITH A SUITABLE RETURN VALUE.
        return False

    def num_completions(self, prefix):
        '''
        How many words in the dictionary start with the specified
        prefix?

        Inputs:
          prefix (string): the prefix

        Returns: int
        '''
        # IMPORTANT: When you replace this version with the trie-based
        # version, do NOT compute the number of completions simply as
        #
        #    len(self.get_completions(prefix))
        #
        # See PA writeup for more details.

        # ADD YOUR CODE HERE AND REPLACE THE ZERO IN THE RETURN WITH A
        # SUITABLE RETURN VALUE.

        return 0

    def get_completions(self, prefix):
        '''
        Get the suffixes in the dictionary of words that start with the
        specified prefix.

        Inputs:
          prefix (string): the prefix

        Returns: list of strings.
        '''

        # ADD YOUR CODE HERE AND REPLACE THE EMPTY LIST
        # IN THE RETURN WITH A SUITABLE RETURN VALUE.

        return []


class TrieNode(object):
    def __init__(self):
        ### REPLACE pass with appropriate documentation and code
        pass

    def add_word(self, word):
        ### REPLACE pass with appropriate documentation and code
        pass

    ### ADD ANY EXTRA METHODS HERE.

if __name__ == "__main__":
    autocorrect_shell.go("english_dictionary")
