import re
import os
import shutil
from pathlib import Path

BASE_DIR = Path(r".")
SOURCE_M3U_FILE = BASE_DIR / "SDU-Multicast.m3u"
OUTPUT_DIR = BASE_DIR / "SDU-Multicast"

CITY_NAMES = [
    "济南", "青岛", "淄博", "潍坊", "烟台", "威海", "日照", "临沂",
    "济宁", "泰安", "德州", "聊城", "滨州", "菏泽", "枣庄", "东营", "莱芜"
]

CITY_NAMES_EN = {
    "济南": "Jinan", "青岛": "Qingdao", "淄博": "Zibo", "潍坊": "Weifang",
    "烟台": "Yantai", "威海": "Weihai", "日照": "Rizhao", "临沂": "Linyi",
    "济宁": "Jining", "泰安": "Taian", "德州": "Dezhou", "聊城": "Liaocheng",
    "滨州": "Binzhou", "菏泽": "Heze", "枣庄": "Zaozhuang", "东营": "Dongying",
    "莱芜": "Laiwu"
}

CITY_CODES = {
    "济南": 242, "青岛": 254, "淄博": 252, "潍坊": 246, "烟台": 248,
    "威海": 230, "日照": 224, "临沂": 238, "济宁": 244, "泰安": 240,
    "德州": 250, "聊城": 228, "滨州": 234, "菏泽": 236, "枣庄": 226,
    "东营": 232, "莱芜": 222
}

FCC_CONFIG = {
    "潍坊": "60.210.139.78:8027",
    "烟台": "124.132.240.66:15970",
    "泰安": "124.132.240.66:15970",
    "临沂": "124.132.240.66:15970",
    "济南": "124.132.240.66:15970",
    "德州": "124.132.240.66:15970",
    "聊城": "124.132.240.66:15970",
    "济宁": "124.132.240.66:15970",
    "枣庄": "124.132.240.66:15970",
}

CITY_CHANNELS = {
    "潍坊": [
        {"extinf": '#EXTINF:-1 tvg-name="潍坊新闻综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东2/潍坊1.png", 潍坊新闻综合', "url": "http://192.168.100.1:5140/rtp/239.253.246.253:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="潍坊经济生活" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东2/潍坊2.png", 潍坊经济生活', "url": "http://192.168.100.1:5140/rtp/239.253.246.254:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="潍坊公共" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东2/潍坊3.png", 潍坊公共', "url": "http://192.168.100.1:5140/rtp/239.253.246.242:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="潍坊科教文化" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东2/潍坊4.png", 潍坊科教文化', "url": "http://192.168.100.1:5140/rtp/239.253.246.241:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="奎文电视台" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊奎文.png", 奎文电视台', "url": "http://192.168.100.1:5140/rtp/239.253.246.250:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="临朐综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊临朐.png", 临朐综合', "url": "http://192.168.100.1:5140/rtp/239.253.246.240:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="昌乐综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊昌乐.png", 昌乐综合', "url": "http://192.168.100.1:5140/rtp/239.253.246.251:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="青州综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊青州.png", 青州综合', "url": "http://192.168.100.1:5140/rtp/239.253.246.247:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="青州文化旅游" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊青州文旅.png", 青州文化旅游', "url": "http://192.168.100.1:5140/rtp/239.253.246.246:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="诸城综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊诸城.png", 诸城综合', "url": "http://192.168.100.1:5140/rtp/239.253.246.249:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="寿光综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊寿光.png", 寿光综合', "url": "http://192.168.100.1:5140/rtp/239.253.246.252:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="寿光蔬菜" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊寿光蔬菜.png", 寿光蔬菜', "url": "http://192.168.100.1:5140/rtp/239.253.246.248:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="安丘综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊安丘.png", 安丘综合', "url": "http://192.168.100.1:5140/rtp/239.253.246.245:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="高密综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊高密.png", 高密综合', "url": "http://192.168.100.1:5140/rtp/239.253.246.243:8000"},
        {"extinf": '#EXTINF:-1 tvg-name="昌邑综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/潍坊昌邑.png", 昌邑综合', "url": "http://192.168.100.1:5140/rtp/239.253.246.244:8000"},
    ],
    "青岛": [
        {"extinf": '#EXTINF:-1 tvg-name="青岛QTV-1" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/QTV1.png", QTV1', "url": "http://192.168.100.1:5140/rtp/239.253.254.249:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="青岛QTV-2" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/QTV2.png", QTV2', "url": "http://192.168.100.1:5140/rtp/239.253.254.250:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="青岛QTV-3" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/QTV3.png", QTV3', "url": "http://192.168.100.1:5140/rtp/239.253.254.251:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="青岛QTV-4" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/QTV4.png", QTV4', "url": "http://192.168.100.1:5140/rtp/239.253.254.252:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="青岛QTV-5" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/QTV5.png", QTV5', "url": "http://192.168.100.1:5140/rtp/239.253.254.253:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="青岛QTV-6" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/QTV6.png", QTV6', "url": "http://192.168.100.1:5140/rtp/239.253.254.254:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="崂山综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/青岛崂山.png", 崂山', "url": "http://192.168.100.1:5140/rtp/239.253.254.242:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="西海岸新闻" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/青岛西海岸.png", 西海岸新闻', "url": "http://192.168.100.1:5140/rtp/239.253.254.243:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="西海岸生活" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/青岛西海岸.png", 西海岸生活', "url": "http://192.168.100.1:5140/rtp/239.253.254.244:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="即墨综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/青岛即墨.png", 即墨', "url": "http://192.168.100.1:5140/rtp/239.253.254.245:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="青岛胶州" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/青岛胶州.png", 胶州综合', "url": "http://192.168.100.1:5140/rtp/239.253.254.246:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="莱西综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/青岛莱西.png", 莱西综合', "url": "http://192.168.100.1:5140/rtp/239.253.254.247:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="平度综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/青岛平度.png", 平度电视台', "url": "http://192.168.100.1:5140/rtp/239.253.254.248:8000?fcc=124.132.240.66:15970"},
    ],
    "泰安": [
        {"extinf": '#EXTINF:-1 tvg-name="泰安综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/泰安.png", 泰安综合', "url": "http://192.168.0.1:5140/rtp/239.253.240.252:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="泰安经济生活" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/泰安.png", 泰安经济生活', "url": "http://192.168.0.1:5140/rtp/239.253.240.253:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="泰山电视频道" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/泰安泰山.png", 泰山电视频道', "url": "http://192.168.0.1:5140/rtp/239.253.240.244:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="岱岳" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/泰安岱岳.png", 岱岳', "url": "http://192.168.0.1:5140/rtp/239.253.240.245:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="新泰乡村" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/泰安新泰乡村.png", 新泰乡村', "url": "http://192.168.0.1:5140/rtp/239.253.240.246:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="宁阳综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/泰安宁阳.png", 宁阳综合', "url": "http://192.168.0.1:5140/rtp/239.253.240.247:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="宁阳二台" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/泰安宁阳.png", 宁阳二台', "url": "http://192.168.0.1:5140/rtp/239.253.240.248:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="东平综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/泰安东平.png", 东平综合', "url": "http://192.168.0.1:5140/rtp/239.253.240.249:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="新泰综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/泰安新泰.png", 新泰综合', "url": "http://192.168.0.1:5140/rtp/239.253.240.250:8000?fcc=124.132.240.66:15970"},
        {"extinf": '#EXTINF:-1 tvg-name="肥城综合" group-title="山东频道" tvg-logo="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/山东/泰安肥城.png", 肥城综合', "url": "http://192.168.0.1:5140/rtp/239.253.240.251:8000?fcc=124.132.240.66:15970"},
    ],
    "济南": [],
    "淄博": [],
    "烟台": [],
    "威海": [],
    "日照": [],
    "临沂": [],
    "济宁": [],
    "德州": [],
    "聊城": [],
    "滨州": [],
    "菏泽": [],
    "枣庄": [],
    "东营": [],
    "莱芜": [],
}

def parse_m3u():
    channels = []
    with open(SOURCE_M3U_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'#EXTINF:-1 (.*?),(.*?)\n(.*?)(?=\n#EXTINF|$)'
    for match in re.findall(pattern, content, re.DOTALL):
        extinf_attrs = match[0]
        channel_name = match[1].strip()
        stream_url = match[2].strip()
        channels.append({
            "name": channel_name,
            "url": stream_url,
            "extinf": f"#EXTINF:-1 {extinf_attrs},{channel_name}"
        })
    return channels

def replace_ip_segment(url, city_code, fcc=None):
    pattern = r'239\.253\.\d+\.(\d+)'
    match = re.search(pattern, url)
    if match:
        fourth_segment = match.group(1)
        new_ip = f'239.253.{city_code}.{fourth_segment}'
        result = re.sub(r'239\.253\.\d+\.\d+', new_ip, url)
        result = re.sub(r'\?fcc=[^&]+', '', result)
        if fcc:
            result = f"{result}?fcc={fcc}"
        return result
    return url

def generate_sdu_multicast():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    all_channels = parse_m3u()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_known_channel_names = set()
    for channels in CITY_CHANNELS.values():
        for ch in channels:
            name_match = re.search(r',(.+)$', ch["extinf"])
            if name_match:
                all_known_channel_names.add(name_match.group(1).strip())

    for city in CITY_NAMES:
        city_code = CITY_CODES[city]
        fcc = FCC_CONFIG.get(city)
        city_channels = CITY_CHANNELS.get(city, [])

        output_lines = ['#EXTM3U url-tvg="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/EPG/sggc.xml.gz"']

        for ch in all_channels:
            name_match = re.search(r',(.+)$', ch["extinf"])
            channel_name = name_match.group(1).strip() if name_match else ch["name"]

            if channel_name in all_known_channel_names:
                continue

            modified_url = replace_ip_segment(ch["url"], city_code, fcc)
            output_lines.append(ch["extinf"])
            output_lines.append(modified_url)

        for ch in city_channels:
            modified_url = replace_ip_segment(ch["url"], city_code, fcc)
            output_lines.append(ch["extinf"])
            output_lines.append(modified_url)

        output_file = OUTPUT_DIR / f"SDU-Multicast-{CITY_NAMES_EN[city]}.m3u"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        ch_count = len(city_channels)
        status = "" if ch_count > 0 else " [无地方台数据]"
        print(f"Generated: {output_file.name} ({ch_count} channels){status}")

if __name__ == "__main__":
    generate_sdu_multicast()
    print(f"\nAll files generated in: {OUTPUT_DIR}")
