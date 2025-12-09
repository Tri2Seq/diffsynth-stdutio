input_dir = "dataset/datasets/dataset"
out_put_txt = "dataset/datasets/sketch2real.txt"
IMG_SUFFIX = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
import os
 
with open(out_put_txt, 'w', encoding='utf-8') as f:
    pass

# 遍历_train结尾的子文件夹
for sub_dir in os.listdir(input_dir):
    sub_dir_path = os.path.join(input_dir, sub_dir)
    if os.path.isdir(sub_dir_path) and sub_dir.endswith('_train'):
        gt_dir = os.path.join(sub_dir_path, 'GT_cat')
        epoch0_dir = os.path.join(sub_dir_path, 'epoch0_cat')
        
        # 1. 读取并筛选GT/epoch0下的图片文件（仅保留文件，过滤文件夹）
        def get_sorted_img_paths(dir_path):
            if not os.path.exists(dir_path):
                return []
            # 筛选图片文件 + 按文件名排序
            img_files = [f for f in os.listdir(dir_path) 
                         if os.path.isfile(os.path.join(dir_path, f)) and f.lower().endswith(IMG_SUFFIX)]
            img_files.sort()  # 按文件名字典序排序
            return [os.path.join(dir_path, f) for f in img_files]
        
        gt_paths = get_sorted_img_paths(gt_dir)
        epoch0_paths = get_sorted_img_paths(epoch0_dir)
        
        # 2. 按排序后的文件名逐行写入（同名图片必在同一行）
        # 取所有唯一文件名（兼容两边文件数量不一致的情况）
        all_filenames = sorted(set(
            [os.path.basename(p) for p in gt_paths] + 
            [os.path.basename(p) for p in epoch0_paths]
        ))
        
        with open(out_put_txt, 'a', encoding='utf-8') as f:
            for filename in all_filenames:
                # 匹配对应路径（无则为空）
                gt_path = os.path.join(gt_dir, filename) if filename in [os.path.basename(p) for p in gt_paths] else ''
                epoch0_path = os.path.join(epoch0_dir, filename) if filename in [os.path.basename(p) for p in epoch0_paths] else ''
                f.write(f"{gt_path}\t{epoch0_path}\n")