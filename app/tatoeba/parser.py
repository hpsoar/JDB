# -*- coding: utf-8 -*-

import pplib
from pplib.base_model import BaseM, classproperty
import models
from datetime import datetime

# jpn, cmn, eng


def data_path(path, filename):
    import os
    path = os.path.join('tatoeba', path)
    return pplib.ff.data_path(path, filename)


class SentenceParser(object):

    @classmethod
    def parse(cls, num=None, lang='', text='', user='', create_time=None, modify_time=None):
        create_time = cls.parse_time(create_time)
        modify_time = cls.parse_time(modify_time)
        return models.Sentence(user=user, num=num, lang=lang, text=text, create_time=create_time, modify_time=modify_time)

    @classmethod
    def parse_time(cls, time_str):
        try:
            if time_str != '\\N':
                time_format = '%Y-%m-%d %H:%M:%S'
                return datetime.strptime(time_str, time_format)
            else:
                return None
        except Exception, ex:
            print ex
            return None

    @classmethod
    def load(cls, filename, store_raw_data=False):
        print 'load: %s' % filename
        if 'sentences' not in cls.__dict__:
            cls.sentences = list()
            cls.sentence_map = dict()

        def parser(line, parts):
            #print parts
            s = cls.parse(*parts)
            if store_raw_data:
                cls.sentence_map[s.num] = line
            else:
                cls.sentences.append(s)
                cls.sentence_map[s.num] = s

        pplib.ff.enum_lines2(filename, parser)

    @classmethod
    def sentence(cls, num):
        return cls.sentence_map[num]

    @classmethod
    def sentence_at(cls, i):
        return cls.sentences[i]

    @classproperty
    def n_sentences(cls):
        return len(cls.sentences)


class LinkParser(BaseM):
    @classmethod
    def parse(cls, origin, translation):
        return models.Link(src=origin, dest=translation)

    @classmethod
    def load(cls, filename, filter_func=None):
        print 'load: %s' % filename

        link_map = dict()  # src -> link
        links = list()

        def parser(line, parts):
            #print parts
            if filter_func and filter_func(*parts):
                return
            l = cls.parse(*parts)
            if l.src not in link_map:
                link_map[l.src] = list()

            link_map[l.src].append(l)
            links.append(l)

        pplib.ff.enum_lines2(filename, parser)
        cls.link_map = link_map
        cls.links = links

    @classmethod
    def link(cls, src):
        return cls.link_map[src]


def sentence_path(lang):
    return pplib.ff.data_path('tatoeba', '%s_sentences.csv' % lang)


def bilingual_path(src_lang, dest_lang, name):
    langs = [src_lang, dest_lang]
    langs = sorted(langs)

    return pplib.ff.data_path('tatoeba', '%s_%s_%s.csv' % (langs[0], langs[1], name))


def link_path(src_lang, dest_lang):
    return bilingual_path(src_lang, dest_lang, 'links')


def merged_setence_path(src_lang, dest_lang):
    return bilingual_path(src_lang, dest_lang, 'sentences')


def link_filter(src, dest):
    return src not in SentenceParser.sentence_map or dest not in SentenceParser.sentence_map


def split_link(src_lang, dest_lang):
    load_sentences(src_lang, dest_lang)

    ff = open(link_path(src_lang, dest_lang), 'w')

    def parser(line, parts):
        if link_filter(*parts):
            return
        ff.write(line)

    all_links = pplib.ff.data_path('tatoeba', 'links.csv')
    pplib.ff.enum_lines2(all_links, parser)


def merge_sentences(src_lang, dest_lang):
    load_sentences(src_lang, dest_lang, raw=True)

    f = open(merged_setence_path(src_lang, dest_lang), 'w')

    def parser(line, parts):
        src, _ = parts
        s = SentenceParser.sentence(src)
        f.write(s)

    pplib.ff.enum_lines2(link_path(src_lang, dest_lang), parser)


def load_sentences(src_lang, dest_lang, raw=False):
    src_path = sentence_path(src_lang)
    dest_path = sentence_path(dest_lang)

    SentenceParser.load(src_path, store_raw_data=raw)
    SentenceParser.load(dest_path, store_raw_data=raw)


def import_data(src_lang, dest_lang):
    SentenceParser.load(merged_setence_path(src_lang, dest_lang))

    LinkParser.load(link_path(src_lang, dest_lang), link_filter)

    print 'save sentences'
    for s in SentenceParser.sentences:
        s.save()

    print 'save links'
    for l in LinkParser.links:
        l.save()


if __name__ == '__main__':
    import sys
    pplib.ff.data_root = '../../data'

    opt = 'i'
    src_lang = 'jpn'
    dest_lang = 'eng'
    if len(sys.argv) > 1:
        opt = sys.argv[1]

    if len(sys.argv) > 3:
        src_lang = sys.argv[2]
        dest_lang = sys.argv[3]

    '''
    0. split sentences:
        bash extract_sentence_by_lang.sh
        eg. extract jpn_sentences.csv to eng_sentences.csv
    1. split_links:
        eg. eng_jpn_links.csv contains only links between eng & jpn sentences
    2. merge_sentences:
        eg. jpn_sentences.csv and eng_sentences.csv to eng_jpn_sentences.csv referring eng_jpn_links.csv
            so, only eng & jpn sentences with entry in eng_jpn_link.csv are reserved
    3. import_data
        import eng_jpn_links.csv & eng_jpn_sentences.csv
    '''

    if opt == 's':
        split_link(src_lang, dest_lang)
    elif opt == 'm':
        merge_sentences(src_lang, dest_lang)
    elif opt == 'i':
        import_data(src_lang, dest_lang)





