# -*- coding:utf-8 -*-

import pplib

def download_audios():
    lines = open('data/learn-jpn/audio_list.txt').readlines()
    def download():
        for l in lines:
            l = l.strip()
            url = 'http://7j1ysu.com1.z0.glb.clouddn.com/riyu/%s.mp3' % l
            path = pplib.ff.data_path('learn-jpn/audios', '%s.mp3' % l)

            if pplib.ff.exists(path):
                print '%s exists' % path
                continue

            print 'download %s' % url
            c, content = pplib.uff.download(url)
            if content:
                print 'save %s' % path
                pplib.ff.save(path, content, 'wb')
            else:
                print 'error: %s' % url

    pplib.task.schedule(download)

if __name__ == '__main__':
    download_audios()

