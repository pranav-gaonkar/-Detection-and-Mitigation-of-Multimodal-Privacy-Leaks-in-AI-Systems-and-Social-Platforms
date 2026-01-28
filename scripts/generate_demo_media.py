"""Generate demo audio/video assets for LeakWatch samples."""

from __future__ import annotations

import math
from pathlib import Path
import wave

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "samples" / "audio"
VIDEO_DIR = ROOT / "samples" / "video"


def build_demo_audio() -> None:
    path = AUDIO_DIR / "demo_call.wav"
    framerate = 16000
    duration_seconds = 2
    amplitude = 8000
    frequency = 440.0
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        total_frames = int(duration_seconds * framerate)
        frames = bytearray()
        for i in range(total_frames):
            value = int(amplitude * math.sin(2 * math.pi * frequency * (i / framerate)))
            frames += value.to_bytes(2, byteorder="little", signed=True)
        wf.writeframes(frames)
    print(f"Created demo audio: {path}")


def build_demo_video() -> None:
    path = VIDEO_DIR / "demo_clip.mp4"
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    fps = 10
    frame_count = 40
    width, height = 320, 240
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError("Unable to open video writer; check OpenCV build")
    for idx in range(frame_count):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        color = ((idx * 5) % 255, (idx * 3) % 255, (idx * 7) % 255)
        frame[:] = color
        text = f"Frame {idx:02d}"
        cv2.putText(frame, text, (40, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        writer.write(frame)
    writer.release()
    print(f"Created demo video: {path}")


if __name__ == "__main__":
    build_demo_audio()
    build_demo_video()
