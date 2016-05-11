#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    Author  :   HuangPeng
    E-mail  :   hpsoar@gmail.com
    Date    :   16/04/17 20:08:25
    Desc    :   
"""


import pplib
from bs4 import BeautifulSoup as BS

def data_path(path, filename):
    import os
    if path:
        path = os.path.join('short_888', path)
    else:
        path = 'short_888'
    return pplib.ff.data_path(path, filename)


def raw_category_path(i):
    return data_path('raw/list', '%d.html' % (i + 1))


def download_list():
    for i in range(3):
        url = 'http://jp.tingroom.com/wap/index.php?moduleid=21&catid=539&page=%d' % (i+1)
        c, content = pplib.uff.download(url)
        if content:
            pplib.ff.save(path, content)


def enum_categories(handle):
    for i in range(3):
        path = raw_category_path(i)
        content = pplib.ff.read(path)
        links = parse_category_links(content)
        for l in links:
            item_id = parse_item_id(l) 
            handle(l, item_id)


def download_categories():
    enum_categories(download_category_content)


def parse_categories():
    enum_categories(parse_category_content)


def check_results():
    ff = pplib.ff.openfile(data_path(None, 'short_link.check'), 'w')
    def check(link, item_id):
        items = pplib.ff.read_json(item_path(item_id))
        print >>ff, '-' * 80
        for i in items:
            print >>ff, '*' * 40
            print >>ff, i['title'].encode('utf-8')
            print >>ff, i['content'].encode('utf-8')
    enum_categories(check)


def parse_category_links(content):
    bs = BS(content)
    ul = bs.find(class_='listtxt1')
    r = list()
    if ul:
        lis = ul.find_all('li')
        for li in lis:
            link = parse_category_link(li)
            if link:
                r.append(link)
    return r


def parse_item_id(link):
    import re
    reg = re.compile('itemid=([0-9]+)')
    r = reg.search(link)
    return r.group(1)

def parse_category_link(li):
    a = li.find('a')
    href = a['href']
    href = 'http://jp.tingroom.com/wap/%s' % href
    return href


def raw_item_path(item_id):
    return data_path('raw/items/', '%s.html' % item_id)

def download_category_content(link, item_id):
    path = raw_item_path(item_id)
    print 'download: %s' % link
    c, content = pplib.uff.download(link)
    if content:
        print 'save: %s' % path
        pplib.ff.save(path, content)
    else:
        print 'error: %s' % link


def parse_category_content(link, item_id):
    path = raw_item_path(item_id)
    bs = BS(open(path))
    content = bs.find(class_='content')
    divs = content.find_all('div')
    div = divs[1]
    ps = div.find_all('p')
    items = list()
    log_file = pplib.ff.openfile(data_path(None, 'parser.log'), 'a')
    print >>log_file, path
    print >>log_file, '-' * 80
    title = None
    for p in ps:
        if p.text.strip():
            if title:
                title = title.lstrip('\n').encode('utf-8')
                content = p.text.lstrip('\n').encode('utf-8')
                log_file.write(title)
                log_file.write(content)
                d = dict()
                d['title'] = title
                d['content'] = content
                items.append(d)
                title = None
            else:
                title = p.text
    path = item_path(item_id)
    pplib.ff.save_json(path, items)
    

def item_path(item_id):
    return data_path('items', '%s.json' % item_id)


if __name__ == '__main__':
    import sys
    opt = 'c'
    if len(sys.argv) > 1:
        opt = sys.argv[1]

    if opt == 'dl': 
        download_list()
    elif opt == 'dc': 
        download_categories()
    elif opt == 'p': 
        parse_categories()
    elif opt == 'c':
        check_results()


