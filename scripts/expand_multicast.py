    import requests
import hashlib
import os
import sys

# ================= 配置区域 =================

# 1. 输入文件路径（你的原始模板）
INPUT_FILE = "expand/multicast-origin.m3u"

# 2. 输出文件路径（补全后的结果）
OUTPUT_FILE = "expand/multicast-expand.m3u"

# 3. 哈希记录文件（用于判断是否需要更新）
HASH_FILE = ".data/expand_hash.txt"

# 4. 外部直播源列表（按优先级排序）
# 格式：(URL, 标记前缀)
# 标记前缀会附加到直播源后面，用于区分来源
EXTERNAL_SOURCES = [
    ("https://raw.githubusercontent.com/q1017673817/iptvz/main/组播_北京联通.txt", "$北京联通"),
    ("https://raw.githubusercontent.com/q1017673817/iptvz/main/组播_天津联通.txt", "$天津联通"),
    ("https://raw.githubusercontent.com/q1017673817/iptvz/main/组播_河北联通.txt", "$河北联通"),
]

# 5. 自定义模糊匹配规则
# 格式: "本地频道名": ["允许匹配的外部名1", "允许匹配的外部名2"]
CUSTOM_MATCH_RULES = {
    "CCTV16": ["CCTV-16奥林匹克", "CCTV16", "奥林匹克"],
    "CCTV4K": ["CCTV-4K", "CCTV4K"],
    "CCTV1": ["CCTV-1", "CCTV1综合"],
    "CCTV-15音乐": ["CCTV15", "CCTV-15"],
    "CCTV-16奥林匹克": ["CCTV16"],
    "CCTV-17农业农村": ["CCTV17"],
    # 在这里添加更多规则...
}

# ===========================================

def get_file_hash(filepath):
    """获取文件的MD5哈希值"""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_content_hash(content):
    """获取内容字符串的MD5哈希值"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def download_external_sources():
    """
    下载所有外部源并返回：
    1. 外部源字典：{频道名: [(url, tag, source_index), ...]}
    2. 外部源哈希列表：[hash1, hash2, ...]
    """
    external_data = {}  # {频道名: [(url, tag, source_index)]}
    external_hashes = []  # 存储每个外部源的哈希
    
    print("正在下载外部源...")
    for source_idx, (url, tag) in enumerate(EXTERNAL_SOURCES):
        try:
            resp = requests.get(url, timeout=10)
            resp.encoding = 'utf-8'
            
            # 计算该外部源的哈希
            source_hash = get_content_hash(resp.text)
            external_hashes.append(source_hash)
            
            lines = resp.text.splitlines()
            for line in lines:
                if ',' in line:
                    parts = line.split(',', 1)
                    name = parts[0].strip()
                    url = parts[1].strip()
                    if name and url:
                        if name not in external_data:
                            external_data[name] = []
                        # 存储URL和对应的标记
                        external_data[name].append((url, tag, source_idx))
            
            print(f"✓ 成功获取: {url} (哈希: {source_hash[:8]}...)")
        except Exception as e:
            print(f"✗ 获取失败 {url}: {e}")
            # 失败时使用空哈希，确保下次重试
            external_hashes.append("")
    
    return external_data, external_hashes

def is_match(local_name, external_name):
    """判断本地频道名和外部频道名是否匹配"""
    # 1. 优先检查自定义规则
    if local_name in CUSTOM_MATCH_RULES:
        allowed_aliases = CUSTOM_MATCH_RULES[local_name]
        for alias in allowed_aliases:
            if alias in external_name or external_name in alias:
                return True
    
    # 2. 反向检查（如果外部名在自定义规则中）
    if external_name in CUSTOM_MATCH_RULES:
        if local_name in CUSTOM_MATCH_RULES[external_name]:
            return True
    
    # 3. 默认模糊匹配：只要名字互相包含（去除特殊字符后）
    clean_local = local_name.replace("-", "").replace(" ", "").replace("频道", "").replace("高清", "").lower()
    clean_external = external_name.replace("-", "").replace(" ", "").replace("频道", "").replace("高清", "").lower()
    
    if clean_local in clean_external or clean_external in clean_local:
        return True
        
    return False

def process_m3u():
    # 1. 检查哈希，决定是否需要运行
    input_hash = get_file_hash(INPUT_FILE)
    
    # 下载外部源（用于哈希比对）
    print("检查源文件变化...")
    try:
        _, external_hashes = download_external_sources()
        external_hash = "|".join(external_hashes)  # 组合所有外部源哈希
    except:
        print("警告：无法获取外部源进行哈希比对，将强制运行。")
        external_hash = "force_run"

    # 计算组合哈希（包括输入文件和所有外部源）
    current_combined_hash = get_content_hash(input_hash + "|" + external_hash)

    # 检查是否需要运行
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            old_hash = f.read().strip()
        if old_hash == current_combined_hash:
            print("✓ 检测到源文件未变化，跳过运行。")
            return
    
    print("✓ 检测到源文件变化，开始处理...")
    
    # 2. 重新下载外部源（用于实际处理）
    external_sources, _ = download_external_sources()
    
    if not os.path.exists(INPUT_FILE):
        print(f"错误：找不到输入文件 {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_lines = []
    append_lines = []  # 存放多出来的源
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        output_lines.append(line)  # 追加当前行
        
        # 如果不是EXTINF行，直接跳到下一行
        if not line.strip().startswith('#EXTINF'):
            i += 1
            continue
        
        # 提取频道名
        channel_name = line.split(',')[-1].strip()
        
        # 检查下一行是否存在
        if i + 1 < n:
            next_line = lines[i + 1]
            next_line_stripped = next_line.strip()
            
            # 判断下一行是否为空行或注释（需要补全）
            is_empty = not next_line_stripped or next_line_stripped.startswith('#')
            is_url = next_line_stripped.startswith('http://') or next_line_stripped.startswith('rtp://')
            
            if not is_empty:
                # 非空行，如果也不是URL行，说明是其他内容，需要跳过
                if is_url:
                    # 已有源，直接保留
                    output_lines.append(next_line)
                    i += 2
                else:
                    # 不是URL也不是空，可能是有问题的情况，跳过
                    i += 1
            else:
                # 空行或注释，需要补全
                matched_sources = []  # [(url, tag, source_index, matched_external_name)]
                matched_names = []
                
                # 在外部源中查找
                for ext_name, sources in external_sources.items():
                    if is_match(channel_name, ext_name):
                        matched_sources.extend([(url, tag, idx, ext_name) for url, tag, idx in sources])
                        matched_names.append(ext_name)
                        print(f"匹配检查: {channel_name} <- {ext_name} (命中)")
                
                if matched_sources:
                    # 按优先级排序（source_index小的在前）
                    matched_sources.sort(key=lambda x: x[2])
                    
                    # 取第一个作为主要源（不带数字）
                    primary_url, primary_tag, _, matched_name = matched_sources[0]
                    output_lines.append(primary_url + primary_tag + "\n")
                    print(f"✓ 匹配成功: {channel_name} <- {matched_name} ({primary_url}{primary_tag})")
                    
                    # 剩下的放入 append_lines（追加到末尾）
                    if len(matched_sources) > 1:
                        # 按来源分组计数，从2开始
                        source_counter = {}  # {source_index: count}
                        for url, tag, idx, matched_name in matched_sources[1:]:
                            # 添加计数标记（从2开始）
                            count = source_counter.get(idx, 1) + 1  # 从2开始计数
                            source_counter[idx] = count
                            
                            full_tag = tag + str(count)
                            append_lines.append(line.rstrip('\n') + '\n')
                            append_lines.append(url + full_tag + '\n')
                            print(f"  → 追加备用源: {matched_name} ({url}{full_tag})")
                else:
                    # 没找到匹配，追加下一行
                    output_lines.append(next_line)
                    print(f"✗ 未匹配: {channel_name}")
                    i += 1
                i += 1
        else:
            i += 1

    # 3. 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
        if append_lines:
            f.write("\n# --- Extra Sources ---\n")
            f.writelines(append_lines)

    print(f"✓ 处理完成，已保存至 {OUTPUT_FILE}")

    # 4. 更新哈希文件
    with open(HASH_FILE, 'w') as f:
        f.write(current_combined_hash)

if __name__ == "__main__":
    process_m3u()
