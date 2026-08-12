# ffmpeg

## make screenshot
ffmpeg -i input.mov -ss 00:00:10 -vframes 1 snapshot.png

## crop video
ffmpeg -i xiaojin.mov -ss 00:00:14 -t 30 -vf "crop=640:360:100:50" -c:a copy output.mp4


## cut video
ffmpeg -i input.mov -ss 00:00:02 -t 204 -vf "crop=1865:970:40:1000" -c:a copy output.mov


## plain cut video by start time and end time, without re-encoding
ffmpeg -i xiaojin.mov -ss 00:00:14 -to 00:01:43 -c copy output.mp4

ffmpeg -i xiaojin.mov -ss 00:00:14 -to 00:01:43 -r 24 output.mp4

# Fix IOS slow motion video
ffmpeg -i xiaojin.mov -ss 00:00:14 -to 00:01:43 -vf "fps=30" output.mp4