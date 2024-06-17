import os
import glob
from PIL import Image


def is_float(x):  # floatかどうか判定
  try:
    float(x)
  except ValueError:
    return False
  return True


def get_concat_h(img1, img2):  # 画像を横に結合
  dst = Image.new('RGB', (img1.width + img2.width, img1.height))
  dst.paste(img1, (0, 0))
  dst.paste(img2, (img1.width,0))
  return dst


def get_concat_v(img1, img2):  # 画像を縦に結合
  dst = Image.new('RGB', (img1.width, img1.height + img2.height))
  dst.paste(img1, (0, 0))
  dst.paste(img2, (0, img1.height))
  return dst


def get_bg_color_h(base_img, left=True):  # 横の背景色を外側の色の平均RGB値として取得
  sum_r, sum_g, sum_b = 0, 0, 0
  if left:
    for y in range(base_img.height):
      r, g, b = base_img.getpixel((0, y))
      sum_r += r
      sum_g += g
      sum_b += b
    return (sum_r // base_img.height, sum_g // base_img.height, sum_b // base_img.height)
  else:
    for y in range(base_img.height):
      r, g, b = base_img.getpixel((base_img.width - 1, y))
      sum_r += r
      sum_g += g
      sum_b += b
    return (sum_r // base_img.height, sum_g // base_img.height, sum_b // base_img.height)


def get_bg_color_v(base_img, top=True):  # 縦の背景色を外側の色の平均RGB値として取得
  sum_r, sum_g, sum_b = 0, 0, 0
  if top:
    for x in range(base_img.width):
      r, g, b = base_img.getpixel((x, 0))
      sum_r += r
      sum_g += g
      sum_b += b
    return (sum_r // base_img.width, sum_g // base_img.width, sum_b // base_img.width)
  else:
    for x in range(base_img.width):
      r, g, b = base_img.getpixel((x, base_img.height - 1))
      sum_r += r
      sum_g += g
      sum_b += b
    return (sum_r // base_img.width, sum_g // base_img.width, sum_b // base_img.width)


def add_bg_h(added_img, size):  # 横の背景を追加
  img_width, img_height = added_img.size
  bg_left_size = (size - img_width) // 2
  bg_right_size = size - img_width - bg_left_size
  bg_left_color = get_bg_color_h(added_img, True)
  bg_right_color = get_bg_color_h(added_img, False)
  bg_left = Image.new('RGB', (bg_left_size, img_height), bg_left_color)
  bg_right = Image.new('RGB', (bg_right_size, img_height), bg_right_color)
  added_img = get_concat_h(bg_left, added_img)
  added_img = get_concat_h(added_img, bg_right)
  return added_img


def add_bg_v(added_img, size):  # 縦の背景を追加
  img_width, img_height = added_img.size
  bg_top_size = (size - img_height) // 2
  bg_bottom_size = size - img_height - bg_top_size
  bg_top_color = get_bg_color_v(added_img, True)
  bg_bottom_color = get_bg_color_v(added_img, False)
  bg_top = Image.new('RGB', (img_width, bg_top_size), bg_top_color)
  bg_bottom = Image.new('RGB', (img_width, bg_bottom_size), bg_bottom_color)
  added_img = get_concat_v(bg_top, added_img)
  added_img = get_concat_v(added_img, bg_bottom)
  return added_img


def resize_square(pil_img, img_size, trim_size, option): # 画像のサイズをimg_size x img_sizeに変更
  img_width, img_height = pil_img.size

  # resize_optionが1の場合、画像をアップスケールまたはダウンスケールする
  if option == 1 and ((img_width != img_size and img_width < img_height ) or (img_height != img_size and img_width > img_height)):
    if img_width < img_height:
      pil_img = pil_img.resize((img_size, int(img_size * img_height / img_width)), Image.LANCZOS)
    elif img_width > img_height:
      pil_img = pil_img.resize((int(img_size * img_width / img_height), img_size), Image.LANCZOS)

  # 画像の大きさを再取得し、画像を正方形に変更する
  img_width, img_height = pil_img.size

  if img_width < img_size:
    pil_img = add_bg_h(pil_img, img_size)
  elif img_width > img_size:
    bg_left_size = (img_width - img_size) // 2
    pil_img = pil_img.crop((bg_left_size, 0, bg_left_size + img_size, img_height))
  if img_height < img_size:
    pil_img = add_bg_v(pil_img, img_size)
  elif img_height > img_size:
    bg_top_size = (img_height - img_size) // trim_size
    pil_img = pil_img.crop((0, bg_top_size, img_size, bg_top_size + img_size))

  return pil_img


def main():

  print("\nThis program resizes png and jpg images to square images and saves them in the new directory as the original image.\n")

  dir_name = input ("input name of directory which have images: ") #ディレクトリ名を取得、ディレクトリが存在しない場合でも問題ないようにする
  dir_path = "./" + dir_name

  output_image = input ("input name of output images (default: directory name): ") # 出力画像名を取得
  if output_image == "":
    output_image = dir_name

  while (1):  # 正方形のサイズを取得
    square_size = input ("input int size of img A (A x A pixel) (default: 1024): ")
    if square_size == "":
      square_size = int(1024)
      break
    elif square_size.isdecimal() == False:
      print("Please input int number")
    else:
      square_size = int(square_size)
      break

  while (1):  # トリミングパラメータを取得
    trim_param = input ("input float trim parameter (default: MAX): ")
    if trim_param == "":
      trim_param = int(65535)
      break
    elif is_float(trim_param) == False or float(trim_param) < 1:
      print("Please input correct number")
    else:
      trim_param = float(trim_param)
      break
  
  while (1):  # リサイズオプションを取得
    resize_selection = input("you want to upscale or downscale images? (default: yes): (y/n) ")
    if resize_selection == "":
      resize_option = 1
      break
    elif resize_selection != "y" and resize_selection != "n" and resize_selection != "Y" and resize_selection != "N":
      print("Please input y or n")
    else:
      if (resize_selection == "Y" or resize_selection == "y"):
        resize_option = 1
      else:
        resize_option = 0
      break

  output_dir = dir_path + "_" + str(square_size)  # 出力ディレクトリを作成
  os.makedirs(output_dir, exist_ok=True)

  file_list_png = glob.glob(os.path.join(dir_path, "*.png"))  # ディレクトリ内のpngとjpgファイルを取得
  file_list_jpg = glob.glob(os.path.join(dir_path, "*.jpg"))

  file_count = 0

  # 画像をリサイズして保存
  for img_path in file_list_png:
    img = Image.open(img_path)
    new_img = resize_square(img, square_size, trim_param, resize_option)
    new_img.save(output_dir + '/' + output_image + '_'+ str(file_count) + '.png', quality=95)
    file_count += 1

  for img_path in file_list_jpg:
    img = Image.open(img_path)
    new_img = resize_square(img, square_size, trim_param, resize_option)
    new_img.save(output_dir + '/' + output_image + '_'+ str(file_count) + '.jpg', quality=95)
    file_count += 1

  print("\nComplete! The " + str(file_count) + " resized images are saved in the directory.\n")


main()