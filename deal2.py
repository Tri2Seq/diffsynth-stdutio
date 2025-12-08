import cv2
import numpy as np
import os
from pathlib import Path
import imagehash
from PIL import Image

def calculate_phash(image_path):
    """
    计算图片的感知哈希值（pHash）
    :param image_path: 图片路径
    :return: 感知哈希值（imagehash.ImageHash对象）
    """
    try:
        # 用PIL读取图片（兼容更多格式），转为灰度图
        img = Image.open(image_path).convert("L")
        # 计算pHash，hash_size越小，哈希值越短，计算越快（默认8，生成64位哈希）
        phash = imagehash.phash(img, hash_size=8)
        return phash
    except Exception as e:
        print(f"计算哈希失败：{image_path}，错误：{e}")
        return None

def calculate_clarity(image_path):
    """
    拉普拉斯方差法计算图片清晰度评分
    :param image_path: 图片路径
    :return: 清晰度评分（方差值），若读取失败返回0
    """
    img = cv2.imread(image_path)
    if img is None:
        return 0
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    clarity_score = np.var(laplacian)
    return clarity_score

def calculate_hamming_distance(hash1, hash2):
    """
    计算两个哈希值的汉明距离
    :param hash1, hash2: 感知哈希值（imagehash.ImageHash对象）
    :return: 汉明距离（越小越相似）
    """
    if hash1 is None or hash2 is None:
        return float("inf")  # 哈希计算失败，视为不相似
    return hash1 - hash2

def process_duplicate_frames(input_dir, output_dir, similarity_threshold=10):
    """
    处理视频截帧，去除相似帧并保留更清晰的图片
    :param input_dir: 原始图片文件夹路径
    :param output_dir: 去重后保存的文件夹路径
    :param similarity_threshold: 相似度阈值（汉明距离≤该值为相似帧）
    """
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 1. 获取文件夹内所有图片，按文件名排序（保证视频截帧的顺序）
    img_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]
    img_paths = [
        os.path.join(input_dir, f) for f in os.listdir(input_dir)
        if Path(f).suffix.lower() in img_extensions
    ]
    # 按文件名排序（关键：保证视频截帧的时间顺序）
    img_paths.sort(key=lambda x: os.path.basename(x))

    if len(img_paths) == 0:
        print("文件夹中未找到图片！")
        return

    # 2. 初始化：保留第一张图片作为基准，遍历后续图片
    saved_img_path = img_paths[0]  # 已保存的基准图片路径
    saved_phash = calculate_phash(saved_img_path)  # 基准图片的哈希值
    saved_clarity = calculate_clarity(saved_img_path)  # 基准图片的清晰度

    # 保存第一张图片
    save_name = os.path.basename(saved_img_path)
    cv2.imwrite(os.path.join(output_dir, save_name), cv2.imread(saved_img_path))
    print(f"初始保存：{save_name}，清晰度：{saved_clarity:.2f}")

    # 3. 从第二张开始遍历，逐张对比
    for current_img_path in img_paths[1:]:
        current_name = os.path.basename(current_img_path)
        current_phash = calculate_phash(current_img_path)
        current_clarity = calculate_clarity(current_img_path)

        # 计算与基准图片的汉明距离
        hamming_dist = calculate_hamming_distance(saved_phash, current_phash)
        print(f"\n对比：{saved_img_path.split('/')[-1]} vs {current_name}")
        print(f"汉明距离：{hamming_dist}，当前图片清晰度：{current_clarity:.2f}")

        if hamming_dist <= similarity_threshold:
            # 相似帧：保留清晰度更高的图片
            if current_clarity > saved_clarity:
                # 当前图片更清晰：删除原基准图片，保存当前图片作为新基准
                os.remove(os.path.join(output_dir, os.path.basename(saved_img_path)))
                cv2.imwrite(os.path.join(output_dir, current_name), cv2.imread(current_img_path))
                print(f"替换：{current_name} 更清晰，已替换原基准图片")
                # 更新基准信息
                saved_img_path = current_img_path
                saved_phash = current_phash
                saved_clarity = current_clarity
            else:
                # 当前图片更模糊：跳过，保留原基准
                print(f"跳过：{current_name} 模糊，保留原基准图片")
        else:
            # 非相似帧：保存当前图片，作为新的基准
            cv2.imwrite(os.path.join(output_dir, current_name), cv2.imread(current_img_path))
            print(f"保存：{current_name} 为新基准，与原基准非相似帧")
            # 更新基准信息
            saved_img_path = current_img_path
            saved_phash = current_phash
            saved_clarity = current_clarity

    print(f"\n处理完成！去重后图片保存在：{output_dir}")
    print(f"原始图片数量：{len(img_paths)}，去重后数量：{len(os.listdir(output_dir))}")

# 主函数调用
if __name__ == "__main__":
    input_dirs = ["/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/no other choice","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/the roses","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/nouvelle","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/legs","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/frankenstein"]
    # 配置参数（根据实际情况修改）
    for i in range(len(input_dirs)):

        SIMILARITY_THRESHOLD = 10  # 相似性阈值（汉明距离），可调整

        # 执行去重处理
        process_duplicate_frames(input_dirs[i], f"{input_dirs[i]}_dedup", SIMILARITY_THRESHOLD)