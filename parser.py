# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup as BS
import pplib.ff
import pplib.uff
import os
import jisho_dict

data_root='data'

def data_filepath(path, filename):
    path = os.path.join(data_root, path)
    return os.path.join(path, filename)

def category_list_filepath():
    return data_filepath('category', 'category_list.txt')

def parse_category_list():
    category_list = list()

    for p in [ 1, 2 ]:
        plist = parse_page(p)
        print len(plist)
        category_list.extend(plist)

    print len(category_list)
    pplib.ff.save_json(category_list_filepath(), category_list)

def download_category_files():
    categories = pplib.ff.read_json(category_list_filepath())
    for c in categories:
        download_category_content(c)

def parse_page(page):
    page_url = 'http://jp.hjenglish.com/new/tag/PAGE/%E6%97%A5%E8%AF%AD%E8%AF%8D%E6%B1%87%E7%B1%BB%E7%BC%96/'
    page = 'page%d' % page
    page_url = page_url.replace('PAGE', page)

    print 'get content: %s' % page_url
    code, content = pplib.uff.download(page_url)

    filename = 'category_words_raw_%s.html' % page
    filename = data_filepath('raw', filename)
    print 'save content to %s' % filename
    pplib.ff.save(filename, content)

    print 'parse content'
    links = parse_category_links(content)
    result = list()
    for link in links:
        d = dict()
        d['url'] = link['href']
        d['title'] = link['title']
        result.append(d)
    return result


def parse_category_links(content):
    bs = BS(content)
    article_list = bs.find(id='article_list')
    if article_list:
        return article_list.find_all('a', class_='black')
    return list()

def category_filepath(url):
    comps = [c for c in url.split('/') if c]
    return data_filepath('raw/categories', '_'.join(comps))

def download_category_content(category):
    title = category['title']
    url = category['url']

    url = 'http://jp.hjenglish.com%s' % url
    print 'get category content: (%s, %s)' % (title, url)
    code, content = pplib.uff.download(url)

    category_file = category_filepath(category['url'])
    print 'save category content: %s' %  category_file
    pplib.ff.save(category_file, content)


def parse_categories():
    categories = pplib.ff.read_json(category_list_filepath())
    count = 0
    for c in categories:
        count += parse_category_content(c)
    print count

def process_categories():
    categories = pplib.ff.read_json(category_list_filepath())
    for c in categories:
        process_category(c)

def processed_cateogory_filepath(url, prefix='p'):
    comps = [c for c in url.split('/') if c]
    return data_filepath('raw/%s_categories' % prefix, '_'.join(comps))

def process_category(category):
    title = category['title']
    print 'title: %s' % title
    url = category['url']
    content = pplib.ff.read(category_filepath(url))
    bs = BS(content)
    main_article = bs.find(class_='main_article')
    f = open(processed_cateogory_filepath(url), 'w')
    print >>f, main_article

def parse_category_content(category):
    # json file
    # csv file
    # mp3 file
    title = category['title']
    print 'title: %s' % title
    url = category['url']

    words = list()
    garbadge = list()
    mp3 = ''
    for line in open(processed_cateogory_filepath(url)):
        line = line.strip()
        if 'script' in line:
            garbadge.append(line)
        elif '<br/>' in line or '</span></p>' in line:
            line = line.replace('<br/>', '').replace('</span></p>', '').replace('<span id="dipbbs_content">', '')
            if line.startswith('<a'):
                line, _ = re.subn('<a.*">', '', line)
                line = line.replace('</a>', '')
            words.append(line)
        else:
            garbadge.append(line)

        # parse mp3
        import re
        p = re.compile(r'soundFile=(.*mp3)&')
        m = p.search(line)
        if m:
            mp3 = m.groups()[0]

    if mp3: 
        words.append('mp3=%s' % mp3)

    pplib.ff.save_json(processed_cateogory_filepath(url, 'pp'), '')
    ff = open(processed_cateogory_filepath(url, 'pp'), 'w')
    for w in words:
        print >>ff, w

    pplib.ff.save_json(processed_cateogory_filepath(url, 'garbadge'), '')
    ff = open(processed_cateogory_filepath(url, 'garbadge'), 'w')
    for g in garbadge:
        print >>ff, g

    return len(words)

def enum_categories_with(handle, callback=None):
    categories = pplib.ff.read_json(category_list_filepath())
    for c in categories:
        result = handle(c)
        if callback:
            callback(result)

def extract_words():
    enum_categories_with(extract_words_in_category)

def extract_words_in_category(category):
    url = category['url']
    result = list()
    mp3 = None
    for line in open(processed_cateogory_filepath(url, 'pp')):
        if 'mp3' in line:
            mp3 = line
            continue

        if '：' in line:
            parts = line.split('：')
        elif ':' in line:
            parts = line.split(':')
        elif ' ' in line:
            parts = line.split(' ')
        elif '」' in line:
            parts = line.split('」')
        else:
            parts = line.split('（')
            if len(parts) > 1:
                parts[1] = '(%s' % parts[1]


        if len(parts) == 1:
            print 'error: %s, %s' % (processed_cateogory_filepath(url, 'pp'), line)
        else:
            word = parts[0]
            meaning = parts[1]
            comps = word.split('「')
            word = comps[0]
            kanji = word
            if len(comps) > 1:
                kanji = comps[1].replace('」', '')
            result.append([ word, kanji, meaning])
            #print '%s, %s, %s' % (word, kanji, meaning)

    outlines = [ ', '.join(r) for r in result ]
    if mp3:
        outlines.append(mp3)
    pplib.ff.save(processed_cateogory_filepath(url, 'words'), '')
    f = open(processed_cateogory_filepath(url, 'words'), 'w')
    f.writelines(outlines)
    f.close()
    return outlines

def query_dict():
    enum_categories_with(query_dict_for_category)

def query_dict_for_category(category):
    url = category['url']
    path = processed_cateogory_filepath(url, 'words')
    print path
    for line in open(path):
        if 'mp3' in line:
            continue
        parts = line.split(', ')
        word = parts[0].strip()
        print 'word: %s, %s' % (word, line)
        w = jisho_dict.query(word)
        print w
        print ''

if __name__ == '__main__':
    #parse_category_list()
    #download_category_files()
    #parse_categories()
    #process_categories()
    #extract_words()
    query_dict()

