import urllib2
import BeautifulSoup as BS

def parse():
    parse_page(1)
    parse_page(2)

def parse_page(page):
    page_url = 'http://jp.hjenglish.com/new/tag/page%d/%E6%97%A5%E8%AF%AD%E8%AF%8D%E6%B1%87%E7%B1%BB%E7%BC%96/' % page
    filename = 'category_words_raw_page_%d.html' % page
    content = urllib2.open(page_url).read()
    open(filename, 'w').write(content)
    bs = BS(content)
    

if __name__ == '__main__':
    parse()
