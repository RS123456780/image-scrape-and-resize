cmake_minimum_required(VERSION 3.8)

project(example_delete_duplication)

# OpenCVのビルドディレクトリを指定
set(OpenCV_DIR C:/cpp_libraries/github/opencv/build)

# OpenCVを見つける
find_package(OpenCV REQUIRED)

add_executable(delete_duplication delete_duplication.cpp)

# 静的リンクの設定
set(BUILD_SHARED_LIBS OFF)

# 静的ランタイムライブラリを使用
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /MT")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /MTd")

# OpenCVライブラリをリンク
target_link_libraries(delete_duplication PRIVATE ${OpenCV_LIBS})

# C++17を指定
set_property(TARGET delete_duplication PROPERTY CXX_STANDARD 17)
set_property(TARGET delete_duplication PROPERTY CXX_STANDARD_REQUIRED ON)
set_property(TARGET delete_duplication PROPERTY CXX_EXTENSIONS OFF)