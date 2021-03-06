# CS122 W'21: Markov models and hash tables
# Jake Underland


TOO_FULL = 0.5
GROWTH_RATIO = 2


class Hash_Table:

    def __init__(self,cells,defval):
        '''
        Construct a new hash table with a fixed number of cells equal to the
        parameter "cells", and which yields the value defval upon a lookup to a
        key that has not previously been inserted
        '''
        self._table = [None] * cells
        self.defval = defval
        self.cells = cells
        self.count = 0

    def lookup(self,key):
        '''
        Retrieve the value associated with the specified key in the hash table,
        or return the default value if it has not previously been inserted.
        ''' 
        index = self.hash_key(key)

        while self._table[index % len(self._table)] and \
            self._table[index % len(self._table)][0] != key: # nonempty and != key
            index += 1
        if self._table[index % len(self._table)]: # if not none then this is the key
            return self._table[index % len(self._table)][1]           
        else:
            return self.defval

    def update(self,key,val):
        '''
        Change the value associated with key "key" to value "val".
        If "key" is not currently present in the hash table,  insert it with
        value "val".
        ''' 
        index = self.hash_key(key)
        while self._table[index % len(self._table)] \
              and self._table[index % len(self._table)][0] != key:
            index += 1
        if not self._table[index % len(self._table)]:  # new entry 
            self.count += 1  # increment count
            if self.count > (len(self._table) * TOO_FULL):
                self.rehash()
        self._table[index % len(self._table)] = (key, val)

    def hash_key(self, key):
        '''
        Hash function that takes a key and returns it in hashed form.
        '''
        hash_ = 0
        for char in key:
            hash_ = (hash_ * 37 + ord(char)) % len(self._table)
        return hash_

    def rehash(self, growth_ratio=GROWTH_RATIO):
        '''
        Expands hash table(self._table) by rate stipulated in growth_ratio
        '''
        self.count = 0
        backup = []
        for tup in self._table:
            if tup:
                backup.append(tup)
        self._table = [None] * len(self._table) * growth_ratio
        for key, value in backup:
            self.update(key, value)


