import imageio
from PIL import Image, ImageDraw, ImageFont
import os

def get_frame_duration(gif_file):
    # 获取GIF动画的持续时间
    with Image.open(gif_file) as im:
        durations = []
        while True:
            try:
                durations.append(im.info['duration'])
                im.seek(im.tell() + 1)
            except EOFError:
                break
    return durations

def merge_gifs(gif_files, output_file, labels, grid=(2, 3), fontsize=30):
    # 读取多个GIF动画并获取它们的帧列表
    gif_frames = [list(imageio.get_reader(gif_file)) for gif_file in gif_files]

    # 获取每个GIF动画的帧数
    frame_counts = [len(frames) for frames in gif_frames]

    # 计算新GIF动画的总帧数
    total_frames = max(frame_counts)

    # 获取每个GIF动画的持续时间
    durations = [get_frame_duration(gif_file) for gif_file in gif_files]

    # 获取第一个GIF动画的大小
    first_gif = Image.fromarray(gif_frames[0][0])
    width, height = first_gif.size

    # 计算新GIF动画的大小（包括标签的空间）
    total_width = width * grid[1]
    total_height = height * grid[0] + fontsize * grid[0]  # 假设每个标签占用fontsize像素的高度

    # 创建新的GIF动画
    new_gif_frames = []

    # 遍历所有帧
    for frame_index in range(total_frames):
        # 创建新的帧
        new_frame = Image.new('RGBA', (total_width, total_height))

        # 遍历所有GIF动画
        for gif_index, frames in enumerate(gif_frames):
            # 如果当前GIF动画的帧数足够，将其粘贴到新的帧上
            if frame_index < len(frames):
                frame = Image.fromarray(frames[frame_index])
                x = ((gif_index+1) % grid[1]) * width
                y = ((gif_index+1) // grid[1]) * (height + fontsize)
                new_frame.paste(frame, (x, y))

                # 在图片下面添加标签
                draw = ImageDraw.Draw(new_frame)
                font = ImageFont.truetype(font="/usr/share/fonts/dejavu/DejaVuSans.ttf", size=fontsize)  
                text_width, text_height = draw.textsize(labels[gif_index], font=font)
                text_x = x + (width - text_width) / 2
                text_y = y + height
                draw.text((text_x, text_y), labels[gif_index], fill="black", font=font)

        # 将新帧添加到帧列表中
        new_gif_frames.append(new_frame)

    # 保存新的GIF动画
    new_gif_frames[0].save(
        output_file,
        save_all=True,
        append_images=new_gif_frames[1:],
        format='GIF',
        loop=0,
        duration=[duration[frame_index % len(duration)] for gif_index, duration in enumerate(durations) for _ in range(len(gif_frames[gif_index]))],
    )
    
# 定义要拼接的GIF文件路径
video_list = os.listdir("./")
video_list = [f for f in video_list if '->' in f]
print(video_list)
for videoname in video_list:
    gif_files = [
        f'{videoname}/1_controlvideo.gif',
        f'{videoname}/3_fatezero.gif',
        f'{videoname}/0_source.gif',
        f'{videoname}/2_controlvideo+semedit.gif',
        f'{videoname}/4_fatezero+semedit.gif',
    ]
    labels = ['ControVideo', 'FateZero', 'Source', 'ControVideo+SemEdit', 'FateZero+SemEdit']
    output_file = f'{videoname}/merged.gif'
    merge_gifs(gif_files, output_file, labels, grid=(2, 3))