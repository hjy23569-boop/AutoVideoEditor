"""自动剪辑视频工具（MoviePy 2.x 版本）。

功能：
1) 读取 input/script.json
2) 按脚本中定义的多个片段进行裁剪
3) 将片段按顺序拼接并导出到 output/final.mp4
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

from moviepy import VideoFileClip, concatenate_videoclips


def load_local_video(video_path: Path) -> VideoFileClip:
    """读取本地视频并返回 VideoFileClip。"""
    if not video_path.exists():
        raise FileNotFoundError(f"未找到视频文件: {video_path}")
    return VideoFileClip(str(video_path))


def load_script_json(script_path: Path) -> List[Dict]:
    """读取并解析 script.json。"""
    if not script_path.exists():
        raise FileNotFoundError(f"未找到脚本文件: {script_path}")

    with script_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("script.json 必须是列表，例如: [{...}, {...}]")
    if not data:
        raise ValueError("script.json 不能为空，至少需要一个片段配置。")

    return data


def cut_video_by_script(script_items: List[Dict], input_dir: Path) -> Tuple[VideoFileClip, List[VideoFileClip]]:
    """根据脚本切片并拼接。

    返回：
    - final_clip: 最终拼接后的视频片段
    - source_clips: 打开的源视频对象列表（用于主流程统一 close）
    """
    source_clips: List[VideoFileClip] = []
    segment_clips: List[VideoFileClip] = []

    for idx, item in enumerate(script_items, start=1):
        filename = item.get("file") or item.get("filename")
        if not filename:
            raise ValueError(f"第 {idx} 个片段缺少 file/filename 字段。")

        if "start" not in item or "end" not in item:
            raise ValueError(f"第 {idx} 个片段必须包含 start 和 end 字段。")

        start = float(item["start"])
        end = float(item["end"])
        if start < 0:
            start = 0.0

        source_path = input_dir / filename
        source_clip = load_local_video(source_path)
        source_clips.append(source_clip)

        end = min(end, float(source_clip.duration))
        if end <= start:
            raise ValueError(f"第 {idx} 个片段时间区间无效: start={start}, end={end}")

        # MoviePy 2.x 推荐用 subclipped()
        segment_clip = source_clip.subclipped(start, end)
        segment_clips.append(segment_clip)

    if not segment_clips:
        raise ValueError("没有可拼接的片段。")

    # 兼容不同分辨率/帧率素材，使用 compose 更稳妥
    final_clip = concatenate_videoclips(segment_clips, method="compose")
    return final_clip, source_clips


def export_result(final_clip: VideoFileClip, output_path: Path) -> None:
    """导出最终视频。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_clip.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
    )


def main() -> None:
    """主流程入口。"""
    input_dir = Path("input")
    script_path = input_dir / "script.json"
    output_path = Path("output/final.mp4")

    source_clips: List[VideoFileClip] = []
    final_clip: VideoFileClip | None = None

    try:
        script_items = load_script_json(script_path)
        final_clip, source_clips = cut_video_by_script(script_items, input_dir)
        export_result(final_clip, output_path)
        print(f"已完成剪辑：{output_path}")
    finally:
        if final_clip is not None:
            final_clip.close()
        for clip in source_clips:
            clip.close()


if __name__ == "__main__":
    main()
