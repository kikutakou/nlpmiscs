#!/bin/bash


set -e
wget --content-disposition "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7bnc5aFZSTE9qNnM"
bzip2 -d mecab-ipadic-2.7.0-20070801.model.bz2
nkf -w --overwrite mecab-ipadic-2.7.0-20070801.model
perl -pe "s/charset: euc-jp/charset: utf-8/g" -i mecab-ipadic-2.7.0-20070801.model




