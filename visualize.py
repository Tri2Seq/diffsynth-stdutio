import os
import os.path as osp
import base64  # 新增：导入base64模块
from jinja2 import Environment, BaseLoader
step = 4
# 设置文件和文件夹路径
caption_visualized_folders = [
    f"test_1126_step4/GT",
    f"test_1126_step4/epoch0",
    f"test_1126_step10/epoch0",
    f"test_1126_step25/epoch0",
    f"test_1126_step{step}/epoch3",
    f"test_1126_step{step}/epoch4"
]

# 提取模型名称
model_names = ["GT",  "step4_epoth0", "step10_epoth0","step25_epoth0","epoch3","epoch4"]

# 图片格式映射：后缀名 -> MIME类型（用于Base64的data URI）
IMG_EXT_TO_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".webp": "image/webp"
}
IMG_EXTS = set(IMG_EXT_TO_MIME.keys())  # 复用格式集合

# 收集所有文件基名（stem）的并集，按字典序排序
all_basenames = set()
for folder in caption_visualized_folders:
    folder_local = osp.join(os.getcwd(), folder)
    if osp.isdir(folder_local):
        for fname in os.listdir(folder_local):
            ext = osp.splitext(fname)[1].lower()
            if ext in IMG_EXTS:
                all_basenames.add(osp.splitext(fname)[0])
    else:
        print(f"Warning: folder not found: {folder_local}")

res_data = []
for base in sorted(all_basenames):
    # 初始化前几个占位字段（模板主要使用索引后面的图片列）
    res_row_info = [base, base, base, base, base, base]

    # 对每个文件夹按基名查找对应的图片，编码为Base64
    for folder in caption_visualized_folders:
        base64_img = None  # 存储Base64编码后的图片字符串
        img_filename = None  # 存储图片文件名（用于显示）
        folder_local = osp.join(os.getcwd(), folder)
        
        if osp.isdir(folder_local):
            # 优先尝试常见扩展的有序匹配
            found = False
            for ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]:
                candidate = osp.join(folder_local, base + ext)
                if osp.isfile(candidate):
                    img_filename = base + ext
                    # 读取图片并编码为Base64
                    with open(candidate, "rb") as f:
                        img_data = f.read()
                        mime_type = IMG_EXT_TO_MIME[ext]
                        # 拼接Base64的data URI格式
                        base64_img = f"data:{mime_type};base64,{base64.b64encode(img_data).decode('utf-8')}"
                    found = True
                    break
            # 如果按扩展没有找到，尝试更宽松的匹配（忽略大小写后缀）
            if not found:
                for fname in sorted(os.listdir(folder_local)):
                    fname_base, fname_ext = osp.splitext(fname)
                    fname_ext_lower = fname_ext.lower()
                    if fname_base == base and fname_ext_lower in IMG_EXTS:
                        img_filename = fname
                        candidate = osp.join(folder_local, fname)
                        with open(candidate, "rb") as f:
                            img_data = f.read()
                            mime_type = IMG_EXT_TO_MIME[fname_ext_lower]
                            base64_img = f"data:{mime_type};base64,{base64.b64encode(img_data).decode('utf-8')}"
                        found = True
                        break
        # 将Base64编码和文件名加入结果（无图则为None）
        res_row_info.append({
            "base64": base64_img,
            "filename": img_filename
        })

    res_data.append(res_row_info)

# Jinja2模板（修改img的src为Base64编码）
template_string = """
<!DOCTYPE html>
<html>
<head>
    <title>Images</title>
    <meta charset="utf-8">
    <style>
        img { max-width: 320px; height: auto; display:block; margin:6px auto }
        td { vertical-align: top; text-align: center }
        table { width: 100%; border-collapse: collapse }
        th, td { border: 1px solid #ddd; padding: 8px }
        th { background: #f4f4f4 }
        .fname { font-size: 12px; color:#555; word-break:break-all; margin-top: 4px }
    </style>
</head>
<body>
    <h2>epoch0-1</h2>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>GT</th>
                <th>step4_epoth0</th>
                <th>step10_epoth0</th>
                <th>step25_epoth0</th>
                <th>epoch3</th>
                <th>epoch4</th>
            </tr>
        </thead>
        <tbody>
        {% for row in data %}
            <tr>
                <td>{{ loop.index }}</td>
                {% for img_info in row[6:12] %}  {# 要改 #}
                    <td>
                        {% if img_info.base64 %}
                            <img src="{{ img_info.base64 }}" alt="img">
                            <div class="fname">{{ img_info.filename or '未知文件' }}</div>
                        {% else %}
                            <div class="fname">(无图)</div>
                        {% endif %}
                    </td>
                {% endfor %}
            </tr>
        {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

# 渲染模板
template = Environment(loader=BaseLoader).from_string(template_string)

# 输出HTML文件
output_html_path = f"showcase1127.html"
with open(output_html_path, "w", encoding='utf-8') as f:
    f.write(template.render(data=res_data, model_names=model_names))

print(f"Base64版HTML文件已保存为 {output_html_path}")