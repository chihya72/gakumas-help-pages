# 帮助页面下载器使用说明

这个Python脚本用于从学园偶像大师的帮助页面下载HTML源代码。

## 功能特点

- 从 `HelpContent.yaml` 文件读取所有帮助页面的URL
- 自动下载HTML源代码并保存为对应的ID文件名
- 支持单个页面下载和批量下载
- 自动创建输出目录
- 包含错误处理和进度显示
- 请求间隔控制，避免过于频繁的访问

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install requests PyYAML
```

## 使用方法

### 1. 批量下载所有帮助页面

```bash
python download_help_pages.py
```

这将：
- 读取 `gakumasu-diff/orig/HelpContent.yaml` 文件
- 下载所有帮助页面的HTML源代码
- 保存到 `downloaded_help_pages/` 目录
- 文件名格式：`{id}.html`

### 2. 下载单个帮助页面

```bash
python download_help_pages.py achievement-produce-achievement
```

这将只下载指定ID的帮助页面。

## 输出文件示例

根据你提供的示例，下载后的文件结构如下：

```
downloaded_help_pages/
├── achievement-produce-achievement.html
├── achievement-achievement.html
├── achievement-idol.html
├── achievement-others.html
├── box-gasha-event.html
├── ...
└── 其他帮助页面.html
```

每个HTML文件包含完整的页面源代码，格式如：

```html
<html lang="ja">
<head>
    <meta charset="utf-8"/>
    <meta name="robots" content="noindex, nofollow"/>
    <meta name="format-detection" content="telephone=no"/>
    <link rel="stylesheet" href="https://stat.game-gakuen-idolmaster.jp/html/css/common.css?_dt=1712920864475"/>
    <script src="https://stat.game-gakuen-idolmaster.jp/html/js/common.js?_dt=1712920864475"></script>
    <title>ヘルプ</title>
</head>
<body>
    <main>
        プロデュースに関するアチーブメントです。プロデュース内で条件を達成することで、アチーブメントの獲得/ランクアップができます。
    </main>
</body>
</html>
```

## 配置选项

你可以在脚本的 `main()` 函数中修改以下配置：

```python
yaml_file = "gakumasu-diff/orig/HelpContent.yaml"  # YAML文件路径
output_dir = "downloaded_help_pages"              # 输出目录
delay = 1.0                                       # 请求间隔时间（秒）
```

## 注意事项

1. **网络连接**: 确保能够访问 `stat.game-gakuen-idolmaster.jp` 域名
2. **请求频率**: 脚本默认在每个请求间暂停1秒，避免过于频繁的访问
3. **文件覆盖**: 如果文件已存在，脚本会跳过下载
4. **错误处理**: 脚本会显示下载失败的页面，并在最后显示统计信息

## 输出示例

```
✓ 成功加载 125 个帮助页面条目

开始下载 125 个帮助页面...
输出目录: D:\GIT\gakumas-master-translation-pm\downloaded_help_pages
------------------------------------------------------------

[1/125] 处理: achievement-achievement
  类别: help-achievement
  名称: アチーブメント
  正在下载: https://stat.game-gakuen-idolmaster.jp/html/help/9386f5f942dfa05aba3098e43a988f4828b21c9f86118f9194c5c3a5dbd635c3/index.html?_cb=c3e6734e2d81779b113c8abea6bbef30b6f45fbaae2362ffcc1bce290abac7a8
  ✓ 已保存: achievement-achievement.html

[2/125] 处理: achievement-produce-achievement
  类别: help-achievement
  名称: プロデュースアチーブメント
  正在下载: https://stat.game-gakuen-idolmaster.jp/html/help/9f91b8fe31a6571d893fd1ad8bdaa7dfc937300014f640f9c5958fd29a8895a1/index.html?_cb=c3e6734e2d81779b113c8abea6bbef30b6f45fbaae2362ffcc1bce290abac7a8
  ✓ 已保存: achievement-produce-achievement.html

...

============================================================
下载完成统计:
  总计: 125
  成功: 120
  失败: 2
  跳过: 3
  输出目录: D:\GIT\gakumas-master-translation-pm\downloaded_help_pages
```

## 故障排除

1. **找不到YAML文件**: 检查 `gakumasu-diff/orig/HelpContent.yaml` 文件是否存在
2. **网络连接失败**: 检查网络连接和防火墙设置
3. **权限错误**: 确保有写入输出目录的权限
4. **依赖包缺失**: 运行 `pip install -r requirements.txt` 安装依赖
