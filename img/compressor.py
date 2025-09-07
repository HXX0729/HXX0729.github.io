import os
import sys
from PIL import Image

# --- 配置区 ---
# 1. 新增：文件大小阈值 (单位: KB)。只有大于这个大小的图片才会被压缩。
MIN_SIZE_TO_COMPRESS_KB = 600

# 2. JPG 压缩质量 (1-95，数值越小体积越小，质量越差。推荐 75-85)
JPG_QUALITY = 80

# 3. 是否处理子文件夹
PROCESS_SUBFOLDERS = True

# 4. 脚本将处理其所在的当前文件夹
TARGET_FOLDER = '.' # '.' 代表当前目录
# --- 配置区结束 ---

def compress_image_inplace(file_path):
    """原地压缩单个图片"""
    try:
        # 检查文件是否为脚本本身
        if file_path == os.path.abspath(__file__):
            return None

        file_extension = os.path.splitext(file_path)[1].lower()
        if not file_extension in ['.jpg', '.jpeg', '.png']:
            return None # 跳过不支持的格式

        original_size = os.path.getsize(file_path)

        # --- 新增的大小判断逻辑 ---
        if original_size < (MIN_SIZE_TO_COMPRESS_KB * 1024):
            print(f"  [跳过] 文件小于 {MIN_SIZE_TO_COMPRESS_KB} KB，无需压缩。")
            return None
        # --- 判断结束 ---

        # 打开图片
        with Image.open(file_path) as img:
            # 如果是 JPG 且模式不对，进行转换
            if file_extension in ['.jpg', '.jpeg']:
                if img.mode in ('RGBA', 'P'):
                    temp_path = file_path + ".tmp.jpg"
                    img.convert('RGB').save(temp_path, 'JPEG', quality=JPG_QUALITY, optimize=True)
                    os.replace(temp_path, file_path)
                else:
                    img.save(file_path, 'JPEG', quality=JPG_QUALITY, optimize=True)
            # 如果是 PNG
            elif file_extension == '.png':
                img.save(file_path, 'PNG', optimize=True)

        compressed_size = os.path.getsize(file_path)
        
        if compressed_size < original_size:
            return original_size, compressed_size
        else:
            return None

    except Exception as e:
        print(f"  [错误] 处理失败: {os.path.basename(file_path)}, 原因: {e}")
        return None

def main():
    """主函数"""
    print(f"--- 开始原地压缩图片 ---")
    print(f"目标文件夹: {os.path.abspath(TARGET_FOLDER)}")
    print(f"将只压缩大于 {MIN_SIZE_TO_COMPRESS_KB} KB 的图片")
    print("警告: 此操作将直接覆盖原始文件！")
    print("-" * 20)

    total_files = 0
    total_original_size = 0
    total_compressed_size = 0

    if PROCESS_SUBFOLDERS:
        for root, _, files in os.walk(TARGET_FOLDER):
            # 排序文件以保证处理顺序一致
            files.sort()
            for filename in files:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, TARGET_FOLDER)
                
                print(f"扫描中: {relative_path}")
                result = compress_image_inplace(file_path)
                
                if result:
                    original_size, compressed_size = result
                    total_files += 1
                    total_original_size += original_size
                    total_compressed_size += compressed_size
                    ratio = (original_size - compressed_size) / original_size * 100
                    print(f"  [成功] {original_size/1024:.1f} KB -> {compressed_size/1024:.1f} KB (节省 {ratio:.1f}%)")

    print("-" * 20)
    if total_files > 0:
        total_ratio = (total_original_size - total_compressed_size) / total_original_size * 100 if total_original_size > 0 else 0
        print(f"处理完成！共压缩 {total_files} 个图片。")
        print(f"总大小: {total_original_size/1024/1024:.2f} MB -> {total_compressed_size/1024/1024:.2f} MB")
        print(f"总体积节省: {total_ratio:.1f}%")
    else:
        print("未找到需要压缩的大于阈值的图片。")

if __name__ == '__main__':
    try:
        from PIL import Image
    except ImportError:
        print("错误: Pillow 库未安装。请运行 'pip install Pillow'")
        sys.exit(1)
    main()