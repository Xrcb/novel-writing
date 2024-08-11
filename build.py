from loguru import logger
import json
from tqdm import tqdm
import time
import os
from openai import OpenAI
# 配置loguru输出到文件
logger.remove()  # 移除默认的控制台输出
logger.add("logs/app_{time:YYYY-MM-DD}.log", level="INFO", rotation="00:00", retention="10 days", compression="zip")

DEEPSEEK_API_KEY = 'sk-4a6a4d2857b44eda829a6bc38126aa4d'

# 设置容错机制，可最多重试 5 次，如果失败记录错误日志
def get_summary_with_retry(text):
    max_retries = 5
    retry_delay = 60  # in seconds
    attempts = 0
    while attempts < max_retries:
        try:
            return get_response(text)
        except Exception as e:
            attempts += 1
            if attempts < max_retries:
                logger.warning(f"Attempt {attempts} failed for text: {text}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"All {max_retries} attempts failed for text: {text}. Error: {e}")
                raise

# 创建文件夹
os.makedirs('./data', exist_ok=True)
os.makedirs('./output', exist_ok=True)
os.makedirs('./dataset', exist_ok=True)

# 使用线程池进行多线程访问，并控制提交任务的速度
def process_texts(texts):
    results = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        future_to_text = {}
        for text in tqdm(texts, desc="Submitting tasks", total=len(texts)):
            future = executor.submit(get_summary_with_retry, text)
            future_to_text[future] = text
            time.sleep(0.2)  # 控制每0.5秒提交一个任务
        for future in tqdm(as_completed(future_to_text), total=len(texts), desc="Processing tasks"):
            text = future_to_text[future]
            try:
                summary = future.result()
                results.append((text, summary))
            except Exception as e:
                logger.error(f"Failed to process text: {text}. Error: {e}")
    
    return results

import torch
from tqdm import tqdm
import json
import logging

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def get_response(text):
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url="https://api.deepseek.com",  # 填写DashScope SDK的base_url
    )
    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                'role': 'system', 
                'content': '总结user提交的内容。用一句不超过100字的话总结这段小说的情节。仅回答总结，不需要添加其他内容。'
            },
            {
                'role': 'user', 
                'content': text
            }
        ])
    
    return completion.choices[0].message.content

def get_summary_with_retry(text):
    # Implement your retry logic here
    try:
        summary = get_response(text)
        return summary
    except Exception as e:
        logger.error(f"Failed to get summary for text: {text}. Error: {e}")
        raise

def build_dataset(novel, texts):
    instruction_prompt = (
        "现在你是一位小说创作助手，你的名字叫曦月。你的任务是模仿用户提供的小说数据集中的作者风格和思维方式，"
        "帮助用户创作新的小说章节。你需要根据用户提供的新小说大纲，生成符合原作者风格的内容。"
        "你的写作风格应当保持一致，包括语言风格、人物塑造、情节发展等方面。"
        "你需要确保生成的内容逻辑连贯，情节紧凑，并且能够吸引读者的兴趣。"
    )
    dataset = []
    dataset_error = []
    print(novel)

    # Check for GPU availability
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    for text in tqdm(texts, desc=f"Processing {novel}", total=len(texts)):
        try:
            summary = get_summary_with_retry(text)
            dataset.append({
                "conversation": [
                    {
                        "input": summary,
                        "output": text
                    }
                ]
            })
        except Exception as e:
            dataset_error.append(text)
            logger.error(f"Failed to process text: {text}. Error: {e}")
            
    with open(f"./data/{novel}.json", "w") as f:
        f.write(json.dumps(dataset, ensure_ascii=False, indent=4))

    with open(f"./data/{novel}_error.txt", "w") as f:
        f.write(json.dumps(dataset_error, ensure_ascii=False, indent=4))
    return dataset

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

# 定义故事名称
story_name = '快穿：反派太宠太撩人'

# 只给前100部分的段落进行打标签
dataset = build_dataset(story_name, paragraphs[:10])

# 输出打标签后的数据集的相关信息
print(f"Total number of entries in the dataset: {len(dataset)}")
print("Sample entries from the dataset:")
for i, entry in enumerate(dataset[:5]):  # Display the first 5 entries as a sample
    print(f"Entry {i+1}:")
    print(f"Input: {entry['conversation'][0]['input']}")
    print(f"Output: {entry['conversation'][0]['output']}")
    print("\n")
