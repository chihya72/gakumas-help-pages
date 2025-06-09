#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学园偶像大师帮助页面下载器 v2
从HelpContent.yaml文件读取帮助页面URL，下载HTML源代码并保存为对应的ID文件名。

v2 更新内容:
- 修复了HTML文件乱码问题
- 智能检测日文网页编码（支持UTF-8、Shift_JIS、EUC-JP等）
- 可选使用chardet库进行更精确的编码检测

乱码问题解决方案:
1. 自动尝试多种日文编码格式
2. 验证解码结果是否包含日文字符
3. 使用chardet库进行智能编码检测（如果已安装）

建议安装chardet以获得更好的编码检测效果:
pip install chardet
"""

import os
import sys
import yaml
import requests
import re
from pathlib import Path
import time
from typing import Dict, List, Optional

# 尝试导入chardet用于更好的编码检测
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False
    print("[提示] 建议安装chardet库以获得更好的编码检测: pip install chardet")


class HelpPageDownloader:
    def __init__(self, yaml_file_path: str, output_dir: str = "downloaded_help_pages"):
        """
        初始化下载器
        
        Args:
            yaml_file_path: HelpContent.yaml文件路径
            output_dir: 下载文件保存目录
        """
        self.yaml_file_path = yaml_file_path
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        
        # 设置请求头，模拟浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 创建输出目录
        self.output_dir.mkdir(exist_ok=True)
        
    def load_help_content(self) -> List[Dict]:
        """从YAML文件加载帮助内容"""
        try:
            with open(self.yaml_file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            print(f"[成功] 加载了 {len(content)} 个帮助页面条目")
            return content
        except Exception as e:
            print(f"[错误] 加载YAML文件失败: {e}")
            return []
    
    def download_html(self, url: str, filename: str) -> bool:
        """
        下载HTML页面
        
        Args:
            url: 要下载的URL
            filename: 保存的文件名
            
        Returns:
            bool: 是否下载成功
        """
        try:
            print(f"  正在下载: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 尝试检测正确的编码
            content = self._get_decoded_content(response)
            
            # 保存HTML文件
            output_file = self.output_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  [OK] 已保存: {filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"  [错误] 下载失败: {e}")
            return False
        except Exception as e:
            print(f"  [错误] 保存失败: {e}")
            return False
    
    def _get_decoded_content(self, response) -> str:
        """
        智能解码响应内容，处理日文编码问题
        
        Args:
            response: requests响应对象
            
        Returns:
            str: 解码后的内容
        """
        content_bytes = response.content
        
        # 方法1: 使用chardet自动检测编码（如果可用）
        if HAS_CHARDET:
            try:
                detected = chardet.detect(content_bytes)
                if detected['confidence'] > 0.7:  # 置信度超过70%
                    encoding = detected['encoding']
                    decoded_content = content_bytes.decode(encoding)
                    print(f"    [编码] chardet检测到编码: {encoding} (置信度: {detected['confidence']:.2f})")
                    return decoded_content
            except (UnicodeDecodeError, LookupError, TypeError):
                pass
        
        # 方法2: 首先尝试从HTTP头获取编码
        if response.encoding and response.encoding.lower() not in ['iso-8859-1', 'windows-1252']:
            try:
                decoded_content = response.text
                # 验证是否包含日文字符
                if self._contains_japanese_text(decoded_content):
                    print(f"    [编码] 使用HTTP头编码: {response.encoding}")
                    return decoded_content
            except UnicodeDecodeError:
                pass
        
        # 方法3: 尝试常见的日文编码
        encodings_to_try = ['utf-8', 'shift_jis', 'euc-jp', 'iso-2022-jp', 'cp932']
        
        for encoding in encodings_to_try:
            try:
                decoded_content = content_bytes.decode(encoding)
                # 检查是否包含日文字符
                if self._contains_japanese_text(decoded_content):
                    print(f"    [编码] 使用编码: {encoding}")
                    return decoded_content
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 方法4: 如果都失败了，使用utf-8并忽略错误
        print("    [警告] 无法确定编码，使用UTF-8并忽略错误")
        return content_bytes.decode('utf-8', errors='ignore')
    
    def _contains_japanese_text(self, text: str) -> bool:
        """
        检查文本是否包含日文字符
        
        Args:
            text: 要检查的文本
            
        Returns:
            bool: 是否包含日文字符
        """
        # 只检查前2000个字符以提高性能
        sample_text = text[:2000]
        
        # 检查是否包含日文字符
        japanese_chars = 0
        for char in sample_text:
            if ('\u3040' <= char <= '\u309F' or  # 平假名
                '\u30A0' <= char <= '\u30FF' or  # 片假名
                '\u4E00' <= char <= '\u9FAF'):   # 汉字
                japanese_chars += 1
        
        # 如果日文字符占比超过1%，认为包含日文
        return japanese_chars > len(sample_text) * 0.01
    
    def process_all_pages(self, delay: float = 1.0) -> None:
        """
        处理所有帮助页面
        
        Args:
            delay: 请求间隔时间（秒），避免过于频繁的请求
        """
        help_content = self.load_help_content()
        if not help_content:
            return
        
        total_pages = len(help_content)
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        print(f"\n开始下载 {total_pages} 个帮助页面...")
        print(f"输出目录: {self.output_dir.absolute()}")
        print("-" * 60)
        
        for i, item in enumerate(help_content, 1):
            # 获取必要信息
            item_id = item.get('id', '')
            detail_url = item.get('detailUrl', '')
            category_id = item.get('helpCategoryId', '')
            name = item.get('name', '')
            
            print(f"\n[{i}/{total_pages}] 处理: {item_id}")
            print(f"  类别: {category_id}")
            print(f"  名称: {name}")
            
            if not detail_url:
                print(f"  [跳过] 没有detailUrl")
                skipped_count += 1
                continue
            
            # 生成文件名
            filename = f"{item_id}.html"
            output_file = self.output_dir / filename
            
            # 检查文件是否已存在
            if output_file.exists():
                print(f"  [跳过] 文件已存在")
                skipped_count += 1
                continue
            
            # 下载页面
            if self.download_html(detail_url, filename):
                success_count += 1
            else:
                failed_count += 1
            
            # 延时，避免请求过于频繁
            if i < total_pages:
                time.sleep(delay)
        
        # 输出统计信息
        print("\n" + "=" * 60)
        print("下载完成统计:")
        print(f"  总计: {total_pages}")
        print(f"  成功: {success_count}")
        print(f"  失败: {failed_count}")
        print(f"  跳过: {skipped_count}")
        print(f"  输出目录: {self.output_dir.absolute()}")
    
    def download_single_page(self, item_id: str) -> bool:
        """
        下载单个页面
        
        Args:
            item_id: 帮助页面ID
            
        Returns:
            bool: 是否下载成功
        """
        help_content = self.load_help_content()
        if not help_content:
            return False
        
        # 查找对应的条目
        target_item = None
        for item in help_content:
            if item.get('id') == item_id:
                target_item = item
                break
        
        if not target_item:
            print(f"[错误] 找不到ID为 '{item_id}' 的帮助页面")
            return False
        
        detail_url = target_item.get('detailUrl', '')
        if not detail_url:
            print(f"[错误] ID '{item_id}' 没有detailUrl")
            return False
        
        filename = f"{item_id}.html"
        print(f"下载单个页面: {item_id}")
        return self.download_html(detail_url, filename)

    def list_all_pages(self) -> None:
        """列出所有可用的帮助页面"""
        help_content = self.load_help_content()
        if not help_content:
            return
        
        print(f"\n共有 {len(help_content)} 个帮助页面:\n")
        categories = {}
        for item in help_content:
            category = item.get('helpCategoryId', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        for category, items in sorted(categories.items()):
            print(f"[{category}]")
            for item in sorted(items, key=lambda x: x.get('order', 0)):
                item_id = item.get('id', '')
                name = item.get('name', '')
                print(f"   {item_id} - {name}")
            print()


def main():
    """主函数"""
    # 默认配置
    yaml_file = "gakumasu-diff/orig/HelpContent.yaml"
    output_dir = "downloaded_help_pages"
    delay = 1.0  # 请求间隔时间
    
    # 显示使用说明
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print("学园偶像大师帮助页面下载器")
        print("=" * 50)
        print("用法:")
        print("  python download_help_pages.py                     # 下载所有帮助页面")
        print("  python download_help_pages.py <页面ID>            # 下载指定ID的页面")
        print("  python download_help_pages.py --list             # 列出所有可用页面ID")
        print("  python download_help_pages.py --help             # 显示此帮助信息")
        print("\n示例:")
        print("  python download_help_pages.py achievement-produce-achievement")
        print("  python download_help_pages.py achievement-achievement")
        return
    
    # 检查YAML文件是否存在
    if not os.path.exists(yaml_file):
        print(f"[错误] 找不到YAML文件: {yaml_file}")
        print("请确保文件路径正确，或者修改脚本中的yaml_file变量")
        return
    
    # 创建下载器
    downloader = HelpPageDownloader(yaml_file, output_dir)
    
    # 处理命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '--list':
            # 列出所有页面ID
            downloader.list_all_pages()
        else:
            # 下载指定ID的页面
            item_id = arg
            success = downloader.download_single_page(item_id)
            if success:
                print(f"[成功] 下载完成: {item_id}.html")
            else:
                print(f"[失败] 下载失败: {item_id}")
    else:
        # 确认批量下载
        help_content = downloader.load_help_content()
        total = len(help_content)
        print(f"\n准备下载 {total} 个帮助页面到目录: {output_dir}")
        print("预计时间:", f"{total * delay / 60:.1f} 分钟")
        
        try:
            confirm = input("\n确认开始下载? (y/N): ").lower().strip()
            if confirm in ['y', 'yes']:
                downloader.process_all_pages(delay)
            else:
                print("取消下载")
        except KeyboardInterrupt:
            print("\n\n用户取消下载")


if __name__ == "__main__":
    main()
