import torch
from diffsynth.pipelines.flux_image_new import FluxImagePipeline, ModelConfig
from PIL import Image
import os
import json
import shutil
from tqdm import tqdm

base_dirs=["/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/no_other_choice","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/the_roses","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/nouvelle","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/legs","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/frankenstein"]
for i in range(len(base_dirs)):
    pipe = FluxImagePipeline.from_pretrained(
        torch_dtype=torch.bfloat16,
        device="cuda:0",# 改1
        model_configs=[
                ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="flux1-kontext-dev.safetensors"),
                ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="text_encoder/model.safetensors"),
                ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="text_encoder_2/"),
                ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="ae.safetensors"),
            ],
    )
    pipe.load_lora(pipe.dit, f"models/train/FLUX.1_lora_1126/epoch-0.safetensors", alpha=1) # 改 2
    # print("load lora successfully")
    step = 10
    input_path = f"{base_dirs[i]}_dedup" # 改3
    base_path = f"{base_dirs[i]}_train" # 改4
    save_path = f"{base_path}/epoch0" # 改5
    save_path_GT = f"{base_path}/GT" # 改6
    os.makedirs(save_path, exist_ok=True)
    os.makedirs(save_path_GT, exist_ok=True)
    for img in tqdm(os.listdir(input_path)):
        shutil.copy2(os.path.join(input_path,img),os.path.join(save_path_GT,img))
    # 改7
    prompt="Convert this image into a line art style: retain the original scenes and characters unchanged, present it as a black-and-white sketch effect, and make it suitable for storyboard design. Requirements: use bold and powerful lines, highlight structures and textures with concise strokes, adopt a style close to comic sketching, roughly outline the scenes and character movements with simple lines, prohibit the depiction of details, and represent the characters' facial features with the simplest lines.",
    # prompt = "convert this sketch into real film photos, each photo are consisted of 6 small pictures"
    print("finished copy gt")
    for fig in os.listdir(input_path):
        # if not fig.endswith(".png") or not fig.endswith(".jpg"):
        #     continue
        if os.path.exists(os.path.join(save_path,fig)):
            continue
        print("begin infer")
        image = pipe(
            prompt = prompt,
            kontext_images=Image.open(os.path.join(input_path,fig)).resize(( 768,768)),# 改8
            height=768, width=768,# 改9
            seed=0,
            num_inference_steps=step
        )
        image.save(os.path.join(save_path,fig))

# for i in range(1):
#     pipe = FluxImagePipeline.from_pretrained(
#     torch_dtype=torch.bfloat16,
#     device="cuda",
#     model_configs=[
#             ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="flux1-kontext-dev.safetensors"),
#             ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="text_encoder/model.safetensors"),
#             ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="text_encoder_2/"),
#             ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="ae.safetensors"),
#         ],
#     )
#     pipe.load_lora(pipe.dit, f"models/train/FLUX.1_lora_spotlight_1203/epoch-{i}.safetensors", alpha=1)
#     step = 5
#     base_path = f"/fi-lib/workspace/sjx/DiffSynth-Studio/validate_result/t2i_1203_STE_{step}"
#     save_path = f"{base_path}/epoch{i}"
#     os.makedirs(save_path, exist_ok=True)
#     with open("nano_comprehension_1201.txt", "r") as f:
#         prompts = f.readlines()
#         for prompt in prompts:
#             prompt = prompt.strip()
#             if prompt == "":
#                 continue
#             prompt_dict = json.loads(prompt)
#             fig = f"{prompt_dict["Image_Name"]}.png"
#             del prompt_dict["Image_Name"]
#             prompt = json.dumps(prompt_dict, ensure_ascii=False)
#             image = pipe(
#                 prompt ="draw a flower",
#                 height=768, width=768,
#                 seed=0,
#                 num_inference_steps=step
#             )
#             image.save(os.path.join(save_path,fig))
    