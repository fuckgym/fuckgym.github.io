import os
import re

def get_h1_title(md_path):
    """
    只读取 Markdown 文件的第一个一级标题 (#) 作为侧边栏的展示名称。
    严格忽略二级 (##) 及以上的标题。
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 只匹配一个 # 开头的标题
                match = re.match(r'^#\s+(.+)', line)
                if match:
                    return match.group(1).strip()
    except Exception as e:
        print(f"读取文件失败 {md_path}: {e}")
    return None

def format_folder_name(name):
    """
    如果文件夹内没有 Markdown 文件或没写标题，用文件夹名兜底。
    例如将 '01-getting-started' 转换为 'Getting started'
    """
    cleaned = re.sub(r'^\d+-', '', name).replace('-', ' ')
    return cleaned.capitalize()

def generate_tree(current_dir, base_dir, depth=0):
    lines = []
    
    try:
        # 只遍历以数字开头的核心教程目录（如 1-js, 2-ui）
        items = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d)) and re.match(r'^\d+', d)]
    except OSError:
        return []

    # 按照开头的数字序号进行排序，保证教程先后顺序
    items.sort()

    for item in items:
        item_path = os.path.join(current_dir, item)
        
        # 寻找当前目录下的入口文件
        md_file = None
        if os.path.exists(os.path.join(item_path, 'article.md')):
            md_file = 'article.md'
        elif os.path.exists(os.path.join(item_path, 'README.md')):
            md_file = 'README.md'

        title = None
        link = ""

        if md_file:
            md_path = os.path.join(item_path, md_file)
            title = get_h1_title(md_path)
            # 转换为相对链接，并保证在不同操作系统下都是正斜杠
            link = os.path.relpath(md_path, base_dir).replace('\\', '/')
        
        if not title:
            title = format_folder_name(item)

        # 保证严格的 Markdown 缩进格式，这对折叠插件至关重要
        indent = '  ' * depth
        if link:
            # 有具体文章的节点
            lines.append(f"{indent}* [{title}]({link})")
        else:
            # 仅作为分类的父级节点，没有文章链接
            lines.append(f"{indent}* **{title}**")

        # 递归进入下一层级
        lines.extend(generate_tree(item_path, base_dir, depth + 1))

    return lines

def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    sidebar_file = os.path.join(base_dir, '_sidebar.md')
    
    print("正在扫描教程目录，提取文件层级结构...")
    sidebar_content = generate_tree(base_dir, base_dir)
    
    if not sidebar_content:
        print("警告：未找到符合格式的目录，请确认脚本运行在正确的根目录下。")
        return

    # 写入 _sidebar.md
    with open(sidebar_file, 'w', encoding='utf-8') as f:
        # 插入顶部的首页导航
        f.write("* [🏠 教程首页](/)\n")
        f.write('\n'.join(sidebar_content))
        f.write('\n')

    print(f"✅ 成功生成！共有 {len(sidebar_content)} 个文件/目录节点被写入 _sidebar.md")
    print("注意：文章内的 h2/h3 标题已全部剔除，请交由 Docsify TOC 插件在右侧动态渲染。")

if __name__ == "__main__":
    main()