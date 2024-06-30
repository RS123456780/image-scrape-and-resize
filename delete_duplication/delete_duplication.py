import os
import glob
from PIL import Image
import cv2
import sys
import numpy as np

# 複数のディレクトリ内のjpgファイルを解像度順にソートし、一つのディレクトリにまとめる
# 同じ画像は重複しないように削除される(似ている画像は片方消されるかも)
# How To
# (1) ソースコードを保存して命名する (e.g. delete_duplication.py)
# (2) プログラムを起動する python delete_duplication.py
# (3) オプション
# python delete_duplication.py (output_dir) input_dir1 input_dir2 input_dir3...
# 出力ディレクトリ名を入力しない場合デフォルトのoutput_dirになる
# 出力ディレクトリ名はすでに存在するものを入力してはいけない
# 入力ディレクトリが1つのみの場合解像度順にソートされる


# 画像を読み込み、解像度情報を返す関数
def get_resolution(filepath):
    img = cv2.imread(filepath)
    if img is None:
        print(f"画像ファイルの読み込みに失敗しました: {filepath}")
        sys.exit(1)
    height, width = img.shape[:2]
    return width * height

def count_resol(directory):
    print(directory)
    files = glob.glob(os.path.join(directory, '*.jpg'))
    d = []
    for file in files:
        resolution = get_resolution(file)
        d.append([resolution, file])
    list_sorted = sorted(d, key=lambda x: x[0], reverse=True)
    print("Done")
    return list_sorted

def get_diagonal_pixels(image, num_samples=10):
    height, width, _ = image.shape
    diagonal_pixels = []
    for i in range(num_samples):
        x = int((i / num_samples) * width)
        y = int((i / num_samples) * height)
        pixel = image[y, x]
        diagonal_pixels.append(pixel)
    return np.array(diagonal_pixels)

def is_same_image(file1, file2, num_samples=10):
    img1 = cv2.imread(file1)
    img2 = cv2.imread(file2)
    if img1 is None or img2 is None:
        print("画像ファイルの読み込みに失敗しました。")
        return False
    diag1 = get_diagonal_pixels(img1, num_samples)
    diag2 = get_diagonal_pixels(img2, num_samples)
    return np.array_equal(diag1, diag2)

def main(args):
    if len(args) < 1:
        print("使用方法: python script.py [出力ディレクトリ (オプション)] <入力ディレクトリ1> <入力ディレクトリ2> ...")
        sys.exit(1)

    output_dir = "output_dir"
    input_dirs = []

    # コマンドライン引数の処理
    if len(args) == 1:
        input_dirs = [args[0]]
    else:
        if os.path.isdir(args[0]):
            input_dirs = args
        else:
            output_dir = args[0]
            input_dirs = args[1:]

    os.makedirs(output_dir, exist_ok=True)

    # 画像リストを取得
    if len(input_dirs) == 1:
        # 入力ディレクトリが1つの場合、解像度順にソート
        sorted_list = count_resol(input_dirs[0])
        merged_list = sorted_list
    else:
        dir_list = []
        for path in input_dirs:
            sorted_list = count_resol(path)
            dir_list.append(sorted_list)

        # 全ての画像リストをマージ
        merged_list = []
        for sublist in dir_list:
            merged_list.extend(sublist)

        # 解像度順に再ソート
        merged_list.sort(key=lambda x: x[0], reverse=True)

        # 同一画像を除外
        i = 0
        while i < len(merged_list):
            j = i + 1
            while j < len(merged_list):
                if merged_list[i][0] == merged_list[j][0] and is_same_image(merged_list[i][1], merged_list[j][1]):
                    merged_list.pop(j)
                else:
                    j += 1
            i += 1

    # 画像を保存
    file_count = 0
    for img_info in merged_list:
        img_path = img_info[1]
        img = Image.open(img_path)
        if img.mode == 'P':
            img = img.convert('RGBA').convert('RGB')  # RGBAに変換してからRGBに変換
        elif img.mode == 'RGBA':
            img = img.convert('RGB')  # RGBモードに変換
        img.save(os.path.join(output_dir, f"img_{file_count}.jpg"), quality=95)
        file_count += 1

if __name__ == '__main__':
    from sys import argv
    try:
        main(argv[1:])
    except KeyboardInterrupt:
        pass
    sys.exit()