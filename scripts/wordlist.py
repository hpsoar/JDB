# -*- coding: utf-8 -*-

import pplib
from pplib.base_model import BaseM


class JLPTGrammar(BaseM):
    def __init__(self, text):
        self.text = text


class WordFreq(BaseM):
    def __init__(self, text, freq):
        self.text = text
        self.freq = freq


class JLPTWord(BaseM):
    def __init__(self, text, kana=None, en = None):
        self.text = text
        self.kana = kana
        self.en = en


class JLPTKanji(BaseM):
    def __init__(self, text, on=None, kun=None, en=None):
        self.text = text
        self.on = on
        self.kun = kun
        self.en = en


class WordList(BaseM):
    def __init__(self):
        self.wordlist = list()
        self.wordmap = dict()


    def add(self, w):
        self.wordlist.append(w)
        self.wordmap[w.text] = w


    def dump_object(self):
        o = dict()
        o['wordlist'] = [w.dump_object() for w in self.wordlist]
        o['wordmap'] = [{ k: w.dump_object() } for (k, w) in self.wordmap.items()]
        return o


def parse_wordlist(f, parser, skip=1):
    r = WordList()
    for l in open(f):
        if skip:
            skip -= 1
        else:
            parts = tuple(l.strip().split('\t'))
            r.add(parser(parts))
    return r


def load_jlpt_words(f):
    def parser(parts):
        return JLPTWord(*parts)
    return parse_wordlist(f, parser)

    
def load_jlpt_kanjis(f):
    def parser(parts):
        return JLPTKanji(*parts)
    return parse_wordlist(f, parser)


def load_jlpt_grammars(f):
    def parser(parts):
        return JLPTGrammar(*parts)
    return parse_wordlist(f, parser)


def load_news_freq_words(f):
    def parser(parts):
        return JLPTWord(*parts)
    return parse_wordlist(f, parser, 3)


def load_word_freq(f):
    def parser(parts):
        return WordFreq(*parts)
    return parse_wordlist(f, parser, 0)


def load_school_kanji(f):
    return load_news_freq_words(f)


if __name__ == '__main__':
    pass

