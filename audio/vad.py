"""
语音活动检测 (VAD) 模块 - 检测音频中的语音片段
"""
import numpy as np
import webrtcvad
from collections import deque
from typing import List, Tuple
from loguru import logger


class VoiceActivityDetector:
    """语音活动检测器"""

    def __init__(self, config: dict, sample_rate: int = 16000):
        """
        初始化 VAD

        Args:
            config: VAD 配置字典
            sample_rate: 音频采样率
        """
        self.config = config
        self.sample_rate = sample_rate
        self.enabled = config.get('enabled', True)

        if not self.enabled:
            logger.info("VAD 已禁用")
            return

        # WebRTC VAD 参数
        self.aggressiveness = config.get('aggressiveness', 3)  # 0-3
        self.vad = webrtcvad.Vad(self.aggressiveness)

        # 时长参数（秒）
        self.min_speech_duration = config.get('min_speech_duration', 0.3)
        self.max_silence_duration = config.get('max_silence_duration', 0.8)
        self.padding_duration = config.get('padding_duration', 0.2)

        # 帧参数（WebRTC VAD 要求 10/20/30ms 帧）
        self.frame_duration_ms = 30  # 毫秒
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)

        # 转换为帧数
        self.min_speech_frames = int(self.min_speech_duration * 1000 / self.frame_duration_ms)
        self.max_silence_frames = int(self.max_silence_duration * 1000 / self.frame_duration_ms)
        self.padding_frames = int(self.padding_duration * 1000 / self.frame_duration_ms)

        # 状态
        self.is_speech = False
        self.speech_frames = 0
        self.silence_frames = 0

        # 音频缓冲
        self.audio_buffer = deque(maxlen=self.padding_frames * 2)

        logger.info(f"VAD 初始化: 激进度={self.aggressiveness}, 帧大小={self.frame_size}")

    def _split_frames(self, audio: np.ndarray) -> List[bytes]:
        """
        将音频分割为固定大小的帧

        Args:
            audio: 音频数据 (float32, -1.0 到 1.0)

        Returns:
            帧列表 (bytes)
        """
        # 转换为 int16
        audio_int16 = (audio * 32767).astype(np.int16)

        frames = []
        for i in range(0, len(audio_int16), self.frame_size):
            frame = audio_int16[i:i + self.frame_size]
            if len(frame) == self.frame_size:
                frames.append(frame.tobytes())

        return frames

    def is_speech_frame(self, frame: bytes) -> bool:
        """
        检测单个帧是否包含语音

        Args:
            frame: 音频帧 (bytes)

        Returns:
            是否为语音帧
        """
        try:
            return self.vad.is_speech(frame, self.sample_rate)
        except Exception as e:
            logger.warning(f"VAD 检测失败: {e}")
            return False

    def process(self, audio: np.ndarray) -> Tuple[bool, np.ndarray]:
        """
        处理音频块，检测语音活动

        Args:
            audio: 音频数据 (float32)

        Returns:
            (是否包含语音, 处理后的音频)
        """
        if not self.enabled:
            return True, audio

        # 分割为帧
        frames = self._split_frames(audio)
        if not frames:
            return False, audio

        # 检测每一帧
        speech_count = 0
        for frame in frames:
            if self.is_speech_frame(frame):
                speech_count += 1

        # 判断是否为语音
        speech_ratio = speech_count / len(frames)
        is_speech = speech_ratio > 0.5

        return is_speech, audio

    def process_stream(self, audio: np.ndarray) -> Tuple[bool, List[np.ndarray]]:
        """
        流式处理音频，返回完整的语音片段

        Args:
            audio: 音频数据 (float32)

        Returns:
            (状态变化, 语音片段列表)
        """
        if not self.enabled:
            return False, [audio]

        # 分割为帧
        frames = self._split_frames(audio)
        speech_segments = []

        for frame in frames:
            is_speech = self.is_speech_frame(frame)

            # 将帧添加到缓冲区
            frame_array = np.frombuffer(frame, dtype=np.int16).astype(np.float32) / 32767.0
            self.audio_buffer.append(frame_array)

            if is_speech:
                self.speech_frames += 1
                self.silence_frames = 0

                if not self.is_speech and self.speech_frames >= self.min_speech_frames:
                    # 开始语音
                    self.is_speech = True
                    logger.debug("检测到语音开始")
            else:
                self.silence_frames += 1

                if self.is_speech and self.silence_frames >= self.max_silence_frames:
                    # 结束语音
                    self.is_speech = False
                    self.speech_frames = 0

                    # 提取语音片段（包含填充）
                    segment = np.concatenate(list(self.audio_buffer))
                    speech_segments.append(segment)

                    logger.debug(f"检测到语音结束，时长={len(segment)/self.sample_rate:.2f}s")

                    # 清空缓冲区
                    self.audio_buffer.clear()

        return self.is_speech, speech_segments

    def reset(self):
        """重置 VAD 状态"""
        self.is_speech = False
        self.speech_frames = 0
        self.silence_frames = 0
        self.audio_buffer.clear()
        logger.debug("VAD 状态已重置")


class EnergyVAD:
    """基于能量的简单 VAD（备用方案）"""

    def __init__(self, threshold: float = 0.01, min_duration: float = 0.3):
        """
        初始化能量 VAD

        Args:
            threshold: 能量阈值
            min_duration: 最小语音时长（秒）
        """
        self.threshold = threshold
        self.min_duration = min_duration
        logger.info(f"能量 VAD 初始化: 阈值={threshold}")

    def process(self, audio: np.ndarray, sample_rate: int = 16000) -> bool:
        """
        检测音频是否包含语音

        Args:
            audio: 音频数据
            sample_rate: 采样率

        Returns:
            是否包含语音
        """
        # 计算 RMS 能量
        rms = np.sqrt(np.mean(audio ** 2))

        # 检查时长
        duration = len(audio) / sample_rate

        is_speech = rms > self.threshold and duration >= self.min_duration

        if is_speech:
            logger.debug(f"能量 VAD: RMS={rms:.4f}, 时长={duration:.2f}s -> 语音")

        return is_speech


if __name__ == "__main__":
    # 测试代码
    import time

    logger.add("vad.log", rotation="10 MB")

    config = {
        'enabled': True,
        'aggressiveness': 3,
        'min_speech_duration': 0.3,
        'max_silence_duration': 0.8,
        'padding_duration': 0.2
    }

    vad = VoiceActivityDetector(config, sample_rate=16000)

    # 生成测试音频（模拟语音）
    sample_rate = 16000
    duration = 2.0

    # 语音部分（正弦波）
    t = np.linspace(0, duration, int(sample_rate * duration))
    speech = 0.3 * np.sin(2 * np.pi * 440 * t)

    # 静音部分
    silence = np.zeros(int(sample_rate * 0.5))

    # 组合
    test_audio = np.concatenate([silence, speech, silence])

    # 分块处理
    chunk_size = int(sample_rate * 0.3)
    for i in range(0, len(test_audio), chunk_size):
        chunk = test_audio[i:i + chunk_size]
        is_speech, segments = vad.process_stream(chunk)

        if segments:
            logger.info(f"提取到 {len(segments)} 个语音片段")
            for seg in segments:
                logger.info(f"  片段时长: {len(seg)/sample_rate:.2f}s")

        time.sleep(0.1)
