#! python3
# -*- coding: utf-8 -*-
#Proofread Recording (PRR)
from nvksupport import *
import tempfile

print('System Audio')
systemAudio = input().replace('\"', '').strip()
print('Voiceover')
voiceOver = input().replace('\"', '').strip()

tempDir = tempfile.gettempdir()+'\\'
tempName = 'prr' + str(random.randint(0,255))
tempPath = tempDir + tempName
tempAudioPath = tempPath + '_a' + '.m4a'

scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
libDir = scriptDir + '\\Program\\'
os.chdir(libDir)
audioArgs_fdk = [ffmpeg_exec,
				#'-loglevel', 'quiet',
				'-i',  systemAudio,
				'-i', voiceOver,
				'-filter_complex', '[1:a:1]highpass=f=200, lowpass=f=8000, aformat=channel_layouts=mono[vo];[0:a:0]aformat=channel_layouts=mono[sys];[vo][sys]amerge=inputs=2,aformat=channel_layouts=mono',
				'-c:a', 'pcm_s16le',
				'-f', 'wav', '-', '|',
				fdk_exec,
				'-I', '--raw-channels', '1',
				'-m', '1', '-',
				'-o', tempAudioPath]
subprocess.run(audioArgs_fdk, shell = True)

print('Video Stream')
sourceVideo  = input().replace('\"', '').strip()

sourceVideo_split = list(os.path.split(sourceVideo))
outPath = os.path.join(sourceVideo_split[0], '[remuxed]' + sourceVideo_split[1])

Remux(sourceVideo, tempAudioPath, outPath)

os.remove(tempAudioPath)
