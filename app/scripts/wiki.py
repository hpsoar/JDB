#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    Author  :   HuangPeng
    E-mail  :   hpsoar@gmail.com
    Date    :   16/04/24 01:11:05
    Desc    :   
"""

import pplib

def datapath(path, filename):
    p = 'wiki'
    if path:
        import os
        os.path.join(p, path)
    return pplib.ff.data_path(p, filename)

def raw_html_path():
    return datapath('raw', '1000words.html')

def download():
    url = 'https://en.m.wiktionary.org/wiki/Appendix:1000_Japanese_basic_words'
    c, content = pplib.uff.download(url)
    print 'download: %s' % url
    if content:
        path = raw_html_path()
        print 'save: %s' % path
        pplib.ff.save(path, content)
    else:
        print 'error'

def parse():
    path = raw_html_path()
    bs = pplib.ff.BSFile(path)
    main = bs.find(id='mw-content-text')

    header = None
    result = dict()
    for c in main.children:
        if 'class' not in c.attrs: continue

        print '-'*80
        cls = c['class']
        if header:
            if 'mf-section-' in ''.join(cls):
                section = dict()
                result[header] = section
                h3 = ''
                for s in c.children:
                    if not s.name: continue
                    print '*'*80
                    if s.name == 'h3':
                        h3 = s.find(class_='mw-headline')
                        h3 = h3.text
                    elif s.name == 'ul':
                        print 'ul'
                        r = None
                        if h3 in section:
                            r = section[h3]
                        else:
                            r = list()
                            section[h3] = r
                        words = parse_words(s)
                        r.extend(words)
                    else:
                        print s
                        print 'unknown'

        if 'section-heading' in cls:
            t = c.find(class_='mw-headline')
            header = t.text
            print header
    return result


def print_words(words):
    for (h, s) in words.items():
        print '-'*80
        print h
        for (hh, ws) in s.items():
            print '*'* 80
            print hh
            for w in ws:
                print w['word']
    path = datapath(None, '1000words.json')
    pplib.ff.save_json(path, words)
            

def parse_words(ul):
    lis = ul.find_all('li')
    result = list()
    for li in lis:
        text = li.text
        comps = text.split(u'\u2013')
        if len(comps) < 2:
            comps = text.split('-')
        if len(comps) > 1:
            d = dict()    
            d['word'] = comps[0]
            d['meaning'] = comps[1]
            result.append(d)
        else:
            print 'wrong format'
            print comps
    return result


if __name__ == '__main__':
    #download()
    print_words(parse())


