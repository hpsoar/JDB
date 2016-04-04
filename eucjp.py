# -*- coding: utf-8 -*-

def convert_line(line):
    return line.decode('euc_jp').encode('utf-8')


def convert_lines(lines):
    return [convert_line(l) for l in lines]


def convert_file(infile, outfile):
    of = open(outfile, 'w')
    for l in open(infile):
        of.write(convert_line(l))


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print 'usage: python eucjp.py <infile> <outfile:optional>'

    if len(sys.argv) > 2:
        convert_file(sys.argv[1], sys.argv[2])
    else:
        for l in open(sys.argv[1]):
            sys.stdout.write(convert_line(l))



