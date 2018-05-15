#! python3
# -*- coding: utf-8 -*-
#Press Audio And Merge (PAAM)
import nvksupport
import subprocess
import tempfile
import random
import sys
import os

#path relative to scriptpath\Program
ffmpeg_dir = 'ffmpeg-3.3.1-win64-shared'
mediaInfo_dir = 'MediaInfo'
mediaInfo_exec = os.path.join(mediaInfo_dir, 'MediaInfo.exe')
ffmpeg_exec = os.path.join(ffmpeg_dir, 'bin', 'ffmpeg.exe')
ffmpeg_exec = 'ffmpeg'
ffprobe_exec = os.path.join(ffmpeg_dir, 'bin', 'ffprobe.exe')
ffprobe_exec = 'ffprobe'
fdk_exec = 'fdkaac.exe'
x264_exec = 'x264.2833kMod.x86_64.exe'
avs_exec = 'avs4x264mod.exe'
remuxer_exec = 'remuxer.exe'

scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))

print('Audio Track from Video')
sourceVideo = input().replace('\"', '').strip()

sourceVideo_split = list(os.path.split(sourceVideo))
sourceVideo_split[1:] = os.path.splitext(sourceVideo_split[1])

tempDir = tempfile.gettempdir()+'\\'
tempName = 'prr' + str(random.randint(0,255))
tempPath = tempDir + tempName
tempAudioPath = tempPath + '_a' + '.m4a'

libDir = scriptDir + '\\Program\\'
os.chdir(libDir)
extractAudioArgs_fdk = [
	ffmpeg_exec,
	'-loglevel', 'quiet',
	'-i',  sourceVideo,
	'-map', '0:a',
	'-c:a', 'pcm_s16le',
	'-f', 'wav', '-', '|',
	fdk_exec,
	'-I', '-m', '1', '-',
	'-o', tempAudioPath
]
subprocess.run(extractAudioArgs_fdk, shell = True)

print('Video Stream')
targetVideo  = input().replace('\"', '')

targetVideo_split = list(os.path.split(targetVideo))
outPath = ''.join(
	[
		targetVideo_split[0],
		'\\[remuxed]',
		targetVideo_split[1]
	]
)

remuxArg = [
	remuxer_exec,
	'-i', targetVideo, '-i', tempAudioPath,
	'-o', outPath
]
subprocess.run(remuxArg)
os.remove(tempAudioPath)
