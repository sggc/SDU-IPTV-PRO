import re
import os
import shutil
from pathlib import Path

BASE_DIR = Path(r".")
SOURCE_M3U_FILE = BASE_DIR / "SDM-Unicast.m3u"
OUTPUT_DIR = BASE_DIR / "SDM-Unicast"

CITY_NAMES = [
    "济南", "青岛", "淄博", "潍坊", "烟台", "威海", "日照", "临沂",
    "济宁", "泰安", "德州", "聊城", "滨州", "菏泽", "枣庄", "东营"
]

CITY_NAMES_EN = {
    "济南": "Jinan", "青岛": "Qingdao", "淄博": "Zibo", "潍坊": "Weifang",
    "烟台": "Yantai", "威海": "Weihai", "日照": "Rizhao", "临沂": "Linyi",
    "济宁": "Jining", "泰安": "Taian", "德州": "Dezhou", "聊城": "Liaocheng",
    "滨州": "Binzhou", "菏泽": "Heze", "枣庄": "Zaozhuang", "东营": "Dongying"
}

CITY_CHANNELS = {
    "枣庄": ["枣庄新闻综合", "枣庄经济生活", "滕州综合"],
    "潍坊": ["潍坊新闻综合", "潍坊经济生活", "潍坊公共", "潍坊科教文化", "寿光综合", "诸城综合", "安丘综合", "昌邑综合", "青州综合", "高密综合", "临朐综合", "青州文化旅游", "潍坊高新", "奎文频道", "昌乐新闻", "寿光蔬菜"],
    "滨州": ["滨州民生", "滨州新闻", "惠民综合", "邹平综合", "阳信综合", "无棣综合", "沾化综合", "博兴综合"],
    "德州": ["德州生活", "德州新闻", "临邑综合", "夏津综合", "宁津综合", "武城综合", "禹城综合", "禹城综艺", "齐河综合", "平原综合", "陵城综合", "夏津公共"],
    "东营": ["东营公共", "东营新闻综合", "广饶综合"],
    "菏泽": ["菏泽-1", "菏泽-2", "东明综合", "巨野新闻", "微山综合", "郓城综合", "定陶综合", "单县综合"],
    "济南": ["济南都市", "济南教育", "济南鲁中", "济南少儿", "济南生活", "济南文旅体育", "济南新闻", "济南娱乐", "济南新闻综合", "商河综合", "平阴综合", "济阳综合", "长清综合", "历城综合", "章丘综合"],
    "济宁": ["济宁高新", "济宁公共", "济宁生活", "济宁综合", "任城生活", "任城综合", "兖州新闻", "嘉祥新闻", "曲阜新闻", "汶上综合", "邹城新闻", "鱼台新闻", "鱼台生活", "泗水综合"],
    "聊城": ["聊城民生", "聊城综合", "东阿综合", "临清综合", "冠县综合", "茌平综合", "莘县综合", "东昌综合"],
    "临沂": ["临沂综合", "临沂经济生活", "临沭综合", "兰陵公共", "兰陵综合", "沂南综合", "沂水生活", "沂水综合", "河东综合", "红色影视", "莒南综合", "蒙阴综合"],
    "泰安": ["泰安经济生活", "泰安综合", "东平综合", "宁阳综合", "新泰乡村", "新泰新闻", "肥城综合", "泰山综合", "岱岳综合", "宁阳影视"],
    "淄博": ["淄博民生", "淄博文旅", "淄博新闻综合", "淄博影视", "张店综合", "沂源综合", "淄川新闻", "高青综合", "桓台综合", "周村新闻", "临淄TV-1"],
    "威海": ["威海新闻", "威海海洋生活", "乳山综合", "荣成综合", "文登综合"],
    "日照": ["日照公共", "日照新闻", "日照科教", "莒县综合", "岚山综合", "五莲新闻"],
    "烟台": ["烟台公共", "烟台新闻", "烟台经济科技", "栖霞综合", "招远综合", "蓬莱综合", "长岛综合", "海阳综合", "海阳综艺", "牟平生活", "牟平综合"],
    "青岛": ["青岛QTV-1", "青岛QTV-2", "青岛QTV-3", "青岛QTV-4", "青岛QTV-5", "胶州综合", "莱西综合", "崂山综合", "平度综合", "黄岛生活", "黄岛综合", "即墨新闻"],
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

def generate_sdm_unicast():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    all_channels = parse_m3u()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for city in CITY_NAMES:
        city_channel_names = set(CITY_CHANNELS.get(city, []))

        output_lines = ['#EXTM3U url-tvg="https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SD-EPG/main/EPG/sggc-desc.xml.gz"']

        for ch in all_channels:
            if ch["name"] in city_channel_names:
                modified_extinf = re.sub(
                    r'group-title="[^"]*"',
                    'group-title="山东频道"',
                    ch["extinf"]
                )
                output_lines.append(modified_extinf)
                output_lines.append(ch["url"])
            else:
                output_lines.append(ch["extinf"])
                output_lines.append(ch["url"])

        output_file = OUTPUT_DIR / f"SDM-Unicast-{CITY_NAMES_EN[city]}.m3u"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        print(f"Generated: {output_file.name} ({len(city_channel_names)} channels)")

if __name__ == "__main__":
    generate_sdm_unicast()
    print(f"\nAll files generated in: {OUTPUT_DIR}")