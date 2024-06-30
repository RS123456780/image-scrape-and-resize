# image-scrape-and-resize

## Overview
画像生成、エッジAIなどでデータセットが必要になったときに使えるツール群です。  
scrape_chrome.pyでgoogle画像検索をして任意の枚数の画像を保存し、delete_duplication.pyで複数フォルダの画像を重複を除外し一つのフォルダにまとめ、image_resizer.pyで画像を正方形にリサイズします。

## Requirement
Python 3.10で動作確認  
scrape_chrome.pyを使う際にはchrome_driver.exeを他サイトからダウンロードし同じディレクトリに入れてください。


## Usage & Features
必要なPythonライブラリをインストールしてください。
```bash
pip install Pillow opencv-python numpy requests selenium
```
scrape_chrome.pyを使う際は、コマンドラインに
```bash
python scrape_chrome.py -s [検索したいワード] -n [保存したい枚数] -o [画像の保存先ディレクトリ] --csv
```
と入力してください。google chromeで自動的に画像が収集されます。146行目、168行目でclass_nameとxpathを入力していますが、環境や時期によって変更されるようです。当該箇所を自ら確認する必要があります。  

　検索したいワードに複数の単語を入れたい場合は"りんご+青+..."と、'+'で単語をつなげてください。  
コマンドライン引数はすべてオプションです。デフォルトでは検索したいワードは"banana"、保存したい枚数は10、画像の保存先ディレクトリは"images"となっています。  
csvファイルには実行内容が保存されています。２回目以降はcsvファイルに保存した値を参照し、前回最後に保存された画像の周辺から収集を再開することができます。  
画像はすべてjpgとして保存されるはずです。

delete_duplication.pyを使う際は、コマンドラインに
```bash
python delete_duplication.py [output_dir] [input_dir1] [input_dir2] [input_dir3]...
```
と入力してください。複数のディレクトリ内の画像が画素数の順にソートされ、画像が重複しないように保存されます。  
出力ディレクトリ名を入力しない場合デフォルトのoutput_dirになります。
出力ディレクトリ名はすでに存在するものを入力してはいけません。
入力ディレクトリが1つのみの場合解像度順にソートされます。

2024/6/30 追加  
delete_duplication.cppを追加しました。pythonバージョンでは似た画像が誤って削除されてしまうので、C++でより高速で正確なプログラムを作成しました。
delete_duplication.exeは静的リンクでコンパイルしたのでOpenCVがインストールされていないWindowsマシンでも動作します。
使用する際はコマンドラインに以下のコマンドを入力してください。
```bash
./delete_duplication.exe [output_dir] [input_dir1] [input_dir2] [input_dir3]...
```


image_resizer.pyを使う際は、コマンドラインに
```bash
python image_resizer.py
```
と入力してください。様々なリサイズのオプションが聞かれて、正方形に画像をリサイズすることができます。  
詳細は省きますが、最初に画像が保存されているディレクトリが聞かれるので入力した後、すべてEnterを押し続けるとデフォルトオプションとなり1024*1024の画像にリサイズしてくれます。

