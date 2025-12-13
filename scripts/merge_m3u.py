import os
import filecmp
import glob
import re

# --- 配置 ---
# 定义备份文件目录和文件路径
backup_dir = 'backup'
temp_unicast_path = os.path.join(backup_dir, 'temp-unicast.m3u')
temp_multicast_r2h_path = os.path.join(backup_dir, 'temp-multicast-r2h.m3u')
temp_multicast_nofcc_path = os.path.join(backup_dir, 'temp-multicast-nofcc.m3u')

# 定义自定义文件目录
custom_dir = 'custom'

# 定义最终输出文件路径
final_unicast_path = 'unicast.m3u'
final_multicast_r2h_path = 'multicast-r2h.m3u'
final_multicast_nofcc_path = 'multicast-nofcc.m3u'

# 标记，用于记录是否有文件被实际更新
any_file_updated = False

def natural_sort_key(s):
    """
    用于自然排序的key函数，确保 'custom2.m3u' 在 'custom10.m3u' 之前。
    """
    # 从路径中提取文件名进行排序
    filename = os.path.basename(s)
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]

def find_and_sort_custom_files():
    """
    查找并排序 custom 目录下的所有自定义文件。
    """
    # 使用 glob 查找所有匹配的文件，例如 'custom/custom.m3u', 'custom/custom1.m3u'
    pattern = os.path.join(custom_dir, 'custom*.m3u')
    custom_files = glob.glob(pattern)
    
    # 对文件列表进行自然排序
    custom_files.sort(key=natural_sort_key)
    
    return custom_files

# --- 主程序 ---
if __name__ == "__main__":
    print("开始合并播放列表...")
    
    # 1. 预先查找所有自定义文件
    all_custom_files = find_and_sort_custom_files()
    
    if not all_custom_files:
        print("警告: 在 'custom' 目录下未找到任何 'custom*.m3u' 文件。")
    else:
        print(f"找到以下自定义文件，将按顺序合并: {', '.join([os.path.basename(f) for f in all_custom_files])}")

    # 2. 定义需要处理的三个合并任务
    merge_tasks = [
        (temp_unicast_path, final_unicast_path),
        (temp_multicast_r2h_path, final_multicast_r2h_path),
        (temp_multicast_nofcc_path, final_multicast_nofcc_path),
    ]

    # 3. 遍历并执行每个合并任务
    for temp_path, final_path in merge_tasks:
        # 读取备份文件内容作为基础
        merged_content = ""
        if os.path.exists(temp_path):
            with open(temp_path, 'r', encoding='utf-8') as f:
                merged_content = f.read()
            print(f"  - 基础文件: {temp_path}")
        else:
            print(f"  - 警告: 基础文件 {temp_path} 不存在，将只合并自定义文件。")
        
        # 依次追加所有自定义文件内容
        for custom_file in all_custom_files:
            if os.path.exists(custom_file):
                with open(custom_file, 'r', encoding='utf-8') as f:
                    merged_content += '\n' + f.read()
                print(f"    + 合并自定义文件: {os.path.basename(custom_file)}")

        # 检查并写入最终文件（仅在内容有变化时）
        if os.path.exists(final_path):
            temp_merged_path = final_path + '.tmp'
            with open(temp_merged_path, 'w', encoding='utf-8') as f:
                f.write(merged_content)
                
            if not filecmp.cmp(final_path, temp_merged_path, shallow=False):
                os.replace(temp_merged_path, final_path)
                print(f"  -> 成功合并并更新: {final_path}")
                any_file_updated = True
            else:
                os.remove(temp_merged_path)
                print(f"  -> 无变化: {final_path} 内容已是最新，跳过更新。")
        else:
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(merged_content)
            print(f"  -> 成功创建: {final_path} (新文件)")
            any_file_updated = True
            
    # 4. 输出最终状态
    print("\n--- 合并任务完成 ---")
    if any_file_updated:
        print("状态: 检测到文件更新，已提交。")
    else:
        print("状态: 所有文件均无变化。")
