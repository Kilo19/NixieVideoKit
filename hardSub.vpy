# -*- coding: utf-8 -*-
from vapoursynth import core
import sys
import os

if sourceVideo:
	video = core.ffms2.Source(sourceVideo.decode('utf-8'))
if sourceSub:
	#video = core.sub.TextFile(clip = video, file = sourceSub.decode('utf-8'))
	sourceSub = sourceSub.decode('utf-8')
	video = core.vsfm.TextSubMod(clip = video,
								file = sourceSub)
if downSize.decode('utf-8').lower() == 'true':
	video = core.resize.Lanczos(video, width = int(targetWidth.decode('utf-8')), height = int(targetHeight.decode('utf-8')))

video.set_output()