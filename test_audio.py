#!/usr/bin/env python3
"""
音频设备测试脚本 - 检查虚拟声卡是否正确配置
"""
import sounddevice as sd
import numpy as np
from loguru import logger
import time

logger.add("test_audio.log", rotation="10 MB")


def list_audio_devices():
    """列出所有音频设备"""
    print("\n" + "="*60)
    print("可用音频设备列表")
    print("="*60)

    devices = sd.query_devices()

    for i, device in enumerate(devices):
        device_type = []
        if device['max_input_channels'] > 0:
            device_type.append("输入")
        if device['max_output_channels'] > 0:
            device_type.append("输出")

        print(f"\n[{i}] {device['name']}")
        print(f"    类型: {' / '.join(device_type)}")
        print(f"    输入通道: {device['max_input_channels']}")
        print(f"    输出通道: {device['max_output_channels']}")
        print(f"    默认采样率: {device['default_samplerate']} Hz")


def test_device_capture(device_name="CABLE Output", duration=5):
    """测试音频捕获"""
    print("\n" + "="*60)
    print(f"测试音频捕获: {device_name}")
    print("="*60)

    # 查找设备
    devices = sd.query_devices()
    device_index = None

    for i, device in enumerate(devices):
        if device_name.lower() in device['name'].lower():
            device_index = i
            print(f"\n找到设备: [{i}] {device['name']}")
            break

    if device_index is None:
        print(f"\n错误: 未找到设备 '{device_name}'")
        print("\n请检查:")
        print("1. 虚拟声卡是否已安装")
        print("2. 设备名称是否正确")
        return False

    print(f"\n开始捕获音频 {duration} 秒...")
    print("请在游戏中播放声音或说话...\n")

    try:
        # 录制音频
        recording = sd.rec(
            int(duration * 16000),
            samplerate=16000,
            channels=1,
            device=device_index,
            dtype=np.float32
        )

        # 实时显示音量
        for i in range(duration):
            time.sleep(1)

            # 计算当前音量
            start = i * 16000
            end = (i + 1) * 16000
            chunk = recording[start:end]
            rms = np.sqrt(np.mean(chunk ** 2))

            # 显示音量条
            bar_length = int(rms * 100)
            bar = "█" * min(bar_length, 50)
            print(f"[{i+1}/{duration}s] 音量: {bar} {rms:.4f}")

        sd.wait()

        # 分析录音
        print("\n" + "-"*60)
        print("录音分析:")
        print("-"*60)

        rms_total = np.sqrt(np.mean(recording ** 2))
        max_amplitude = np.max(np.abs(recording))

        print(f"平均音量 (RMS): {rms_total:.4f}")
        print(f"最大振幅: {max_amplitude:.4f}")

        if rms_total < 0.001:
            print("\n⚠️  警告: 音量过低或无声音")
            print("\n可能原因:")
            print("1. 游戏音频未输出到虚拟声卡")
            print("2. 虚拟声卡未正确配置")
            print("3. 游戏音量过低")
            return False
        else:
            print("\n✓ 音频捕获正常！")
            return True

    except Exception as e:
        print(f"\n错误: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("音频设备测试工具")
    print("="*60)

    # 列出设备
    list_audio_devices()

    # 测试捕获
    print("\n")
    input("按 Enter 开始测试音频捕获...")

    success = test_device_capture("CABLE Output", duration=5)

    print("\n" + "="*60)
    if success:
        print("✓ 测试通过！可以运行主程序了")
    else:
        print("✗ 测试失败，请检查配置")
    print("="*60)

    input("\n按 Enter 退出...")


if __name__ == "__main__":
    main()
