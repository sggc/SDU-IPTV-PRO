# scripts/merge_m3u.py
import os
import sys

def merge_files(temp_file, custom_file, output_file):
    """
    将临时文件和自定义文件合并，生成最终文件。
    临时文件内容在前，自定义文件内容在后。
    """
    try:
        # 读取临时文件内容
        with open(temp_file, 'r', encoding='utf-8') as f:
            temp_content = f.read()

        # 读取自定义文件内容
        with open(custom_file, 'r', encoding='utf-8') as f:
            custom_content = f.read()

        # 拼接内容
        final_content = temp_content + custom_content

        # 写入最终文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"成功合并: {temp_file} + {custom_file} -> {output_file}")
        return True

    except FileNotFoundError as e:
        print(f"错误: 文件未找到 - {e.filename}")
        return False
    except Exception as e:
        print(f"合并时发生未知错误: {e}")
        return False

if __name__ == "__main__":
    # 定义文件路径
    custom_file = "custom/custom.m3u"
    
    # 定义需要合并的文件对 (临时文件, 最终输出文件)
    merge_jobs = [
        ("temp/temp-unicast.m3u", "unicast.m3u"),
        ("temp/temp-multicast-r2h.m3u", "multicast-r2h.m3u"),
        ("temp/temp-multicast-nofcc.m3u", "multicast-nofcc.m3u"),
    ]

    all_success = True
    for temp_file, output_file in merge_jobs:
        if not merge_files(temp_file, custom_file, output_file):
            all_success = False

    if not all_success:
        sys.exit(1) # 如果有任何一个失败，则以错误码退出
