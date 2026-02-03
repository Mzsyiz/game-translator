#!/bin/bash

# Mac 上的测试脚本
# 测试代码质量和模块导入

echo "═══════════════════════════════════════════════════════════"
echo "  游戏翻译助手 - Mac 测试脚本"
echo "═══════════════════════════════════════════════════════════"
echo

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
PASSED=0
FAILED=0

# 测试函数
test_step() {
    echo -n "[测试] $1 ... "
}

test_pass() {
    echo -e "${GREEN}✓ 通过${NC}"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}✗ 失败${NC}"
    if [ -n "$1" ]; then
        echo "  错误: $1"
    fi
    ((FAILED++))
}

test_skip() {
    echo -e "${YELLOW}⊘ 跳过 (仅 Windows)${NC}"
}

echo "[1/8] 检查 Python 环境"
echo "─────────────────────────────────────────────────────────"

test_step "Python 版本"
if python3 --version &> /dev/null; then
    VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python $VERSION${NC}"
    ((PASSED++))
else
    test_fail "Python 未安装"
fi

echo
echo "[2/8] 检查项目文件"
echo "─────────────────────────────────────────────────────────"

test_step "主程序文件"
if [ -f "main.py" ]; then
    test_pass
else
    test_fail "main.py 不存在"
fi

test_step "配置文件"
if [ -f "config/settings.yaml" ]; then
    test_pass
else
    test_fail "config/settings.yaml 不存在"
fi

test_step "黑话词典"
if [ -f "translation/slang_dict.json" ]; then
    test_pass
else
    test_fail "translation/slang_dict.json 不存在"
fi

test_step "依赖清单"
if [ -f "requirements.txt" ]; then
    test_pass
else
    test_fail "requirements.txt 不存在"
fi

echo
echo "[3/8] 检查目录结构"
echo "─────────────────────────────────────────────────────────"

for dir in audio asr translation overlay config scripts; do
    test_step "目录 $dir/"
    if [ -d "$dir" ]; then
        test_pass
    else
        test_fail "目录不存在"
    fi
done

echo
echo "[4/8] 检查 Python 依赖"
echo "─────────────────────────────────────────────────────────"

test_step "PyYAML"
if python3 -c "import yaml" 2>/dev/null; then
    test_pass
else
    test_fail "未安装，运行: pip3 install pyyaml"
fi

test_step "loguru"
if python3 -c "import loguru" 2>/dev/null; then
    test_pass
else
    test_fail "未安装，运行: pip3 install loguru"
fi

test_step "numpy"
if python3 -c "import numpy" 2>/dev/null; then
    test_pass
else
    test_fail "未安装，运行: pip3 install numpy"
fi

echo
echo "[5/8] 测试配置文件"
echo "─────────────────────────────────────────────────────────"

test_step "YAML 配置解析"
if python3 -c "import yaml; yaml.safe_load(open('config/settings.yaml'))" 2>/dev/null; then
    test_pass
else
    test_fail "配置文件格式错误"
fi

test_step "JSON 词典解析"
if python3 -c "import json; json.load(open('translation/slang_dict.json'))" 2>/dev/null; then
    test_pass
else
    test_fail "词典文件格式错误"
fi

echo
echo "[6/8] 测试模块导入"
echo "─────────────────────────────────────────────────────────"

test_step "audio 模块"
if python3 -c "import sys; sys.path.insert(0, '.'); from audio import capture, vad, processor" 2>/dev/null; then
    test_pass
else
    test_fail "模块导入失败"
fi

test_step "asr 模块"
if python3 -c "import sys; sys.path.insert(0, '.'); from asr import whisper_engine" 2>/dev/null; then
    test_pass
else
    test_fail "模块导入失败"
fi

test_step "translation 模块"
if python3 -c "import sys; sys.path.insert(0, '.'); from translation import translator_manager" 2>/dev/null; then
    test_pass
else
    test_fail "模块导入失败"
fi

test_step "overlay 模块"
if python3 -c "import sys; sys.path.insert(0, '.'); from overlay import subtitle_window" 2>/dev/null; then
    test_pass
else
    test_fail "模块导入失败"
fi

echo
echo "[7/8] 测试 Windows 专用功能"
echo "─────────────────────────────────────────────────────────"

test_step "虚拟声卡检测"
test_skip

test_step "音频捕获"
test_skip

test_step "VAD 检测"
test_skip

echo
echo "[8/8] 检查文档"
echo "─────────────────────────────────────────────────────────"

for doc in README.md INSTALL.md QUICKSTART.md PROJECT_SUMMARY.md; do
    test_step "文档 $doc"
    if [ -f "$doc" ]; then
        test_pass
    else
        test_fail "文件不存在"
    fi
done

echo
echo "═══════════════════════════════════════════════════════════"
echo "  测试完成"
echo "═══════════════════════════════════════════════════════════"
echo
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    echo
    echo "注意："
    echo "  • Windows 专用功能无法在 Mac 上测试"
    echo "  • 建议在 Windows 虚拟机中进行完整测试"
    echo "  • 或使用 Parallels Desktop / VMware Fusion"
    exit 0
else
    echo -e "${RED}✗ 有 $FAILED 个测试失败${NC}"
    echo
    echo "请修复失败的测试后再继续"
    exit 1
fi
