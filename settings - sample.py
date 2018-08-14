#! python3
# -*- coding: utf-8 -*-
#下载视频是否使用代理
#禁止传播带有有效voicebaseToken的设置文件
import os
useProxy = False
#代理地址和端口
proxy = 'localhost:1080'
#是否下载720p
source720p = False
#是否启用自定义下载目录 (默认启用)
#禁用则下载到脚本所在文件夹下的Video子文件夹)
overrideDownDir = True
#自定义下载目录路径
customDownDirRelative = 'NixieVideoDepot/'.replace('/', os.sep)
customDownDirRoot = 'L:/'.replace('/', os.sep)
customDownDir = os.path.join(customDownDirRoot, customDownDirRelative)
#降低转码优先级防止转码时电脑卡顿，6核及以下建议开启
#注意需要安装psutil以启用该功能
useQuell = False
#是否启用自定义输出目录 (默认启用)
#转码时手动指定输出路径则无视该选项
#不指定的话
#启用该选项
#并原视频在customDownDir中
#同时不提供输出路径的话
#输出视频会被移动到customOutDir中
#并自动放入输出视频同名文件夹中
#(没有则自动在customOutDir中创建)
#否则输出到源视频同目录下
overrideOutDir = True
cloudRoot = 'L:/NixieCloud/'.replace('/', os.sep)
cloudDir = 'Raw/LMG/'.replace('/', os.sep)
curMonthDir = '2018/AUG/'.replace('/', os.sep)
customOutDir = os.path.join(cloudRoot, cloudDir, curMonthDir)
#Bili_Enc最高码率，单位kbps，支持压制ass字幕
#一般用于投稿
#使用crf分配码率
#编码器判定目标视频不需要最高码率的话
#输出平均码率可能显著低于该值
#属于正常现象
#若原视频达到beBitrate(单位kbps)的90%则采用2-pass压制
#时间是1-pass CRF至少两倍，但码率保证等于beBitrate
beBitrate = 3000
beCRF = 25
#Bili_Enc预设
bePreset = 'slow'
#Bili_Enc输出视频高度，单位像素
#输出总会等比例缩放
#保证纵向分辨率尽可能等于该值
#因为视频编码原理所以分辨率只能是偶数
#更多设定参考nvksupport.py中ConvertVideo_1PassCRF()
beDecisionHeight = 1080
#NixieCloud_Enc目标码率，单位kbps，分辨率720p
#2-pass方式保证尽可能接近该码率
#该模式用于高压，适用于预览和分发视频
#更多设定参考nvksupport.py中ConvertVideo_2Pass
nceBitrate = 1000
#NixieCloud_Enc预设
ncePreset = 'slow'
#是否使用Voicebase
#没有Token无法使用，会报错
useVoicebase = False
#使用voicebase所需的Token，参考voicebase本身API
voicebaseToken = '请输入你自己的token'
