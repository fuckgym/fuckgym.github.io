import os
import re

def get_title_from_md(md_path):
    """
    尝试从 Markdown 文件中读取第一个一级标题 (# 标题) 作为目录名称。
    如果读取失败，则返回 None。
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.match(r'^#\s+(.+)', line)
                if match:
                    return match.group(1).strip()
    except Exception as e:
        print(f"读取文件警告 {md_path}: {e}")
    return None

def clean_folder_name(name):
    """
    如果 Markdown 中没有标题，则回退使用文件夹名称。
    去除开头的数字和中划线，例如 "01-getting-started" -> "Getting started"
    """
    cleaned = re.sub(r'^\d+-', '', name).replace('-', ' ')
    return cleaned.title()

def generate_sidebar_lines(current_dir, base_dir, depth=0):
    lines = []
    
    # 1. 获取当前目录下所有的文件夹
    try:
        # 只处理以数字开头的文件夹（过滤掉 .git, node_modules 等无关目录）
        items = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d)) and re.match(r'^\d+', d)]
    except OSError:
        return []

    # 2. 按文件夹名称排序（依赖于原仓库开头的 01, 02 序号，保证教程顺序）
    items.sort()

    for item in items:
        item_path = os.path.join(current_dir, item)
        
        # 3. 寻找该层级下的核心 Markdown 文件
        md_file = None
        if os.path.exists(os.path.join(item_path, 'article.md')):
            md_file = 'article.md'
        elif os.path.exists(os.path.join(item_path, 'README.md')):
            md_file = 'README.md'

        title = None
        link = ""

        # 4. 如果存在 Markdown 文件，提取标题和相对路径
        if md_file:
            md_path = os.path.join(item_path, md_file)
            title = get_title_from_md(md_path)
            # 转换为相对路径，并确保使用正斜杠 (兼容 Windows)
            link = os.path.relpath(md_path, base_dir).replace('\\', '/')
        
        # 5. 如果没有解析到标题，使用清理后的文件夹名称兜底
        if not title:
            title = clean_folder_name(item)

        # 6. 根据目录深度生成 Markdown 列表的缩进
        indent = '  ' * depth
        if link:
            lines.append(f"{indent}* [{title}]({link})")
        else:
            # 如果这是一个中间层的分类文件夹（没有具体的 article.md），仅展示加粗文本
            lines.append(f"{indent}* **{title}**")

        # 7. 递归处理子文件夹
        lines.extend(generate_sidebar_lines(item_path, base_dir, depth + 1))

    return lines

def main():
    # 获取当前脚本所在目录作为基础目录
    base_dir = os.path.abspath(os.path.dirname(__file__))
    sidebar_file = os.path.join(base_dir, '_sidebar.md')
    
    print("开始扫描目录结构...")
    # 提取生成的 Markdown 内容
    sidebar_content = generate_sidebar_lines(base_dir, base_dir)
    
    if not sidebar_content:
        print("未找到符合格式的目录，请确保脚本在项目根目录下运行。")
        return

    # 将内容写入 _sidebar.md 文件
    with open(sidebar_file, 'w', encoding='utf-8') as f:
        # 可以手动加一个首页链接
        f.write("* [🏠 教程首页](/)\n")
        f.write('\n'.join(sidebar_content))
        f.write('\n')

    print(f"成功生成！已将 {len(sidebar_content)} 条目录项写入 _sidebar.md")

if __name__ == "__main__":
    main()