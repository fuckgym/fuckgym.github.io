import os
import re

def clean_name(name):
    """
    清理物理目录名称，作为侧边栏展示的标题。
    例如: '01-getting-started' -> 'Getting started'
    """
    cleaned = re.sub(r'^\d+-', '', name).replace('-', ' ')
    return cleaned.capitalize()

def generate_physical_tree(current_dir, base_dir, depth=0):
    result_lines = []
    
    try:
        # 仅过滤出当前层级以数字开头的目录
        items = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d)) and re.match(r'^\d+', d)]
    except OSError:
        return []

    # 按物理名称排序，确保目录树的先后顺序与官方一致
    items.sort()

    for item in items:
        item_path = os.path.join(current_dir, item)
        title = clean_name(item)
        indent = '  ' * depth
        
        # 检查该物理目录下是否存在教程内容文件
        md_file = None
        if os.path.exists(os.path.join(item_path, 'article.md')):
            md_file = 'article.md'
        elif os.path.exists(os.path.join(item_path, 'README.md')): # 保留 README 兼容性
            md_file = 'README.md'

        # 【核心逻辑】：先递归获取所有子文件夹的结果
        children_lines = generate_physical_tree(item_path, base_dir, depth + 1)
        
        if md_file:
            # 命中1：当前文件夹直接包含 article.md，这是一个有效的内容节点
            link = os.path.relpath(os.path.join(item_path, md_file), base_dir).replace('\\', '/')
            result_lines.append(f"{indent}* [{title}]({link})")
            # 把它的子节点也挂载上来
            result_lines.extend(children_lines)
            
        else:
            # 命中2：当前文件夹没有 article.md
            # 判断它有没有包含有效文章的子节点，如果有，它就是一个有效的“分类父节点”
            if children_lines:
                result_lines.append(f"{indent}* **{title}**")
                result_lines.extend(children_lines)
                
            # 命中3：如果没有 article.md，且子节点全为空（children_lines 为空列表）
            # 这里什么都不做（直接 pass），等于将这个“空目录”彻底从侧边栏中剔除

    return result_lines

def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    sidebar_file = os.path.join(base_dir, '_sidebar.md')
    
    print("正在基于纯物理目录提取结构，并自动剪枝空目录...")
    sidebar_content = generate_physical_tree(base_dir, base_dir)
    
    if not sidebar_content:
        print("未识别到目标结构，请确认在正确目录下运行。")
        return

    with open(sidebar_file, 'w', encoding='utf-8') as f:
        f.write("* [🏠 Home](/)\n")
        f.write('\n'.join(sidebar_content))
        f.write('\n')

    print(f"✅ 生成成功！所有不包含 article.md 的多余空文件夹已被彻底忽略。")

if __name__ == "__main__":
    main()