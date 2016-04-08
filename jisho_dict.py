# -*- coding: utf-8 -*-

import pplib
from bs4 import BeautifulSoup as BS
from word import *

def data_path(path, filename):
    import os
    path = os.path.join('jisho', path)
    return pplib.ff.data_path(path, filename)
    
def parse_audios(bs):
    srcs = list()

    if not bs: return srcs

    audios = bs.find_all('source')

    for a in audios:
        src = a['src']
        if src:
            srcs.append(src)
    return srcs


def parse_content(bs):
    audios = parse_audios(bs)
    meaning_area = bs.find(class_='kanji_light_content')
    
    return content


# extract part match to word meaning
# discard extending information
def except_content(content):
    bs = BS(content)
    concept = bs.find(class_='exact_block')
    return concept

def extract_concept(content):
    content = except_content(content)
    content = parse_content(content)
    print content

def search(word):
    url = 'http://jisho.org/search/%s' % word
    code, content = pplib.uff.download(url)

    path = data_path('sraw', word)

    pplib.ff.save(path, content)

    extract_concept(content)

def query(word):
    url = 'http://jisho.org/word/%s' % word
    print url

    path = data_path('raw', word)
    content = pplib.ff.read(path)

    if content:
        print 'load %s' % path
    else:
        code, content = pplib.uff.download(url)

        if code == 200:
            print 'download succeed'
            pplib.ff.save(path, content)
        else:
            print 'download failed: %d' % code
            return None

    return extract_word_content(BS(content))

def extract_word_file(word):
    path = data_path('raw', word)
    content = pplib.ff.read(path)
    bs = BS(content)

    return extract_word_content(bs)

def extract_word_content(bs):
    word_info = bs.find(class_='concept_light clearfix')
    word = extract_word_info(word_info)

    meanings = bs.find(class_='meanings-wrapper')
    word.meanings = extract_word_meanings(meanings)
    return word

def extract_word_meanings(bs):
    meaning_parts = bs.find_all('div', recursive=False)

    meanings = list()
    tags = None
    for p in meaning_parts:
        if 'meaning-tags' in p['class']:
            tags = p.text
        elif tags:
            m = extract_word_meaning(p, tags)
            meanings.append(m)

    return meanings


def extract_word_meaning(bs, tags):
    m = WordMeaning()
    
    m.tags = tags

    meaning = bs.find(class_='meaning-meaning')
    if meaning:
        m.meaning = meaning.text.strip()
    
    sentences = bs.find(class_='sentences')
    m.sentences = extract_example_sentences(sentences)

    info = bs.find(class_='supplemental_info')
    if info:
        m.info = info.text.strip()
    return m


def extract_example_sentences(bs):
    if not bs: return list()

    sentences = bs.find_all('ul')
    result = list()
    for s in sentences:
        sentence = extract_example_sentence(s)
        if sentence:
            result.append(sentence)
    return result   

def extract_example_sentence(bs):
    lis = bs.find_all('li', class_='clearfix')
    sentence = Sentence()
    for li in lis:
        furigana = li.find(class_='furigana')
        text = li.find(class_='unlinked')
        word = Kanji(text.text.strip())
        if furigana:
            word.furigana = furigana.text.strip()
        sentence.words.append(word)
    li = bs.find(class_='english')
    if li:
        sentence.translation = li.text.strip()
    return sentence


def extract_word_info(bs):
    w = Word()

    # word basic info
    word_part = bs.find(class_='concept_light-representation')
    furigana = word_part.find(class_='furigana')
    text = word_part.find(class_='text')

    w.words = extract_word_kanjis(furigana, text)

    # tags
    extra = bs.find(class_='concept_light-status')
    tags = extra.find_all(class_='concept_light-tag')

    if tags:
        w.tags = [t.text for t in tags]

    # audio
    audio = bs.find('audio')
    w.audios = parse_audios(audio)

    return w


def extract_word_kanjis(furigana, text):
    spans = text.find_all('span')
    for s in spans: s.extract()
    ss = [s.text.strip() for s in spans]
    ss = ''.join(ss)
    kanjis = list(text.text.strip())

    furiganas = list()
    if furigana:
        furiganas =  furigana.find_all('span')
        furiganas = [f.text for f in furiganas if f.text]

    words = list()
    if len(kanjis) != len(furiganas):
        print 'error parsing word: %s%s' % (''.join(kanjis), ss)
        print kanjis
        print furiganas
    else:
        for i in range(len(kanjis)):
            k = Kanji(kanjis[i], furiganas[i])
            words.append(k)
        if ss:
            k = Kanji('', ss)
            words.append(k)
    return words


def parse_raw_file(word):
    path = data_path('raw', word)
    content = pplib.ff.read(path)
    extract_concept(content)


def query_words(words, callback=None):
    error_words_path = data_path('state', 'query_error_words')
    f_error_words = pplib.ff.openfile(error_words_path, 'a')
    error_words_map = load_fail_word_map(error_words_path)

    for w in words:
        print 'query: %s' % w
        if w in error_words_map:
            print 'word `%s` was failed' % w
            if callback: callback(w, None)
            continue

        f = data_path('dict_json', w)
        word = load_word(f)
        if word:
            print 'load: %s' % w
        else:
            word = query(w)
            if word:
                print 'query success: %s' % w
            else:
                print 'query failed: %s' % w
                print >> f_error_words, w

        if word:
            print 'save to: %s' % f
            pplib.ff.save(f, str(word))

        if callback: callback(w, word)

def load_fail_word_map(f):
    r = dict()
    for l in pplib.ff.read_lines(f):
        r[l] = True
    return r


def load_word(f):
    j = pplib.ff.read_json(f)
    if j:
        w = Word()
        w.load_object(j)
        return w
    return None


def test():
    word = '長い'
    #word = '発明'
    #word = '数ヵ月'
    #search(word)
    #parse_raw_file(word)
    #query(word)
    #word = extract_word_file(word)
    w = query(word)
    print w

    print [str(ww) for ww in w.words]
    for m in w.meanings:
        print m
        for s in m.sentences:
            print s

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        load_word(sys.argv[1])
    else:
        test()

