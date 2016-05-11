# -*- coding: utf-8 -*-

from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime
from pplib.base_model import BaseM

db = SqliteExtDatabase('../data/tatoeba/tatoeba.db')


time_format = '%Y-%m-%d %H:%M:%S'


class BaseModel(Model, BaseM):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)


class Sentence(BaseModel):

    user = CharField(null=True)  # username

    num = IntegerField(primary_key=True)
    lang = FixedCharField(8)
    text = CharField()

    create_time = DateTimeField(default=datetime.datetime.now, null=True)
    modify_time = DateTimeField(default=datetime.datetime.now, null=True)

    def dump_object(self):
        o = dict()
        o['num'] = self.num
        o['text'] = self.text
        o['lang'] = self.lang
        o['user'] = self.user
        o['create_time'] = None
        o['modify_time'] = None
        return o


class UserLanguageLevel(BaseModel):
    user = IntegerField()
    lang = FixedCharField(max_length=8)
    level = IntegerField()


class SentenceRating(BaseModel):
    sentence = IntegerField()
    rating = IntegerField(default=0)


class Link(BaseModel):
    src = IntegerField(primary_key=True)
    dest = IntegerField()

    def dump_object(self):
        o = dict()
        o['src'] = self.src
        o['dest'] = self.dest
        return o


db.connect()


if __name__ == '__main__':
    db.create_tables([User, Sentence, Link, UserLanguageLevel, SentenceRating])

