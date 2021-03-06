
import os
import pandas as pd
import numpy as np
import requests
import time
import re

# ---------------------------------------------------------------------
# Question #1
# ---------------------------------------------------------------------

def get_book(url):
    """
    get_book that takes in the url of a 'Plain Text UTF-8' book and 
    returns a string containing the contents of the book.

    The function should satisfy the following conditions:
        - The contents of the book consist of everything between 
        Project Gutenberg's START and END comments.
        - The contents will include title/author/table of contents.
        - You should also transform any Windows new-lines (\r\n) with 
        standard new-lines (\n).
        - If the function is called twice in succession, it should not 
        violate the robots.txt policy.

    :Example: (note '\n' don't need to be escaped in notebooks!)
    >>> url = 'http://www.gutenberg.org/files/57988/57988-0.txt'
    >>> book_string = get_book(url)
    >>> book_string[:20] == '\\n\\n\\n\\n\\nProduced by Chu'
    True
    """
    s = requests.get(url).text
    s1 = re.search("\*\*\* START[^\*]+\*\*\*((.|\n)+)\*\*\* END[^\*]+\*\*\*", s).group(1)
    s2 = s1.replace("\r\n", "\n")
    time.sleep(5)
    return s2
    
# ---------------------------------------------------------------------
# Question #2
# ---------------------------------------------------------------------

def tokenize(book_string):
    """
    tokenize takes in book_string and outputs a list of tokens 
    satisfying the following conditions:
        - The start of any paragraph should be represented in the 
        list with the single character \x02 (standing for START).
        - The end of any paragraph should be represented in the list 
        with the single character \x03 (standing for STOP).
        - Tokens in the sequence of words are split 
        apart at 'word boundaries' (see the regex lecture).
        - Tokens should include no whitespace.

    :Example:
    >>> test_fp = os.path.join('data', 'test.txt')
    >>> test = open(test_fp, encoding='utf-8').read()
    >>> tokens = tokenize(test)
    >>> tokens[0] == '\x02'
    True
    >>> tokens[9] == 'dead'
    True
    >>> sum([x == '\x03' for x in tokens]) == 4
    True
    >>> '(' in tokens
    True
    """
    book_string = book_string.strip()
    ss2 = re.split("\\b", re.sub("\n{2,}", " x03 x02 ", book_string))
    ss3 = ["\x02"] + ss2 + ["\x03"]
    pattern = "\A\s*\Z"
    prog = re.compile(pattern)
    list3 = list(filter(lambda x: prog.search(x) is None, ss3))
    list4 = pd.Series(list3).str.strip(" ").replace({"x02":"\x02", "x03":"\x03"}).tolist()

    return list4
    
# ---------------------------------------------------------------------
# Question #3
# ---------------------------------------------------------------------


class UniformLM(object):
    """
    Uniform Language Model class.
    """

    def __init__(self, tokens):
        """
        Initializes a Uniform languange model using a
        list of tokens. It trains the language model
        using `train` and saves it to an attribute
        self.mdl.
        """
        self.mdl = self.train(tokens)
        
    def train(self, tokens):
        """
        Trains a uniform language model given a list of tokens.
        The output is a series indexed on distinct tokens, and
        values giving the (uniform) probability of a token occuring
        in the language.

        :Example:
        >>> tokens = tuple('one one two three one two four'.split())
        >>> unif = UniformLM(tokens)
        >>> isinstance(unif.mdl, pd.Series)
        True
        >>> set(unif.mdl.index) == set('one two three four'.split())
        True
        >>> (unif.mdl == 0.25).all()
        True
        """
        arr1 = list(pd.Series(tokens).unique())
        arr2 = [1/len(arr1) for _ in range(len(arr1))]
        
        return pd.Series(dict(zip(arr1, arr2)))
    
    def probability(self, words):
        """
        probability gives the probabiliy a sequence of words
        appears under the language model.
        :param: words: a tuple of tokens
        :returns: the probability `words` appears under the language
        model.

        :Example:
        >>> tokens = tuple('one one two three one two four'.split())
        >>> unif = UniformLM(tokens)
        >>> unif.probability(('five',))
        0
        >>> unif.probability(('one', 'two')) == 0.0625
        True
        """
        result = 1
        for word in words:
            if word not in list(self.mdl.index):
                return 0
            else:
                result = result * self.mdl[word]
        return result
        
    def sample(self, M):
        """
        sample selects tokens from the language model of length M, returning
        a string of tokens.

        :Example:
        >>> tokens = tuple('one one two three one two four'.split())
        >>> unif = UniformLM(tokens)
        >>> samp = unif.sample(1000)
        >>> isinstance(samp, str)
        True
        >>> len(samp.split()) == 1000
        True
        >>> s = pd.Series(samp.split()).value_counts(normalize=True)
        >>> np.isclose(s, 0.25, atol=0.05).all()
        True
        """
        string = ""
        for i in range(M):
            string = string + " " + np.random.choice(np.array(self.mdl.index))
        return string

            
# ---------------------------------------------------------------------
# Question #4
# ---------------------------------------------------------------------


class UnigramLM(object):
    
    def __init__(self, tokens):
        """
        Initializes a Unigram languange model using a
        list of tokens. It trains the language model
        using `train` and saves it to an attribute
        self.mdl.
        """
        self.mdl = self.train(tokens)
    
    def train(self, tokens):
        """
        Trains a unigram language model given a list of tokens.
        The output is a series indexed on distinct tokens, and
        values giving the probability of a token occuring
        in the language.

        :Example:
        >>> tokens = tuple('one one two three one two four'.split())
        >>> unig = UnigramLM(tokens)
        >>> isinstance(unig.mdl, pd.Series)
        True
        >>> set(unig.mdl.index) == set('one two three four'.split())
        True
        >>> unig.mdl.loc['one'] == 3 / 7
        True
        """
        lst = list(pd.Series(tokens).unique())
        num_occurrence = [tokens.count(word) for word in lst]
        freq = [x / len(tokens) for x in num_occurrence]
        
        return pd.Series(dict(zip(lst, freq)))
    
    def probability(self, words):
        """
        probability gives the probabiliy a sequence of words
        appears under the language model.
        :param: words: a tuple of tokens
        :returns: the probability `words` appears under the language
        model.

        :Example:
        >>> tokens = tuple('one one two three one two four'.split())
        >>> unig = UnigramLM(tokens)
        >>> unig.probability(('five',))
        0
        >>> p = unig.probability(('one', 'two'))
        >>> np.isclose(p, 0.12244897959, atol=0.0001)
        True
        """
        result = 1
        for word in words:
            if word not in list(self.mdl.index):
                return 0
            else:
                result = result * self.mdl[word]
        return result
        
    def sample(self, M):
        """
        sample selects tokens from the language model of length M, returning
        a string of tokens.

        >>> tokens = tuple('one one two three one two four'.split())
        >>> unig = UnigramLM(tokens)
        >>> samp = unig.sample(1000)
        >>> isinstance(samp, str)
        True
        >>> len(samp.split()) == 1000
        True
        >>> s = pd.Series(samp.split()).value_counts(normalize=True).loc['one']
        >>> np.isclose(s, 0.41, atol=0.05).all()
        True
        """

        words = np.array(self.mdl.index)
        prob = np.array(self.mdl.values)
        string = " ".join(np.random.choice(words, p=prob, size = M))
        return string
        

# ---------------------------------------------------------------------
# Question #5,6,7,8
# ---------------------------------------------------------------------

class NGramLM(object):
    
    def __init__(self, N, tokens):
        """
        Initializes a N-gram languange model using a
        list of tokens. It trains the language model
        using `train` and saves it to an attribute
        self.mdl.
        """
        self.k = 5
        self.N = N
        ngrams = self.create_ngrams(tokens)

        self.ngrams = ngrams
        self.mdl = self.train(ngrams)

        if N < 2:
            raise Exception('N must be greater than 1')
        elif N == 2:
            self.prev_mdl = UnigramLM(tokens)
        else:
            mdl = NGramLM(N-1, tokens)
            self.prev_mdl = mdl

    def create_ngrams(self, tokens):
        """
        create_ngrams takes in a list of tokens and returns a list of N-grams. 
        The START/STOP tokens in the N-grams should be handled as 
        explained in the notebook.

        :Example:
        >>> tokens = tuple('\x02 one two three one four \x03'.split())
        >>> bigrams = NGramLM(2, [])
        >>> out = bigrams.create_ngrams(tokens)
        >>> isinstance(out[0], tuple)
        True
        >>> out[0]
        ('\\x02', 'one')
        >>> out[2]
        ('two', 'three')
        """
        
        nGrams = []
        loop = len(tokens)-self.N+1
        for i in range(loop):
            lst = []
            for j in range(self.N):
                lst.append(tokens[i+j])
            tup = tuple(lst)
            nGrams.append(tup)

        return nGrams
        
    def train(self, ngrams):
        """
        Trains a n-gram language model given a list of tokens.
        The output is a dataframe with three columns (ngram, n1gram, prob).

        :Example:
        >>> tokens = tuple('\x02 one two three one four \x03'.split())
        >>> bigrams = NGramLM(2, tokens)
        >>> set(bigrams.mdl.columns) == set('ngram n1gram prob'.split())
        True
        >>> bigrams.mdl.shape == (6, 3)
        True
        >>> bigrams.mdl['prob'].min() == 0.5
        True
        """

        # ngram counts C(w_1, ..., w_n)
        ...
        # n-1 gram counts C(w_1, ..., w_(n-1))
        ...

        # Create the conditional probabilities
        ...
        
        # Put it all together
        out = self.ngrams
        df = pd.DataFrame()
        df["ngram"] = out
        df["n1gram"] = df["ngram"].apply(lambda x: x[:-1])
        helper1 = df["ngram"].value_counts().to_frame().rename(columns = {"ngram":"count_ngram"})
        helper2 = df["n1gram"].value_counts().to_frame().rename(columns = {"n1gram":"count_n1gram"})
        df1 = pd.merge(df, helper1, how = "left", left_on = "ngram", right_index = True)
        df2 = pd.merge(df1, helper2, how = "left", left_on = "n1gram", right_index = True)
        df2["prob"] = df2["count_ngram"]/df2["count_n1gram"]
        df3 = df2.drop(columns = ["count_ngram", "count_n1gram"])
        
        return df3.drop_duplicates()
    
    def probability(self, words):
        """
        probability gives the probabiliy a sequence of words
        appears under the language model.
        :param: words: a tuple of tokens
        :returns: the probability `words` appears under the language
        model.

        :Example:
        >>> tokens = tuple('\x02 one two one three one two \x03'.split())
        >>> bigrams = NGramLM(2, tokens)
        >>> p = bigrams.probability('two one three'.split())
        >>> np.isclose(p, (1/4)*(1/2)*(1/3))
        True
        >>> bigrams.probability('one two five'.split()) == 0
        True
        """

        idx = len(words)

        def _help(curr, idx):
            if idx <= 0:
                return 1
            while idx < curr.N:
                curr = curr.prev_mdl
                if isinstance(curr, UnigramLM):
                    break
            table = curr.mdl
            _probability = 0
            if idx == 1:
                if words[0] not in table.index:
                    _probability = 0
                else:
                    _probability = table[words[0]]
            else:
                if (table["ngram"] == tuple(words[idx-curr.N:idx])).sum() == 0:
                    _probability = 0
                else:
                    _probability = table[(table["ngram"] == tuple(words[idx-curr.N:idx])) & (table["n1gram"] == tuple(words[idx-curr.N:idx-1]))]["prob"].iloc[0]
            
            return  _probability * _help(curr, idx - 1)

        probability =  _help(self, idx)

        return probability


    def sample(self, M):
        """
        sample selects tokens from the language model of length M, returning
        a string of tokens.

        :Example:
        >>> tokens = tuple('\x02 one two three one four \x03'.split())
        >>> bigrams = NGramLM(2, tokens)
        >>> samp = bigrams.sample(3)
        >>> len(samp.split()) == 4  # don't count the initial START token.
        True
        >>> samp[:2] == '\\x02 '
        True
        >>> set(samp.split()) <= {'\\x02', '\\x03', 'one', 'two', 'three', 'four'}
        True
        """
        output = []
        counter = 1
        
        self_ngrams = self.ngrams

        def findModel(currModel, targetNum):
            while currModel.N > targetNum:
                currModel = currModel.prev_mdl
                if isinstance(currModel, UnigramLM):
                    break
            return currModel

        while counter <= M:
            if counter == 1:
                curr_mdl = self.mdl
                # Make the model bigram
                model = findModel(self, 1).mdl 
                output.append(np.random.choice(list(model.index), p = list(model.values)))
                
            else:
                if counter >= self.N:
                    model = self.mdl
                else:
                    model = findModel(self, counter).mdl

                prior_words = tuple(output[-self.N+1:])
                
                # change the tuple into string
                pri_word = prior_words[-1:]
                
                
                values = model["n1gram"].apply(lambda x: x[0]).values
                # check if we have more tokens
                if pri_word not in values:
                    # if not, end with '\x03'
                    output.append('\x03')
                else:
                    # if have tokens, sample it with condition
                    df = model[model["n1gram"] == tuple(output[-self.N+1:])]
                    next_word = np.random.choice(list(df["ngram"].apply(lambda x: x[-1])), p = df["prob"].values)
                    output.append(next_word)
            counter = counter + 1
        
        string =  '\x02 '
        for word in output:
            string = string + str(word) + ' '
           
        return string[:-1]

    def sampleChinese(self, M):
        """
        sample selects tokens from the language model of length M, returning
        a string of tokens.

        :Example:
        >>> tokens = tuple('\x02 one two three one four \x03'.split())
        >>> bigrams = NGramLM(2, tokens)
        >>> samp = bigrams.sample(3)
        >>> len(samp.split()) == 4  # don't count the initial START token.
        True
        >>> samp[:2] == '\\x02 '
        True
        >>> set(samp.split()) <= {'\\x02', '\\x03', 'one', 'two', 'three', 'four'}
        True
        """
        output = []
        counter = 1
        
        self_ngrams = self.ngrams

        def findModel(currModel, targetNum):
            while currModel.N > targetNum:
                currModel = currModel.prev_mdl
                if isinstance(currModel, UnigramLM):
                    break
            return currModel

        while counter <= M:
            if counter == 1:
                curr_mdl = self.mdl
                # Make the model bigram
                model = findModel(self, 1).mdl 
                output.append(np.random.choice(list(model.index), p = list(model.values)))
                
            else:
                if counter >= self.N:
                    model = self.mdl
                else:
                    model = findModel(self, counter).mdl

                prior_words = tuple(output[-self.N+1:])
                
                # change the tuple into string
                pri_word = prior_words[-1:]
                
                
                values = model["n1gram"].apply(lambda x: x[0]).values
                # check if we have more tokens
                if pri_word not in values:
                    # if not, end with '\x03'
                    output.append('\x03')
                else:
                    # if have tokens, sample it with condition
                    df = model[model["n1gram"] == tuple(output[-self.N+1:])]
                    next_word = np.random.choice(list(df["ngram"].apply(lambda x: x[-1])), p = df["prob"].values)
                    output.append(next_word)
            counter = counter + 1
        
        string =  '\x02 '
        for word in output:
            string = string + str(word) + ''
           
        return string[:-1]
        



        
        # Transform the tokens to strings
        


# ---------------------------------------------------------------------
# DO NOT TOUCH BELOW THIS LINE
# IT'S FOR YOUR OWN BENEFIT!
# ---------------------------------------------------------------------


# Graded functions names! DO NOT CHANGE!
# This dictionary provides your doctests with
# a check that all of the questions being graded
# exist in your code!

GRADED_FUNCTIONS = {
    'q01': ['get_book'],
    'q02': ['tokenize'],
    'q03': ['UniformLM'],
    'q04': ['UnigramLM'],
    'q05': ['NGramLM']
}


def check_for_graded_elements():
    """
    >>> check_for_graded_elements()
    True
    """
    
    for q, elts in GRADED_FUNCTIONS.items():
        for elt in elts:
            if elt not in globals():
                stmt = "YOU CHANGED A QUESTION THAT SHOULDN'T CHANGE! \
                In %s, part %s is missing" %(q, elt)
                raise Exception(stmt)

    return True
