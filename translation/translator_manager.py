"""
翻译管理器 - 统一管理本地和在线翻译，支持混合模式
"""
from typing import Optional, Dict
from loguru import logger
import json
import os

from .local_translator import LocalTranslator
from .online_translator import OnlineTranslator


class TranslatorManager:
    """翻译管理器"""

    def __init__(self, config: dict):
        """
        初始化翻译管理器

        Args:
            config: 翻译配置字典
        """
        self.config = config
        self.mode = config.get('mode', 'hybrid')  # local / online / hybrid
        self.target_language = config.get('target_language', 'zh')

        # 游戏黑话词典
        self.slang_dict = {}
        slang_config = config.get('slang_dict', {})
        if slang_config.get('enabled', True):
            self._load_slang_dict(slang_config.get('dict_path', './translation/slang_dict.json'))

        # 初始化翻译器
        self.local_translator = None
        self.online_translator = None

        if self.mode in ['local', 'hybrid']:
            try:
                self.local_translator = LocalTranslator(config.get('local', {}))
                self.local_translator.config['target_language'] = self.target_language
                logger.info("本地翻译器已启用")
            except Exception as e:
                logger.warning(f"本地翻译器初始化失败: {e}")

        if self.mode in ['online', 'hybrid']:
            try:
                self.online_translator = OnlineTranslator(config.get('online', {}))
                self.online_translator.target_language = self.target_language
                logger.info("在线翻译器已启用")
            except Exception as e:
                logger.warning(f"在线翻译器初始化失败: {e}")

        logger.info(f"翻译管理器初始化: 模式={self.mode}, 目标语言={self.target_language}")

    def _load_slang_dict(self, dict_path: str):
        """
        加载游戏黑话词典

        Args:
            dict_path: 词典文件路径
        """
        try:
            if not os.path.exists(dict_path):
                logger.warning(f"黑话词典文件不存在: {dict_path}")
                return

            with open(dict_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 展平嵌套的词典
            for category, terms in data.items():
                if isinstance(terms, dict):
                    self.slang_dict.update(terms)

            logger.info(f"已加载 {len(self.slang_dict)} 个黑话词条")

        except Exception as e:
            logger.error(f"加载黑话词典失败: {e}")

    def _apply_slang_dict(self, text: str) -> str:
        """
        应用黑话词典替换

        Args:
            text: 原始文本

        Returns:
            替换后的文本
        """
        if not self.slang_dict:
            return text

        result = text

        # 按词条长度排序（长的优先，避免部分匹配）
        sorted_terms = sorted(self.slang_dict.items(), key=lambda x: len(x[0]), reverse=True)

        for term, translation in sorted_terms:
            # 不区分大小写替换
            result = result.replace(term.lower(), translation)
            result = result.replace(term.upper(), translation)
            result = result.replace(term.capitalize(), translation)

        if result != text:
            logger.debug(f"黑话替换: \"{text}\" -> \"{result}\"")

        return result

    def translate(self, text: str, source_language: str) -> Optional[str]:
        """
        翻译文本（根据模式选择翻译器）

        Args:
            text: 待翻译文本
            source_language: 源语言代码

        Returns:
            翻译结果
        """
        if not text or not text.strip():
            return None

        # 检查是否需要翻译
        if source_language.lower() == self.target_language.lower():
            logger.debug(f"源语言与目标语言相同 ({source_language})，跳过翻译")
            return text

        translated = None

        # 根据模式选择翻译器
        if self.mode == 'local':
            translated = self._translate_local(text, source_language)

        elif self.mode == 'online':
            translated = self._translate_online(text, source_language)

        elif self.mode == 'hybrid':
            # 混合模式：优先本地，失败时使用在线
            translated = self._translate_local(text, source_language)

            if not translated:
                logger.info("本地翻译失败，切换到在线翻译")
                translated = self._translate_online(text, source_language)

        # 应用黑话词典
        if translated:
            translated = self._apply_slang_dict(translated)

        return translated

    def _translate_local(self, text: str, source_language: str) -> Optional[str]:
        """
        使用本地翻译器

        Args:
            text: 待翻译文本
            source_language: 源语言代码

        Returns:
            翻译结果
        """
        if not self.local_translator:
            return None

        try:
            return self.local_translator.translate_auto(text, source_language)
        except Exception as e:
            logger.error(f"本地翻译失败: {e}")
            return None

    def _translate_online(self, text: str, source_language: str) -> Optional[str]:
        """
        使用在线翻译器

        Args:
            text: 待翻译文本
            source_language: 源语言代码

        Returns:
            翻译结果
        """
        if not self.online_translator:
            return None

        try:
            return self.online_translator.translate_auto(text, source_language)
        except Exception as e:
            logger.error(f"在线翻译失败: {e}")
            return None

    def translate_with_fallback(self, text: str, source_language: str) -> Dict:
        """
        翻译文本（带回退机制，返回详细信息）

        Args:
            text: 待翻译文本
            source_language: 源语言代码

        Returns:
            翻译结果字典
        """
        result = {
            'original': text,
            'translated': None,
            'source_language': source_language,
            'target_language': self.target_language,
            'method': None,
            'success': False
        }

        # 尝试翻译
        translated = self.translate(text, source_language)

        if translated:
            result['translated'] = translated
            result['method'] = self.mode
            result['success'] = True
        else:
            # 翻译失败，返回原文
            result['translated'] = text
            result['method'] = 'none'

        return result

    def set_mode(self, mode: str):
        """
        动态切换翻译模式

        Args:
            mode: 翻译模式 (local/online/hybrid)
        """
        if mode not in ['local', 'online', 'hybrid']:
            logger.warning(f"无效的翻译模式: {mode}")
            return

        self.mode = mode
        logger.info(f"翻译模式已切换: {mode}")

    def add_slang_term(self, term: str, translation: str):
        """
        动态添加黑话词条

        Args:
            term: 原始词条
            translation: 翻译
        """
        self.slang_dict[term.lower()] = translation
        logger.info(f"添加黑话词条: {term} -> {translation}")

    def get_stats(self) -> Dict:
        """
        获取翻译器统计信息

        Returns:
            统计信息字典
        """
        stats = {
            'mode': self.mode,
            'target_language': self.target_language,
            'local_enabled': self.local_translator is not None,
            'online_enabled': self.online_translator is not None,
            'slang_terms': len(self.slang_dict)
        }

        if self.local_translator:
            stats['local_packages'] = len(self.local_translator.installed_packages)

        if self.online_translator:
            stats['online_provider'] = self.online_translator.provider

        return stats


if __name__ == "__main__":
    # 测试代码
    logger.add("translator_manager.log", rotation="10 MB")

    config = {
        'mode': 'hybrid',
        'target_language': 'zh',
        'local': {
            'enabled': True,
            'model_cache': './models/argos'
        },
        'online': {
            'provider': 'google',
            'api_key': '',
            'timeout': 3,
            'retry': 2
        },
        'slang_dict': {
            'enabled': True,
            'dict_path': './translation/slang_dict.json'
        }
    }

    manager = TranslatorManager(config)

    # 测试翻译
    test_cases = [
        ("Hello, push B!", "en"),
        ("Enemy behind you!", "en"),
        ("Grenade!", "en")
    ]

    for text, lang in test_cases:
        result = manager.translate_with_fallback(text, lang)
        logger.info(f"翻译结果: {result}")

    # 显示统计
    stats = manager.get_stats()
    logger.info(f"翻译器统计: {stats}")
