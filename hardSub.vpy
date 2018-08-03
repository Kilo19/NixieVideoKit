# -*- coding: utf-8 -*-
import vapoursynth as vs
import sys
import os

core = vs.get_core()
sourceVideo = sourceVideo.decode('utf-8')
sourceSub = sourceSub.decode('utf-8')
targetWidth = targetWidth.decode('utf-8')
targetHeight = targetHeight.decode('utf-8')

#Vegas使用帧服务器输出高清视频教程
#https://www.bilibili.com/read/cv326234/

#Not working in Sony Vegas Movie Studio HD Platinum 11
#· Issue #17 · satishsampath/frame-server
#https://github.com/satishsampath/frame-server/issues/17

#https://forum.videohelp.com/threads/386181-cannot-load-frame-server-avi-into-Vapoursynth
#cannot load frame server avi into Vapoursynth - VideoHelp Forum

if os.path.isfile(sourceVideo):
	if sourceVideo.lower().endswith(".avi"):
		video = core.avisource.AVISource(sourceVideo)
		video = core.resize.Point(
			clip=video, format=vs.YUV420P8, matrix_s="470bg", range_s="full"
		)
	else:
		video = core.ffms2.Source(sourceVideo)

if os.path.isfile(sourceSub):
	#video = core.sub.TextFile(clip = video, file = sourceSub)
	video = core.vsfm.TextSubMod(
		clip = video, file = sourceSub
	)

if downSize.decode('utf-8').lower() == 'true':
	video = core.resize.Lanczos(
		video,
		width = int(targetWidth),
		height = int(targetHeight)
	)

video.set_output()
