# SDU-IPTV-PRO
基于 [plsy1/iptv](https://github.com/plsy1/iptv) 

## 📒 聚合型EPG
以项目 [plsy1/epg](https://github.com/plsy1/epg) 为蓝本，一方面对标多渠道 EPG 数据源进行交叉核验，另一方面定向采集电视猫与搜视网平台的山东地市频道节目信息，通过内容增补、数据替换等精细化优化，着力打造适配本仓库的最全版本 EPG 资源。

### 使用方法
复制以下任意链接到常见直播壳中即可使用：
- 无desc节目描述：https://raw.githubusercontent.com/sggc/SD-EPG/refs/heads/main/EPG/sggc.xml.gz
- 有desc节目描述：https://raw.githubusercontent.com/sggc/SD-EPG/refs/heads/main/EPG/sggc-desc.xml.gz

## 📖 频道列表
### 更新时间

### 所有频道


## 🔧 关键转换规则
### 频道排序优化
1. CGTN相关频道归类至「其他频道」
2. 山东卫视复制一份至央视频道组，方便集中观看
3. CCTV4欧洲/美洲调整至山东少儿频道之后
4. 山东经济广播移至频道列表末尾

### URL格式转换
#### 回看源转换
`rtsp://...\({...:utc}...`
→
`http://192.168.100.1/rtsp/...\)
{...}...&r2h-seek-offset=-28800`
- 单播RTSP协议转HTTP协议，兼容Ku9播放器
- 适配rtp2httpd网页端播放器回看格式，优化时间戳同步

#### 直播源转换
- 组播源地址 `192.168.0.1` 统一替换为 `192.168.100.1`
- 组播RTP协议转HTTP协议，提升跨设备兼容性

## 🚨 免责声明
1. 本项目不生产、不存储任何直播内容，所有数据均来源于公开网络及原作者仓库，仅做格式转换与整理。
2. 直播内容的版权归电视台、广电机构等原版权方所有，本项目不承担内容合法性、可用性的担保责任。
3. 仅供个人学习、测试使用，下载后请在24小时内删除，严禁用于商业用途或非法传播。
4. 如因使用本项目内容引发版权纠纷、法律责任，均由使用者自行承担，与项目维护者无关。
5. 若本项目内容侵犯您的合法权益（如版权、商标权等），请通过GitHub Issues联系，我们将在核实后24小时内删除相关内容。

## 🙏 致谢
正是无数技术先行者的默默耕耘与无私分享，才让优质IPTV资源触手可及。特别感谢 [plsy1/iptv](https://github.com/plsy1/iptv) 项目提供的原始源文件与核心处理思路，以及 [sumingyd/IPTV-Scanner-Editor-Pro](https://github.com/sumingyd/IPTV-Scanner-Editor-Pro) 项目提供的检测源有效性工具，为本次开发奠定了坚实基础，谨致以最诚挚的敬意与感谢！
