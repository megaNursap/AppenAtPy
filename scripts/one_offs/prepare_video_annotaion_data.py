import subprocess
import json
import pathlib
import re


if __name__ == '__main__':
    # download original video
    cmd_download_puppies = "aws s3 cp s3://annotation-sandbox/puppies.mp4 ."
    subprocess.check_output(cmd_download_puppies, shell=1)

    src_file = 'puppies.mp4'
    src_file_size = 246
    frames_per_unit = 1
    _seconds_per_unit = frames_per_unit * 1/25
    _num_units = src_file_size / frames_per_unit
    _range = range(int(_num_units))
    # split video into 1s segments
    pathlib.Path('./puppies-segs').mkdir(exist_ok=True)
    cmd = 'ffmpeg -i {src_file} -ss {t0} -t {t1} {out_file}'
    for i in _range:
        _cmd = cmd.format(
            src_file=src_file,
            t0=i * _seconds_per_unit,
            t1=_seconds_per_unit,
            out_file=f'./puppies-segs/seg_{i}.mp4'
        )
        subprocess.check_output(_cmd, shell=1)

    # print number of frames in each segment file
    # cmd = 'ffmpeg -i {filename} 2>&1 | sed -n "s/.*, \\(.*\\) fp.*/\\1/p"'
    cmd = 'ffmpeg -i {filename} -map 0:v:0 -c copy -f null - 2>&1'
    frame_counts = []
    for i in _range:
        filename = f'./puppies-segs/seg_{i}.mp4'
        _cmd = cmd.format(filename=filename)
        res = subprocess.check_output(_cmd, shell=1).decode('utf8')
        total_frames = re.findall(r"(?<=frame\=) +[0-9]*", res)[0].strip()
        print(f"{filename}: {total_frames}")
        frame_counts.append(int(total_frames))

    # create json annotations for each segment
    # mkdir annotations
    pathlib.Path('./annotations').mkdir(exist_ok=True)
    for i in _range:
        data = []
        x = frame_counts[i]
        for j in range(x):
            data.append([
                {'type': 'box', 'id': 'left_hand_box', 'category': 'Left Hand', 'annotated_by': 'human', 'x': 100+j*3, 'y': 100+j*3, 'width': 10+i*10, 'height': 10+i*10, 'visibility': 'visible'},
                {'type': 'box', 'id': 'right_hand_box', 'category': 'Right Hand', 'annotated_by': 'human', 'x': 0, 'y': 0, 'width': 0, 'height': 0, 'visibility': 'hidden'}
                ])
        with open(f'./annotations/seg_{i}.json', 'w') as outfile:
            json.dump(data, outfile)

    # upload videos
    cmd_upload_videos = f"aws s3 cp ./puppies-segs/ s3://annotation-sandbox/puppies-segs/{frame_counts[0]}/ --recursive --region us-east-1"
    subprocess.check_output(cmd_upload_videos, shell=1)
    # upload annotations
    upload_annotations = f"aws s3 cp ./annotations/ s3://annotation-sandbox/puppies-segs/{frame_counts[0]}/annotations/ --recursive"
    subprocess.check_output(upload_annotations, shell=1)

    # cleanup
    subprocess.check_output('rm -r ./puppies.mp4', shell=1)
    subprocess.check_output('rm -r ./puppies-segs', shell=1)
    subprocess.check_output('rm -r ./annotations', shell=1)
