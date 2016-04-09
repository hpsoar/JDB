# -*- coding: utf-8 -*-

class T(object):
  def __init__(self):
    self.text = 'text2'
    self.furigana = 'furigana'

def test(self):
    print self.text

T.test = test

if __name__ == '__main__':
    import sys
    #read(sys.argv[1])

    t = T()
    t.test()
