# -*- coding: utf-8 -*-

def format_object(o):
    import json
    return json.dumps(o, indent=4)

class Word(object):
    def __init__(self, text='', furigana=None):
        self.words = list() # [Kanji]
        self.romaji = ''
        self.audios = list() # audio urls
        self.meanings = list() # meanings
        self.tags = list() # common, jlpt level, wanikani level, etc.


    def __unicode__(self):
        return format_object(self.dump_object())


    def __str__(self):
        return unicode(self).encode('utf-8')


    def dump_object(self):
        '''
        '''
        o = self.__dict__.copy()
        o['words'] = Kanji.dump_objects(self.words)
        o['meanings'] = [m.dump_object() for m in self.meanings]
        return o


    def load_json(self, json):
        self.__dict__.update(json)
        self.words = Kanji.load_objects(json['words'])
        self.meanings = WordMeaning.load_objects(json['meanings'])


class Kanji(object):
    def __init__(self, text, furigana=''):
        self.text = text # 如果是假名，就没有text
        self.furigana = furigana


    def __str__(self):
        return unicode(self).encode('utf-8')


    def __unicode__(self):
        return format_object(self.dump_object())


    def dump_object(self):
        return self.__dict__.copy()


    @staticmethod
    def text(kanjis):
        if not kanjis: return ''
        t = [k.text for k in kanjis]
        return ''.join(t)


    @staticmethod
    def furigana(kanjis):
        if not kanjis: return ''
        f = [k.furigana for k in kanjis]
        return ''.join(f)


    @staticmethod
    def dump_objects(kanjis):
        if not kanjis: return list()
        return [k.dump_object() for k in kanjis]


    @staticmethod
    def load_objects(jarray):
        '''
        jarray: json array
        '''
        if not jarray: return list()
        return [Kanji(**j) for j in jarray]


class WordMeaning(object):
    def __init__(self):
        self.tags = ''    # eg. Noun, Suru verb
        self.meaning = '' # eg. invention
        self.info = ''    # Only use in some scenario
        self.sentences = list()  # [Sentence] example sentences


    def __str__(self):
        return unicode(self).encode('utf-8')


    def __unicode__(self):
        return format_object(self.dump_object())


    def dump_object(self):
        o = self.__dict__.copy()
        o['sentences'] = [s.dump_object() for s in self.sentences]
        return o


    def load_object(self, json):
        self.__dict__.update(json)
        self.sentences = Sentence.load_objects(json['sentences'])


    @staticmethod
    def load_object(json):
        m = WordMeaning()
        m.load_object(json)


    @staticmethod
    def load_objects(jarray):
        if not jarray: return list()
        return [WordMeaning.load_object(j) for j in jarray]


class Sentence(object):
    def __init__(self):
        self.words = list() # [Kanji]
        self.translation = '' # translation


    def __unicode__(self):
        return format_object(self.dump_object())


    def __str__(self):
        return unicode(self).encode('utf-8')


    def dump_object(self):
        o = self.__dict__.copy()
        o['words'] = Kanji.dump_objects(self.words)
        return o


    def load_object(self, json):
        self.__dict__.update(json)
        self.words = Kanji.load_objects(json['words'])


    @staticmethod
    def load_object(json):
        s = Sentence()
        s.load_object(json)


    @staticmethod
    def load_objects(jarray):
        if not jarray: return list()
        return [Sentence.load_object(j) for j in jarray]


