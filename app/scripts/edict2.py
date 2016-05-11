# -*- coding: utf-8 -*-
import pplib
from pplib.base_model import BaseM
import copy
from jdict import models

markings = ['(X)', '(abbr)', '(arch)', '(ateji)', '(chn)', '(col)', '(derog)', '(eK)', '(ek)', '(fam)', '(fem)', '(gikun)', '(hon)', '(hum)', '(ik)', '(iK)', '(id)', '(io)', '(m-sl)', '(male)', '(male-sl)', '(oK)', '(obs)', '(obsc)', '(ok)', '(on-mim)', '(poet)', '(pol)', '(rare)', '(sens)', '(sl)', '(uK)', '(uk)', '(vulg)']


def parse_tags(text):
    parts = text.split('(')
    text = parts[0]
    parts = parts[1:]
    tags = [p.replace(')', '').strip() for p in parts]
    return text, tags


class Kana(BaseM):
    def __init__(self, kana):
        self.kana = kana
        self.parse_tags()

    def parse_tags(self):
        self.kana, self.tags = parse_tags(self.kana)


class Meaning(BaseM):
    @staticmethod
    def parse(raw_meanings):

        if not raw_meanings: return list()
    
        m = None
        result = list()
        num = 1
        num_str = '(1)'
        for c in raw_meanings:
            if not m or num_str in c:
                m = Meaning.parse_one_meaning(c, num_str)
                result.append(m)

                num += 1
                num_str = '(%d)' % num
            else:
                if c != '(P)':
                    m.glosses.append(c)
        return result

    @staticmethod
    def parse_one_meaning(comp, num = None):
        # (poses) (1) (uk) {food} (pun on ...) (See ...)
        import re
        reg_mark = re.compile('^\((\S*)\)')
        m = reg_mark.search(comp)
        if not m:
            print '-'*80
            print 'error'
            return None

        poses = m.group(1).split(',')
        
        # strip poses
        comp = comp.replace(m.group(0), '').strip()
        
        # strip (1)
        if comp.startswith(num):
            comp = comp.replace(num, '').strip()

        # strip (ui), etc.
        tags = list()
        for m in markings:
            if m in comp:
                comp = comp.replace(m, '')
                tags.append(m.replace('(', '').replace(')', ''))
        comp = comp.strip()

        # strip {food}
        reg_foa = re.compile('^\{(\S*)\}')
        m = reg_foa.search(comp)
        foas = list()
        if m:
            foas = m.group(1).split(',')
            comp = comp.replace(m.group(0), '').strip()

        gloss = comp

        meaning = Meaning()
        meaning.poses = poses
        meaning.glosses.append(gloss)
        meaning.tags = tags
        meaning.foas = foas

        return meaning

    def __init__(self):
        self.poses = list()  # [part of speech]
        self.glosses = list() # [gloss]
        self.tags = list() # [marking
        self.foas = list() # [field of application]


class RawWord(BaseM):
    def __init__(self):
        self.text = ''
        self.kanas = list()
        self.meanings = list()
        self.seq_num = ''
        self.tags = list()
        self.alternatives = list()

    def dump_object(self):
        o = copy.deepcopy(self.__dict__)
        o['kanas'] = [k.dump_object() for k in self.kanas]
        o['meanings'] = [m.dump_object() for m in self.meanings]
        o['alternatives'] = [w.dump_object() for w in self.alternatives]
        return o

    def parse_alternatives(self):
        if ';' in self.text:
            parts = self.text.split(';')
            self.alternatives = [self.splited_word(p) for p in parts]
        else:
            self.parse_tags()

    def splited_word(self, text):
        w = RawWord()
        w.__dict__.update(copy.deepcopy(self.__dict__))
        w.text = text
        w.parse_tags()
        w.clean_kanas()
        return w

    def clean_kanas(self):
        result = list()
        # iter all kanas and their tags
        for k in self.kanas:
            if not k.tags:
                result.append(k)
                continue

            for t in k.tags:
                if ',' in t: # if tag contains ','
                    parts = t.split(',')
                    if self.text in parts:
                        k.tags.remove(t) # remove the tag
                        result.append(k) # add the kana
                        break

        self.kanas = result

    def parse_tags(self):
        self.text, self.tags = parse_tags(self.text)

    def parse_text_kanas(self, content):
        parts = content.split('[')
        if len(parts) == 1:
            parts = content.split(';')

        self.text = parts[0]

        if len(parts) > 1:
            kanas = parts[1].replace(']', '').split(';')
            self.kanas = [Kana(k) for k in kanas]
        self.parse_alternatives()

    def parse_meanings(self, comps):
        if comps:
            self.meanings = Meaning.parse(comps)


class Edict2(object):
    def __init__(self):
        self.words = list()

    def load(self, filename):
        print 'load: %s' % filename
        count = 0
        for line in open(filename):
            count += 1
            if count == 1:
                continue

            comps = line.split('/')
            comps = [c for c in comps if c.strip()]

            w = RawWord()
            w.seq_num = comps[-1]
            w.parse_text_kanas(comps[0])
            w.parse_meanings(comps[1: -1])

            self.words.append(w)
            #print comps
            #print comps[1:-1]

            #if count > 20: break

    def log(self):
        def p(w):
            print w
        self.enumerate(p)

    def enumerate(self, f):
        for w in self.words:
            if w.alternatives:
                for a in w.alternatives:
                    f(a)
            else:
                f(w)

    def import_to_db(self):
        for w in self.words:
            self.import_word(w)

    def import_words(self, words):
        translation_key = None
        alternatives = ''
        if len(words) > 1:
            alternatives = [w.text for w in words]

        for w in words:
            if not translation_key:
                translation_key = w.text
            kanas = [k.kana for k in w.kanas]
            db_word = models.Word(text=w.text, kana=','.join(kanas), tags=','.join(w.tags))
            db_word.translation_key = translation_key
            db_word.alternatives = alternatives
            db_word.tags = ','.join(w.tags)
            try:
                db_word.save(force_insert=True)
            except Exception, ex:
                print ex
                print w
        return translation_key

    count = 0
    def import_word(self, w):
        translation_key = self.import_words(w.alternatives or [w])

        for m in w.meanings:
            db_translation = models.Translation(word=translation_key, text=','.join(m.glosses))
            db_translation.part_of_speech = ','.join(m.poses)
            db_translation.tags = ','.join(m.tags)
            db_translation.field_of_application = ','.join(m.foas)
            try:
                db_translation.save(force_insert=True)
            except Exception, ex:
                print ex
                print w
                print db_translation

#        Edict2.count += 1
#        if Edict2.count > 10:
#            import sys
#            sys.exit(0)

    def import_word_with_alternatives(self, w):
        pass

    def inspect_data(self):
        print 'total: %d' % len(self.words)

        def count_word(w):
            count_word.count += 1

        count_word.count = 0
        self.enumerate(count_word)
        print 'total with alternatives: %d' % count_word.count

        def inspect_kana(w):
            if len(w.kanas) > 1:
                inspect_kana.count += 1
                print w
        inspect_kana.count = 0
        self.enumerate(inspect_kana)
        print 'words with multiple kana: %d' % inspect_kana.count


if __name__ == '__main__':
    import sys
    edict2 = Edict2()
    f = '../data/edict2_utf8'
    if len(sys.argv) > 1:
        f = sys.argv[1]
    edict2.load(f)
    #edict2.inspect_data()
    edict2.import_to_db()

