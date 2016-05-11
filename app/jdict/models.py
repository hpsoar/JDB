# -*- coding: utf-8 -*-

from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
from pplib.base_model import BaseM


db = SqliteExtDatabase('../data/jdict_v1.db')


time_format = '%Y-%m-%d %H:%M:%S'


class BaseModel(Model, BaseM):
    class Meta:
        database = db

    def dict__property(self, k):
        d = self.__dict__['_data']
        return d[k] if k in d else None


class Word(BaseModel):
    text = CharField(primary_key=True)
    kana = CharField()
    romaji = CharField(null=True)
    audio = CharField(null=True)

    translation_key = CharField()  # first alternatives or text

    tags = CharField(null=True)  # ','.join([tag1, tag2])

    kanjis = CharField(null=True)  # ','.join([kanji1, kanji2])
    alternatives = CharField(null=True)  # ','.join([text1, text2])

    def properties_to_dump(self):
        return ['text', 'kana', 'romaji', 'audio', 'translation_key', 'tags', 'kanjis', 'alternatives']


class Kanji(Word):
    pass


class Translation(BaseModel):
    word = CharField()
    text = CharField()
    part_of_speech = CharField(null=True)
    tags = CharField(null=True)  # ','.join([tag1, tag2])
    field_of_application = CharField(null=True)  # ','.join([])

    def properties_to_dump(self):
        return ['word', 'text', 'part_of_speech', 'tags', 'field_of_application']


class Sentence(BaseModel):
    src = CharField()
    dest = CharField()
    audio = CharField(null=True)

    def properties_to_dump(self):
        return ['src', 'dest', 'audio']


class WordSentence(BaseModel):
    word = CharField()  # word text
    sentence = ForeignKeyField(Sentence, "sentence")


db.connect()


def query_words(text):
    print 'query words: %s' % text
    r = Word.select().where(Word.text % text)
    return [w for w in r]


def query_word(text):
    print 'query word: %s' % text
    r = Word.select().where(Word.text == text)
    return [w for w in r]


def query_translations(text):
    print 'query tranlsation: %s' % text
    r = Translation.select().where(Translation.text.contains(text))
    return [t for t in r]


def query_word_translations(text):
    print 'query translations for word: %s' % text
    r = Translation.select().where(Translation.word == text)
    return [t for t in r]


def query_translation_words(text):
    ts = query_translations(text)
    r = list()
    for t in ts:
        ws = query_word(t.word)
        r.extend(ws)
    return r


def print_result(r):
    print str(r)


if __name__ == '__main__':
    import sys
    opt = sys.argv[1]
    if opt == 'create':
        db.create_tables([Word, Kanji, Translation, Sentence, WordSentence])
    elif opt == 'qw':
        text = sys.argv[2]
        print_result(query_words(text))
    elif opt == 'qt':
        text = sys.argv[2]
        print_result(query_translations(text))
    elif opt == 'qwt':
        print_result(query_word_translations(sys.argv[2]))
    elif opt == 'qtw':
        print_result(query_translation_words(sys.argv[2]))




