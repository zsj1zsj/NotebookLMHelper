import shutil
import os


def read_file_list(file_path, path_prefix):
    """从 txt 文件中读取文件路径列表并加上前缀"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 去除每行的换行符并加上前缀
            return [os.path.join(path_prefix, line.strip()) for line in f.readlines()]
    except Exception as e:
        print(f"读取文件列表时出错: {e}")
        return []


def copy_files(file_list, target_dir):
    """将文件列表中的文件拷贝到目标目录"""
    # 确保目标目录存在，不存在则创建
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    successful_copies = 0
    failed_files = []

    for file in file_list:
        if os.path.exists(file):
            try:
                shutil.copy(file, target_dir)
                successful_copies += 1
            except Exception as e:
                failed_files.append((file, str(e)))
        else:
            failed_files.append((file, "文件不存在"))

    # 总结输出
    print(f"共拷贝 {len(file_list)} 个文件。")
    print(f"成功拷贝 {successful_copies} 个文件。")

    if failed_files:
        print("以下文件拷贝失败：")
        for file, error in failed_files:
            print(f"{file} - 错误: {error}")
    else:
        print("所有文件拷贝成功！")


# 从 txt 文件中读取文件路径列表
path_prefix = '/Users/lynn/Library/CloudStorage/Dropbox/Private/obsidian/personal/'
file_list_path = "/Users/lynn/Downloads/clippings.txt"  # 请替换为你的文件路径
file_list = read_file_list(file_list_path, path_prefix)
# 目标目录
destination = "/Users/lynn/Documents/notebooklm/"

# 调用函数进行文件拷贝
copy_files(file_list, destination)
