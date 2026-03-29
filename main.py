"""
自动剪辑视频工具（项目初始化版本）

这是一个给 Python 初学者的脚手架示例：
1. 读取本地视频
2. 根据脚本切割视频
3. 导出结果视频

你可以先运行：python main.py
"""

from pathlib import Path
from typing import List, Dict

from moviepy.editor import VideoFileClip


def load_local_video(video_path: str) -> VideoFileClip:
    """读取本地视频并返回 moviepy 视频对象。"""
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"未找到视频文件: {video_path}")

    # 用 moviepy 打开视频文件
    return VideoFileClip(str(path))


def parse_cut_script() -> List[Dict]:
    """定义切割脚本。当前需求：固定取前 5 秒。"""
    return [
        {"start": 0, "end": 5, "note": "前 5 秒"},
    ]


def cut_video_by_script(video_obj: VideoFileClip, segments: List[Dict]) -> VideoFileClip:
    """按脚本切割视频。

    当前实现会读取第一个片段，并返回该片段的子视频。
    """
    if not segments:
        raise ValueError("segments 不能为空，至少需要一个切割片段。")

    first_segment = segments[0]
    start = float(first_segment.get("start", 0))
    end = float(first_segment.get("end", 5))

    if start < 0:
        start = 0

    # 防止 end 超过原视频时长
    end = min(end, float(video_obj.duration))
    if end <= start:
        raise ValueError(f"切割区间无效: start={start}, end={end}")

    # moviepy 的 subclip 会返回一个新的视频片段对象
    return video_obj.subclip(start, end)


def export_result(final_clip: VideoFileClip, output_path: str = "output/final.mp4"):
    """导出结果视频。"""
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    final_clip.write_videofile(
        str(out_path),
        codec="libx264",
        audio_codec="aac",
    )


def main():
    """主流程：把 input/sample.mp4 的前 5 秒导出到 output/final.mp4。"""
    input_video = "input/sample.mp4"

    try:
        video_obj = load_local_video(input_video)
    except FileNotFoundError as e:
        print(e)
        print("提示：请先把测试视频放到 input/sample.mp4，再运行。")
        return

    segments = parse_cut_script()

    try:
        final_clip = cut_video_by_script(video_obj, segments)
        export_result(final_clip, "output/final.mp4")
        print("已完成剪辑：output/final.mp4")
    finally:
        # 释放资源，避免文件句柄占用
        if 'final_clip' in locals():
            final_clip.close()
        video_obj.close()


if __name__ == "__main__":
    main()
