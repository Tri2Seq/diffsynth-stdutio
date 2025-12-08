# 配置文件路径（请将此处的 original.txt 替换为你的源文件路径）
input_file_path = "dataset/CUHK-Pedes/pairs.txt"  # 源txt文件
output_file_path = "dataset/CUHK-Pedes/pairs_filter.txt"   # 筛选后的新文件

# 打开源文件和目标文件，指定编码为utf-8避免乱码
with open(input_file_path, "r", encoding="utf-8") as infile, \
     open(output_file_path, "w", encoding="utf-8") as outfile:
    
    # 逐行读取源文件
    for line_num, line in enumerate(infile, 1):
        # 去除行首尾的空白字符（换行、空格、制表符等）
        clean_line = line.strip()
        
        # 跳过空行
        if not clean_line:
            continue
        
        # 分割行内容为列（按任意空白符分割，适配空格/制表符分隔）
        columns = clean_line.split()
        
        # 跳过列数不足的行（避免索引报错）
        if len(columns) < 1:
            print(f"第{line_num}行：列数不足，已跳过")
            continue
        
        # 获取第一列并检查是否以.png结尾
        first_column = columns[0]
        if first_column.endswith(".png"):
            # 保留该行（写入原始行内容，而非清洗后的，保留原有格式）
            outfile.write(line)

print(f"筛选完成！符合条件的内容已保存至 {output_file_path}")
