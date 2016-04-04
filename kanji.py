try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from xmljson import badgerfish as bf


class Base(object):
    def __init__(self, ele):
        self.ele = ele


    def __str__(self):
        return unicode(self).encode('utf-8')


    def __unicode__(self):
        return '' if self.ele is None else ET.tostring(self.ele) 


    # by tag
    
    def text(self, tag):
        e = self.one(tag)
        return '' if e is None else e.text


    def texts(self, tag):
        return [e.text for e in self.all(tag)]


    # Elements with no subelements will test as False. use element is None to test existence
    def one(self, tag):
        eles = self.all(tag)
        return eles[0] if eles else None


    def all(self, tag):
        if self.ele is None: return list()
        iters = self.ele.iter(tag)
        return [ele for ele in iters]


    # by path

    def path(self, xpath):
        eles = self.all_path(xpath)
        return eles[0] if eles else None


    def all_path(self, xpath):
        if self.ele is None: return list()
        iters = self.ele.iterfind(xpath)
        return [e for e in iters]

    
    def texts_of_path(self, xpath):
        return [e.text for e in self.all_path(xpath)]


    def text_of_path(self, xpath):
        e = self.path(xpath)
        return '' if e is None else e.text


class Reading(Base):
    @property
    def kun(self):
        return self.reading_of_type('ja_kun')


    @property
    def on(self):
        return self.reading_of_type('ja_on')


    @property
    def pinyin(self):
        return self.reading_of_type('pinyin')


    def reading_of_type(self, r_type):
        return self.text_of_path('reading[@r_type="%s"]' % r_type).encode('utf-8')


class Meaning(Base):

    @property
    def en_meanings(self):
        return self.get(lang='en')


    def get(self, lang=''):
        if not lang:
            return self.texts('meaning')
        elif lang == 'en':
            return [e.text for e in self.all('meaning') if not e.keys()]
        else:
            return self.texts_of_path('meaning[@m_lang="%s"]' % lang)


class Kanji(Base):
    def __init__(self, ele):
        super(Kanji, self).__init__(ele)

        reading_meaning = self.one('rmgroup')

        self.reading = Reading(reading_meaning)
        self.meaning = Meaning(reading_meaning)


    def log(self):
        print '-'*80
        print self
        print self.meaning.get()
        print self.meaning.get('en')
        print self.meaning.en_meanings
        print self.meaning.get('fr')
        print self.meaning.get('es')
        print self.reading.kun


    @property
    def literal(self):
        return self.text('literal')


class Manager(object):
    def __init__(self):
        self.kanji_map = dict()
        self.kanjis = list()


    def load_xml(self, filename):
        print 'load..'
        tree = ET.ElementTree(file=filename)

        print 'parse characters...'
        it = tree.iterfind('character')
        eles = [k for k in it]

        self.kanjis = [Kanji(e) for e in eles]

        self.compile_map()


    def compile_map(self):
        for k in self.kanjis:
            if k.literal:
                self.kanji_map[k.literal] = k
            else:
                print 'error'
                print k


    
    def convert_xml_to_json(self, eles):
        print 'convert to json...'
        kanjis = [bf.data(e) for e in eles]

        print 'clean..'
        kanjis = [k['character'] for k in kanjis]

        print kanjis[0]
        print kanjis[1]



if __name__ == '__main__':
    import sys
    m = Manager()
    m.load_xml(sys.argv[1])

