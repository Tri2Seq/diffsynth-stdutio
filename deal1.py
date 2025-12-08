import cv2
import os
import sys
from datetime import timedelta

def extract_frames_per_second(video_path, output_dir, interval_seconds=3):
    """
    从视频中每隔 interval_seconds 提取一帧并保存到指定目录（按时间定位，保证时间戳单调递增）。
    :param video_path: 视频文件的路径
    :param output_dir: 帧图片的保存目录
    :param interval_seconds: 每隔多少秒保存一帧（默认3秒）
    """
    os.makedirs(output_dir, exist_ok=True)
    # 1. 如果输出目录已存在且非空则跳过，避免重复处理
    if os.path.exists(output_dir) and os.listdir(output_dir):
        print(f"输出目录已存在且非空，跳过提取：{os.path.abspath(output_dir)}")
        return
    os.makedirs(output_dir, exist_ok=True)
    print(f"帧保存目录：{os.path.abspath(output_dir)}")

    # 2. 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"无法打开视频文件：{video_path}")

    # 3. 获取视频基本信息
    fps = cap.get(cv2.CAP_PROP_FPS)  # 视频帧率（每秒帧数）
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 视频总帧数
    duration = total_frames / fps if fps > 0 else 0  # 视频总时长（秒）
    print(f"视频信息：帧率={fps:.2f} FPS | 总帧数={total_frames} | 总时长={timedelta(seconds=duration)}")

    if fps <= 0:
        raise ValueError("无法获取视频帧率，视频文件可能损坏或格式不支持")

    saved_count = 0  # 已保存的帧序号

    try:
        t = 0.0  # 当前时间点（秒）
        # 使用按时间定位的方式读取帧，避免帧计数舍入或读取跳帧导致时间戳混乱
        while t <= duration:
            # 定位到指定毫秒位置（更可靠地获取指定时间的帧）
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ret, frame = cap.read()
            if not ret:
                # 定位或读取失败，跳出循环
                break

            # 使用时间戳作为文件名的一部分，保证按时间顺序保存
            frame_filename = f"{saved_count:06d}_{t:.2f}s.jpg"
            frame_path = os.path.join(output_dir, frame_filename)

            # 保存帧图片
            cv2.imwrite(frame_path, frame)
            saved_count += 1

            # 打印进度（每10帧打印一次，避免刷屏）
            if saved_count % 10 == 0:
                progress = (t / duration) * 100 if duration > 0 else 0
                print(f"进度：{progress:.1f}% | 已保存 {saved_count} 帧 | 时间：{t:.2f}s")

            t += interval_seconds

    except Exception as e:
        raise RuntimeError(f"提取帧时发生错误：{str(e)}")
    finally:
        # 释放视频资源
        cap.release()
        cv2.destroyAllWindows()

    # 打印最终结果
    print(f"\n提取完成！共保存 {saved_count} 帧，保存路径：{os.path.abspath(output_dir)}")

output_dirs = ["/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/no other choice","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/the roses","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/nouvelle","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/legs","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/frankenstein"]
input_dirs = ["/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/films/어쩔수가없다 NO OTHER CHOICE, 2025.1080p.WEB-DL.H264.AAC.mp4","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/films/The.Roses.2025.2160p.WEB-DL.DDP5.1.Atmos.SDR.H265-AOC/The.Roses.2025.2160p.WEB-DL.DDP5.1.Atmos.SDR.H265-AOC.mkv","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/films/NOUVELLE.VAGUE.2025.2160p.NF.WEB-DL.DDP.5.1.H.265-CHDWEB[PianYuan]/NOUVELLE.VAGUE.2025.2160p.NF.WEB-DL.DDP.5.1.H.265-CHDWEB.mkv","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/films/If.I.Had.Legs.Id.Kick.You.2025.1080p.iT.WEB-DL.DDP5.1.Atmos.H264-BTM/If.I.Had.Legs.Id.Kick.You.2025.1080p.iT.WEB-DL[Ben The Men].mkv","/fi-lib/workspace/sjx/DiffSynth-Studio/dataset/films/Frankenstein.2025.1080p.NF.WEB-DL.DDP5.1.Atmos.H.264-FLUX/Frankenstein.2025.1080p.NF.WEB-DL.DDP5.1.Atmos.H.264-FLUX.mkv"]
if __name__ == "__main__":
    # 执行帧提取（每3秒保存一帧）
    for i in range(len(output_dirs)):
        try:
            extract_frames_per_second(video_path=input_dirs[i],output_dir=output_dirs[i],interval_seconds=3)
        except Exception as e:
            print(f"程序异常：{str(e)}", file=sys.stderr)
            sys.exit(1)
