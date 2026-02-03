"""
透明字幕窗口模块 - 游戏内 Overlay 显示
"""
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
from typing import Optional, List
from collections import deque
import sys

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SubtitleLabel(QLabel):
    """单条字幕标签"""

    def __init__(self, text: str, style_config: dict, parent=None):
        super().__init__(text, parent)
        self._apply_style(style_config)

    def _apply_style(self, config: dict):
        """应用字幕样式"""
        font_family = config.get('font_family', 'Microsoft YaHei')
        font_size = config.get('font_size', 24)
        font_weight = config.get('font_weight', 'bold')
        text_color = config.get('text_color', '#FFFFFF')
        outline_color = config.get('outline_color', '#000000')
        outline_width = config.get('outline_width', 2)
        bg_color = config.get('background_color', 'rgba(0, 0, 0, 0.6)')
        padding = config.get('padding', 15)

        # 设置字体
        font = QFont(font_family, font_size)
        if font_weight == 'bold':
            font.setBold(True)
        self.setFont(font)

        # 设置样式表（文字描边效果）
        self.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                background-color: {bg_color};
                padding: {padding}px;
                border-radius: 8px;
                text-shadow:
                    {outline_width}px {outline_width}px 0px {outline_color},
                    -{outline_width}px {outline_width}px 0px {outline_color},
                    {outline_width}px -{outline_width}px 0px {outline_color},
                    -{outline_width}px -{outline_width}px 0px {outline_color};
            }}
        """)

        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)


class SubtitleWindow(QWidget):
    """透明字幕窗口"""

    # 信号
    subtitle_added = pyqtSignal(str)
    subtitle_cleared = pyqtSignal()

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.style_config = config.get('style', {})
        self.display_config = config.get('display', {})

        # 窗口参数
        self.position = config.get('position', 'bottom')
        self.offset_x = config.get('offset_x', 0)
        self.offset_y = config.get('offset_y', 100)
        self.window_width = config.get('width', 1200)
        self.window_height = config.get('height', 150)

        # 显示参数
        self.max_lines = self.display_config.get('max_lines', 3)
        self.stay_duration = self.display_config.get('stay_duration', 5.0) * 1000  # 转为毫秒
        self.show_language_tag = self.display_config.get('show_language_tag', True)

        # 字幕队列
        self.subtitle_queue = deque(maxlen=self.max_lines)
        self.subtitle_labels: List[SubtitleLabel] = []

        # 定时器（自动清除字幕）
        self.clear_timer = QTimer()
        self.clear_timer.timeout.connect(self._auto_clear_subtitle)

        self._init_ui()
        self._setup_window_flags()

        logger.info(f"字幕窗口初始化: 位置={self.position}, 大小={self.window_width}x{self.window_height}")

    def _init_ui(self):
        """初始化 UI"""
        # 设置窗口大小
        self.setFixedSize(self.window_width, self.window_height)

        # 设置布局
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignBottom)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)

        # 设置透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(1.0)

    def _setup_window_flags(self):
        """设置窗口标志（置顶、无边框、鼠标穿透）"""
        flags = (
            Qt.WindowStaysOnTopHint |      # 永远置顶
            Qt.FramelessWindowHint |       # 无边框
            Qt.Tool |                      # 工具窗口（不显示在任务栏）
            Qt.WindowTransparentForInput   # 鼠标穿透
        )
        self.setWindowFlags(flags)

        # Windows 特定设置（需要 pywin32）
        try:
            import win32gui
            import win32con

            # 获取窗口句柄
            hwnd = int(self.winId())

            # 设置扩展样式（透明、分层、鼠标穿透）
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

            logger.debug("已应用 Windows 特定窗口样式")

        except ImportError:
            logger.warning("未安装 pywin32，部分功能可能不可用")
        except Exception as e:
            logger.warning(f"设置 Windows 窗口样式失败: {e}")

    def _calculate_position(self):
        """计算窗口位置"""
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # 水平居中
        x = (screen_width - self.window_width) // 2 + self.offset_x

        # 垂直位置
        if self.position == 'top':
            y = self.offset_y
        elif self.position == 'center':
            y = (screen_height - self.window_height) // 2 + self.offset_y
        else:  # bottom
            y = screen_height - self.window_height - self.offset_y

        self.move(x, y)
        logger.debug(f"窗口位置: ({x}, {y})")

    def add_subtitle(self, text: str, language: Optional[str] = None):
        """
        添加字幕

        Args:
            text: 字幕文本
            language: 语言代码（用于显示标签）
        """
        if not text or not text.strip():
            return

        # 添加语言标签
        if self.show_language_tag and language:
            display_text = f"[{language.upper()}] {text}"
        else:
            display_text = text

        # 高亮关键词
        display_text = self._highlight_keywords(display_text)

        # 添加到队列
        self.subtitle_queue.append(display_text)

        # 更新显示
        self._update_display()

        # 重置清除定时器
        self.clear_timer.stop()
        self.clear_timer.start(int(self.stay_duration))

        # 发送信号
        self.subtitle_added.emit(text)

        logger.debug(f"添加字幕: {display_text}")

    def _highlight_keywords(self, text: str) -> str:
        """
        高亮关键词

        Args:
            text: 原始文本

        Returns:
            高亮后的文本（HTML）
        """
        highlight_config = self.display_config.get('highlight', {})
        if not highlight_config.get('enabled', False):
            return text

        keywords = highlight_config.get('keywords', [])
        color = highlight_config.get('color', '#FF4444')

        result = text
        for keyword in keywords:
            # 不区分大小写替换
            result = result.replace(
                keyword.lower(),
                f'<span style="color: {color}; font-weight: bold;">{keyword.lower()}</span>'
            )
            result = result.replace(
                keyword.upper(),
                f'<span style="color: {color}; font-weight: bold;">{keyword.upper()}</span>'
            )
            result = result.replace(
                keyword.capitalize(),
                f'<span style="color: {color}; font-weight: bold;">{keyword.capitalize()}</span>'
            )

        return result

    def _update_display(self):
        """更新字幕显示"""
        # 清除旧标签
        for label in self.subtitle_labels:
            label.deleteLater()
        self.subtitle_labels.clear()

        # 创建新标签
        for subtitle_text in self.subtitle_queue:
            label = SubtitleLabel(subtitle_text, self.style_config, self)
            self.layout.addWidget(label)
            self.subtitle_labels.append(label)

    def _auto_clear_subtitle(self):
        """自动清除字幕"""
        if self.subtitle_queue:
            self.subtitle_queue.popleft()
            self._update_display()

            if not self.subtitle_queue:
                self.clear_timer.stop()
                self.subtitle_cleared.emit()
                logger.debug("字幕已清空")

    def clear_all(self):
        """清除所有字幕"""
        self.subtitle_queue.clear()
        self._update_display()
        self.clear_timer.stop()
        self.subtitle_cleared.emit()
        logger.debug("手动清空字幕")

    def show_window(self):
        """显示窗口"""
        self._calculate_position()
        self.show()
        logger.info("字幕窗口已显示")

    def hide_window(self):
        """隐藏窗口"""
        self.hide()
        logger.info("字幕窗口已隐藏")

    def toggle_visibility(self):
        """切换显示/隐藏"""
        if self.isVisible():
            self.hide_window()
        else:
            self.show_window()


if __name__ == "__main__":
    # 测试代码
    import time

    app = QApplication(sys.argv)

    config = {
        'position': 'bottom',
        'offset_x': 0,
        'offset_y': 100,
        'width': 1200,
        'height': 150,
        'style': {
            'font_family': 'Microsoft YaHei',
            'font_size': 24,
            'font_weight': 'bold',
            'text_color': '#FFFFFF',
            'outline_color': '#000000',
            'outline_width': 2,
            'background_color': 'rgba(0, 0, 0, 0.6)',
            'padding': 15
        },
        'display': {
            'max_lines': 3,
            'stay_duration': 5.0,
            'show_language_tag': True,
            'highlight': {
                'enabled': True,
                'keywords': ['behind', 'grenade', 'enemy'],
                'color': '#FF4444'
            }
        }
    }

    window = SubtitleWindow(config)
    window.show_window()

    # 测试添加字幕
    QTimer.singleShot(1000, lambda: window.add_subtitle("Enemy behind you!", "en"))
    QTimer.singleShot(2000, lambda: window.add_subtitle("敌人在你后面！", "zh"))
    QTimer.singleShot(3000, lambda: window.add_subtitle("Throw grenade!", "en"))

    sys.exit(app.exec_())
