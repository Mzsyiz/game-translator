"""
游戏实时语音翻译工具 - 主程序
"""
import sys
import yaml
import numpy as np
from pathlib import Path
from threading import Thread, Event
from queue import Queue, Empty
from loguru import logger
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 导入模块
from audio.capture import AudioCapture
from audio.vad import VoiceActivityDetector
from audio.processor import AudioProcessor
from asr.whisper_engine import WhisperEngine
from translation.translator_manager import TranslatorManager
from overlay.subtitle_window import SubtitleWindow


class GameTranslator:
    """游戏翻译主程序"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        初始化游戏翻译器

        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = self._load_config(config_path)

        # 初始化组件
        self.audio_capture = AudioCapture(self.config['audio'])
        self.vad = VoiceActivityDetector(self.config['vad'], sample_rate=16000)
        self.audio_processor = AudioProcessor(sample_rate=16000)
        self.whisper_engine = WhisperEngine(self.config['whisper'])
        self.translator = TranslatorManager(self.config['translation'])

        # 字幕窗口（稍后初始化）
        self.subtitle_window = None

        # 工作队列
        self.audio_queue = Queue(maxsize=50)
        self.result_queue = Queue(maxsize=50)

        # 控制标志
        self.is_running = Event()
        self.is_capturing = Event()

        # 工作线程
        self.capture_thread = None
        self.process_thread = None
        self.display_thread = None

        logger.info("游戏翻译器初始化完成")

    def _load_config(self, config_path: str) -> dict:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

    def _capture_worker(self):
        """
        音频捕获工作线程
        """
        logger.info("音频捕获线程启动")

        try:
            self.audio_capture.start()

            while self.is_running.is_set():
                if not self.is_capturing.is_set():
                    continue

                # 获取音频块
                audio_chunk = self.audio_capture.get_audio_chunk(timeout=0.5)

                if audio_chunk is not None:
                    # VAD 检测
                    is_speech, audio = self.vad.process(audio_chunk)

                    if is_speech:
                        # 放入处理队列
                        try:
                            self.audio_queue.put(audio, timeout=0.1)
                            logger.debug(f"音频块入队: {len(audio)/16000:.2f}s")
                        except:
                            logger.warning("音频队列已满，丢弃数据")

        except Exception as e:
            logger.error(f"音频捕获线程异常: {e}")
        finally:
            self.audio_capture.stop()
            logger.info("音频捕获线程退出")

    def _process_worker(self):
        """
        音频处理工作线程（ASR + 翻译）
        """
        logger.info("音频处理线程启动")

        # 加载 Whisper 模型
        self.whisper_engine.load_model()

        # 音频缓冲（累积多个块）
        audio_buffer = []
        buffer_duration = 0.0
        max_buffer_duration = 3.0  # 最大缓冲 3 秒

        try:
            while self.is_running.is_set():
                try:
                    # 获取音频块
                    audio_chunk = self.audio_queue.get(timeout=0.5)

                    # 预处理音频
                    processed = self.audio_processor.process(
                        audio_chunk,
                        normalize=True,
                        remove_dc=True,
                        bandpass=True,
                        trim=False
                    )

                    # 添加到缓冲区
                    audio_buffer.append(processed)
                    buffer_duration += len(processed) / 16000

                    # 如果缓冲区足够大，进行识别
                    if buffer_duration >= max_buffer_duration:
                        # 合并音频
                        full_audio = np.concatenate(audio_buffer)

                        # 语音识别
                        logger.info(f"开始识别音频: {buffer_duration:.2f}s")
                        asr_result = self.whisper_engine.transcribe(full_audio)

                        if asr_result['text']:
                            # 翻译
                            translated = self.translator.translate(
                                asr_result['text'],
                                asr_result['language']
                            )

                            # 放入结果队列
                            result = {
                                'original': asr_result['text'],
                                'translated': translated or asr_result['text'],
                                'language': asr_result['language'],
                                'confidence': asr_result.get('language_probability', 0.0)
                            }

                            self.result_queue.put(result)

                            logger.info(
                                f"识别结果: [{asr_result['language']}] {asr_result['text'][:50]}... "
                                f"-> {translated[:50] if translated else '(未翻译)'}..."
                            )

                        # 清空缓冲区
                        audio_buffer.clear()
                        buffer_duration = 0.0

                except Empty:
                    # 超时，检查缓冲区
                    if audio_buffer and buffer_duration >= 1.0:
                        # 处理剩余音频
                        full_audio = np.concatenate(audio_buffer)
                        asr_result = self.whisper_engine.transcribe(full_audio)

                        if asr_result['text']:
                            translated = self.translator.translate(
                                asr_result['text'],
                                asr_result['language']
                            )

                            result = {
                                'original': asr_result['text'],
                                'translated': translated or asr_result['text'],
                                'language': asr_result['language'],
                                'confidence': asr_result.get('language_probability', 0.0)
                            }

                            self.result_queue.put(result)

                        audio_buffer.clear()
                        buffer_duration = 0.0

                except Exception as e:
                    logger.error(f"处理音频异常: {e}")
                    audio_buffer.clear()
                    buffer_duration = 0.0

        except Exception as e:
            logger.error(f"音频处理线程异常: {e}")
        finally:
            self.whisper_engine.unload_model()
            logger.info("音频处理线程退出")

    def _display_worker(self):
        """
        字幕显示工作线程
        """
        logger.info("字幕显示线程启动")

        try:
            while self.is_running.is_set():
                try:
                    # 获取结果
                    result = self.result_queue.get(timeout=0.5)

                    # 显示字幕
                    if self.subtitle_window:
                        self.subtitle_window.add_subtitle(
                            result['translated'],
                            result['language']
                        )

                except Empty:
                    continue
                except Exception as e:
                    logger.error(f"显示字幕异常: {e}")

        except Exception as e:
            logger.error(f"字幕显示线程异常: {e}")
        finally:
            logger.info("字幕显示线程退出")

    def start(self):
        """
        启动翻译器
        """
        if self.is_running.is_set():
            logger.warning("翻译器已在运行")
            return

        logger.info("启动翻译器...")

        # 设置运行标志
        self.is_running.set()
        self.is_capturing.set()

        # 启动工作线程
        self.capture_thread = Thread(target=self._capture_worker, daemon=True)
        self.process_thread = Thread(target=self._process_worker, daemon=True)
        self.display_thread = Thread(target=self._display_worker, daemon=True)

        self.capture_thread.start()
        self.process_thread.start()
        self.display_thread.start()

        logger.info("翻译器已启动")

    def stop(self):
        """
        停止翻译器
        """
        if not self.is_running.is_set():
            return

        logger.info("停止翻译器...")

        # 清除运行标志
        self.is_running.clear()
        self.is_capturing.clear()

        # 等待线程退出
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        if self.process_thread:
            self.process_thread.join(timeout=2.0)
        if self.display_thread:
            self.display_thread.join(timeout=2.0)

        logger.info("翻译器已停止")

    def toggle_capture(self):
        """
        切换捕获状态
        """
        if self.is_capturing.is_set():
            self.is_capturing.clear()
            logger.info("暂停捕获")
        else:
            self.is_capturing.set()
            logger.info("恢复捕获")


def main():
    """
    主函数
    """
    # 配置日志
    log_config = {
        'level': 'INFO',
        'file': './logs/app.log',
        'rotation': '10 MB',
        'retention': '7 days'
    }

    logger.add(
        log_config['file'],
        rotation=log_config['rotation'],
        retention=log_config['retention'],
        level=log_config['level'],
        encoding='utf-8'
    )

    logger.info("="*60)
    logger.info("游戏实时语音翻译工具启动")
    logger.info("="*60)

    # 创建 Qt 应用
    app = QApplication(sys.argv)

    # 创建翻译器
    translator = GameTranslator()

    # 创建字幕窗口
    translator.subtitle_window = SubtitleWindow(translator.config['overlay'])
    translator.subtitle_window.show_window()

    # 启动翻译器
    translator.start()

    # 设置快捷键（TODO: 实现全局快捷键）
    logger.info("快捷键:")
    logger.info("  Ctrl+Shift+S: 开始/停止捕获")
    logger.info("  Ctrl+Shift+H: 显示/隐藏字幕")
    logger.info("  Ctrl+Shift+Q: 退出程序")

    # 运行应用
    try:
        exit_code = app.exec_()
    except KeyboardInterrupt:
        logger.info("收到中断信号")
        exit_code = 0
    finally:
        # 清理
        translator.stop()
        logger.info("程序退出")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
