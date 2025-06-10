#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
from pathlib import Path
import requests
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAIHTMLTranslator:
    def __init__(self, source_dir, target_dir=None):
        """
        初始化翻译器
        :param source_dir: 源HTML文件目录
        :param target_dir: 目标目录，如果为None则覆盖原文件
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir) if target_dir else self.source_dir
        
        # API配置
        self.api_key = "sk-hahvmqxujppfdqlmqupkjfndcxrunhhfjnqznvbwmncdplnw"
        self.model = "Pro/deepseek-ai/DeepSeek-V3"
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        
        # 确保目标目录存在
        if not self.target_dir.exists():
            self.target_dir.mkdir(parents=True, exist_ok=True)
    
    def is_japanese_text(self, text):
        """检查文本是否包含日语字符"""
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
        return bool(japanese_pattern.search(text))
    
    def call_openai_api(self, text, max_retries=3):
        """调用OpenAI API进行翻译"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""请将以下日语文本翻译成中文，只返回翻译结果，不要添加任何解释：

{text}"""
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=data,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                translated_text = result['choices'][0]['message']['content'].strip()
                
                time.sleep(0.5)  # 避免请求过快
                return translated_text
                
            except Exception as e:
                logger.warning(f"API调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待后重试
                else:
                    logger.error(f"API调用最终失败: {text[:50]}...")
                    return text  # 返回原文
    
    def translate_text(self, text):
        """翻译文本"""
        if not text.strip() or not self.is_japanese_text(text):
            return text
        
        return self.call_openai_api(text)
    
    def extract_text_segments(self, content):
        """提取文本片段，保留HTML标签位置"""
        # 分割内容为文本和标签
        parts = re.split(r'(<[^>]+>)', content)
        
        text_segments = []
        for i, part in enumerate(parts):
            if not part:
                continue
            if part.startswith('<') and part.endswith('>'):
                # HTML标签，保持原样
                text_segments.append((i, 'tag', part))
            else:
                # 文本内容，需要翻译
                if part.strip():  # 只处理非空文本
                    text_segments.append((i, 'text', part))
                else:
                    # 保留空白字符
                    text_segments.append((i, 'whitespace', part))
        
        return text_segments
    
    def translate_main_content(self, html_content):
        """翻译HTML中main标签内的内容"""
        try:
            # 使用正则表达式找到main标签内容
            main_pattern = r'<main>(.*?)</main>'
            main_match = re.search(main_pattern, html_content, re.DOTALL)
            
            if not main_match:
                logger.warning("未找到main标签")
                return html_content
            
            main_content = main_match.group(1)
            original_main_content = main_content
            
            # 提取文本片段
            segments = self.extract_text_segments(main_content)
            
            # 翻译文本片段
            translated_segments = []
            for index, segment_type, content in segments:
                if segment_type == 'text':
                    translated_content = self.translate_text(content)
                    translated_segments.append((index, segment_type, translated_content))
                else:
                    translated_segments.append((index, segment_type, content))
            
            # 重建main标签内容
            translated_main_content = ''.join([content for _, _, content in translated_segments])
            
            # 替换原始HTML中的main标签内容
            translated_html = html_content.replace(original_main_content, translated_main_content)
            
            return translated_html
            
        except Exception as e:
            logger.error(f"处理HTML内容时出错: {e}")
            return html_content
    
    def translate_file(self, file_path):
        """翻译单个HTML文件"""
        try:
            logger.info(f"开始翻译: {file_path.name}")
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 翻译内容
            translated_content = self.translate_main_content(html_content)
            
            # 保存翻译后的文件
            target_file = self.target_dir / file_path.name
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            logger.info(f"翻译完成: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"翻译文件 {file_path.name} 时出错: {e}")
            return False
    
    def translate_all_files(self):
        """翻译目录下所有HTML文件"""
        html_files = list(self.source_dir.glob('*.html'))
        
        if not html_files:
            logger.warning("未找到HTML文件")
            return
        
        logger.info(f"找到 {len(html_files)} 个HTML文件")
        
        success_count = 0
        for file_path in html_files:
            if self.translate_file(file_path):
                success_count += 1
            time.sleep(1)  # 避免请求过快
        
        logger.info(f"翻译完成！成功: {success_count}/{len(html_files)}")

def main():
    """主函数"""
    # 设置源目录和目标目录
    source_directory = "downloaded_help_pages"
    target_directory = "translated_help_pages"  # 如果要覆盖原文件，设为None
    
    # 检查源目录是否存在
    if not Path(source_directory).exists():
        logger.error(f"源目录不存在: {source_directory}")
        return
    
    # 创建翻译器并开始翻译
    translator = OpenAIHTMLTranslator(source_directory, target_directory)
    translator.translate_all_files()

if __name__ == "__main__":
    main() 