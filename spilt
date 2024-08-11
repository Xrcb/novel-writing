import jieba
import re
import json

def clean_text(text):
    # 去除所有空格和占位符
    text = re.sub(r'\s+', '', text)
    # 删除章节标题
    text = re.sub(r'第\d+章.*?\d+', '', text)
    return text

def split_text_to_paragraphs(text, max_length=1000):
    paragraphs = []
    while len(text) > max_length:
        paragraphs.append(text[:max_length])
        text = text[max_length:]
    if text:
        paragraphs.append(text)
    return paragraphs

def extract_and_clean_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Debug: Print the raw text length
    print(f"Raw text length: {len(text)}")

    # 使用正则表达式匹配章节并合并为一个整体文本
    chapters = re.split(r'------------', text)
    chapters = [chapter.strip() for chapter in chapters if chapter.strip()]
    full_text = ''.join(chapters)

    # Debug: Print the length of the combined chapters text
    print(f"Combined chapters text length: {len(full_text)}")

    # 清理文本
    cleaned_text = clean_text(full_text)

    # Debug: Print the length of the cleaned text
    print(f"Cleaned text length: {len(cleaned_text)}")

    return cleaned_text

def save_paragraphs_to_json(paragraphs, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(paragraphs, file, ensure_ascii=False, indent=4)

# 示例用法
file_path = '/root/xiaoshuo/快穿：反派太宠太撩人.txt'
output_file = '/root/xiaoshuo/chapters.json'

# 提取并清理文本
cleaned_text = extract_and_clean_text(file_path)

# 将文本拆分成1000字的段落
paragraphs = split_text_to_paragraphs(cleaned_text)

# 保存段落到JSON文件
save_paragraphs_to_json(paragraphs, output_file)

# 输出相关提示信息
print(f"Total number of paragraphs: {len(paragraphs)}")
print("Character count of the first 10 paragraphs:")
for i, paragraph in enumerate(paragraphs[:10]):
    print(f"Paragraph {i+1}: {len(paragraph)} characters")

# 打印前10个段落的内容
print("Content of the first 10 paragraphs:")
for i, paragraph in enumerate(paragraphs[:10]):
    print(f"Paragraph {i+1}: {paragraph}")

print(f"Paragraphs have been saved to {output_file}")
