import os
import re

def get_h1_title(md_path):
    """
    尝试从文件中提取第一个 '# ' 开头的标题。
    严格忽略二级 (##) 及以上的标题。
    """
    if not os.path.exists(md_path):
        return None
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 只匹配一个 # 开头的标题，并忽略前后的空白字符
                match = re.match(r'^#\s+(.+)', line)
                if match:
                    return match.group(1).strip()
    except Exception as e:
        print(f"读取文件失败 {md_path}: {e}")
    return None

def clean_name(name):
    """
    清理物理目录名称，作为最终兜底的标题。
    例如: '01-getting-started' -> 'Getting started'
    """
    cleaned = re.sub(r'^\d+-', '', name).replace('-', ' ')
    return cleaned.capitalize()

def generate_tree(current_dir, base_dir, depth=0):
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
        indent = '  ' * depth
        
        # 1. 确定当前目录下的核心内容文件，确立优先级
        target_md = None
        if os.path.exists(os.path.join(item_path, 'article.md')):
            target_md = 'article.md'
        elif os.path.exists(os.path.join(item_path, 'index.md')):
            target_md = 'index.md'
        elif os.path.exists(os.path.join(item_path, 'README.md')):
            target_md = 'README.md'

        # 2. 递归获取所有子文件夹的结果（用于剪枝判定）
        children_lines = generate_tree(item_path, base_dir, depth + 1)
        
        # 3. 剪枝核心逻辑：判断当前路径是否为“有效路径”
        # 有效条件：自身包含目标md文件，或者其子目录中存在有效文件（children_lines 不为空）
        is_valid_node = (target_md is not None) or (len(children_lines) > 0)
        
        if is_valid_node:
            title = None
            
            # 4. 尝试根据优先级提取文件中的 H1 标题
            if target_md:
                title = get_h1_title(os.path.join(item_path, target_md))
            
            # 5. 兜底逻辑：如果没有有效文件，或文件中未写 H1 标题，使用物理文件夹名
            if not title:
                title = clean_name(item)
            
            # 6. 生成 Markdown 目录节点
            if target_md:
                # 这是一个具体的文章节点，生成带链接的列表项
                link = os.path.relpath(os.path.join(item_path, target_md), base_dir).replace('\\', '/')
                result_lines.append(f"{indent}* [{title}]({link})")
            else:
                # 这是一个单纯的分类父节点（内部没有文章，但子文件夹有），仅加粗展示标题
                result_lines.append(f"{indent}* **{title}**")
            
            # 将它的有效子节点挂载到下方
            result_lines.extend(children_lines)
            
        # 如果 is_valid_node 为 False，说明既没有文件，子目录也全空，直接 pass 丢弃

    return result_lines

def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    sidebar_file = os.path.join(base_dir, '_sidebar.md')
    
    print("正在扫描目录并提取中文大标题，同时执行空目录剪枝...")
    sidebar_content = generate_tree(base_dir, base_dir)
    
    if not sidebar_content:
        print("未识别到目标结构，请确认在正确目录下运行。")
        return

    with open(sidebar_file, 'w', encoding='utf-8') as f:
        f.write("* [🏠 教程首页](/)\n")
        f.write('\n'.join(sidebar_content))
        f.write('\n')

    print(f"✅ 生成成功！自动提取了文章的 '# ' 标题，并剔除了所有冗余的空文件夹。")

if __name__ == "__main__":
    main()