# -*- coding: utf-8 -*-
import pplib
from pplib.base_model import BaseM
import copy

markings = [ '(X)', '(abbr)', '(arch)', '(ateji)', '(chn)', '(col)', '(derog)', '(eK)', '(ek)', '(fam)', '(fem)', '(gikun)', '(hon)', '(hum)', '(ik)', '(iK)', '(id)', '(io)', '(m-sl)', '(male)', '(male-sl)', '(oK)', '(obs)', '(obsc)', '(ok)', '(on-mim)', '(poet)', '(pol)', '(rare)', '(sens)', '(sl)', '(uK)', '(uk)', '(vulg)' ]


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


class Word(BaseM):
    def __init__(self):
        self.text = ''
        self.kanas = list()
        self.meanings = list()
        self.seq_num = ''
        self.tags = list()


    def dump_object(self):
        o = copy.deepcopy(self.__dict__)
        o['kanas'] = [k.dump_object() for k in self.kanas]
        o['meanings'] = [m.dump_object() for m in self.meanings]
        return o


    def split_words(self):
        if ';' in self.text:
            parts = self.text.split(';')
            return [self.splited_word(p) for p in parts]
        else:
            self.parse_tags()
            return [self]


    def splited_word(self, text):
        w = Word()
        w.__dict__.update(copy.deepcopy(self.__dict__))
        w.text = text
        w.parse_tags()
        w.clean_kanas()
        return w


    def clean_kanas(self):
        result = list()
        flag = False
        # iter all kanas and their tags
        for k in self.kanas:
            for t in k.tags:
                if ',' in t: # if tag contains ','
                    flag = True
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


    def parse_meanings(self, comps):
        if comps:
            self.meanings = Meaning.parse(comps)


class Edict2(object):
    def __init__(self):
        pass

    def load(self, filename):
        count = 0
        for line in open(filename):
            count += 1
            if count == 1: continue

            comps = line.split('/')
            comps = [c for c in comps if c.strip()]

            w = Word()
            w.seq_num = comps[-1]
            w.parse_text_kanas(comps[0])
            w.parse_meanings(comps[1: -1])
            #print comps
            #print comps[1:-1]

            ws = w.split_words() # 有的多个词在同一行

            for w in ws:
                print w

            #if count > 20: break


if __name__ == '__main__':
    import sys
    edict2 = Edict2()
    edict2.load(sys.argv[1])

