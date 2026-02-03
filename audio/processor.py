"""
音频预处理模块 - 音频增强和标准化
"""
import numpy as np
from scipy import signal
from typing import Optional
from loguru import logger


class AudioProcessor:
    """音频预处理器"""

    def __init__(self, sample_rate: int = 16000):
        """
        初始化音频处理器

        Args:
            sample_rate: 音频采样率
        """
        self.sample_rate = sample_rate
        logger.info(f"音频处理器初始化: 采样率={sample_rate}Hz")

    def normalize(self, audio: np.ndarray, target_level: float = -20.0) -> np.ndarray:
        """
        标准化音频音量

        Args:
            audio: 输入音频
            target_level: 目标音量 (dB)

        Returns:
            标准化后的音频
        """
        # 计算当前 RMS
        rms = np.sqrt(np.mean(audio ** 2))

        if rms < 1e-6:
            return audio

        # 计算当前音量 (dB)
        current_level = 20 * np.log10(rms)

        # 计算增益
        gain_db = target_level - current_level
        gain = 10 ** (gain_db / 20)

        # 应用增益
        normalized = audio * gain

        # 防止削波
        max_val = np.max(np.abs(normalized))
        if max_val > 1.0:
            normalized = normalized / max_val * 0.95

        return normalized

    def remove_dc_offset(self, audio: np.ndarray) -> np.ndarray:
        """
        移除直流偏移

        Args:
            audio: 输入音频

        Returns:
            处理后的音频
        """
        return audio - np.mean(audio)

    def apply_highpass_filter(self, audio: np.ndarray, cutoff: float = 80.0) -> np.ndarray:
        """
        应用高通滤波器（去除低频噪音）

        Args:
            audio: 输入音频
            cutoff: 截止频率 (Hz)

        Returns:
            滤波后的音频
        """
        nyquist = self.sample_rate / 2
        normalized_cutoff = cutoff / nyquist

        # 设计 Butterworth 高通滤波器
        b, a = signal.butter(4, normalized_cutoff, btype='high')

        # 应用滤波器
        filtered = signal.filtfilt(b, a, audio)

        return filtered

    def apply_lowpass_filter(self, audio: np.ndarray, cutoff: float = 8000.0) -> np.ndarray:
        """
        应用低通滤波器（去除高频噪音）

        Args:
            audio: 输入音频
            cutoff: 截止频率 (Hz)

        Returns:
            滤波后的音频
        """
        nyquist = self.sample_rate / 2
        normalized_cutoff = cutoff / nyquist

        # 设计 Butterworth 低通滤波器
        b, a = signal.butter(4, normalized_cutoff, btype='low')

        # 应用滤波器
        filtered = signal.filtfilt(b, a, audio)

        return filtered

    def apply_bandpass_filter(self, audio: np.ndarray,
                             low_cutoff: float = 80.0,
                             high_cutoff: float = 8000.0) -> np.ndarray:
        """
        应用带通滤波器（保留语音频段）

        Args:
            audio: 输入音频
            low_cutoff: 低截止频率 (Hz)
            high_cutoff: 高截止频率 (Hz)

        Returns:
            滤波后的音频
        """
        nyquist = self.sample_rate / 2
        low = low_cutoff / nyquist
        high = high_cutoff / nyquist

        # 设计 Butterworth 带通滤波器
        b, a = signal.butter(4, [low, high], btype='band')

        # 应用滤波器
        filtered = signal.filtfilt(b, a, audio)

        return filtered

    def reduce_noise_simple(self, audio: np.ndarray, noise_level: float = 0.01) -> np.ndarray:
        """
        简单降噪（噪声门）

        Args:
            audio: 输入音频
            noise_level: 噪声阈值

        Returns:
            降噪后的音频
        """
        # 计算短时能量
        frame_length = int(self.sample_rate * 0.02)  # 20ms
        hop_length = frame_length // 2

        # 分帧
        frames = []
        for i in range(0, len(audio) - frame_length, hop_length):
            frame = audio[i:i + frame_length]
            rms = np.sqrt(np.mean(frame ** 2))

            # 噪声门
            if rms < noise_level:
                frame = frame * 0.1  # 衰减而不是完全静音

            frames.append(frame)

        # 重建音频
        if not frames:
            return audio

        # 使用重叠相加
        output = np.zeros(len(audio))
        for i, frame in enumerate(frames):
            start = i * hop_length
            end = start + len(frame)
            if end <= len(output):
                output[start:end] += frame

        return output

    def resample(self, audio: np.ndarray, target_rate: int) -> np.ndarray:
        """
        重采样音频

        Args:
            audio: 输入音频
            target_rate: 目标采样率

        Returns:
            重采样后的音频
        """
        if self.sample_rate == target_rate:
            return audio

        # 计算重采样比例
        num_samples = int(len(audio) * target_rate / self.sample_rate)

        # 使用 scipy 重采样
        resampled = signal.resample(audio, num_samples)

        logger.debug(f"重采样: {self.sample_rate}Hz -> {target_rate}Hz")

        return resampled

    def trim_silence(self, audio: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """
        裁剪首尾静音

        Args:
            audio: 输入音频
            threshold: 能量阈值

        Returns:
            裁剪后的音频
        """
        # 计算短时能量
        frame_length = int(self.sample_rate * 0.02)  # 20ms
        energy = np.array([
            np.sqrt(np.mean(audio[i:i + frame_length] ** 2))
            for i in range(0, len(audio) - frame_length, frame_length)
        ])

        # 找到非静音区域
        non_silent = np.where(energy > threshold)[0]

        if len(non_silent) == 0:
            return audio

        # 计算起止位置
        start_frame = non_silent[0]
        end_frame = non_silent[-1] + 1

        start_sample = start_frame * frame_length
        end_sample = min(end_frame * frame_length, len(audio))

        return audio[start_sample:end_sample]

    def process(self, audio: np.ndarray,
               normalize: bool = True,
               remove_dc: bool = True,
               bandpass: bool = True,
               trim: bool = False) -> np.ndarray:
        """
        完整的音频预处理流程

        Args:
            audio: 输入音频
            normalize: 是否标准化
            remove_dc: 是否移除直流偏移
            bandpass: 是否应用带通滤波
            trim: 是否裁剪静音

        Returns:
            处理后的音频
        """
        processed = audio.copy()

        # 移除直流偏移
        if remove_dc:
            processed = self.remove_dc_offset(processed)

        # 带通滤波（保留语音频段）
        if bandpass:
            processed = self.apply_bandpass_filter(processed, 80.0, 8000.0)

        # 裁剪静音
        if trim:
            processed = self.trim_silence(processed)

        # 标准化音量
        if normalize:
            processed = self.normalize(processed)

        return processed


if __name__ == "__main__":
    # 测试代码
    logger.add("processor.log", rotation="10 MB")

    processor = AudioProcessor(sample_rate=16000)

    # 生成测试音频
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # 语音信号（多个频率混合）
    speech = 0.3 * np.sin(2 * np.pi * 440 * t) + 0.2 * np.sin(2 * np.pi * 880 * t)

    # 添加噪音
    noise = 0.05 * np.random.randn(len(speech))
    noisy_speech = speech + noise

    # 添加直流偏移
    noisy_speech += 0.1

    logger.info(f"原始音频: RMS={np.sqrt(np.mean(noisy_speech**2)):.4f}")

    # 处理音频
    processed = processor.process(noisy_speech)

    logger.info(f"处理后音频: RMS={np.sqrt(np.mean(processed**2)):.4f}")
    logger.info(f"音频长度: {len(processed)/sample_rate:.2f}s")
