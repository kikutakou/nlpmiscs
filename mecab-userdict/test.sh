#!/bin/bash


set -e
cd $(dirname $0)

[ -e mecab-ipadic-2.7.0-20070801.model ] || bash download_model_utf8.sh

cat > wordlist.txt << 'EOF'
ノンフリ－ト
レッドブック
EOF


echo "##### generate dic"
python mecab-userdict.py wordlist.txt -o test.dic -m mecab-ipadic-2.7.0-20070801.model


echo "##### test"
set -x
mecab < wordlist.txt
mecab -u test.dic < wordlist.txt


