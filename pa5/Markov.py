# CS122 W'21: Markov models and hash tables
# Jake Underland

import sys
import math
import Hash_Table

HASH_CELLS = 57

class Markov:

    def __init__(self,k,s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"
        '''
        self.k = k
        self.s = s
        self.kgram_hash = Hash_Table.Hash_Table(HASH_CELLS, 0)
        self.train_markov(s)

    def log_probability(self,s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.
        '''
        alphabet = set(self.s)
        s = s[-self.k:] + s
        sum_prob = 0
        for i, _ in enumerate(s):
            if i >= self.k:
                whole = s[i-self.k:i+1]
                prefix = s[i-self.k:i]
                sum_prob += math.log((self.lookup(whole) + 1) \
                         / (self.lookup(prefix) + len(alphabet)))
        
        return sum_prob
                
    def train_markov(self, s):
        '''
        Train markov model by passing in string(s) and recording the number of 
        occurences of k+1 grams and kgrams. 
        Inputs:
          s: string
        Does not return anything but modifies self.kgram_hash
        '''
        s = s[-self.k:] + s
        for i, _ in enumerate(s):
            if i >= self.k:
                whole = s[i-self.k:i+1]
                prefix = s[i-self.k:i]
                self.kgram_hash.update(whole, self.kgram_hash.lookup(whole) + 1)
                self.kgram_hash.update(prefix, self.kgram_hash.lookup(prefix) + 1)
    
    def lookup(self, key):
        '''
        Looks up the count of key in self.kgram_hash
        '''
        return self.kgram_hash.lookup(key)


def identify_speaker(speech1, speech2, speech3, order):
    '''
    Given sample text from two speakers (1 and 2), and text from an
    unidentified speaker (3), return a tuple with the *normalized* log probabilities
    of each of the speakers
    uttering that text under a "order" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.
    '''
    speakerA = Markov(order, speech1)
    speakerB = Markov(order, speech2)
    norm_probA = speakerA.log_probability(speech3) / len(speech3)
    norm_probB = speakerB.log_probability(speech3) / len(speech3)
    if norm_probA > norm_probB:
        conclusion = "A"
    else:
        conclusion = "B"
    
    return norm_probA, norm_probB, conclusion


def print_results(res_tuple):
    '''
    Given a tuple from identify_speaker, print formatted results to the screen
    '''
    (likelihood1, likelihood2, conclusion) = res_tuple
    
    print("Speaker A: " + str(likelihood1))
    print("Speaker B: " + str(likelihood2))

    print("")

    print("Conclusion: Speaker " + conclusion + " is most likely")


if __name__=="__main__":
    num_args = len(sys.argv)

    if num_args != 5:
        print("usage: python3 " + sys.argv[0] + " <file name for speaker A> " +
              "<file name for speaker B>\n  <file name of text to identify> " +
              "<order>")
        sys.exit(0)
    
    with open(sys.argv[1], "r") as file1:
        speech1 = file1.read()

    with open(sys.argv[2], "r") as file2:
        speech2 = file2.read()

    with open(sys.argv[3], "r") as file3:
        speech3 = file3.read()

    res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[4]))

    print_results(res_tuple)

