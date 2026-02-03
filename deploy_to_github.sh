#!/bin/bash

# 快速部署到 GitHub 并触发自动打包
# 使用方法: ./deploy_to_github.sh

echo "═══════════════════════════════════════════════════════════"
echo "  游戏翻译助手 - 快速部署到 GitHub"
echo "═══════════════════════════════════════════════════════════"
echo

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否已经是 Git 仓库
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}[1/6] 初始化 Git 仓库...${NC}"
    git init
    echo -e "${GREEN}✓ Git 仓库初始化完成${NC}"
else
    echo -e "${GREEN}✓ Git 仓库已存在${NC}"
fi

echo
echo -e "${YELLOW}[2/6] 添加文件到 Git...${NC}"
git add .
echo -e "${GREEN}✓ 文件添加完成${NC}"

echo
echo -e "${YELLOW}[3/6] 创建提交...${NC}"
git commit -m "Initial commit: 游戏实时语音翻译工具

功能特性:
- 多语言语音识别 (Whisper)
- 双翻译引擎 (本地 + 在线)
- 透明字幕 Overlay
- 游戏黑话词典
- 低延迟优化
- 完整文档

技术栈:
- Python 3.10+
- PyQt5
- faster-whisper
- argostranslate
- sounddevice
- webrtcvad
"
echo -e "${GREEN}✓ 提交创建完成${NC}"

echo
echo "─────────────────────────────────────────────────────────"
echo -e "${BLUE}请在 GitHub 上创建新仓库${NC}"
echo "─────────────────────────────────────────────────────────"
echo
echo "1. 访问: https://github.com/new"
echo "2. 仓库名称: game-translator (或其他名称)"
echo "3. 描述: 游戏实时语音翻译工具"
echo "4. 选择: Public 或 Private"
echo "5. 不要勾选 'Initialize this repository with a README'"
echo "6. 点击 'Create repository'"
echo
read -p "创建完成后，请输入仓库 URL (例如: https://github.com/username/game-translator.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo -e "${RED}✗ 未输入仓库 URL，退出${NC}"
    exit 1
fi

echo
echo -e "${YELLOW}[4/6] 添加远程仓库...${NC}"
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"
echo -e "${GREEN}✓ 远程仓库添加完成${NC}"

echo
echo -e "${YELLOW}[5/6] 推送代码到 GitHub...${NC}"
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 代码推送完成${NC}"
else
    echo -e "${RED}✗ 推送失败，请检查网络连接和仓库权限${NC}"
    exit 1
fi

echo
echo -e "${YELLOW}[6/6] 创建 Tag 触发自动构建...${NC}"
git tag v1.0.0
git push origin v1.0.0

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Tag 创建完成，自动构建已触发${NC}"
else
    echo -e "${RED}✗ Tag 推送失败${NC}"
    exit 1
fi

echo
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}  部署完成！${NC}"
echo "═══════════════════════════════════════════════════════════"
echo
echo "下一步："
echo
echo "1. 访问 GitHub Actions 页面查看构建进度:"
REPO_NAME=$(echo "$REPO_URL" | sed 's/.*github.com[:/]\(.*\)\.git/\1/')
echo -e "   ${BLUE}https://github.com/$REPO_NAME/actions${NC}"
echo
echo "2. 等待构建完成 (约 10-15 分钟)"
echo
echo "3. 下载构建结果:"
echo "   - 点击最新的 workflow run"
echo "   - 在 'Artifacts' 部分下载 '游戏翻译助手'"
echo
echo "4. 或者访问 Releases 页面:"
echo -e "   ${BLUE}https://github.com/$REPO_NAME/releases${NC}"
echo
echo "5. 将下载的 zip 文件复制到 Windows 电脑进行测试"
echo
echo "═══════════════════════════════════════════════════════════"
