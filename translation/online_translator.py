"""
在线翻译模块 - 支持 DeepL 和 Google Translate
"""
from deep_translator import GoogleTranslator, DeeplTranslator
from typing import Optional
from loguru import logger
import time


class OnlineTranslator:
    """在线翻译器"""

    def __init__(self, config: dict):
        """
        初始化在线翻译器

        Args:
            config: 翻译配置字典
        """
        self.config = config
        self.provider = config.get('provider', 'google')  # google / deepl
        self.api_key = config.get('api_key', '')  # DeepL 需要
        self.timeout = config.get('timeout', 3)
        self.retry = config.get('retry', 2)
        self.target_language = config.get('target_language', 'zh')

        # 翻译器实例
        self.translator = None

        logger.info(f"在线翻译器初始化: 提供商={self.provider}, 目标语言={self.target_language}")

    def _get_translator(self, from_code: str, to_code: str):
        """
        获取翻译器实例

        Args:
            from_code: 源语言代码
            to_code: 目标语言代码

        Returns:
            翻译器实例
        """
        # 语言代码映射（统一格式）
        lang_map = {
            'zh': 'zh-CN',  # 简体中文
            'zh-cn': 'zh-CN',
            'zh-tw': 'zh-TW',  # 繁体中文
            'en': 'en',
            'ja': 'ja',
            'ko': 'ko',
            'ru': 'ru',
            'fr': 'fr',
            'de': 'de',
            'es': 'es',
            'it': 'it',
            'pt': 'pt',
            'ar': 'ar',
            'hi': 'hi',
            'th': 'th',
            'vi': 'vi',
            'id': 'id',
            'tr': 'tr'
        }

        source = lang_map.get(from_code.lower(), from_code)
        target = lang_map.get(to_code.lower(), to_code)

        if self.provider == 'deepl':
            if not self.api_key:
                logger.warning("DeepL 需要 API Key，切换到 Google Translate")
                return GoogleTranslator(source=source, target=target)

            return DeeplTranslator(
                api_key=self.api_key,
                source=source,
                target=target,
                use_free_api=not self.api_key  # 无 key 使用免费版
            )
        else:
            return GoogleTranslator(source=source, target=target)

    def translate(self, text: str, from_code: str, to_code: Optional[str] = None) -> Optional[str]:
        """
        翻译文本

        Args:
            text: 待翻译文本
            from_code: 源语言代码
            to_code: 目标语言代码（None 使用配置的目标语言）

        Returns:
            翻译结果，失败返回 None
        """
        if not text or not text.strip():
            return None

        target = to_code or self.target_language

        # 检查是否需要翻译
        if from_code.lower() == target.lower():
            logger.debug(f"源语言与目标语言相同 ({from_code})，跳过翻译")
            return text

        # 重试机制
        for attempt in range(self.retry + 1):
            try:
                translator = self._get_translator(from_code, target)

                start_time = time.time()
                translated = translator.translate(text)
                elapsed = time.time() - start_time

                logger.debug(
                    f"翻译完成 ({self.provider}): [{from_code}] \"{text[:30]}...\" -> "
                    f"[{target}] \"{translated[:30]}...\" (耗时 {elapsed:.2f}s)"
                )

                return translated

            except Exception as e:
                logger.warning(f"翻译失败 (尝试 {attempt + 1}/{self.retry + 1}): {e}")

                if attempt < self.retry:
                    time.sleep(0.5)  # 短暂延迟后重试
                else:
                    logger.error(f"翻译最终失败: {e}")
                    return None

        return None

    def translate_auto(self, text: str, detected_language: str) -> Optional[str]:
        """
        自动翻译（根据检测到的语言）

        Args:
            text: 待翻译文本
            detected_language: 检测到的语言代码

        Returns:
            翻译结果
        """
        return self.translate(text, detected_language, self.target_language)

    def translate_batch(self, texts: list, from_code: str, to_code: Optional[str] = None) -> list:
        """
        批量翻译

        Args:
            texts: 待翻译文本列表
            from_code: 源语言代码
            to_code: 目标语言代码

        Returns:
            翻译结果列表
        """
        results = []

        for text in texts:
            result = self.translate(text, from_code, to_code)
            results.append(result if result else text)  # 失败时返回原文

        return results

    def test_connection(self) -> bool:
        """
        测试翻译服务连接

        Returns:
            是否连接成功
        """
        try:
            test_text = "Hello"
            result = self.translate(test_text, 'en', 'zh')
            return result is not None

        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    logger.add("online_translator.log", rotation="10 MB")

    # 测试 Google Translate
    config_google = {
        'provider': 'google',
        'api_key': '',
        'timeout': 3,
        'retry': 2,
        'target_language': 'zh'
    }

    translator = OnlineTranslator(config_google)

    # 测试连接
    if translator.test_connection():
        logger.info("翻译服务连接成功")

        # 测试翻译
        test_texts = [
            ("Hello, how are you?", "en"),
            ("Привет, как дела?", "ru"),
            ("こんにちは、元気ですか？", "ja"),
            ("Bonjour, comment allez-vous?", "fr")
        ]

        for text, lang in test_texts:
            result = translator.translate(text, lang, 'zh')
            logger.info(f"[{lang}] {text} -> {result}")
    else:
        logger.error("翻译服务连接失败")
