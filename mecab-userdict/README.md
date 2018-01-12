# mecabユーザ辞書作成スクリプト



## mecab-userdict.py

ElasticSearch辞書などを読み込んで、mecabの辞書dicファイルに変換するpythonスクリプト
引数は入力ファイル。複数のファイルを同時に指定することも可能。
内部では、コロン(,)、タブ(\t)、エラスティックサーチの矢印(=>)で単語を分割し、全ての単語をリストアップする。



使い方：
```
$ python mecab-userdict.py [file1.txt] [file2.txt] ...
```


オプション：
`-c COST`      コストを整数で指定（デフォルトは10）。
`-o OUTPUT`    出力。
