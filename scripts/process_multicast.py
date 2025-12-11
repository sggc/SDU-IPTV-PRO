#!/usr/bin/env python3
import requests
import re
import hashlib
import os
from datetime import datetime, timezone, timedelta

# ==================== 配置 ====================
SOURCE_M3U_URL = "https://raw.githubusercontent.com/plsy1/iptv/refs/heads/main/multicast/multicast-weifang.m3u"
OUTPUT_FILENAME = "temp/multicast-rtp.m3u"
OUTPUT_NOFCC_FILENAME = "temp/multicast-nofcc.m3u"  # 新增配置
HASH_FILE = ".data/multicast_hash.txt"
# ==============================================

class MulticastM3UProcessor:
    def __init__(self, source_url, output_file, output_nofcc_file, hash_file):  # 修改构造函数
        self.source_url = source_url
        self.output_file = output_file
        self.output_nofcc_file = output_nofcc_file  # 新增属性
        self.hash_file = hash_file
        self.channels = []
        self.extm3u_line = "#EXTM3U"  # 保存原始的EXTM3U行
    
    def get_beijing_time(self):
        """获取北京时间（东八区）"""
        beijing_tz = timezone(timedelta(hours=8))
        return datetime.now(beijing_tz)
    
    def get_content_hash(self, content):
        """计算内容的MD5哈希值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_previous_hash(self):
        """获取之前保存的源文件哈希值"""
        if os.path.exists(self.hash_file):
            with open(self.hash_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return None
    
    def save_current_hash(self, content):
        """保存当前源文件的哈希值"""
        current_hash = self.get_content_hash(content)
        os.makedirs(os.path.dirname(self.hash_file), exist_ok=True)
        with open(self.hash_file, 'w', encoding='utf-8') as f:
            f.write(current_hash)
        return current_hash
    
    def has_source_changed(self, content):
        """检查源文件是否发生变化"""
        current_hash = self.get_content_hash(content)
        previous_hash = self.get_previous_hash()
        
        if previous_hash is None:
            print("首次运行，没有之前的哈希记录")
            return True
        
        if current_hash == previous_hash:
            print("源文件没有变化，跳过处理")
            return False
        else:
            print(f"源文件发生变化: 旧哈希 {previous_hash[:8]}... -> 新哈希 {current_hash[:8]}...")
            return True
    
    def download_file(self):
        """下载M3U文件"""
        print(f"下载M3U文件从: {self.source_url}")
        response = requests.get(self.source_url, timeout=30)
        response.raise_for_status()
        return response.text
    
    def parse_m3u(self, content):
        """解析M3U文件内容"""
        self.channels = []
        lines = content.split('\n')
        current_channel = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 保存原始的EXTM3U行（包含EPG信息）
            if line.startswith('#EXTM3U'):
                self.extm3u_line = line
                print(f"保留EXTM3U行: {line}")
                continue
            
            if line.startswith('#EXTINF:'):
                if current_channel and current_channel.get('url'):
                    self.channels.append(current_channel)
                
                current_channel = {
                    'extinf': line,
                    'url': None,
                    'name': self.extract_channel_name(line),
                    'tvg_name': self.extract_tvg_attribute(line, 'tvg-name'),
                    'group_title': self.extract_tvg_attribute(line, 'group-title'),
                }
            elif not line.startswith('#') and current_channel:
                current_channel['url'] = line
                self.channels.append(current_channel)
                current_channel = {}
        
        if current_channel and current_channel.get('url'):
            self.channels.append(current_channel)
    
    def extract_channel_name(self, extinf_line):
        """从EXTINF行提取频道名称"""
        match = re.search(r',([^,]+)$', extinf_line)
        if match:
            return match.group(1).strip()
        return ""
    
    def extract_tvg_attribute(self, extinf_line, attribute_name):
        """提取tvg属性值"""
        pattern = f'{attribute_name}="([^"]*)"'
        match = re.search(pattern, extinf_line)
        if match:
            return match.group(1)
        return ""
    
    def update_group_title(self, channel, new_group_title):
        """更新频道的group-title属性"""
        old_extinf = channel['extinf']
        
        if 'group-title=' in old_extinf:
            new_extinf = re.sub(
                r'group-title="[^"]*"',
                f'group-title="{new_group_title}"',
                old_extinf
            )
        else:
            new_extinf = old_extinf.replace(
                '#EXTINF:-1 ',
                f'#EXTINF:-1 group-title="{new_group_title}" '
            )
        
        channel['extinf'] = new_extinf
        channel['group_title'] = new_group_title
    
    def find_channel_index(self, name_patterns, exact_match=False):
        """查找匹配的频道索引"""
        for i, channel in enumerate(self.channels):
            if exact_match:
                if any(pattern == channel['name'] for pattern in name_patterns):
                    return i
            else:
                if any(pattern in channel['name'] for pattern in name_patterns):
                    return i
        return -1
    
    def find_all_channel_indices(self, name_patterns, exact_match=False):
        """查找所有匹配的频道索引"""
        indices = []
        for i, channel in enumerate(self.channels):
            if exact_match:
                if any(pattern == channel['name'] for pattern in name_patterns):
                    indices.append(i)
            else:
                if any(pattern in channel['name'] for pattern in name_patterns):
                    indices.append(i)
        return indices
    
    def move_channels_after_target(self, source_patterns, target_pattern, exact_match=False):
        """将源频道移动到目标频道之后"""
        target_idx = self.find_channel_index([target_pattern], exact_match=exact_match)
        if target_idx == -1:
            print(f"警告: 未找到目标频道 '{target_pattern}'")
            return False
        
        source_indices = self.find_all_channel_indices(source_patterns, exact_match=exact_match)
        if not source_indices:
            print(f"警告: 未找到源频道 {source_patterns}")
            return False
        
        print(f"找到目标频道 '{target_pattern}' 在位置 {target_idx}")
        print(f"找到源频道 {source_patterns} 在位置 {source_indices}")
        
        channels_to_move = []
        for idx in sorted(source_indices, reverse=True):
            channel = self.channels.pop(idx)
            channels_to_move.insert(0, channel)
        
        # 重新查找目标位置（因为列表已改变）
        target_idx = self.find_channel_index([target_pattern], exact_match=exact_match)
        insert_position = target_idx + 1
        
        for channel in channels_to_move:
            self.channels.insert(insert_position, channel)
            print(f"已将 {channel['name']} 移动到 {target_pattern} 后面 (位置: {insert_position})")
            insert_position += 1
        
        return True
    
    def process_sorting(self):
        """排序规则处理"""
        print("开始处理频道排序和分类...")
        
        # 1. 将CGTN相关频道改为"其他频道"
        cgtn_indices = self.find_all_channel_indices(['CGTN'])
        for idx in cgtn_indices:
            old_group = self.channels[idx]['group_title'] or '未知分组'
            self.update_group_title(self.channels[idx], "其他频道")
            print(f"将 {self.channels[idx]['name']} 从 '{old_group}' 改为 '其他频道'")
        
        # 2. 复制山东卫视（不包括4K版本）到CCTV1下面，并改为"央视频道"
        shandong_idx = self.find_channel_index(['山东卫视'], exact_match=True)
        cctv1_idx = self.find_channel_index(['CCTV1', 'CCTV-1'])
        
        if shandong_idx != -1 and cctv1_idx != -1:
            original_shandong = self.channels[shandong_idx]
            copied_shandong = original_shandong.copy()
            copied_shandong['extinf'] = original_shandong['extinf']  # 确保复制
            
            self.update_group_title(copied_shandong, "央视频道")
            
            insert_position = cctv1_idx + 1
            self.channels.insert(insert_position, copied_shandong)
            print(f"已复制山东卫视并插入到CCTV1后面 (位置: {insert_position})，分组改为央视频道")
        
        # 3. 将CCTV4欧洲和美洲移动到山东少儿之后
        self.move_channels_after_target(
            source_patterns=['CCTV4欧洲', 'CCTV4美洲'],
            target_pattern='山东少儿',
            exact_match=False
        )
        
        # 4. 处理山东经济广播
        shandong_economic_radio_idx = self.find_channel_index(['山东经济广播'], exact_match=True)
        
        if shandong_economic_radio_idx != -1:
            radio_channel = self.channels[shandong_economic_radio_idx]
            old_group = radio_channel['group_title'] or '未知分组'
            self.update_group_title(radio_channel, "广播频道")
            print(f"将 {radio_channel['name']} 从 '{old_group}' 改为 '广播频道'")
            
            radio_channel = self.channels.pop(shandong_economic_radio_idx)
            self.channels.append(radio_channel)
            print(f"已将 {radio_channel['name']} 移动到列表末尾")
        
        print("频道排序处理完成")
    
    def convert_catchup_source(self, extinf_line):
        """转换回看源地址 - 修改后的转换规则"""
        # 使用正则表达式提取和转换回看源
        def replace_catchup_source(match):
            original_url = match.group(1)  # 原始rtsp地址
            # 转换时间戳格式
            # ${(b)yyyyMMddHHmmss:utc} -> ${(b)yyyyMMddHHmmss}
            # ${(e)yyyyMMddHHmmss:utc} -> ${(e)yyyyMMddHHmmss}
            converted_url = original_url.replace(
                '${(b)yyyyMMddHHmmss:utc}', '${(b)yyyyMMddHHmmss}'
            ).replace(
                '${(e)yyyyMMddHHmmss:utc}', '${(e)yyyyMMddHHmmss}'
            )
            
            # 构建新的URL
            new_url = f"http://192.168.100.1:5140/rtsp/{converted_url}&r2h-seek-offset=-28800"
            return f'catchup-source="{new_url}"'
        
        # 匹配catchup-source属性
        pattern = r'catchup-source="rtsp://([^"]+)"'
        return re.sub(pattern, replace_catchup_source, extinf_line)
    
    def convert_live_url(self, url):
        """转换直播源地址"""
        # 将 http://192.168.0.1:5140/rtp/... 改为 http://192.168.100.1:5140/rtp/...
        return url.replace('http://192.168.0.1:5140/', 'http://192.168.100.1:5140/')
    
    def remove_fcc_suffix(self, url):
        """删除直播源中的FCC后缀"""
        # 删除 ?fcc=124.132.240.66:15970 后缀
        return re.sub(r'\?fcc=124\.132\.240\.66:15970$', '', url)
    
    def process_url_conversion(self):
        """处理URL转换 - 包含新的回看源转换规则"""
        print("开始处理URL转换...")
        
        catchup_count = 0
        live_count = 0
        
        for channel in self.channels:
            # 转换回看源（新的转换规则）
            old_extinf = channel['extinf']
            new_extinf = self.convert_catchup_source(old_extinf)
            if old_extinf != new_extinf:
                channel['extinf'] = new_extinf
                catchup_count += 1
                
                # 输出转换示例（前几个）
                if catchup_count <= 3:
                    print(f"回看源转换示例 {catchup_count}:")
                    print(f"  原始: {old_extinf[:100]}...")
                    print(f"  转换: {new_extinf[:120]}...")
            
            # 转换直播源
            old_url = channel['url']
            new_url = self.convert_live_url(old_url)
            if old_url != new_url:
                channel['url'] = new_url
                live_count += 1
        
        print(f"URL转换完成: 回看源转换 {catchup_count} 个, 直播源转换 {live_count} 个")
        
        # 转换示例
        if catchup_count > 0:
            print("\n转换规则示例:")
            print("  原格式: rtsp://112.245.125.39:1554/...?tvdr=${{(b)yyyyMMddHHmmss:utc}}GMT-${{(e)yyyyMMddHHmmss:utc}}GMT")
            print("  新格式: http://192.168.100.1:5140/rtsp/112.245.125.39:1554/...?tvdr=${{(b)yyyyMMddHHmmss}}GMT-${{(e)yyyyMMddHHmmss}}GMT&r2h-seek-offset=-28800")
    
    def generate_m3u_content(self, remove_fcc=False):  # 修改方法签名
        """生成新的M3U内容"""
        beijing_time = self.get_beijing_time()
        
        # 使用原始的EXTM3U行（保留EPG信息）
        header = f"""{self.extm3u_line}
# 源文件: {self.source_url}
# 修改时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)
# 处理规则:
# 1. CGTN频道改为"其他频道"
# 2. 复制山东卫视到CCTV1下面并改为"央视频道"
# 3. CCTV4欧洲/美洲移动到山东少儿之后
# 4. 山东经济广播移到末尾并改为"广播频道"
# 5. 回看源转换规则:
#    rtsp://...${{(b)yyyyMMddHHmmss:utc}}...${{(e)yyyyMMddHHmmss:utc}}...
#    -> http://192.168.100.1:5140/rtsp/...${{(b)yyyyMMddHHmmss}}...${{(e)yyyyMMddHHmmss}}...&r2h-seek-offset=-28800
# 6. 直播源: 192.168.0.1 -> 192.168.100.1"""
        
        # 如果是生成无FCC版本，添加说明
        if remove_fcc:
            header += "\n# 7. 移除FCC后缀: ?fcc=124.132.240.66:15970"
        
        header += "\n\n"
        
        content = header
        for channel in self.channels:
            content += channel['extinf'] + '\n'
            url = channel['url']
            # 如果需要移除FCC后缀，则处理URL
            if remove_fcc:
                url = self.remove_fcc_suffix(url)
            content += url + '\n'
        
        return content
    
    def process(self):
        """主处理流程"""
        try:
            # 下载源文件
            content = self.download_file()
            
            # 检查源文件是否发生变化
            if not self.has_source_changed(content):
                print("源文件没有变化，跳过处理")
                return True
            
            # 解析M3U内容
            self.parse_m3u(content)
            print(f"解析完成，共 {len(self.channels)} 个频道")
            
            # 执行排序规则
            self.process_sorting()
            
            # 执行URL转换
            self.process_url_conversion()
            
            # 生成标准版本内容并保存
            standard_content = self.generate_m3u_content(remove_fcc=False)
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(standard_content)
            print(f"标准版本已保存到 {self.output_file}")
            
            # 生成无FCC版本内容并保存
            nofcc_content = self.generate_m3u_content(remove_fcc=True)
            with open(self.output_nofcc_file, 'w', encoding='utf-8') as f:
                f.write(nofcc_content)
            print(f"无FCC版本已保存到 {self.output_nofcc_file}")
            
            # 保存当前哈希值
            self.save_current_hash(content)
            
            print("处理完成")
            return True
            
        except Exception as e:
            print(f"处理过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    processor = MulticastM3UProcessor(SOURCE_M3U_URL, OUTPUT_FILENAME, OUTPUT_NOFCC_FILENAME, HASH_FILE)  # 修改调用
    success = processor.process()
    
    if not success:
        print("处理失败")
        exit(1)


if __name__ == "__main__":
    main()
