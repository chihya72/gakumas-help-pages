#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path
from googletrans import Translator
import time
from bs4 import BeautifulSoup
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HTMLTranslator:
    def __init__(self, source_dir, target_dir=None):
        """
        初始化翻译器
        :param source_dir: 源HTML文件目录
        :param target_dir: 目标目录，如果为None则覆盖原文件
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir) if target_dir else self.source_dir
        self.translator = Translator()
        
        # 确保目标目录存在
        if not self.target_dir.exists():
            self.target_dir.mkdir(parents=True, exist_ok=True)
    
    def is_japanese_text(self, text):
        """检查文本是否包含日语字符"""
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
        return bool(japanese_pattern.search(text))
    
    def translate_text(self, text, max_retries=3):
        """翻译文本，带重试机制"""
        if not text.strip() or not self.is_japanese_text(text):
            return text
        
        for attempt in range(max_retries):
            try:
                result = self.translator.translate(text, src='ja', dest='zh-cn')
                time.sleep(0.1)  # 避免请求过快
                return result.text
            except Exception as e:
                logger.warning(f"翻译失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # 等待后重试
                else:
                    logger.error(f"翻译最终失败: {text[:50]}...")
                    return text  # 返回原文
    
    def translate_main_content(self, html_content):
        """翻译HTML中main标签内的内容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            main_tag = soup.find('main')
            
            if not main_tag:
                logger.warning("未找到main标签")
                return html_content
            
            # 获取main标签内的所有文本节点
            def translate_text_nodes(element):
                for child in element.children:
                    if child.name is None:  # 文本节点
                        if child.strip():  # 非空文本
                            translated = self.translate_text(child.strip())
                            child.replace_with(translated)
                    else:  # 元素节点，递归处理
                        translate_text_nodes(child)
            
            translate_text_nodes(main_tag)
            
            # 返回完整的HTML
            return str(soup)
            
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
            time.sleep(0.5)  # 避免请求过快
        
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
    translator = HTMLTranslator(source_directory, target_directory)
    translator.translate_all_files()

if __name__ == "__main__":
    main() 