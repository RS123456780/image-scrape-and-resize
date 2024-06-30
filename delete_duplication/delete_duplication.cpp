#include <filesystem>
#include <iostream>
#include <string>
#include <vector>
#include <utility>
#include <opencv2/opencv.hpp>
using namespace std;
using namespace cv;


class Images{
  public:
    Images(vector<pair<int, filesystem::path>> list, filesystem::path output_dir){
      this->list = list;
      this->output_dir = output_dir;
    }
    Images(filesystem::path input_dir){
      this->input_dir = input_dir;
      for (const auto& entry : filesystem::directory_iterator(input_dir)){
        this->list.push_back(make_pair(get_resolution(entry.path()), entry.path()));
      }
      this->output_dir = "output_dir";
    }
    Images(filesystem::path input_dir, filesystem::path output_dir){
      this->input_dir = input_dir;
      this->output_dir = output_dir;
      for (const auto& entry : filesystem::directory_iterator(input_dir)){
        this->list.push_back(make_pair(get_resolution(entry.path()), entry.path()));
      }
    }
    int get_resolution(filesystem::path filepath){
      Mat img = imread(filepath.string());
      return img.rows * img.cols;
    }
    bool is_same_image(filesystem::path file1, filesystem::path file2, int num_samples){
      Mat img1 = imread(file1.string());
      Mat img2 = imread(file2.string());
      return is_same_image(img1, img2, num_samples);
    }
    bool is_same_image(const Mat &img1, const Mat &img2, int num_samples){
      if (img1.empty() || img2.empty())
      {
        throw runtime_error("Failed to load image for comparison");
      }
      if (img1.rows != img2.rows || img1.cols != img2.cols)
      {
        return false;
      }
      vector<Vec3b> all_pixels1 = get_all_pixels(img1, num_samples);
      vector<Vec3b> all_pixels2 = get_all_pixels(img2, num_samples);
      for (long unsigned int i = 0; i < all_pixels2.size(); i++){
        if (all_pixels1[i] != all_pixels2[i]){
          return false;
        }
      }
      return true;
    }
    void set_list(vector<pair<int, filesystem::path>> list){
      this->list = list;
    }
    vector<pair<int, filesystem::path>> get_list(){
      return list;
    }
    int get_list_size(){
      return (int)list.size();
    }
    void resol_sort(){
      sort(list.begin(),list.end(),[](const pair<int, filesystem::path> &alpha,const pair<int, filesystem::path> &beta){return alpha.first > beta.first;});
      return;
    }
    void save_imgs(){
      int file_count = 0;
      for (const auto& entry : list){
        save_one_img(entry.second, file_count);
        file_count++;
      }
    }
  private:
    filesystem::path input_dir;
    filesystem::path output_dir;
    vector<pair<int, filesystem::path>> list;

    void save_one_img(filesystem::path filepath, int file_count){
      Mat img = imread(filepath.string());
      filesystem::path filename = "img_" + to_string(file_count) + ".jpg";
      filesystem::path output_path = output_dir / filename;
      imwrite(output_path.string(), img);
    }
    vector<Vec3b> get_all_pixels(Mat img, int num_samples=1){
      vector<Vec3b> all_pixels;
      int height = img.rows;
      int width = img.cols;

      for (int i = 0; i < height; i+=num_samples){
        for (int j = 0; j < width; j+=num_samples){
          Vec3b pixel = img.at<Vec3b>(i, j);
          all_pixels.push_back(pixel);
        }
        
      }
      return all_pixels;
    }
};

int main(int argc, char* argv[]){
  if (argc < 2){
      printf("使用方法: python script.py [出力ディレクトリ (オプション)] <入力ディレクトリ1> <入力ディレクトリ2> ...");
      exit(1);
  }
  filesystem::path output_dir = "output_dir";
  filesystem::path output_temp = string(argv[1]);
  vector<filesystem::path> input_dirs;
  vector<pair<int, filesystem::path>> images_list;

  int num_samples = 5;

  if (argc == 2){
    input_dirs.push_back(string(argv[1]));
  } else {
    if (filesystem::exists(output_temp) && filesystem::is_directory(output_temp)){
      for (int i = 1; i < argc; i++)
        input_dirs.push_back(string(argv[i]));
    } else {
      output_dir = string(argv[1]);
      for (int i = 2; i < argc; i++)
        input_dirs.push_back(string(argv[i]));
    }
  }

  if (!filesystem::exists(output_dir))
    filesystem::create_directory(output_dir);

  unordered_map<string, Mat> image_map;

  if (input_dirs.size() == 1) {
    Images list_operate(input_dirs[0], output_dir);
    list_operate.resol_sort();
    list_operate.save_imgs();
  } else {
    for (const auto& dir : input_dirs) {
      Images list_operate(dir);
      vector<pair<int, filesystem::path>> list_temp = list_operate.get_list();
      for (const auto& item : list_temp) {
        Mat img = imread(item.second.string());
        image_map[item.second.string()] = img;
      }
        images_list.insert(images_list.end(), list_temp.begin(), list_temp.end());
    }
    Images list_operate_last(images_list, output_dir);

    int i = 0;
    while (i < list_operate_last.get_list_size()) {
      string a = list_operate_last.get_list()[i].second.string();
      cout << a << std::endl;
      auto it = remove_if(
        images_list.begin() + i + 1,
        images_list.end(),
        [&](const pair<int, filesystem::path>& item) {
          const string& b = item.second.string();
          return list_operate_last.is_same_image(image_map[a], image_map[b], num_samples);
        }
      );
      images_list.erase(it, images_list.end());
      list_operate_last.set_list(images_list);
      i++;
    }
    list_operate_last.set_list(images_list);
    list_operate_last.resol_sort();
    list_operate_last.save_imgs();
  }
  return 0;
}