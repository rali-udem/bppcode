import copy
class Trie():
    
    def __init__(self, value = True):
        self.children = {}
        self.value = value
        
    def add(self, sequence, value):
        l = len(sequence)
        if l == 0 :
            return None
        elem = sequence[0]
        if l == 1 :
            if elem in self.children :
                self.children[elem].value = value
            else :
                self.children[elem] = Trie(value)
        else :
            current_trie = None
            if elem in self.children :
                current_trie = self.children[elem]
            else :
                current_trie = Trie(None)
                self.children[elem] = current_trie
            current_trie.add(sequence[1:], value)
    
    def find(self, searched_sequence):
        idx = 0
        current_trie = self
        res = []
        start_idx = -1
        end_idx = -1
        length = len(searched_sequence)
        while idx < length:
            
            forward = True
            elem = searched_sequence[idx]
            
            if elem in current_trie.children:
                if start_idx < 0 :
                    start_idx = idx
                current_trie = current_trie.children[elem]
                if current_trie.value:
                    end_idx = idx + 1
            
            else :
                if start_idx >= 0:
                    if end_idx >= 0:
                        res.append((start_idx, end_idx))
                        idx = end_idx
                    else :
                        idx = start_idx + 1
                    forward = False
                start_idx = -1
                end_idx = -1
                current_trie = self
            
            if forward :
                idx += 1
        if start_idx >= 0 and end_idx >= 0:
                    res.append((start_idx, end_idx))
        return res
    
    def search(self, searched_sequence):
        ranges = self.find(searched_sequence)
        if not ranges :
            return None
        ls = []
        for r in ranges:
            ls.append(searched_sequence[r[0]:r[1]])
        return ls
    
    def get(self, sequence):
        if not sequence :
            return self.value
        else :
            if sequence[0] in self.children :
                return self.children[sequence[0]].get(sequence[1:])
            else :
                raise KeyError
            
    def __contains__(self, sequence):
        try:
            if self.get(sequence):
                return True
            else :
                return False
        except KeyError :
            return False
        
class CountingTrie():
    
    def __init__(self):
        self.trie = Trie()
        
    def add(self, sequence):
        if sequence in self.trie :
            self.trie.add(sequence, self.trie.get(sequence) + 1)
        else :
            self.trie.add(sequence, 1)
            
    def find(self, searched_sequence):
        return self.trie.find(searched_sequence)
    
    def search(self, searched_sequence):
        return self.trie.search(searched_sequence)
    
    def __contains__(self, sequence):
        return sequence in self.trie
    
    def get(self, sequence):
        return self.trie.get(sequence)

    