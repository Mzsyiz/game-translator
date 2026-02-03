"""
Whisper 语音识别引擎模块
"""
import numpy as np
from faster_whisper import WhisperModel
from typing import Optional, Dict, List, Tuple
from loguru import logger
import time


class WhisperEngine:
    """Whisper 语音识别引擎"""

    def __init__(self, config: dict):
        """
        初始化 Whisper 引擎

        Args:
            config: Whisper 配置字典
        """
        self.config = config
        self.model_size = config.get('model_size', 'medium')
        self.device = config.get('device', 'cuda')
        self.compute_type = config.get('compute_type', 'float16')
        self.beam_size = config.get('beam_size', 5)
        self.language = config.get('language', None)  # None = 自动检测
        self.task = config.get('task', 'transcribe')  # transcribe / translate
        self.vad_filter = config.get('vad_filter', True)

        self.model: Optional[WhisperModel] = None
        self.is_loaded = False

        logger.info(f"Whisper 引擎初始化: 模型={self.model_size}, 设备={self.device}")

    def load_model(self):
        """
        加载 Whisper 模型
        """
        if self.is_loaded:
            logger.warning("模型已加载")
            return

        try:
            logger.info(f"正在加载 Whisper 模型: {self.model_size}...")
            start_time = time.time()

            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root="./models/whisper"
            )

            load_time = time.time() - start_time
            self.is_loaded = True

            logger.info(f"模型加载成功，耗时 {load_time:.2f}s")

        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise

    def transcribe(self, audio: np.ndarray,
                   language: Optional[str] = None) -> Dict:
        """
        转录音频

        Args:
            audio: 音频数据 (float32, 单声道)
            language: 源语言代码（None 为自动检测）

        Returns:
            识别结果字典
        """
        if not self.is_loaded:
            self.load_model()

        try:
            start_time = time.time()

            # 使用配置的语言或传入的语言
            lang = language or self.language

            # 转录
            segments, info = self.model.transcribe(
                audio,
                language=lang,
                task=self.task,
                beam_size=self.beam_size,
                vad_filter=self.vad_filter,
                vad_parameters=dict(
                    threshold=0.5,
                    min_speech_duration_ms=250,
                    min_silence_duration_ms=500
                )
            )

            # 提取文本和时间戳
            results = []
            full_text = ""

            for segment in segments:
                results.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                })
                full_text += segment.text.strip() + " "

            full_text = full_text.strip()

            # 处理时间
            process_time = time.time() - start_time
            audio_duration = len(audio) / 16000  # 假设 16kHz
            rtf = process_time / audio_duration if audio_duration > 0 else 0

            result = {
                'text': full_text,
                'segments': results,
                'language': info.language,
                'language_probability': info.language_probability,
                'duration': audio_duration,
                'process_time': process_time,
                'rtf': rtf  # Real-Time Factor
            }

            logger.info(
                f"识别完成: [{info.language}] \"{full_text[:50]}...\" "
                f"(耗时 {process_time:.2f}s, RTF={rtf:.2f}x)"
            )

            return result

        except Exception as e:
            logger.error(f"转录失败: {e}")
            return {
                'text': '',
                'segments': [],
                'language': 'unknown',
                'error': str(e)
            }

    def detect_language(self, audio: np.ndarray) -> Tuple[str, float]:
        """
        检测音频语言

        Args:
            audio: 音频数据

        Returns:
            (语言代码, 置信度)
        """
        if not self.is_loaded:
            self.load_model()

        try:
            # 只取前 30 秒用于语言检测
            sample_audio = audio[:16000 * 30]

            segments, info = self.model.transcribe(
                sample_audio,
                language=None,
                task='transcribe',
                beam_size=1,
                vad_filter=False
            )

            # 消费生成器
            _ = list(segments)

            logger.info(f"检测到语言: {info.language} (置信度: {info.language_probability:.2f})")

            return info.language, info.language_probability

        except Exception as e:
            logger.error(f"语言检测失败: {e}")
            return 'unknown', 0.0

    def transcribe_stream(self, audio_chunks: List[np.ndarray]) -> List[Dict]:
        """
        流式转录（批量处理多个音频块）

        Args:
            audio_chunks: 音频块列表

        Returns:
            识别结果列表
        """
        results = []

        for i, chunk in enumerate(audio_chunks):
            logger.debug(f"处理音频块 {i+1}/{len(audio_chunks)}")
            result = self.transcribe(chunk)
            if result['text']:
                results.append(result)

        return results

    def unload_model(self):
        """
        卸载模型释放内存
        """
        if self.model:
            del self.model
            self.model = None
            self.is_loaded = False
            logger.info("模型已卸载")

    def __enter__(self):
        """上下文管理器入口"""
        self.load_model()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.unload_model()


class WhisperStreamProcessor:
    """Whisper 流式处理器（优化延迟）"""

    def __init__(self, engine: WhisperEngine, buffer_duration: float = 3.0):
        """
        初始化流式处理器

        Args:
            engine: Whisper 引擎实例
            buffer_duration: 缓冲时长（秒）
        """
        self.engine = engine
        self.buffer_duration = buffer_duration
        self.sample_rate = 16000
        self.buffer_size = int(buffer_duration * self.sample_rate)

        # 音频缓冲
        self.audio_buffer = np.array([], dtype=np.float32)

        # 上次处理的文本（用于去重）
        self.last_text = ""

        logger.info(f"流式处理器初始化: 缓冲时长={buffer_duration}s")

    def add_audio(self, audio: np.ndarray) -> Optional[Dict]:
        """
        添加音频块并尝试处理

        Args:
            audio: 音频数据

        Returns:
            识别结果（如果有）
        """
        # 添加到缓冲区
        self.audio_buffer = np.concatenate([self.audio_buffer, audio])

        # 如果缓冲区足够大，进行识别
        if len(self.audio_buffer) >= self.buffer_size:
            result = self.engine.transcribe(self.audio_buffer)

            # 去重（避免重复输出）
            if result['text'] and result['text'] != self.last_text:
                self.last_text = result['text']

                # 清空缓冲区（保留最后 0.5s 用于上下文）
                overlap_size = int(0.5 * self.sample_rate)
                self.audio_buffer = self.audio_buffer[-overlap_size:]

                return result
            else:
                # 清空缓冲区
                self.audio_buffer = np.array([], dtype=np.float32)

        return None

    def flush(self) -> Optional[Dict]:
        """
        处理缓冲区中剩余的音频

        Returns:
            识别结果（如果有）
        """
        if len(self.audio_buffer) > self.sample_rate * 0.5:  # 至少 0.5s
            result = self.engine.transcribe(self.audio_buffer)
            self.audio_buffer = np.array([], dtype=np.float32)
            return result

        return None

    def reset(self):
        """重置处理器状态"""
        self.audio_buffer = np.array([], dtype=np.float32)
        self.last_text = ""
        logger.debug("流式处理器已重置")


if __name__ == "__main__":
    # 测试代码
    logger.add("whisper.log", rotation="10 MB")

    config = {
        'model_size': 'base',  # 测试用小模型
        'device': 'cpu',       # 测试用 CPU
        'compute_type': 'int8',
        'beam_size': 5,
        'language': None,
        'task': 'transcribe',
        'vad_filter': True
    }

    # 创建引擎
    engine = WhisperEngine(config)
    engine.load_model()

    # 生成测试音频（静音）
    sample_rate = 16000
    duration = 3.0
    test_audio = np.zeros(int(sample_rate * duration), dtype=np.float32)

    # 测试转录
    result = engine.transcribe(test_audio)
    logger.info(f"测试结果: {result}")

    # 卸载模型
    engine.unload_model()
