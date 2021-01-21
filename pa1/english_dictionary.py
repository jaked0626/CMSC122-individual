# CS122: Auto-completing keyboard using Tries
# Distribution
#
# Matthew Wachs
# Autumn 2014
#
# Revised: August 2015, AMR
#   December 2017, AMR
#
# Jake Underland

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
        try:
            return self.words.traverse_nodes(w).final
        except:  # word does not exist within self.words
            return False

    def num_completions(self, prefix):
        '''
        How many words in the dictionary start with the specified
        prefix?

        Inputs:
          prefix (string): the prefix

        Returns: int
        '''

        try:
            return self.words.traverse_nodes(prefix).count
        except:  # prefix does not exist within self.words
            return 0

    def get_completions(self, prefix):
        '''
        Get the suffixes in the dictionary of words that start with the
        specified prefix.

        Inputs:
          prefix (string): the prefix

        Returns: list of strings.
        '''
        if self.is_word(prefix):
            return [""] + self.words.traverse_nodes(prefix).find_words()
        else: 
            return self.words.traverse_nodes(prefix).find_words()



class TrieNode(object):
    def __init__(self):
        '''
        Constructor
        '''
        self.children = {} # keys will be letters, values the node class
        self.count = 0
        self.final = False

    def add_word(self, word):
        '''
        Adds word to a node, creating a node for each letter in the word.

        Inputs:
          word (string): The word
        '''
        self.count += 1
        if not word:  # base case. No more letters indicates end of word
            self.final = True

        else:  # recursive case. If new letter, create new node.
            if not self.children.get(word[0]):
                self.children[word[0]] = TrieNode()
            self.children[word[0]].add_word(word[1:])

    def traverse_nodes(self, word):
        '''
        Of a word already in self, navigates to the node of the last letter in 
        the word. 
        
        Inputs:
          word (string): the word. Must already be within self.

        Returns the TrieNode object for the last letter in word
        '''
        if not word:
            return self
        else:
            return self.children[word[0]].traverse_nodes(word[1:])

    def find_words(self, prefix=""):
        '''
        Lists all complete words that are found under a given node. 

        Inputs:
          prefix (string): stores the route from the initial node to the
          current node. Should not be manually entered. 
        
        Returns a list of words (strings) under the node. 
        '''
        words = []
        for child_char, child in self.children.items():
            if child.final:
                words += [prefix + child_char]
            words += child.find_words(prefix + child_char)
        
        return words

if __name__ == "__main__":
    autocorrect_shell.go("english_dictionary")
