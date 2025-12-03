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
        self.api_key = "sk-MC5B3H948s5YhiVN591f578fC74a4eC484659cC6005bB603"
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
    prompt = """You are a concise storyboard narrator focused on core scene and composition description. Based on the 1 vertically stitched image containing multiple storyboards (identified as Storyboard 1 to Storyboard N in top-to-bottom order, N = actual number), output ONLY a simple story background and concise composition descriptions for each shot. Strictly follow the JSON format below, with each "Image Composition" limited to ~100 words:
{"Simple Story Background": "1-2 sentences summarizing the basic story context (e.g., 'A girl searches for her lost cat in a suburban neighborhood on a sunny afternoon')","Storyboard_List": [{"Shot Number": 1,"Scene": "Specific location (e.g., front yard of a cottage, forest trail, downtown café)","Image Composition": "Concise description of characters (appearance, posture), key props, framing (shot type: close-up/medium/long/wide), lighting, and core visual elements (max 100 words)","Emotional Tone": "Brief atmosphere (e.g., warm, tense, peaceful)"},{"Shot Number": N,"Scene": "Same as above","Image Composition": "Same as above (max 100 words)","Emotional Tone": "Same as above"}]}
Requirements
All fields are mandatory; no redundant content.
"Image Composition" focuses only on critical visual information (characters, framing, key props, lighting) – no excessive details.
Strictly match the number/order of storyboards in the image (top-to-bottom numbering).
JSON format must be error-free, ready for direct use.
No extra text outside the JSON structure."""

    INPUT_DIR = "dataset/spotlight_sketch_cat/GT"
    OUTPUT_DIR = "dataset/spotlight_sketch_cat"
    RATIO = "16:9"
    # 对输入文件夹内的图片进行排序处理

    output_path = os.path.join(OUTPUT_DIR, "spotlight_nano_comprehension_1203.txt")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    input_files = sorted(
        fname for fname in os.listdir(INPUT_DIR)
        if os.path.isfile(os.path.join(INPUT_DIR, fname))
    )

    for idx, fname in tqdm(enumerate(input_files), total=len(input_files)):
        src_path = os.path.join(INPUT_DIR, fname)
        # 调用nano_image_comprehension
        # try:
        # pil_in = Image.open(src_path).convert("RGB")

        result = g.nano_image_comprehension({
            "image": src_path,
        },prompt)
        base_name = os.path.splitext(fname)[0]
        with open(output_path, "a", encoding="utf-8") as f:
            result = result.replace("\n", "")
            result = result.replace("```", "")
            result = result.replace("json", "")
            result = result.replace('"Simple Story Background"', f'"Image_Name": "{base_name}", "Simple Story Background"')

            f.write(result.strip("\n") + "\n")
        # except Exception as e:
        #     print(f"处理文件 {fname} 时出错: {e}")