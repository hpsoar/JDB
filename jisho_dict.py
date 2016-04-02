# -*- coding: utf-8 -*-

import pplib
from bs4 import BeautifulSoup as BS

class Word(object):
    def __init__(self, text='', furigana=None):
        self.text = text

        self.furigana = furigana

        self.audios = list()

        self.meanings = list()

        self.tags = list()

    def __unicode__(self):
        parts = list()
        parts.append('%s, %s' % (self.text, self.furigana))

        if self.audios:
            parts.append(str(self.audios))

        if self.meanings:
            parts.append('\nmeaning\n'.join([unicode(m) for m in self.meanings]))

        if self.tags:
            parts.append(str(self.tags))

        return '\n'.join(parts)

    def __str__(self):
        return unicode(self).encode('utf-8')

class WordMeaning(object):
    def __init__(self):
        self.tags = ''
        self.meaning = ''
        self.info = ''
        self.sentences = list()

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        parts = list()
        if self.tags:
            parts.append(self.tags)

        parts.append(self.meaning)

        if self.info:
            parts.append(self.info)

        if self.sentences:
            parts.append('\n'.join([unicode(s) for s in self.sentences]))

        return '\n'.join(parts)

class Sentence(object):
    def __init__(self):
        self.words = list()
        self.translation = ''

    def __unicode__(self):
        parts = list()
        for w in self.words:
            parts.append(w.text)
            if w.furigana:
                parts.append('(%s)' % w.furigana)

        #parts.append('。')
        line = ''.join(parts)

        if self.translation:
            line = '\n'.join([line, self.translation])

        return line

    def __str__(self):
        return unicode(self).encode('utf-8')

def data_path(path, filename):
    import os
    path = os.path.join('jisho', path)
    return pplib.ff.data_path(path, filename)
    
def parse_audios(bs):
    audios = bs.find('source')

    srcs = list()
    for a in audios:
        src = a['src']
        if src:
            srcs.append(srcs)
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
    code, content = pplib.uff.download(url)

    if code != 200:
        print 'download failed: %d' % code
        return None

    path = data_path('raw', word)
    pplib.ff.save(path, content)

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
        word = Word(text.text.strip())
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
    kanji = word_part.find(class_='kanji-2-up kanji')
    text = word_part.find(class_='text')

    if text:
        w.text = text.text.strip()
    
    if kanji:
        w.furigana = kanji.text.strip()

    # tags
    extra = bs.find(class_='concept_light-status')
    tags = extra.find_all(class_='concept_light-tag')

    if tags:
        w.tags = [t.text for t in tags]

    # audio
    audio = bs.find('audio')
    if audio:
        sources = audio.find('source')
        w.audios = [s['src'] for s in sources]

    return w


def parse_raw_file(word):
    path = data_path('raw', word)
    content = pplib.ff.read(path)
    extract_concept(content)

if __name__ == '__main__':
    word = '長い'
    word = '数ヵ月'
    #search(word)
    #parse_raw_file(word)
    #query(word)
    #word = extract_word_file(word)
    print query(word)

