# SDU-IPTV-PRO
基于 [plsy1/iptv](https://github.com/plsy1/iptv) 项目开发的自动化 IPTV 源处理和发布系统。
## 📁 项目结构
```
your-repo-name/
├── unicast.m3u                    # 处理后的单播源
├── multicast-rtp.m3u              # 处理后的组播源
├── scripts/                       # 处理脚本
│   ├── process_unicast.py         # 单播处理
│   └── process_multicast.py       # 组播处理
├── .data/                         # 数据文件
├── .github/workflows/              # 自动化工作流
└── README.md
```
## 🚀 功能特性
- **自动更新**: 每小时检查源文件变化
- **智能排序**: 频道自动分类和排序
- **URL转换**: 组播源回看地址自动转换
- **自动发布**: 变更时自动创建 Release
- **EPG保留**: 完整保留原始 EPG 信息
## 📖 使用方法
### 直接使用
- **单播源**: `unicast.m3u`
- **组播源**: `multicast-rtp.m3u`
### 历史版本
查看仓库 [Releases](../../releases) 页面
## ⚙️ 配置说明
### 源地址配置
编辑 `scripts/` 目录下对应脚本的配置部分：
```python
SOURCE_M3U_URL = "你的源地址"
OUTPUT_FILENAME = "输出文件名"
```
### 工作流时间
- **更新频率**: 每小时（北京时间）
- **发布频率**: 每天凌晨（北京时间）
## 🔧 主要转换规则
### 频道排序
1. CGTN 频道归类到"其他频道"
2. 复制山东卫视到央视频道组
3. CCTV4 欧洲/美洲移动到山东少儿后
4. 山东经济广播移到末尾
### URL转换
**回看源**: `rtsp://...${(b)yyyyMMddHHmmss:utc}...` → `http://192.168.100.1:5140/rtsp/...${(b)yyyyMMddHHmmss}...&r2h-seek-offset=-28800`
**直播源**: `192.168.0.1` → `192.168.100.1`

---
感谢 [plsy1/iptv](https://github.com/plsy1/iptv) 项目提供的原始源文件和处理思路。
