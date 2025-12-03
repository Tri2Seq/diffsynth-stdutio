
# import os
# render2real_path = "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/spotlight_sketch/epoch0"
# sketch_enhance_body_path = "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/spotlight_sketch/GT"
# render2real_files = set(os.listdir(render2real_path))
# sketch_enhance_body_files = set(os.listdir(sketch_enhance_body_path))
# for file in render2real_files:
#     if file not in sketch_enhance_body_files:
#         print(f"Removing {file} from render2real_path")
#         os.remove(os.path.join(render2real_path, file))
# for file in sketch_enhance_body_files:
#     if file not in render2real_files:
#         print(f"Removing {file} from sketch_enhance_body_path")
#         os.remove(os.path.join(sketch_enhance_body_path, file))

# import os
# input_path = "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/mbti/Realistic"
# for file in os.listdir(input_path):
#     # 把文件名称最后的_Realistic去掉
#     new_name = file.replace("_Realistic", "")
#     os.rename(os.path.join(input_path, file), os.path.join(input_path, new_name))

# import os
# for file in os.listdir("dataset/spotlight_sketch/GT"):
#     with open("dataset/spotlight_sketch/pairs.txt", "a") as f:  
#         # 目标图 原图          
#         f.write(f"GT/{file}\tepoch0/{file}\n")

import os
import json
from tqdm import tqdm
input_txt = "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/spotlight_sketch_cat/spotlight_nano_comprehension_1203.txt"
with open(input_txt, "r") as f:
    lines = f.readlines()
    for i in tqdm(range(len(lines))):
        data = json.loads(lines[i])   
        fig_id = f"{data['Image_Name']}.png"
        del data["Image_Name"]
        input_dir = "dataset/spotlight_sketch_cat/epoch0"
        for file in os.listdir(input_dir): 
            if fig_id in file:
                with open("dataset/spotlight_sketch_cat/pairs.txt", "a") as f:
                    f.write(f"{input_dir}/{file}\t{data}\n")

# 把文件夹中的图片每六张拼成一个3行两列的大图，保存到另一个文件夹中，原图拼接不要截图
# import os
# from PIL import Image
# from tqdm import tqdm
# import numpy as np
# input_path = "dataset/spotlight_sketch/epoch0"
# save_path = "dataset/spotlight_sketch_cat/epoch0"
# os.makedirs(save_path, exist_ok=True)
# files = os.listdir(input_path)
# files.sort()
# for i in tqdm(range(0, len(files), 6)):
#     # 按照原图拼接，不做裁剪
#     merged_image = np.zeros((3 * 512, 2 * 512, 3), dtype=np.uint8)
#     for j in range(6):
#         if i + j < len(files):
#             img = Image.open(os.path.join(input_path, files[i + j])).resize((512, 512),resample=Image.LANCZOS)
#             row = j // 2
#             col = j % 2
#             merged_image[row * 512:(row + 1) * 512, col * 512:(col + 1) * 512, :] = np.array(img)
#     Image.fromarray(merged_image).save(os.path.join(save_path, f'merged_{i//6}.png'))