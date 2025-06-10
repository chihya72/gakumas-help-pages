import json

def update_detail_urls(input_file, output_file=None):
    """
    更新JSON文件中的detailUrl字段
    
    Args:
        input_file (str): 输入JSON文件路径
        output_file (str): 输出JSON文件路径，如果为None则覆盖原文件
    """
    # 新的URL模板
    url_template = "https://chihya72.github.io/gakumas-help-pages/translated_help_pages/{id}.html?_cb=c3e6734e2d81779b113c8abea6bbef30b6f45fbaae2362ffcc1bce290abac7a8"
    
    try:
        # 读取JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 更新每个条目的detailUrl
        updated_count = 0
        for item in data.get('data', []):
            if 'id' in item and 'detailUrl' in item:
                old_url = item['detailUrl']
                new_url = url_template.format(id=item['id'])
                item['detailUrl'] = new_url
                updated_count += 1
                print(f"已更新 ID: {item['id']}")
                print(f"  旧URL: {old_url}")
                print(f"  新URL: {new_url}")
                print()
        
        # 保存更新后的JSON文件
        output_path = output_file if output_file else input_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功更新了 {updated_count} 个URL")
        print(f"✅ 文件已保存到: {output_path}")
        
    except FileNotFoundError:
        print(f"❌ 错误: 找不到文件 {input_file}")
    except json.JSONDecodeError:
        print(f"❌ 错误: {input_file} 不是有效的JSON文件")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

def main():
    """主函数"""
    # 输入文件路径
    input_file = "HelpContent.json"
    
    # 可选：指定输出文件路径（如果不指定则覆盖原文件）
    # output_file = "HelpContent_updated.json"
    output_file = None  # 直接覆盖原文件
    
    print("开始更新detailUrl字段...")
    print(f"输入文件: {input_file}")
    print("-" * 50)
    
    update_detail_urls(input_file, output_file)

if __name__ == "__main__":
    main() 