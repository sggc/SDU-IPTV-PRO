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

# 4. 外部直播源列表（按优先级排序，排在前面的优先匹配）
EXTERNAL_SOURCES = [
    "https://raw.githubusercontent.com/q1017673817/iptvz/main/组播_北京联通.txt",
    "https://raw.githubusercontent.com/q1017673817/iptvz/main/组播_天津联通.txt"
]

# 5. 自定义模糊匹配规则
# 格式: "本地频道名": ["允许匹配的外部名1", "允许匹配的外部名2"]
# 如果外部源的名字包含在这些列表里，就会被视为匹配成功。
# 留空则使用默认模糊匹配逻辑（包含关系）
CUSTOM_MATCH_RULES = {
    "CCTV16": ["CCTV-16奥林匹克", "CCTV16", "奥林匹克"],
    "CCTV4K": ["CCTV-4K", "CCTV4K"],
    "CCTV1": ["CCTV-1", "CCTV1综合"],
    # 在这里添加更多规则...
}

# ===========================================

def get_file_hash(filepath):
    """获取文件的MD5哈希值"""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_content_hash(content_list):
    """获取内容列表的MD5哈希值"""
    combined = "".join(content_list)
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def download_external_sources():
    """下载所有外部源并合并为一个字典 {name: [url1, url2]}"""
    external_data = {}
    print("正在下载外部源...")
    for url in EXTERNAL_SOURCES:
        try:
            resp = requests.get(url, timeout=10)
            resp.encoding = 'utf-8'
            lines = resp.text.splitlines()
            for line in lines:
                if ',' in line:
                    name, url = line.split(',', 1)
                    name = name.strip()
                    url = url.strip()
                    if name and url:
                        if name not in external_data:
                            external_data[name] = []
                        external_data[name].append(url)
            print(f"成功获取: {url}")
        except Exception as e:
            print(f"获取失败 {url}: {e}")
    return external_data

def is_match(local_name, external_name):
    """判断本地频道名和外部频道名是否匹配"""
    # 1. 优先检查自定义规则
    if local_name in CUSTOM_MATCH_RULES:
        allowed_aliases = CUSTOM_MATCH_RULES[local_name]
        for alias in allowed_aliases:
            if alias in external_name or external_name in alias:
                return True
    
    # 2. 默认模糊匹配：只要名字互相包含（去除特殊字符后）
    clean_local = local_name.replace("-", "").replace(" ", "").lower()
    clean_external = external_name.replace("-", "").replace(" ", "").lower()
    
    if clean_local in clean_external or clean_external in clean_local:
        return True
        
    return False

def process_m3u():
    # 1. 检查哈希，决定是否需要运行
    input_hash = get_file_hash(INPUT_FILE)
    
    # 获取外部源的内容用于哈希比对（不解析，只比对内容变化）
    try:
        external_contents = []
        for url in EXTERNAL_SOURCES:
            r = requests.get(url, timeout=10)
            external_contents.append(r.text)
        external_hash = get_content_hash(external_contents)
    except:
        print("警告：无法获取外部源进行哈希比对，将强制运行。")
        external_hash = "force_run"

    current_combined_hash = hashlib.md5((input_hash + external_hash).encode('utf-8')).hexdigest()

    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            old_hash = f.read().strip()
        if old_hash == current_combined_hash:
            print("检测到源文件未变化，跳过运行。")
            return

    # 2. 开始处理
    print("源文件有变化，开始处理...")
    external_sources = download_external_sources()
    
    if not os.path.exists(INPUT_FILE):
        print(f"错误：找不到输入文件 {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_lines = []
    append_lines = [] # 存放多出来的源
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].strip()
        output_lines.append(lines[i]) # 保留原行格式（含换行符等）
        
        if line.startswith('#EXTINF'):
            # 下一行应该是直播源
            if i + 1 < n:
                next_line = lines[i+1].strip()
                # 提取频道名，假设格式为 ... , ChannelName
                channel_name = line.split(',')[-1].strip()
                
                # 判断下一行是否为空、注释或无效链接（即"扣好空了"）
                if not next_line or next_line.startswith('#') or "replace_me" in next_line.lower():
                    # 需要补全
                    matched_urls = []
                    matched_names = []
                    
                    # 在外部源中查找
                    for ext_name, urls in external_sources.items():
                        if is_match(channel_name, ext_name):
                            matched_urls.extend(urls)
                            matched_names.append(ext_name)
                    
                    if matched_urls:
                        # 填入第一个匹配的源
                        output_lines.append(matched_urls[0] + '\n')
                        print(f"匹配成功: {channel_name} <- {matched_names[0]} ({matched_urls[0]})")
                        
                        # 剩下的源放入 append_lines
                        if len(matched_urls) > 1:
                            for extra_url in matched_urls[1:]:
                                append_lines.append(line + '\n')
                                append_lines.append(extra_url + '\n')
                    else:
                        # 没找到匹配，保留原样或者留空
                        output_lines.append(lines[i+1]) 
                        print(f"未匹配: {channel_name}")
                    i += 1 # 跳过下一行，因为已经处理过了
                else:
                    # 已有源，直接保留
                    output_lines.append(lines[i+1])
                    i += 1
            else:
                i += 1
        else:
            i += 1

    # 3. 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
        if append_lines:
            f.write("\n# --- Extra Sources ---\n")
            f.writelines(append_lines)

    print(f"处理完成，已保存至 {OUTPUT_FILE}")

    # 4. 更新哈希文件
    with open(HASH_FILE, 'w') as f:
        f.write(current_combined_hash)

if __name__ == "__main__":
    process_m3u()
