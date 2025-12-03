import torch
from diffsynth.pipelines.flux_image_new import FluxImagePipeline, ModelConfig
from PIL import Image
import os
import json



# for i in range(2):
#     pipe.load_lora(pipe.dit, f"models/train/FLUX.1_lora_1126/epoch-{i}.safetensors", alpha=1)
#     step = 25
#     input_path = "dataset/multi_frame"
#     base_path = f"validate_result/multi_frame{step}"
#     save_path = f"{base_path}/epoch{i}"
#     save_path_GT = f"{base_path}/GT"
#     os.makedirs(save_path, exist_ok=True)
#     os.makedirs(save_path_GT, exist_ok=True)
#     for img in os.listdir(input_path):
#         image = Image.open(os.path.join(input_path,img))
#         image.save(os.path.join(save_path_GT,img))
#     prompt="Convert this image into a line art style: retain the original scenes and characters unchanged, present it as a black-and-white sketch effect, and make it suitable for storyboard design. Requirements: use bold and powerful lines, highlight structures and textures with concise strokes, adopt a style close to comic sketching, roughly outline the scenes and character movements with simple lines, prohibit the depiction of details, and represent the characters' facial features with the simplest lines.",
#     # prompt = "Convert this image into a mbti style"
#     for fig in os.listdir(input_path):
#         if not fig.endswith(".png"):
#             continue
#         image = pipe(
#             prompt = prompt,
#             kontext_images=Image.open(os.path.join(input_path,fig)).resize((768, 768)),
#             height=768, width=768,
#             seed=0,
#             num_inference_steps=step
#         )
#         image.save(os.path.join(save_path,fig))

for i in range(2):
    pipe = FluxImagePipeline.from_pretrained(
    torch_dtype=torch.bfloat16,
    device="cuda",
    model_configs=[
            ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="flux1-kontext-dev.safetensors"),
            ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="text_encoder/model.safetensors"),
            ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="text_encoder_2/"),
            ModelConfig(model_id="black-forest-labs/FLUX.1-Kontext-dev", origin_file_pattern="ae.safetensors"),
        ],
    )
    pipe.load_lora(pipe.dit, f"models/train/FLUX.1_lora_1126/epoch-{i}.safetensors", alpha=1)
    step = 25
    base_path = "/fi-lib/workspace/sjx/DiffSynth-Studio/validate_result/t2i_1201{step}"
    save_path = f"{base_path}/epoch{i}"
    os.makedirs(save_path, exist_ok=True)
    with open("nano_comprehension_1201.txt", "r") as f:
        prompts = f.readlines()
        for prompt in prompts:
            prompt = prompt.strip()
            if prompt == "":
                continue
            prompt_dict = json.loads(prompt)
            fig = f"{prompt_dict["Image_Name"]}.png"
            del prompt_dict["Image_Name"]
            prompt = json.dumps(prompt_dict, ensure_ascii=False)
            image = pipe(
                prompt = prompt,
                height=768, width=768,
                seed=0,
                num_inference_steps=step
            )
            image.save(os.path.join(save_path,fig))
    