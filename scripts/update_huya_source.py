#!/usr/bin/env python3
import requests
import hashlib
import os
import re

# ==================== 配置 ====================
SOURCE_URL = "https://raw.githubusercontent.com/ls125781003/tvboxtg/refs/heads/main/%E9%A5%AD%E5%A4%AA%E7%A1%AC/lives/%E8%99%8E%E7%89%99%E4%B8%80%E8%B5%B7%E7%9C%8B.txt"
OUTPUT_FILE = "custom/custom1.m3u"
HASH_FILE = ".data/huya_source_hash.txt"
# ==============================================

def get_content_hash(content):
    """计算内容的MD5哈希值"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def get_previous_hash():
    """获取之前保存的源文件哈希值"""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def save_current_hash(content):
    """保存当前源文件的哈希值"""
    current_hash = get_content_hash(content)
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)
    with open(HASH_FILE, 'w', encoding='utf-8') as f:
        f.write(current_hash)
    return current_hash

def has_source_changed(content):
    """检查源文件是否发生变化"""
    current_hash = get_content_hash(content)
    previous_hash = get_previous_hash()
    
    if previous_hash is None:
        print("首次运行，没有之前的哈希记录")
        return True
    
    if current_hash == previous_hash:
        print("虎牙源文件没有变化，跳过处理")
        return False
    else:
        print(f"虎牙源文件发生变化: 旧哈希 {previous_hash[:8]}... -> 新哈希 {current_hash[:8]}...")
        return True

def process_huya_source():
    """主处理流程"""
    try:
        print(f"开始处理虎牙源文件: {SOURCE_URL}")
        
        # 1. 下载源文件
        response = requests.get(SOURCE_URL, timeout=30)
        response.raise_for_status()
        content = response.text
        
        # 2. 检查源文件是否发生变化
        if not has_source_changed(content):
            return True # 无变化，视为成功
            
        # 3. 【关键修正】筛选和转换内容
        print("开始筛选和转换频道...")
        processed_lines = []
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 保留 M3U 头部
            if line.startswith('#EXTM3U'):
                processed_lines.append(line)
                continue
            
            # 【核心逻辑】筛选并修改 EXTINF 行
            if line.startswith('#EXTINF:'):
                if 'group-title="一起看"' in line:
                    # 修改分组标题
                    new_line = line.replace('group-title="一起看"', 'group-title="虎牙一起看"')
                    processed_lines.append(new_line)
                    # 检查下一行是否存在且是URL，如果是则一并添加
                    if i + 1 < len(lines) and not lines[i+1].strip().startswith('#'):
                        processed_lines.append(lines[i+1].strip())
        
        # 4. 保存处理后的文件
        channel_count = len([l for l in processed_lines if not l.startswith('#')])
        print(f"处理完成，共找到 {channel_count} 个目标频道。")
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(processed_lines))
        
        print(f"已成功保存到 {OUTPUT_FILE}")
        
        # 5. 更新哈希记录
        save_current_hash(content)
        
        return True
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = process_huya_source()
    if not success:
        print("处理失败")
        exit(1)
