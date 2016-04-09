# -*- coding: utf-8 -*-

import pplib
from pplib.base_model import BaseM
import jisho_dict as jisho

class JLPTGrammar(BaseM):
    def __init__(self, text):
        self.text = text


class WordFreq(BaseM):
    def __init__(self, text, freq):
        self.text = text
        self.freq = freq


class JLPTWord(BaseM):
    def __init__(self, text, kana=None, en = None):
        self.text = text or kana
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


    def words(self):
        return [w.text for w in self.wordlist]


    def dump_object(self):
        o = dict()
        o['wordlist'] = [w.dump_object() for w in self.wordlist]
        o['wordmap'] = [{ k: w.dump_object() } for (k, w) in self.wordmap.items()]
        return o


def parse_wordlist(f, parser, skip=1):
    r = WordList()
    for l in open(f):
        print l
        if skip:
            skip -= 1
        else:
            parts = tuple([w.strip() for w in l.strip().split('\t')])
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
        print parts
        return JLPTWord(*parts)
    return parse_wordlist(f, parser, 3)


def load_school_kanjis(f):
    return load_news_freq_words(f)


def load_word_freq(f):
    def parser(parts):
        return WordFreq(*parts)
    return parse_wordlist(f, parser, 0)


def load_failure_words(f):
    def parser(parts):
        return JLPTWord(*parts)
    return parse_wordlist(f, parser, 0)


def jlpt_path(f):
    import os
    return os.path.join('data/jlpt/txt', f)


def query_jlpt_words():
    print 'query jlpt vocabulary'
    for i in range(5):
        f = jlpt_path('vocabulary-n%d.txt' % (i + 1))
        print f
        wl = load_jlpt_words(f)
        query_words(wl.words())


def query_jlpt_kanjis():
    print 'query jlpt kanji'
    for i in range(5):
        f = jlpt_path('kanji-n%d.txt' % (i+1))
        print f
        wl = load_jlpt_kanjis(f)
        query_words(wl.words())


def query_school_kanjis():
    print 'query school kanji'
    f = jlpt_path('school_jlpt_n3_kanji.txt')
    print f
    wl = load_school_kanjis(f)
    query_words(wl.words())


def query_news_words():
    print 'query news words'
    f = jlpt_path('news_jlpt_n3_vocabulary.txt')
    print f
    wl = load_news_freq_words(f)
    query_words(wl.words())


def query_failure_words():
    print 'query failure words'
    f = 'data/jisho/state/query_error_words'
    print f
    wl = load_failure_words(f)
    query_words(wl.words())


def query_words(words):
    def task():
        def callback(w, word):
            task.count += 1
            print task.count

        remain_words = words[task.count:]
        print 'query %d words' % len(remain_words)
        jisho.query_words(remain_words, callback, query_words.wait, query_words.ignore_failed)

    print 'hello'
    task.count = 0

    pplib.task.schedule(task)


if __name__ == '__main__':
    query_words.wait = 0.02
    query_words.ignore_failed = True
    import sys
    if len(sys.argv) > 1:
        query_words.wait = float(sys.argv[1])
    if len(sys.argv) > 2:
        query_words.ignore_failed = False

    #query_jlpt_words()
    #query_jlpt_kanjis()
    #query_school_kanjis()
    #query_news_words()
    query_failure_words()

