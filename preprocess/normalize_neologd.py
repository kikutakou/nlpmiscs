#!/usr/bin/env python

# encoding: utf8
from pprint import pprint
import difflib
import argparse
import re
import unicodedata
import sys
import os


def unicode_normalize(cls, s):
    regex_str = '([{}]+)'.format(cls)
    pt = re.compile(regex_str)
    s = ''.join(unicodedata.normalize('NFKC', x) if i % 2 else x for i, x in enumerate(re.split(pt, s)))
    return s


def remove_space_between(cls1, cls2, s):
    regex_str = '(?<=[{}]) (?=[{}])'.format(cls1, cls2)
    p = re.compile(regex_str)
    s = p.sub('', s)
    return s


def remove_extra_spaces(s):
    blocks = ''.join(('\u4E00-\u9FFF',  # CJK UNIFIED IDEOGRAPHS
                      '\u3040-\u309F',  # HIRAGANA
                      '\u30A0-\u30FF',  # KATAKANA
                      '\u3000-\u303F',  # CJK SYMBOLS AND PUNCTUATION
                      '\uFF00-\uFFEF'   # HALFWIDTH AND FULLWIDTH FORMS
                      ))
    basic_latin = '\u0000-\u007F'

    s = remove_space_between(blocks, blocks, s)
    s = remove_space_between(blocks, basic_latin, s)
    s = remove_space_between(basic_latin, blocks, s)
    return s

def normalize_neologd(s):
    s = unicodedata.normalize('NFKC', s)
    s = s.strip()
    s = unicode_normalize('０-９Ａ-Ｚａ-ｚ｡-ﾟ', s)   # normalize FULL-WIDTH alphanum
    s = re.sub('－', '-', s)   # normalize hyphens

    s = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', s)  # normalize hyphens
    # MODIFIER LETTER MINUS SIGN(U+02D7), ARMENIAN HYPHEN(U+058A), ハイフン(U+2010), ノンブレーキングハイフン(U+2011), フィギュアダッシュ(U+2012)
    # エヌダッシュ(U+2013), Hyphen bullet(U+2043), 上付きマイナス(U+207B), .下付きマイナス(U+208B), 負符号(U+2212)
    s = re.sub('[﹣－ｰ—―─━ー]+', 'ー', s)  # normalize choonpus
    # エムダッシュ(U+2014), ホリゾンタルバー(U+2015), 横細罫線(U+2500), 横太罫線(横太罫線), SMALL HYPHEN-MINUS(U+FE63), 全角ハイフンマイナス(U+FF0D), 半角長音記号(U+FF70)
    s = re.sub('[~∼∾〜〰～]', '', s)  # remove tildes
    # 半角チルダ, チルダ演算子, INVERTED LAZY S, 波ダッシュ, WAVY DASH, 全角チルダ


    # normalize FULL-WIDTH symbols
    s = s.translate( str.maketrans('!"#$%&\'()*+,-./:;<=>?@[¥]^_`{|}~｡､･｢｣',
                                   '！”＃＄％＆’（）＊＋，－．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」'))

    # remove_extra_spaces
    s = re.sub('[ 　]+', ' ', s)
    s = remove_extra_spaces(s)
    s = unicode_normalize('！”＃＄％＆’（）＊＋，－．／：；＜＞？＠［￥］＾＿｀｛｜｝〜', s)  # keep [＝・「]
    s = re.sub('[’]', '\'', s)
    s = re.sub('[”]', '"', s)
    return s

def test():
    assert "0123456789" == normalize_neologd("０１２３４５６７８９")
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ" == normalize_neologd("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ")
    assert "abcdefghijklmnopqrstuvwxyz" == normalize_neologd("ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ")
    assert "!\"#$%&'()*+,-./:;<>?@[¥]^_`{|}" == normalize_neologd("！”＃＄％＆’（）＊＋，－．／：；＜＞？＠［￥］＾＿｀｛｜｝")
    assert "＝。、・「」" == normalize_neologd("＝。、・「」")
    assert "ハンカク" == normalize_neologd("ﾊﾝｶｸ")
    assert "o-o" == normalize_neologd("o₋o")
    assert "majikaー" == normalize_neologd("majika━")
    assert "わい" == normalize_neologd("わ〰い")
    assert "スーパー" == normalize_neologd("スーパーーーー")
    assert "!#" == normalize_neologd("!#")
    assert "ゼンカクスペース" == normalize_neologd("ゼンカク　スペース")
    assert "おお" == normalize_neologd("お             お")
    assert "おお" == normalize_neologd("      おお")
    assert "おお" == normalize_neologd("おお      ")
    assert "検索エンジン自作入門を買いました!!!" == normalize_neologd("検索 エンジン 自作 入門 を 買い ました!!!")
    assert "アルゴリズムC" == normalize_neologd("アルゴリズム C")
    assert "PRML副読本" == normalize_neologd("　　　ＰＲＭＬ　　副　読　本　　　")
    assert "Coding the Matrix" == normalize_neologd("Coding the Matrix")
    assert "南アルプスの天然水Sparking Lemonレモン一絞り" == normalize_neologd("南アルプスの　天然水　Ｓｐａｒｋｉｎｇ　Ｌｅｍｏｎ　レモン一絞り")
    assert "南アルプスの天然水-Sparking*Lemon+レモン一絞り" == normalize_neologd("南アルプスの　天然水-　Ｓｐａｒｋｉｎｇ*　Ｌｅｍｏｎ+　レモン一絞り")



def fileopen(filename):
    if not os.path.exists(filename):
        raise argparse.ArgumentTypeError("input file {} not exist".format(filename))
    return open(filename)


def fileDescripter(filename):
    return open(filename, "w")


if __name__ == "__main__":

    # do test
    test()

    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=fileopen, default=sys.stdin)
    parser.add_argument("-o", "--output", type=fileDescripter, default=sys.stdout)
    args = parser.parse_args()

    d = difflib.Differ()

    # normalize
    for line in args.input:
        normalized = normalize_neologd(line)
        print(normalized)








