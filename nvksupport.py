#! python3
# -*- coding: utf-8 -*-
#Nixie Video Kit Supporting Library
#NixieVideoKit is licensed under MIT license (https://github.com/Kilo19/NixieVideoKit/blob/master/LICENSE.txt)
import sys
def show_exception_and_exit(exc_type, exc_value, tb):
	import traceback
	traceback.print_exception(exc_type, exc_value, tb)
	input('''脚本遇到错误，请截图此画面发送给Kilo19。按回车键退出
	Error encountered, please send a screenshot of this error to Kilo19
	Press Enter to Exit
	''')
	sys.exit(-1)

sys.excepthook = show_exception_and_exit

import subprocess
import multiprocessing
import shutil
import urllib.parse
import random
import codecs
import json
import math
import time
import os

import settings

enable_PSUTIL = False
try:
	import psutil
	enable_PSUTIL = True
except ImportError:
	pass

#installed in system (chocolatey on win/package manager on *nix)
ffmpeg_exec = 'ffmpeg'
ffprobe_exec = 'ffprobe'
#path relative to scriptpath/Program
mediaInfo_dir = 'MediaInfo'
mediaInfo_exec = os.path.join(mediaInfo_dir, 'MediaInfo.exe')
vspipe_exec = r"C:\Program Files (x86)\VapourSynth\core32\vspipe.exe"
fdk_exec = 'fdkaac.exe'
vpyPath = '../hardSub.vpy'
scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))

def safeDeleteFile(filePath):
	if os.path.isfile(filePath):
		os.remove(filePath)

def tempClean(temp):
	for v in temp.values():
		safeDeleteFile(v)

def PromptVideo():
	print('Drag video here or enter YouTube/NixieCloud URL, and press enter')
	return input().strip()


def PromptSub():
	print('Drag subtitle here and press enter. Just press enter if there\'s no subtitle')
	return input().strip()


def PromptDir():
	print('Drag output dir here and press enter. Press enter to follow settings')
	return input()

def ConvertPath(inPath):
	inPath = inPath.strip()
	inPath = inPath.replace('\"', '')
	inPath = inPath.replace('\\\\', '\\')
	localPath = inPath
	if os.path.isdir(localPath) and not localPath.endswith(os.sep):
		localPath += os.sep
	if os.path.exists(localPath):
		return localPath

	anchor = localPath.find(settings.customDownDirRelative)
	if anchor != -1:
		localPath = settings.customDownDirRoot + localPath[anchor:]
	if os.path.exists(localPath):
		return localPath

	anchor = localPath.find(settings.cloudDir)
	if anchor == -1:
		return inPath
	else:
		localPath = settings.cloudRoot + localPath[anchor:]
	if os.path.exists(localPath):
		return localPath

	#try to find corresponding local address from NixieCloud address
	localPath = urllib.parse.unquote_plus(inPath)
	anchor = localPath.find(settings.cloudDir)
	if anchor == -1:
		return inPath
	else:
		localPath = settings.cloudRoot + localPath[anchor:]
	if os.path.isdir(localPath) and localPath.endswith(os.sep):
		localPath += os.sep
	if not os.path.exists(localPath):
		localPath = localPath.replace('&files=', os.sep)

	return localPath

#VapourSynth某些插件识别unicode/GBK符号有问题，此处替换
#注意：本函数只检测文件名本身，父目录问题请自行解决
tl = [('\u2013', '\u002D'), ('\u2019', '\u0027'), ('\u2026', '')]
def ReplaceNaughtyCharacters(source, troubleList):
	dirName, baseName = os.path.split(str(source))
	for troubleMaker in troubleList:
		if troubleMaker[0] in baseName:
			baseName = baseName.replace(troubleMaker[0], troubleMaker[1])
	newSource = os.path.join(dirName, baseName)
	if source != newSource:
		os.rename(source, newSource)
	return newSource

def DownloadVid(url, folder):
	down = {}
	downJson = None

	if "youtube.com" in url or "youtu.be" in url:
		if not settings.source720p:
			downJson = DownloadVidHelper(url, folder, '140')
			downJson['_filename'] = ReplaceNaughtyCharacters(downJson['_filename'], tl)
			down['audio'] = downJson['_filename']

			downJson = DownloadVidHelper(url, folder, '137/bestvideo')
			downJson['_filename'] = ReplaceNaughtyCharacters(downJson['_filename'], tl)
			down['video'] = downJson['_filename']
		else:
			downJson = DownloadVidHelper(url, folder)
			downJson['_filename'] = ReplaceNaughtyCharacters(downJson['_filename'], tl)
			down['audio'] = down['video'] = downJson['_filename']
	return down, downJson


def DownloadVidHelper(url, folder, vidFormat =''):
	#folder path can be relative or absolute

	downArgs = ['youtube-dl', url, '--console-title', '--print-json']

	if settings.useProxy:
		downArgs += ['--proxy', settings.proxy]
	#defaults to 720p with audio without '-f' for YouTube
	if vidFormat:
		downArgs += ['-f', vidFormat]

	downArgs += ['-o', os.path.join(folder, '%(title)s.%(ext)s'),
				'--write-thumbnail']

	out, err = subprocess.Popen(downArgs, stdout = subprocess.PIPE).communicate()
	out = out.decode(sys.stdout.encoding).strip()
	return json.loads(out)

def GetTemp(sourceVideo_split):
	#get rid of those troublesome filenames
	#tempDir = tempfile.gettempdir()
	tempDir = os.path.join(sourceVideo_split[0], 'temp')
	os.makedirs(tempDir, exist_ok = True)
	serial = str(random.randint(0, 65536))
	tempName = sourceVideo_split[1] + serial
	temp = {}
	#temp['path'] = tempDir + tempName
	#This path does follow the number rule
	temp['ffindex_path'] = os.path.join(
		sourceVideo_split[0],
		sourceVideo_split[1] + sourceVideo_split[2] + '.ffindex'
	)

	temp['path'] = os.path.join(tempDir, serial)
	temp['audio_path'] = temp['path'] + '_a.m4a'
	temp['video_path'] = temp['path'] + '_v.mp4'
	temp['sub_path'] = temp['path'] + '_s.ass'
	temp['stats_path'] = temp['path'] + '.stats'
	temp['mbtree_path'] = temp['stats_path'] + '.mbtree'
	while os.path.isfile(temp['audio_path']):
		serial = str(random.randint(0, 65536))
		temp['audio_path'] = temp['path'] + '_a.m4a'
		temp['video_path'] = temp['path'] + '_v.mp4'
		temp['sub_path'] = temp['path'] + '_s.ass'
		temp['stats_path'] = temp['path'] + '.stats'
		temp['mbtree_path'] = temp['stats_path'] + '.mbtree'
	return temp

def ConvertAudio(videoIn, audioOut):
	#For piping to fdk to work, you need to pass the parameter as a single string
	#could be repalced by Python's own piping feature
	#Thus shell = True
	if findRateAudio(videoIn) and findRateAudio(videoIn) < 128:
		extract_args = [ffmpeg_exec,
				'-loglevel', 'quiet',
				'-nostdin',
				'-stats',
				'-i', videoIn,
				'-map', '0:a',
				'-c', 'copy',
				audioOut]
		subprocess.Popen(extract_args)
	else:
		ffmpeg_args = [ffmpeg_exec,
				'-loglevel', 'quiet',
				'-nostdin',
				'-stats',
				'-i',  videoIn,
				'-map', '0:a',
				'-c:a', 'pcm_s16le',
				'-f', 'wav', '-']
		fdk_args = [fdk_exec,
				'-I', '-m', '5', '-',
				'-o', audioOut]
		p1 = subprocess.Popen(ffmpeg_args, stdout=subprocess.PIPE)
		p2 = subprocess.Popen(fdk_args, stdin=p1.stdout)

		p1.stdout.close()
		p2.communicate()

#voicebase likes MP3 of higher bitrate
def ConvertAudioVoicebase(videoIn, audioOut):
	args = [ffmpeg_exec,
			'-loglevel', 'quiet',
			'-nostdin',
			'-stats',
			'-i',  videoIn,
			'-map', '0:a',
			'-c:a', 'libmp3lame',
			'-q:a', '4',
			audioOut]
	return subprocess.run(args)

def GetContainer(filename):
	cmnd = [ffprobe_exec,
						'-show_entries', 'format=format_name',
						'-of', 'default=noprint_wrappers=1:nokey=1',
						'-v', 'quiet', filename]
	p = subprocess.Popen(cmnd,
													stdout = subprocess.PIPE,
													stderr = subprocess.PIPE)
	out, err = p.communicate()
	return out.lower().decode()

def quoted(s):
	return '"' + s + '"'

def findRateVideo(filename):
	cmnd = [ffprobe_exec,
						'-select_streams', 'v:0',
						'-show_entries', 'stream=bit_rate',
						'-of', 'default=noprint_wrappers=1:nokey=1',
						'-v', 'quiet', filename]
	if not isAudioExist(filename):
		cmnd[4] = 'format=bit_rate'
	p = subprocess.Popen(cmnd,
						stdout = subprocess.PIPE,
						stderr = subprocess.PIPE)
	out, err = p.communicate()
	try:
		#ffprobe returns bit_rate in bps, integer division is used
		out = int(out) // 1000
	except:
		print('Failed to find video stream bitrate, trying format bitrate')
		cmnd[4] = 'format=bit_rate'
		p = subprocess.Popen(cmnd,
							stdout = subprocess.PIPE,
							stderr = subprocess.PIPE)
		out, err = p.communicate()
		try:
			out = int(out) // 1000
		except:
			print('Failed to get format bitrate')
			return None
	return int(out)

def prepareVsPipeParam(sourceVideo, sourceSub, libDir, decisionHeight):
	targetWidth = 0
	targetHeight = 0
	vsPipeParams = {"sourceVideo": sourceVideo,
			"sourceSub": sourceSub,
			"libDir": libDir,
			"downSize": False,
			"targetWidth": targetWidth,
			"targetHeight": targetHeight,
			}
	res = FindRes(sourceVideo)
	if res and decisionHeight and res[1] > decisionHeight:
		vsPipeParams["downSize"] = True
		decisionHeight = decisionHeight // 2 * 2
		targetWidth = res[0] * decisionHeight // res[1]
		targetWidth = targetWidth // 2 * 2
		targetHeight = decisionHeight

		vsPipeParams['targetWidth'] = targetWidth
		vsPipeParams['targetHeight'] = targetHeight
	vsPipeArgsFull = [vspipe_exec]
	for key, value in vsPipeParams.items():
		vsPipeArgsFull.append('-a')
		vsPipeArgsFull.append('='.join([key, str(value)]))
	vsPipeArgsFull += ['--y4m', vpyPath, '-']
	#vsPipeArgsFull += ['--y4m', vpyPath, '.']
	#subprocess.Popen(vsPipeArgsFull).wait()
	return vsPipeArgsFull

def encodeVid_pipeFF2pass(pipeArgs, log, videoOut, targetBitRate, preset):
	ffHead = [ffmpeg_exec,
				'-loglevel', 'quiet',
				'-nostdin',
				'-stats',
				'-i', 'pipe:',
				'-map', '0:v',
				'-c:v', 'libx264',
				'-preset', preset,
				'-x264-params', 'me=umh:qcomp=0.9:ap-mode=3:merange=48',
				'-b:v', str(targetBitRate) + 'k']
	ffHead += ['-passlogfile', log]
	firstPassArgs = ffHead + ['-y', '-pass', '1', '-f', 'mp4', 'NUL']

	EncodeInvokeWithPipe(pipeArgs, firstPassArgs)
	secondPassArgs = ffHead + ['-pass', '2', videoOut]

	EncodeInvokeWithPipe(pipeArgs, secondPassArgs)
	safeDeleteFile(log + '-0.log')
	safeDeleteFile(log + '-0.log.mbtree')

def encodeVid_pipeFF1passCRF(pipeArgs, videoOut, CRF, preset):
	ffHead = [ffmpeg_exec,
				'-loglevel', 'quiet',
				'-stats',
				'-i', 'pipe:',
				'-map', '0:v',
				'-c:v', 'libx264',
				'-preset', preset,
				'-x264-params', 'me=umh:qcomp=0.9:ap-mode=3:merange=48',
				'-crf', str(round(CRF, 3)),
				videoOut]
	EncodeInvokeWithPipe(pipeArgs, ffHead)

def MediaInfo(filename):
	cmnd = [mediaInfo_exec, filename]
	p = subprocess.Popen(cmnd,
													stdout = subprocess.PIPE,
													stderr = subprocess.PIPE)
	out, err = p.communicate()
	mediaInfoDict = {}
	newSection = False
	for line in out.splitlines():
		if newSection:
			pass

def findRateAudio(filename):
	if not isAudioExist(filename):
		return False
	cmnd = [ffprobe_exec,
						'-select_streams', 'a:0',
						'-show_entries', 'stream=bit_rate',
						'-of', 'default=noprint_wrappers=1:nokey=1',
						'-v', 'quiet', filename]
	p = subprocess.Popen(cmnd,
													stdout = subprocess.PIPE,
													stderr = subprocess.PIPE)
	out, err = p.communicate()
	try:
		#ffprobe returns bit_rate in bps, integer division is used
		out = int(out) // 1000
	except:
		out = False
	return out

def isAudioExist(filename):
	cmnd = [ffprobe_exec,
					'-select_streams', 'a',
					'-show_streams',
					'-v', 'quiet', filename]
	p = subprocess.Popen(cmnd,
													stdout = subprocess.PIPE,
													stderr = subprocess.PIPE)
	out, err = p.communicate()
	return bool(out)

def FindTime(filename):
	cmnd = [ffprobe_exec,
						'-show_entries', 'format=duration',
						'-of', 'default=noprint_wrappers=1:nokey=1',
						'-v', 'quiet', filename]
	p = subprocess.Popen(cmnd,
													stdout = subprocess.PIPE,
													stderr = subprocess.PIPE)
	out, err = p.communicate()
	return int(math.ceil(out))

def FindRes(filename):
	cmnd = [ffprobe_exec,
						'-select_streams', '0:v',
						'-show_entries', 'stream=width,height',
						'-of', 'default=noprint_wrappers=1:nokey=1',
						'-v', 'quiet', filename]
	p = subprocess.Popen(cmnd,
													stdout = subprocess.PIPE,
													stderr = subprocess.PIPE)
	out, err = p.communicate()
	out = out.decode('utf-8').strip()
	out = out.split('\n')
	if len(out) == 2:
		try:
			out = [int(out[0]), int(out[1])]
		except:
			out = False
	else:
		out = False
	return out

def EncodeInvoke(args, quellTarget):
	#newArgs = [arg.encode('utf-8') for arg in args]
	p = subprocess.Popen(args)
	if settings.useQuell:
		if enable_PSUTIL:
			Quell(quellTarget)
		else:
			print('failed to import psutil, unable to quell as desired')
	p.wait()

def EncodeInvokeWithPipe(inletArgs, outletArgs):
	p1 = subprocess.Popen(inletArgs, stdout=subprocess.PIPE)
	p2 = subprocess.Popen(outletArgs, stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
	output = p2.communicate()[0]

def Quell(name):
	time.sleep(1)
	#加入延时是因为x264需要一定时间才能启动
	#如果立刻抓取进程列表的话会看不到x264压制进程
	for proc in psutil.process_iter():
		if name in proc.name():
			proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

def ConvertVideo_2Pass(videoIn, log, videoOut, targetBitRate, preset):
	ffHead = [ffmpeg_exec,
						'-loglevel', 'quiet',
						'-nostdin',
						'-stats',
						'-i', videoIn,
						'-map', '0:v',
						'-c:v', 'libx264',
						'-preset', preset,
						'-x264-params', 'me=umh:qcomp=0.9:ap-mode=3:merange=48',
						'-b:v', str(targetBitRate) + 'k']
	if not settings.source720p:
		ffHead += ['-vf', 'scale=trunc(oh*a/2)*2:720']

	ffHead += ['-passlogfile', log]

	firstPassArg = ffHead + ['-y', '-pass', '1', '-f', 'mp4', 'NUL']
	EncodeInvoke(firstPassArg, 'ffmpeg')

	secondPassArg = ffHead + ['-pass', '2', videoOut]
	EncodeInvoke(secondPassArg, 'ffmpeg')
	safeDeleteFile(log + '-0.log')
	safeDeleteFile(log + '-0.log.mbtree')

def Remux(vStream, aStream, outPath):
	remuxArg_ffmpeg = [ffmpeg_exec,
					'-i', vStream, '-i', aStream,
					'-c', 'copy', '-y',
					outPath]
	subprocess.run(remuxArg_ffmpeg)

def nce():
	print(sys.argv)
	#absolute path
	if len(sys.argv) > 1:
		sourceVideo = sys.argv[1]
	else:
		sourceVideo = PromptVideo()
	sourceVideo = ConvertPath(sourceVideo)

	libDir = os.path.join(scriptDir, 'Program')
	os.chdir(libDir)

	downDir = os.path.join(scriptDir, 'Video')
	if settings.overrideDownDir:
		downDir = os.path.join(settings.customDownDir, 'temp')

	down = {}
	downJson = ''
	if os.path.isfile(sourceVideo):
		sourceVideo = ReplaceNaughtyCharacters(sourceVideo, tl)
		down['audio'] = sourceVideo
		down['video'] = sourceVideo
	else:
		#DownloadVid本身会处理非法字符问题
		down, downJson = DownloadVid(sourceVideo, downDir)
		sourceVideo_split = list(os.path.split(down['video']))
		sourceVideo_split[1:] = os.path.splitext(sourceVideo_split[1])

		outJsonName = sourceVideo_split[1] + '.json'
		outJsonPath = os.path.join(settings.customDownDir, outJsonName)
		outJsonFile = codecs.open(outJsonPath, encoding = 'utf-8', mode = 'w')
		json.dump(downJson, outJsonFile)
		outJsonFile.close()
		#let AutoNCE take care of us
		downImage = os.path.join(
			sourceVideo_split[0],
			sourceVideo_split[1] + os.path.splitext(downJson['thumbnail'])[-1]
		)
		shutil.move(downImage, settings.customOutDir)
		Remux(
			down['video'], down['audio'],
			os.path.join(
				settings.customDownDir,
				sourceVideo_split[1] + '_remux' + sourceVideo_split[2]
			)
		)
		safeDeleteFile(down['video'])
		safeDeleteFile(down['audio'])
		return

	sourceVideo_split = list(os.path.split(sourceVideo))
	sourceVideo_split[1:] = os.path.splitext(sourceVideo_split[1])
	temp = GetTemp(sourceVideo_split)
	#bitrate MUST be an integer, or x264 would yell at you
	print('Target video bit rate: ' + str(settings.nceBitrate) + 'kbps')

	outName_noExt = ''.join(['[NCE_', str(settings.nceBitrate), 'k]',
							sourceVideo_split[1]])
	outVidName = outName_noExt + '.mp4'
	outTxtName = outName_noExt + '.txt'
	outJsonName = sourceVideo_split[1] + '.json'

	if settings.overrideOutDir and settings.customDownDir in sourceVideo:
		outPathCommon = os.path.join(settings.customOutDir, outName_noExt)
		os.makedirs(outPathCommon, exist_ok=True)
		outPath = outPathCommon
	else:
		outPath = sourceVideo_split[0]
	outTxtPath = os.path.join(outPath, outTxtName)
	commandTimeString = time.ctime()
	txtPrompt = ['#生肉下令时间 (远程机时间) : ' + commandTimeString,
				'#此文件表明下令成功',
				'#生肉需要视频一半时长压制完成',
				'#同步到网盘速度不定',
				'#未来可能添加更多信息']
	txtPrompt = [l + '\n' for l in txtPrompt]
	with codecs.open(outTxtPath, 'w', 'utf-8') as txtFile:
		txtFile.writelines(txtPrompt)

	outVidPath = os.path.join(outPath, outVidName)
	outJsonPath = os.path.join(outPath, outJsonName)

	# 为防止新老肉混淆，新肉下令后会删除老肉（如果有的话）
	safeDeleteFile(outVidPath)

	if not isAudioExist(down['audio']) and os.path.isfile(down['audio'][:-5] + '.m4a'):
		down['audio'] = down['audio'][:-5] + '.m4a'
	ConvertAudio(down['audio'], temp['audio_path'])
	if isAudioExist(down['audio']):
		if settings.useVoicebase:
			transcribePath = os.path.splitext(outVidPath)[0] + '_trans'
			subprocess.Popen(['py', '-3',
							  os.path.join(scriptDir, 'voicebase.py'),
							  down['audio'], transcribePath],
							 creationflags = subprocess.CREATE_NEW_CONSOLE)

		ConvertVideo_2Pass(sourceVideo,
							temp['path'],
							temp['video_path'],
							settings.nceBitrate,
							settings.ncePreset)
		Remux(temp['video_path'], temp['audio_path'], outVidPath)
	else:
		print('No audio or failed to convert Audio')
		ConvertVideo_2Pass(sourceVideo,
							temp['path'],
							outVidPath,
							settings.nceBitrate,
							settings.ncePreset)
	if downJson:
		outJsonFile = codecs.open(outJsonPath, encoding = 'utf-8', mode = 'w')
		json.dump(downJson, outJsonFile)
		outJsonFile.close()

	if down['audio'] != down['video']:
		Remux(down['video'], down['audio'],
				os.path.join(sourceVideo_split[0],
							 sourceVideo_split[1] + '_remux' + sourceVideo_split[2]))
	safeDeleteFile(outTxtPath)
	tempClean(temp)
	print('Transcoding Complete!')

def be():
	global scriptDir
	print(sys.argv)
	#absolute path
	if len(sys.argv) > 1:
		sourceVideo = sys.argv[1]
	else:
		sourceVideo = PromptVideo()
	sourceVideo = ConvertPath(sourceVideo)

	if len(sys.argv) > 2:
		sourceSub = sys.argv[2]
	elif len(sys.argv) == 1:
		sourceSub = PromptSub()
	sourceSub = ConvertPath(sourceSub)

	if os.path.isdir(sourceSub):
		outDir = sourceSub
		candidate = []
		with os.scandir(sourceSub) as it:
			for entry in it:
				if entry.is_file() and entry.name[-4:] == '.ass':
					candidate.append(entry.path)
		if len(candidate) != 1:
			print(candidate)
			print('Multile or no .ass files in the same folder, unable to resolve')
			sourceSub = PromptSub()
		else:
			sourceSub = candidate[0]

	if os.path.isfile(sourceSub):
		sourceSub = ReplaceNaughtyCharacters(sourceSub, tl)

	if len(sys.argv) > 3 and sys.argv[3].strip():
		outDir = sys.argv[3]
	elif len(sys.argv) == 1:
		outDir = PromptDir()
	outDir = ConvertPath(outDir)

	scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
	libDir = os.path.join(scriptDir, 'Program')
	os.chdir(libDir)

	downDir = os.path.join(scriptDir, 'Video')
	if settings.overrideDownDir:
		downDir = settings.customDownDir

	down = {}
	if not os.path.isfile(sourceVideo):
		down, downJson = DownloadVid(sourceVideo, downDir)
		sourceVideo = down['video']
	elif len(sourceVideo) >= 6 and sourceVideo[-5:] == '.json':
		inJsonFile = codecs.open(sourceVideo, encoding = 'utf-8', mode = 'r')
		inJson = json.load(inJsonFile)
		inJsonFile.close()
		sourceVideo = inJson['_filename']
		down['audio'] = sourceVideo
		if not os.path.isfile(sourceVideo):
			sourceVideo = inJson['webpage_url']
			down, downJson = DownloadVid(sourceVideo, downDir)
			sourceVideo = down['video']
	else:
		down['audio'] = sourceVideo

	if not isAudioExist(down['audio']) and os.path.isfile(down['audio'][:-5] + '.m4a'):
		down['audio'] = down['audio'][:-5] + '.m4a'

	sourceVideo_split = list(os.path.split(sourceVideo))
	sourceVideo_split[1:] = os.path.splitext(sourceVideo_split[1])

	temp = GetTemp(sourceVideo_split)
	#VSFilterMod still sucks at non-ASCII
	#Luckily subtitles are small compared to videos
	#We can afford copying subs to a nice path
	if os.path.isfile(sourceSub):
		shutil.copy(sourceSub, temp['sub_path'])
		vsPipeArgsFull = prepareVsPipeParam(sourceVideo, temp['sub_path'], libDir, settings.beDecisionHeight)
	else:
		vsPipeArgsFull = prepareVsPipeParam(sourceVideo, '', libDir, settings.beDecisionHeight)

	#bitrate MUST be an integer, or x264 would yell at you
	print('Target video bit rate: ' + str(settings.beBitrate) + 'kbps')

	outName = ''.join(['[BE_', str(settings.beBitrate), 'k]',
					   sourceVideo_split[1]])
	outTxtName = outName + '.txt'
	outVidName = outName + '.mp4'

	if os.path.isdir(outDir):
		outPath = outDir
	elif settings.overrideOutDir and os.path.isdir(settings.customOutDir):
		outPath = settings.customOutDir
	else:
		outPath = sourceVideo_split[0]

	outTxtPath = os.path.join(outPath, outTxtName)
	commandTimeString = time.ctime()
	txtPrompt = ['#熟肉下令时间 (远程机时间) : ' + commandTimeString,
				'#此文件表明下令成功',
				'#熟肉压制完成需要视频一半到全长1.1倍时间',
				'#同步到网盘速度不定']
	txtPrompt = [l + '\n' for l in txtPrompt]
	with codecs.open(outTxtPath, 'w', 'utf-8') as txtFile:
		txtFile.writelines(txtPrompt)

	outVidPath = os.path.join(outPath, outVidName)
	# 为防止新老肉混淆，新肉下令后会删除老肉（如果有的话）
	safeDeleteFile(outVidPath)

	ConvertAudio(down['audio'], temp['audio_path'])

	videoBitrate = findRateVideo(sourceVideo)

	if videoBitrate is None\
		or videoBitrate > settings.beBitrate * 0.9:
		encodeVid_pipeFF2pass(vsPipeArgsFull,
							temp['path'],
							temp['video_path'],
							settings.beBitrate,
							settings.bePreset)
	else:
		encodeVid_pipeFF1passCRF(vsPipeArgsFull,
							temp['video_path'],
							settings.beCRF,
							settings.bePreset)

	if isAudioExist(down['audio']):
		Remux(temp['video_path'], temp['audio_path'], outVidPath)
	else:
		print('No audio or failed to convert Audio')
		shutil.move(temp['video_path'], outVidPath)
	safeDeleteFile(outTxtPath)

	tempClean(temp)
	print('Transcoding Complete!')
