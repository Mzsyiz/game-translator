"""
音频捕获模块 - 从虚拟声卡捕获游戏语音
"""
import sounddevice as sd
import numpy as np
from queue import Queue
from typing import Optional, Callable
from loguru import logger


class AudioCapture:
    """音频捕获器"""

    def __init__(self, config: dict):
        """
        初始化音频捕获器

        Args:
            config: 音频配置字典
        """
        self.config = config
        self.device_name = config.get('device_name', 'CABLE Output')
        self.sample_rate = config.get('sample_rate', 16000)
        self.channels = config.get('channels', 1)
        self.chunk_duration = config.get('chunk_duration', 0.3)
        self.buffer_size = config.get('buffer_size', 1024)

        # 计算每个音频块的帧数
        self.chunk_frames = int(self.sample_rate * self.chunk_duration)

        # 音频队列
        self.audio_queue = Queue(maxsize=100)

        # 音频流
        self.stream: Optional[sd.InputStream] = None
        self.is_capturing = False

        # 回调函数
        self.callback: Optional[Callable] = None

        logger.info(f"音频捕获器初始化: 设备={self.device_name}, 采样率={self.sample_rate}Hz")

    def list_devices(self) -> list:
        """
        列出所有可用的音频设备

        Returns:
            设备列表
        """
        devices = sd.query_devices()
        logger.info("可用音频设备:")
        for i, device in enumerate(devices):
            logger.info(f"  [{i}] {device['name']} (输入通道: {device['max_input_channels']})")
        return devices

    def find_device_index(self) -> Optional[int]:
        """
        查找指定名称的音频设备索引

        Returns:
            设备索引，未找到返回 None
        """
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if self.device_name.lower() in device['name'].lower():
                logger.info(f"找到音频设备: [{i}] {device['name']}")
                return i

        logger.warning(f"未找到设备 '{self.device_name}'，使用默认输入设备")
        return None

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """
        音频流回调函数

        Args:
            indata: 输入音频数据
            frames: 帧数
            time_info: 时间信息
            status: 状态标志
        """
        if status:
            logger.warning(f"音频流状态: {status}")

        # 转换为单声道
        if indata.shape[1] > 1:
            audio_data = np.mean(indata, axis=1)
        else:
            audio_data = indata[:, 0]

        # 放入队列
        if not self.audio_queue.full():
            self.audio_queue.put(audio_data.copy())
        else:
            logger.warning("音频队列已满，丢弃数据")

        # 调用外部回调
        if self.callback:
            self.callback(audio_data)

    def start(self, callback: Optional[Callable] = None):
        """
        开始捕获音频

        Args:
            callback: 音频数据回调函数
        """
        if self.is_capturing:
            logger.warning("音频捕获已在运行")
            return

        self.callback = callback
        device_index = self.find_device_index()

        try:
            self.stream = sd.InputStream(
                device=device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.chunk_frames,
                callback=self._audio_callback,
                dtype=np.float32
            )

            self.stream.start()
            self.is_capturing = True
            logger.info("音频捕获已启动")

        except Exception as e:
            logger.error(f"启动音频捕获失败: {e}")
            raise

    def stop(self):
        """停止捕获音频"""
        if not self.is_capturing:
            return

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self.is_capturing = False
        logger.info("音频捕获已停止")

    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        从队列获取音频块

        Args:
            timeout: 超时时间（秒）

        Returns:
            音频数据，超时返回 None
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except:
            return None

    def clear_queue(self):
        """清空音频队列"""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break
        logger.debug("音频队列已清空")

    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop()


if __name__ == "__main__":
    # 测试代码
    from loguru import logger
    import time

    logger.add("audio_capture.log", rotation="10 MB")

    config = {
        'device_name': 'CABLE Output',
        'sample_rate': 16000,
        'channels': 1,
        'chunk_duration': 0.3
    }

    capture = AudioCapture(config)

    # 列出所有设备
    capture.list_devices()

    # 开始捕获
    capture.start()

    try:
        logger.info("开始捕获音频，按 Ctrl+C 停止...")
        while True:
            audio_chunk = capture.get_audio_chunk(timeout=1.0)
            if audio_chunk is not None:
                logger.info(f"捕获音频块: {audio_chunk.shape}, RMS={np.sqrt(np.mean(audio_chunk**2)):.4f}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("停止捕获")
    finally:
        capture.stop()
