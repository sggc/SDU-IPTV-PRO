#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据源文件更新本地文件中的 catchup-source IP 和路径
"""

import re
import requests
import hashlib
import os

# 配置
SOURCE_URL = "https://github.com/plsy1/iptv/raw/refs/heads/main/unicast/unicast-ku9.m3u"
LOCAL_FILE = ".github/expand/multicast-origin.m3u"
OUTPUT_FILE = ".github/expand/multicast-merge.m3u"
HASH_FILE = ".data/catchup_source_hash.txt"


def download_source(url):
    """下载源文件"""
    print(f"正在下载源文件: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def parse_source_m3u(content):
    """
    解析源文件，提取 tvg-name 和对应的 catchup-source 中的关键路径
    返回: {tvg_name: "ip:port/path/to/channel.rsc"}
    """
    source_map = {}
    lines = content.strip().split('\n')
    
    for line in lines:
        if line.startswith('#EXTINF'):
            # 提取 tvg-name
            tvg_name_match = re.search(r'tvg-name="([^"]+)"', line)
            if not tvg_name_match:
                continue
            tvg_name = tvg_name_match.group(1)
            
            # 提取 catchup-source 中的关键部分
            # 格式: catchup-source="rtsp://112.245.125.38:1554/iptv/Tvod/iptv/001/001/ch12122514263996485740.rsc?tvdr=..."
            catchup_match = re.search(r'catchup-source="rtsp://([^"?]+)', line)
            if catchup_match:
                # 提取 ip:port/path.rsc 部分
                full_path = catchup_match.group(1)
                # 匹配到 .rsc 结尾
                rsc_match = re.match(r'(.+?\.rsc)', full_path)
                if rsc_match:
                    source_map[tvg_name] = rsc_match.group(1)
                    print(f"  源文件 [{tvg_name}]: {rsc_match.group(1)}")
    
    print(f"\n源文件共解析到 {len(source_map)} 个频道的 catchup-source")
    return source_map


def update_local_file(local_content, source_map):
    """
    更新本地文件中的 catchup-source
    本地格式: catchup-source="http://192.168.100.1:5140/rtsp/112.245.125.39:1554/iptv/.../xxx.rsc?tvdr=...&r2h-seek-offset=-28800"
    需要替换的部分: 112.245.125.39:1554/iptv/.../xxx.rsc
    """
    lines = local_content.strip().split('\n')
    updated_lines = []
    update_count = 0
    
    for line in lines:
        if line.startswith('#EXTINF') and 'catchup-source=' in line:
            # 提取 tvg-name
            tvg_name_match = re.search(r'tvg-name="([^"]+)"', line)
            if tvg_name_match:
                tvg_name = tvg_name_match.group(1)
                
                if tvg_name in source_map:
                    new_path = source_map[tvg_name]
                    
                    # 匹配本地文件中 catchup-source 里的 ip:port/path.rsc 部分
                    # 格式: http://192.168.100.1:5140/rtsp/112.245.125.39:1554/iptv/.../xxx.rsc?tvdr=...
                    pattern = r'(catchup-source="http://[^/]+/rtsp/)([^"?]+\.rsc)(\?[^"]*")'
                    match = re.search(pattern, line)
                    
                    if match:
                        old_path = match.group(2)
                        if old_path != new_path:
                            # 替换路径
                            new_line = re.sub(
                                pattern,
                                rf'\g<1>{new_path}\g<3>',
                                line
                            )
                            print(f"  更新 [{tvg_name}]:")
                            print(f"    旧: {old_path}")
                            print(f"    新: {new_path}")
                            line = new_line
                            update_count += 1
        
        updated_lines.append(line)
    
    print(f"\n共更新 {update_count} 个频道的 catchup-source")
    return '\n'.join(updated_lines)


def get_content_hash(content):
    """计算内容哈希"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def read_hash():
    """读取上次的哈希值"""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            return f.read().strip()
    return ""


def save_hash(hash_value):
    """保存哈希值"""
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)
    with open(HASH_FILE, 'w') as f:
        f.write(hash_value)


def main():
    print("=" * 60)
    print("开始更新 catchup-source")
    print("=" * 60)
    
    # 下载源文件
    try:
        source_content = download_source(SOURCE_URL)
    except Exception as e:
        print(f"下载源文件失败: {e}")
        return False
    
    # 检查源文件是否有变化
    new_hash = get_content_hash(source_content)
    old_hash = read_hash()
    
    # 检查是否强制更新
    force_update = os.environ.get('FORCE_UPDATE', 'false').lower() == 'true'
    
    if new_hash == old_hash and not force_update:
        print("\n源文件没有变化，跳过更新")
        return False
    
    if force_update:
        print("\n强制更新模式")
    else:
        print(f"\n源文件已更新 (hash: {old_hash[:8] if old_hash else 'none'}... -> {new_hash[:8]}...)")
    
    # 解析源文件
    print("\n--- 解析源文件 ---")
    source_map = parse_source_m3u(source_content)
    
    if not source_map:
        print("源文件解析失败，没有找到有效的频道信息")
        return False
    
    # 读取本地文件
    print("\n--- 读取本地文件 ---")
    if not os.path.exists(LOCAL_FILE):
        print(f"本地文件不存在: {LOCAL_FILE}")
        return False
    
    with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
        local_content = f.read()
    
    print(f"本地文件: {LOCAL_FILE}")
    
    # 更新本地文件
    print("\n--- 更新 catchup-source ---")
    updated_content = update_local_file(local_content, source_map)
    
    # 保存更新后的文件
    output_dir = os.path.dirname(OUTPUT_FILE)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"\n已保存到: {OUTPUT_FILE}")
    
    # 保存哈希
    save_hash(new_hash)
    
    print("\n" + "=" * 60)
    print("更新完成!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    # 输出结果供 GitHub Actions 使用
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"updated={'true' if success else 'false'}\n")
