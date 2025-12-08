# ## 图片拼接：
# import os
# from PIL import Image
# from tqdm import tqdm
# import numpy as np


# def process_single_image(img_path, crop_size, resize_size):
#     """
#     单张图片处理：中心裁剪 → 补黑 → 下采样
#     :param img_path: 图片路径
#     :param crop_size: 裁剪尺寸 (w, h)
#     :param resize_size: 下采样尺寸 (w, h)
#     :return: 处理后的图片numpy数组
#     """
#     try:
#         img = Image.open(img_path).convert("RGB")
#         target_w, target_h = crop_size
#         img_w, img_h = img.size

#         # 中心裁剪
#         left = max(0, (img_w - target_w) // 2)
#         top = max(0, (img_h - target_h) // 2)
#         right = min(img_w, left + target_w)
#         bottom = min(img_h, top + target_h)
#         cropped = img.crop((left, top, right, bottom))
        
#         # 补黑到目标裁剪尺寸
#         new_img = Image.new("RGB", (target_w, target_h), (0, 0, 0))
#         new_img.paste(cropped, ((target_w - cropped.width) // 2, (target_h - cropped.height) // 2))
        
#         # 下采样（LANCZOS更适合缩小）
#         resized = new_img.resize(resize_size, resample=Image.LANCZOS)
#         return np.array(resized)
    
#     except Exception as e:
#         print(f"处理图片失败 {img_path}: {e}")
#         return np.zeros((resize_size[1], resize_size[0], 3), dtype=np.uint8)


# def merge_6_images(imgs_np_list, resize_size, line_width):
#     """
#     6张图片拼接：3行2列，尺寸完全由单张图+黑线自动计算
#     :param imgs_np_list: 图片numpy数组列表
#     :param resize_size: 单张图片尺寸 (w, h)
#     :param line_width: 黑线宽度
#     :return: 拼接后的numpy数组
#     """
#     # 补全6张图（不足填黑）
#     imgs_np_list = imgs_np_list[:6]
#     while len(imgs_np_list) < 6:
#         imgs_np_list.append(np.zeros((resize_size[1], resize_size[0], 3), dtype=np.uint8))

#     # 自动计算拼接后的总尺寸
#     img_w, img_h = resize_size
#     # 3行2列：宽度=2*单张宽 + 1*竖线宽；高度=3*单张高 + 2*横线宽
#     total_w = img_w * 2 + line_width
#     total_h = img_h * 3 + line_width * 2
    
#     # 初始化黑色画布（尺寸完全由拼接逻辑决定）
#     merged = np.zeros((total_h, total_w, 3), dtype=np.uint8)

#     # 逐个放置图片（精确计算位置，无越界）
#     for idx, img_np in enumerate(imgs_np_list):
#         row = idx // 2  # 0/1/2行
#         col = idx % 2   # 0/1列
        
#         # 计算当前图片的起始位置（含黑线偏移）
#         x_start = col * (img_w + line_width)
#         y_start = row * (img_h + line_width)
        
#         # 计算结束位置
#         x_end = x_start + img_w
#         y_end = y_start + img_h
        
#         # 赋值（确保图片尺寸匹配）
#         merged[y_start:y_end, x_start:x_end, :] = img_np[:img_h, :img_w, :]

#     return merged


# # 主流程
# if __name__ == "__main__":
#     # 核心配置（可根据需求调整）
#     base_dirs = [
#         "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/no_other_choice",
#         "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/the_roses",
#         "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/nouvelle",
#         "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/legs",
#         "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/frankenstein"
#     ]
    
#     # 单张图片处理配置
#     # crop_size = (1920, 800)    # 中心裁剪尺寸
#     # resize_size = (480, 200)   # 下采样尺寸（单张最终尺寸）
#     crop_size = (768, 768)    # 中心裁剪尺寸
#     resize_size = (768, 768)   # 下采样尺寸（单张最终尺寸）
#     line_width = 6             # 图片间黑线宽度

#     # 遍历每个数据集目录
#     for k in range(len(base_dirs)):
        
#         current_dir = base_dirs[k]
#         print(f"处理目录: {current_dir}")
        
#         # 定义输入输出路径
#         input_path = f"{current_dir}_train/epoch0"
#         save_path = f"{current_dir}_train/epoch0_cat"
#         os.makedirs(save_path, exist_ok=True)

#         # 获取输入目录下的图片列表（按名称排序）
#         img_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
#         files = [
#             f for f in os.listdir(input_path) 
#             if f.lower().endswith(img_extensions)
#         ]
#         files.sort()  # 保证拼接顺序稳定

#         # 无图片时跳过
#         if not files:
#             print(f"目录 {input_path} 下未找到图片，跳过")
#             continue

#         # 每6张图片拼接一次
#         for i in tqdm(range(0, len(files), 6), desc=f"拼接 {current_dir} 图片"):
#             # 读取并处理当前批次的图片
#             imgs_list = []
#             for j in range(6):
#                 if i + j < len(files):
#                     img_path = os.path.join(input_path, files[i+j])
#                     imgs_list.append(process_single_image(img_path, crop_size, resize_size))
            
#             # 拼接6张图片
#             merged_img_np = merge_6_images(imgs_list, resize_size, line_width)
            
#             # 保存拼接后的图片
#             save_name = f'merged_{i//6}.png'
#             save_full_path = os.path.join(save_path, save_name)
#             Image.fromarray(merged_img_np).save(save_full_path)

#     print("所有目录处理完成！")

## 对应文件夹文件清洗：



## nanobanana结果清洗：
import json
import os

# 目标文件路径
file_path = "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/frankenstein_train/GT_cat_i2t.txt"

# 初始化存储：key是数字，value是出现次数
num_count = {}
# 有效范围：1-362
valid_min = 0
valid_max = 461

# 第一步：读取文件，统计所有merged_数字的出现次数
if not os.path.exists(file_path):
    print(f"错误：文件 {file_path} 不存在！")
else:
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                # 解析JSON并提取Image_Name
                data = json.loads(line)
                img_name = data.get("Image_Name", "")
                
                # 提取merged_后的数字
                if img_name.startswith("merged_"):
                    num_str = img_name.split("_")[1]
                    if num_str.isdigit():
                        num = int(num_str)
                        # 统计出现次数
                        num_count[num] = num_count.get(num, 0) + 1
            except Exception as e:
                print(f"处理文件json{line} 时出错: {e}")
                continue

# 第二步：检查1-362缺失的数字
print("===== 缺失的数字（1-362） =====")
missing = []
for i in range(valid_min, valid_max + 1):
    if i not in num_count:
        missing.append(i)
        print(i)
if not missing:
    print("无缺失")

# 第三步：检查重复的数字（出现次数>1）
print("\n===== 重复的数字（出现次数>1） =====")
duplicate = [num for num, count in num_count.items() if count > 1]
if duplicate:
    for num in duplicate:
        print(f"{num}（出现{num_count[num]}次）")
else:
    print("无重复")

# 第四步：检查多余的数字（超出1-362范围）
print("\n===== 多余的数字（超出1-362） =====")
extra = [num for num in num_count.keys() if num < valid_min or num > valid_max]
if extra:
    for num in sorted(extra):
        print(num)
else:
    print("无多余")


            
        

