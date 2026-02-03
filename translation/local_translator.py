"""
本地翻译模块 - 使用 Argos Translate 离线翻译
"""
import argostranslate.package
import argostranslate.translate
from typing import Optional, List
from loguru import logger
import os


class LocalTranslator:
    """本地翻译器（Argos Translate）"""

    def __init__(self, config: dict):
        """
        初始化本地翻译器

        Args:
            config: 翻译配置字典
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        self.model_cache = config.get('model_cache', './models/argos')
        self.target_language = config.get('target_language', 'zh')

        # 确保缓存目录存在
        os.makedirs(self.model_cache, exist_ok=True)

        # 已安装的翻译包
        self.installed_packages = {}

        if self.enabled:
            logger.info(f"本地翻译器初始化: 目标语言={self.target_language}")
            self._load_installed_packages()

    def _load_installed_packages(self):
        """
        加载已安装的翻译包
        """
        try:
            # 更新包索引
            argostranslate.package.update_package_index()

            # 获取已安装的包
            installed = argostranslate.package.get_installed_packages()

            for package in installed:
                key = f"{package.from_code}-{package.to_code}"
                self.installed_packages[key] = package
                logger.debug(f"已加载翻译包: {package.from_name} -> {package.to_name}")

            logger.info(f"已加载 {len(self.installed_packages)} 个翻译包")

        except Exception as e:
            logger.error(f"加载翻译包失败: {e}")

    def list_available_packages(self) -> List[dict]:
        """
        列出所有可用的翻译包

        Returns:
            翻译包列表
        """
        try:
            argostranslate.package.update_package_index()
            available = argostranslate.package.get_available_packages()

            packages = []
            for package in available:
                packages.append({
                    'from_code': package.from_code,
                    'from_name': package.from_name,
                    'to_code': package.to_code,
                    'to_name': package.to_name,
                    'package_version': package.package_version
                })

            return packages

        except Exception as e:
            logger.error(f"获取可用包列表失败: {e}")
            return []

    def install_package(self, from_code: str, to_code: str) -> bool:
        """
        安装翻译包

        Args:
            from_code: 源语言代码
            to_code: 目标语言代码

        Returns:
            是否安装成功
        """
        try:
            logger.info(f"正在安装翻译包: {from_code} -> {to_code}...")

            # 更新包索引
            argostranslate.package.update_package_index()

            # 查找包
            available = argostranslate.package.get_available_packages()
            package_to_install = None

            for package in available:
                if package.from_code == from_code and package.to_code == to_code:
                    package_to_install = package
                    break

            if not package_to_install:
                logger.error(f"未找到翻译包: {from_code} -> {to_code}")
                return False

            # 下载并安装
            download_path = package_to_install.download()
            argostranslate.package.install_from_path(download_path)

            # 重新加载
            self._load_installed_packages()

            logger.info(f"翻译包安装成功: {from_code} -> {to_code}")
            return True

        except Exception as e:
            logger.error(f"安装翻译包失败: {e}")
            return False

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
        if not self.enabled:
            return None

        if not text or not text.strip():
            return None

        target = to_code or self.target_language

        try:
            # 检查是否需要翻译
            if from_code == target:
                logger.debug(f"源语言与目标语言相同 ({from_code})，跳过翻译")
                return text

            # 查找翻译包
            package_key = f"{from_code}-{target}"

            if package_key not in self.installed_packages:
                logger.warning(f"未安装翻译包: {package_key}，尝试自动安装...")
                if not self.install_package(from_code, target):
                    return None

            # 执行翻译
            translated = argostranslate.translate.translate(text, from_code, target)

            logger.debug(f"翻译完成: [{from_code}] \"{text[:30]}...\" -> [{target}] \"{translated[:30]}...\"")

            return translated

        except Exception as e:
            logger.error(f"翻译失败: {e}")
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
        # 语言代码映射（Whisper -> Argos）
        language_map = {
            'en': 'en',
            'zh': 'zh',
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
            'tr': 'tr',
            'pl': 'pl',
            'nl': 'nl',
            'sv': 'sv',
            'da': 'da',
            'no': 'no',
            'fi': 'fi'
        }

        from_code = language_map.get(detected_language, detected_language)

        return self.translate(text, from_code, self.target_language)

    def is_package_installed(self, from_code: str, to_code: str) -> bool:
        """
        检查翻译包是否已安装

        Args:
            from_code: 源语言代码
            to_code: 目标语言代码

        Returns:
            是否已安装
        """
        package_key = f"{from_code}-{to_code}"
        return package_key in self.installed_packages


if __name__ == "__main__":
    # 测试代码
    logger.add("local_translator.log", rotation="10 MB")

    config = {
        'enabled': True,
        'model_cache': './models/argos',
        'target_language': 'zh'
    }

    translator = LocalTranslator(config)

    # 列出可用包
    logger.info("可用翻译包:")
    packages = translator.list_available_packages()
    for pkg in packages[:10]:  # 只显示前 10 个
        logger.info(f"  {pkg['from_name']} -> {pkg['to_name']}")

    # 测试翻译（需要先安装对应的包）
    test_text = "Hello, how are you?"
    result = translator.translate(test_text, 'en', 'zh')

    if result:
        logger.info(f"翻译结果: {test_text} -> {result}")
    else:
        logger.warning("翻译失败（可能需要先安装翻译包）")
