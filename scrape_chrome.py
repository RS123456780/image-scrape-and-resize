
# 必要なライブラリのインポート
import os
import time
import argparse
import sys
import urllib.request, urllib.error
import io
import csv
import datetime
 
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# How To
# (1) ソースコードを保存して命名する (e.g. scrape_chrome.py)
# (2) プログラムを起動する python scrape_chrome.py
# (3) オプション
# -s: Google Imagesにかける検索キーワード、検索語が複数の場合は+でつなげる
# -n: ダウンロードする画像の数量 (デフォルト 10枚)
# -o: 画像の保存先 (デフォルト　images)
# --csv: 前回作られたcsvファイルを参照したい場合
#たまに違うURLのGoogle画像検索画面が出て失敗することがある
 

# 1枚の画像を保存する関数
def save_img(url, file_path, i):
    print("requests...")
    # set User-Agent to HTTP header in urllib.request
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', UA)]
    urllib.request.install_opener(opener) # ヘッダをつけるとエラーが減る
    # save an img file
    urllib.request.urlretrieve(url, os.path.join(file_path, "img_"+str(i+1)+".jpg"))
 
 
# 複数の画像のダウンロードを行う関数
def download_imgs(img_urls, save_dir, index):
    # ディレクトリが存在しなければ作成する
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for i, url in enumerate(img_urls):
        save_img(url, save_dir, i + index)  # 画像の保存
        if (i + 1) % 10 == 0 or (i + 1) == len(img_urls):
            print(f"{i + 1} / {len(img_urls)} done")


# 画面をスクロールする関数
def scroll(chrome_driver):
    # 止まるまでスクロールする
    while True:
        prev_html = chrome_driver.page_source  # スクロール前のソースコード
        chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 最下部までスクロール
        time.sleep(1.0)   # 1秒待機
        current_html = chrome_driver.page_source  # スクロール後のソースコード
    
        # スクロールの前後で変化が無ければループを抜ける
        if prev_html != current_html:
            prev_html = current_html
        else:
            # 「もっと見る」ボタンがあればクリック
            try:
                button = chrome_driver.find_elements(By.XPATH, '//*[@id="yDmH0d"]') #後で修正
                button.click()
            except:
                break
    return chrome_driver


# csvファイルを読み込む関数。存在しないもしくは読み込まない場合は0に初期化
def read_csv(path, reference):
    if os.path.exists(path) and reference:
        with open(path, 'r') as csv_file:
            f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
            for row in f:
                pass
            previous_count = int(row[3])
            first_inde = int(row[5])
    else:
        previous_count = 0
        first_inde = 0
    return previous_count, first_inde


# 実行パラメータをcsvファイルに保存する関数
def save_csv(path, csv_data):
    if not os.path.exists(path):
        with open(path, 'w', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(csv_data[0])
            writer.writerow(csv_data[1])
    else:
        with open(path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(csv_data[1])


# chromeドライバーをセットし、ウェブサイトにアクセスする。ドライバーを返す
def access_website(query):
    # Webdriverの設定
    options = webdriver.ChromeOptions()
    #option.add_argument('--headless')   # UI無しで操作する
    # set header of Webdriver
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'
    options.add_argument('--user-agent=' + UA)
    cService = webdriver.ChromeService(chrome_options=options, executable_path='./chromedriver.exe')
    driver = webdriver.Chrome(service = cService)  # WebDriverのパスを設定
    
    # Google画像検索へアクセス
    search_url = "https://www.google.co.jp/search?q={}&source=lnms&udm=2"
    driver.get(search_url.format(query))  # 指定したURLへアクセス
    return driver


# メイン関数
def main(args):
    parser = argparse.ArgumentParser(description='Options for scraping Google images') # コマンドライン引数を取得
    parser.add_argument('-s', '--search', default='banana', type=str, help='search term')
    parser.add_argument('-o', '--directory', default='images', type=str, help='output directory')
    parser.add_argument('-n', '--num_images', default=10, type=int, help='num of images to scrape')
    parser.add_argument('--csv', action='store_true', help='prev csv file refer to first_index and prev_count')
    args = parser.parse_args()

    word = args.search  # 検索するワード
    save_dir = args.directory + '/' + word  # スクレイピングした画像を保存するディレクトリパス
    num_img = args.num_images # number of save images
    csv_reference = args.csv #csvファイルの利用の有無を決定

    csv_path = './'+save_dir+'.csv' #csvファイルのパスを設定
    prev_count, first_ind = read_csv(csv_path, csv_reference) #csvファイルを読み込み

    urls = []  # 画像URLを格納するリスト
    sleep_between_interactions = 3 # 2秒待たないとロード時間が足りず低解像度の画像が保存される
    website = 'Google_img' #検索するウェブサイト
    date = datetime.date.today() #収集した日付を取得

    # ドライバーをセットし、ウェブサイトにアクセスする
    driver = access_website(word)
    # 画像検索画面をスクロールする
    driver = scroll(driver)
    
    # 画像タグをすべて取得 うまくいかない場合は右クリ検証でCLASS_NAMEを調べる
    elements_all = driver.find_elements(By.CLASS_NAME, 'YQ4gaf')
    if len(elements_all) == 0: #違うURLで開かれている場合、プログラムを終了する
        print("URL false! please retry")
        return
    elements = elements_all[first_ind:]
    elem_ind = -1 #要素のインデックス
    count = 0 #URL取得回数を数える

    # 指定枚数の画像URLを抜き出す
    for element_index, elem in enumerate(elements):
        if count == num_img:
            if count % 10 != 0:
                extra_index = count - (count % 10) #残りの画像の一番最初のインデックス
                download_imgs(urls[extra_index:count], save_dir, extra_index + prev_count)   # 残りの画像をダウンロードする
                print("saved " + str(count) + " / " + str(num_img) + " images")
            elem_ind = element_index
            break
        try:
            # enlarge an image
            elem.click()
            time.sleep(sleep_between_interactions)
            # 拡大画像urlを取得 うまくいかない場合はXPATHを調べる。右クリ検証、該当箇所右クリcopy、copy XPATHで可能
            url_candidates = driver.find_elements(By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div/div[3]/div[1]/a/img[1]')
            # get urls of images
            url = url_candidates[0].get_attribute("src")
            if url not in urls and url.startswith('http'): # remove error
                count += 1
                urls.append(url)  # urlをリストに追加する
                print(url)
                if count % 10 == 0:
                    download_imgs(urls[count-10:count], save_dir, count - 10 + prev_count)   # 10枚の画像を一旦ダウンロードする(エラー予防のため)
                    print("saved " + str(count) + " / " + str(num_img) + " images")
            # 新たに開いたタブを消す
            while driver.window_handles[1] != None:
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except Exception as e:
            continue
        
    time.sleep(sleep_between_interactions)
    driver.close()   # driverをクローズする

    if elem_ind == -1:
        next_index = -1
        print("saved all images!")
    else:
        next_index = first_ind + elem_ind # 次回スクレイピングをする際のインデックスを計算
        print("You should start with " + str(next_index) +" next time.")

    data = [
        ['search', 'directory', 'num_images', 'saved_images', 'first_index', 'next_index', 'website', 'datetime'],
        [word, save_dir, num_img, count+prev_count, first_ind, next_index, website, date]
    ]
    save_csv(csv_path, data) #データをcsvファイルに保存
    return


if __name__ == '__main__':
    from sys import argv
    try:
        main(argv)
    except KeyboardInterrupt:
        pass
    sys.exit()
