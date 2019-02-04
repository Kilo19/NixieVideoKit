# 代码库结构  
本代码库存放辉光字幕组部分辅助工具，大部分文件没有文档  
- nvksupport.py：压制工具  
- nvkdeamon.py：监视生肉文件夹并自动压制，监视下令txt并启动熟肉压制  
- paam.py, prr.py：压制/混流校对录像音频  
- Bili_Enc.py：启动熟肉/上传版压制  
- NixieCloud_Enc.py：启动生肉/预览版压制  
- settings - sample.py：nvksupport的配置文件，详情查看文件内注释。使用时请更名为settings.py  
- voicebase.py：抓取机器识别稿，自带时间戳，精确到词，使用需要voicebase的token  
- Full-auto_M134_public.py: 从双语文本稿生成ass文件，如果搭配voicebase输出的json可以自动生成时间戳（打轴）  
- 翻译分段.py：按视频长度和翻译人数生成每个翻译负责的时间段  
- Adaptive CRF.tm & .pdf：论证了CRF和视频体积的关系（英文）  
- hardSub.vpy：熟肉/上传版压制需要的VapourSynth脚本  
- 辉光样式.ass：辉光字幕组使用的字幕样式，下载后用aegisub打开，样式管理器中即有全部样式。如需使用请遵守下方协议  

# 授权协议  
本代码库中文件如无说明均采用MIT协议，引用自其他库的代码遵循源协议  
"辉光样式.ass"除外，见下文  

## 使用辉光样式  
本样式脚本分辨率 (https://aegi.vmoe.info/docs/3.2/Script_Resolution/) 固定1280x720  
与上方链接的推荐不同，如果将该样式应用在其他分辨率的视频上，建议保持脚本分辨率不变  
“辉中”为中文样式，“辉英”为英文样式  
“辉注”为注释样式，“LTT intro”为白屏intro样式  

若使用此样式，请公开样式参数，并声明样式原作者  

公开方式（以下任选其一）：  
- 在视频本体或简介中注明本代码库链接或包含此样式的网页的链接  
- 以截图贴出样式参数  
- 贴出“辉光样式.ass”文件内容  

声明作者方式（以下任选其一）：  
- 在视频本体或简介中注明样式来自本代码库，并提供本代码库链接  
- 在视频本体或简介中注明该样式来自辉光字幕组  

在多个视频中重复使用可以只声明并公开一次，但每次观众询问样式来源均需要指向本库  

说实话这个字幕样式没多少原创成分，如果你不希望做上面两条的话，则可以（以下任选其一）：  
- 在同一脚本分辨率下，样式参数中任意数值与原值差距超过10%  
- 不使用ass字幕文件，而在其他软件中重现此样式  

此时可选择注明“样式修改自辉光字幕组样式”并提供本库链接，但不必须。  

# 安装  
1. 将settings - sample.py重命名为settings.py  
1. VapourSynth R45以下安装python 3.6 (https://www.python.org/downloads/ )，R45及以上安装python 3.7
	- 3.6或3.7中任何一个子版本均可 (如3.6.1与3.6.7, 3.7.0与3.7.1)  
	- 32(x86)或64位(x86-64)均可，但后面安装VapourSynth和VSFilterMod需要匹配  
	- 32位库更多，上手的话个人建议32位  
	- 安装64位则需要修改nvksupport.py:47的vspipe_exec以指向64位版vspipe  
	- **安装时请勾选Add Python to PATH**，安装结束时建议选择Disable Path Length Limit  
	- Install for all users可以不选，选了的话未来通过pip安装新的python库需要管理员权限  
1. 安装ffmpeg (https://ffmpeg.org/ )
	- 建议走chocolatey (https://chocolatey.org/ ), ffmpeg包地址: https://chocolatey.org/packages/ffmpeg  
1. 代码库自带编译好的fdkaac (位于Program文件夹下)，无需自行编译安装  
1. 安装VapourSynth (http://www.vapoursynth.com/doc/installation.html )  
	- 请选择VapourSynth installer (也就是不带Portable后缀的.exe安装包)，程序会根据python位宽自动选择32/64位  
1. 还需要VapourSynth版的VSFilterMod (https://github.com/sorayuki/VSFilterMod/releases )  
	- x86对应32位python，x64对应64位，请与python位宽保持一致  
	- 下载对应版本后将压缩包中的VSFilterMod.dll复制到VapourSynth插件文件夹中 (http://www.vapoursynth.com/doc/autoloading.html )  
	- 例: 32位VapourSynth对应的路径是C:\\Program Files (x86)\\VapourSynth\\plugins32  
1. 以类似的方式安装ffms2 (https://github.com/FFMS/ffms2/releases )  
	- 下载.7z压缩包后，32位库位于x86文件夹下，64位库位于x64文件夹

# 使用  
压制B站视频 (可选内嵌.ass字幕)，双击Bili_Enc.py，按提示操作  
B站除大会员画质外全线二压，参考 https://t.bilibili.com/156780174754121850?tab=1  
**字幕文件所在文件夹的绝对路径中只能有ASCII字符**  
	- 如果你将字幕放在C:\\翻译\\New Project中，那么压制会因为路径中有“翻译”这个文件夹名而失败  
	- 字幕文件的文件名反倒不用担心，脚本会自动复制并更名  
		- C:\\SOUND HOLIC\\PVD\\TOKUTEN\\MP4\\東方好八起トレーラー.ass 可以压制  
