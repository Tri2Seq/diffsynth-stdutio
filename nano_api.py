import io
import requests
import json
import base64
import re
import os
import os.path as osp
import datetime
from typing import Optional, Tuple
from PIL import Image
from io import BytesIO
from tqdm import tqdm
# from api_class.utils import base64_to_image,encode_pil_to_base64
def encode_pil_to_base64(image_pil):
    # 将PIL图像编码为base64字符串
    buffered = BytesIO()
    image_pil.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    mime_type = "image/png"
    return img_base64, mime_type

def base64_to_image(base64_str):
    # 将base64字符串解码为PIL图像
    img_bytes = base64.b64decode(base64_str)
    image_pil = Image.open(BytesIO(img_bytes))
    return image_pil
class GeminiImageGenerator:
    def __init__(self,  api_url: str = "https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent"):
        self.api_key = "sk-ooPY7VxCXOfumS59E5E4E21474E54c32866b08D62b11D29e"
        self.api_url = api_url
        self.api_url_compre="https://api.apiyi.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.SUPPORTED_ASPECT_RATIOS = [
        "21:9", "16:9", "4:3", "3:2", "1:1",
        "9:16", "3:4", "2:3", "5:4", "4:5"]
        
        self.SUPPORTED_RESOLUTION=["1K","2K","4K"]

    def nano_imageEditing(self,data_dict):
        required_keys = {"prompt","image_list","ratio","resolution"}
        assert required_keys <= data_dict.keys(), \
            f"缺少必要字段，必须包含: {required_keys}，实际提供: {list(data_dict.keys())}"
        ratio=data_dict["ratio"]
        resolution=data_dict["resolution"]
        assert ratio in self.SUPPORTED_ASPECT_RATIOS, f"不支持的比例,支持比例为{self.SUPPORTED_ASPECT_RATIOS}"
        assert resolution in self.SUPPORTED_RESOLUTION,f"不支持的分辨率,支持分辨率为{self.SUPPORTED_RESOLUTION}"
        prompt=data_dict["prompt"]
        img_payload=[]
        for image_pil in data_dict["image_list"]:
            image_pil = Image.open(image_pil)
            image_base64, mime_type=encode_pil_to_base64(image_pil)
            img_payload.append({
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_base64
                            }
                        })
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]+img_payload
                }]
            }

            if ratio:
                payload["generationConfig"] = {
                    "responseModalities": ["IMAGE"],
                    "imageConfig": {
                        "aspectRatio": ratio,
                        "image_size": resolution
                    }
                }

            print("📡 发送请求到 Gemini API...")
            # 发送非流式请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            print("✅ API请求成功，正在解析响应...")
            
            # 解析非流式JSON响应
            try:
                result = response.json()
                print("✅ 成功解析JSON响应")
            except json.JSONDecodeError as e:
                return False, f"JSON解析失败: {str(e)}",None
            
            if "candidates" not in result or len(result["candidates"]) == 0:
                return False, "未找到图片数据", None

            candidate = result["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"]:
                return False, "响应格式错误",None

            parts = candidate["content"]["parts"]
            output_image_data = None

            for part in parts:
                if "inlineData" in part and "data" in part["inlineData"]:
                    output_image_data = part["inlineData"]["data"]
                    break

            if not output_image_data:
                return False, "未找到图片数据",None
            
            try:            
                pil_img=base64_to_image(output_image_data)
                return pil_img
            except Exception as e:
                raise ValueError(f"图片加载失败: {e}")
    
                
        except requests.exceptions.Timeout:
            raise RuntimeError("请求超时（300秒）")
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"连接错误: {str(e)}")
        except Exception as e:
            raise ValueError(f"未知错误: {str(e)}")



    def nano_text2image(self, data_dict) :
        required_keys = {"prompt", "ratio","resolution"}
        assert required_keys <= data_dict.keys(), \
            f"缺少必要字段，必须包含: {required_keys}，实际提供: {list(data_dict.keys())}"
        ratio=data_dict["ratio"]
        assert ratio in self.SUPPORTED_ASPECT_RATIOS, f"不支持的比例,支持比例为{self.SUPPORTED_ASPECT_RATIOS}"
        
        prompt="帮我生成图片,图片提示词如下: "+data_dict["prompt"]
        resolution=data_dict["resolution"]
        print("🚀 开始生成图片...")
        print(f"提示词: {prompt}")

        try:
            # 构建请求数据
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }

            if ratio:
                payload["generationConfig"] = {
                    "responseModalities": ["IMAGE"],
                    "imageConfig": {
                        "aspectRatio": ratio,
                        "image_size": resolution
                    }
                }

            print("📡 发送请求到 Gemini API...")
            # 发送非流式请求

            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f", 错误详情: {error_detail}"
                except:
                    error_msg += f", 响应内容: {response.text[:500]}"
                return False, error_msg,None
            
            print("✅ API请求成功，正在解析响应...")
            
            # 解析非流式JSON响应
            try:
                result = response.json()
                print("✅ 成功解析JSON响应")
            except json.JSONDecodeError as e:
                return False, f"JSON解析失败: {str(e)}",None
            
            #提取图片数据
            if "candidates" not in result or len(result["candidates"]) == 0:
                return False, "未找到图片数据",None

            candidate = result["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"]:
                return False, "响应格式错误",None

            parts = candidate["content"]["parts"]
            image_data = None

            for part in parts:
                if "inlineData" in part and "data" in part["inlineData"]:
                    image_data = part["inlineData"]["data"]
                    break

            if not image_data:
                return False, "未找到图片数据",None
            try:            
                pil_img=base64_to_image(image_data)
                return pil_img
            except Exception as e:
                raise ValueError(f"图片加载失败: {e}")
                
        except requests.exceptions.Timeout:
            raise RuntimeError("请求超时（300秒）")
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"连接错误: {str(e)}")
        except Exception as e:
            raise ValueError(f"未知错误: {str(e)}")

    def _extract_image_from_base64(self,content: str) -> Tuple[bool, Optional[Image.Image], str]:
        """
        高效提取base64图片并返回PIL Image对象
        
        Args:
            content: 包含图片数据的内容
            
        Returns:
            Tuple[是否成功, PIL Image对象(或None), 消息]
        """
        try:
            print(f"📄 内容预览（前200字符）: {content[:200]}")
            
            # 匹配 base64 图片数据
            base64_pattern = r'data:image/([^;]+);base64,([A-Za-z0-9+/=]+)'
            match = re.search(base64_pattern, content)
            
            if not match:
                print('⚠️  未找到base64图片数据')
                raise ValueError("No image founded!")
            
            image_format = match.group(1)
            b64_data = match.group(2)
            
            print(f'🎨 图像格式: {image_format}')
            print(f'📏 Base64数据长度: {len(b64_data)} 字符')
            
            # 解码 base64
            image_data = base64.b64decode(b64_data)
            
            if len(image_data) < 100:
                return False, None, "解码后的图片数据太小，可能无效"
            
            # 使用 PIL 读取图像
            image = Image.open(io.BytesIO(image_data))
            print(f'🖼️ 图片加载成功，尺寸: {image.size}, 模式: {image.mode}')
            
            return True, image, f"成功提取图像 ({image_format})"
            
        except Exception as e:
            return False, None, f"处理图片时发生错误: {str(e)}"

    def nano_image_comprehension(self, data_dict,prompt):
        required_keys = {"image"}
        assert required_keys <= data_dict.keys(), \
            f"缺少必要字段，必须包含: {required_keys}，实际提供: {list(data_dict.keys())}"
        im=data_dict["image"]
        im = Image.open(im)
        im_base64,_=encode_pil_to_base64(im)
        headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        # Prepare payload - generated image first, then ground truth
        payload = {
            "model": "gemini-2.5-flash",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": im_base64}
                        },
                    ]
                }
            ],
            "max_tokens": 5000
        }

        # Make API call
        response = requests.post(self.api_url_compre, headers=headers, json=payload, timeout=600)
        response.raise_for_status()

            
        # Extract response content
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        
        print(content)
        return content

if __name__=="__main__":
    g = GeminiImageGenerator()
    # 描述性提示词（根据需要修改）
    prompt = """You are a storyteller skilled in interpreting visual narratives. You can extract core information from storyboard images, organize a complete story logic, supplement rich and contextually fitting detailed descriptions, and possess rigorous JSON format output capabilities. Based on the 6 storyboard images I provide (arranged in 3 rows and 2 columns, ordered from left to right and top to bottom), first organize the complete story structure collectively told by the images, then generate corresponding visual descriptions for each image. Strictly output in the following JSON format, ensuring coherent story logic, accurate visual details, and concise responses:
{"story_summary": "Briefly narrate the story thread connected by the 6 images in 10-20 words","storyboard_list": [{"shot_number": 1,"visual_content": "Detailedly describe the scene environment (light, color, prop arrangement), characters (appearance, clothing, gestures, facial expressions), and key details (e.g., items held by characters, special symbols in the background, light and shadow changes) in the image. You can supplement reasonable details based on existing image elements to make the scene more vivid (less than 30 words)"},{"shot_number": 2,"visual_content": "Same as above"}]}"""
    base_dirs = [
            "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/no_other_choice",
            "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/the_roses"
            "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/nouvelle",
            "/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/frankenstein"
        ]
    issues0=[52,292,308,344,357] # no other choice 362
    issues1=[32,291,298,300,301,301] # the roses 302
    issues2=[31,40,96] # nouvelle 96 
    issues3=[32,291,298,300,301,301] # frankenstein 462




    for k in range(len(base_dirs)):
        print(base_dirs[k])
        # INPUT_DIR = "dataset/no_other_choice_train/GT_cat"
        INPUT_DIR = f"{base_dirs[k]}_train/GT_cat"
        # OUTPUT_DIR = "dataset/no_other_choice_train"
        OUTPUT_DIR =f"{base_dirs[k]}_train"

        RATIO = "16:9"
        # 对输入文件夹内的图片进行排序处理

        output_path = os.path.join(OUTPUT_DIR, "GT_cat_i2t.txt")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        input_files = sorted(
            fname for fname in os.listdir(INPUT_DIR)
            if os.path.isfile(os.path.join(INPUT_DIR, fname))
        )

        for idx, fname in tqdm(enumerate(input_files), total=len(input_files)):
            print(idx,fname)

            # if idx < 37 :
            #     print(fname)
            #     continue
            src_path = os.path.join(INPUT_DIR, fname)
            # 调用nano_image_comprehension
            # try:
            # pil_in = Image.open(src_path).convert("RGB")
            base_name = os.path.splitext(fname)[0]
            if base_name.startswith("merged_"):
                num = int(fname.split("_")[1].strip(".png"))
                if num not in f"issues{k}":
                    print("not inssue")
                    continue
            try:
                result = g.nano_image_comprehension({
                    "image": src_path,
                },prompt)
            except Exception as e:
                print(f"处理文件 {fname} 时出错: {e}")
                continue
            with open(output_path, "a", encoding="utf-8") as f:
                result = result.replace("\n", "")
                result = result.replace("```", "")
                result = result.replace("json", "")
                result = result.replace('"story_summary"', f'"Image_Name": "{base_name}", "story_summary"')

                f.write(result.strip("\n") + "\n")
            