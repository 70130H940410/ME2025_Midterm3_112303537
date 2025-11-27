#!/bin/bash
set -e

########################################
# 基本設定
########################################

# 你的專案名稱（資料夾名稱）
PROJECT_NAME="ME2025_Midterm3_112303537"

# ✅ 這是你剛給的 GitHub 連結
REPO_URL="https://github.com/70130H940410/ME2025_Midterm3_112303537.git"

# 這支腳本所在的資料夾
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 預設：專案目錄就是腳本所在的資料夾
PROJECT_DIR="$SCRIPT_DIR"
VENV_DIR="$PROJECT_DIR/.venv"

echo "腳本位置：$SCRIPT_DIR"
echo "專案路徑：$PROJECT_DIR"
echo "虛擬環境：$VENV_DIR"

########################################
# 如果腳本在「專案的父資料夾」，就把 PROJECT_DIR 指到專案裡
########################################

if [ ! -f "$PROJECT_DIR/app.py" ] && [ -d "$SCRIPT_DIR/$PROJECT_NAME" ]; then
    PROJECT_DIR="$SCRIPT_DIR/$PROJECT_NAME"
    VENV_DIR="$PROJECT_DIR/.venv"
    echo "偵測到腳本在父資料夾，專案目錄改為：$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

########################################
# 情境 A：完全沒有專案 → 自動 clone（首次執行）
########################################

# 這個情境是：deploy.sh 放在一個空資料夾裡，旁邊沒有專案
if [ ! -d "$PROJECT_DIR/.git" ] && [ ! -f "$PROJECT_DIR/app.py" ]; then
    echo "=== 首次部署：自動 clone repository、建立虛擬環境、安裝套件並啟動 app.py ==="
    echo "開始 git clone：$REPO_URL -> $PROJECT_NAME"

    git clone "$REPO_URL" "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    PROJECT_DIR="$(pwd)"
    VENV_DIR="$PROJECT_DIR/.venv"

    # 建立虛擬環境 .venv
    python3 -m venv "$VENV_DIR"

    # 啟用虛擬環境
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then
        source "$VENV_DIR/Scripts/activate"
    fi

    # 安裝 requirements.txt 套件
    pip install --upgrade pip
    pip install -r requirements.txt

    # 啟動 app.py
    echo "啟動 app.py ..."
    nohup python3 app.py > app.log 2>&1 &

    echo "部署完成。"
    exit 0
fi

########################################
# 情境 B：專案已存在但沒有 .venv → 首次執行（建立 venv + 安裝 + 啟動）
########################################

if [ ! -d "$VENV_DIR" ]; then
    echo "=== 首次部署（專案已存在）：建立虛擬環境、安裝套件並啟動 app.py ==="

    # 建立虛擬環境
    python3 -m venv "$VENV_DIR"

    # 啟用虛擬環境
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then
        source "$VENV_DIR/Scripts/activate"
    fi

    # 安裝 requirements.txt
    pip install --upgrade pip
    pip install -r requirements.txt

    # 啟動 app.py
    echo "啟動 app.py ..."
    nohup python3 app.py > app.log 2>&1 &

    echo "部署完成。"
    exit 0
fi

########################################
# 情境 C：第二次以後執行（已有 .venv）→ 更新 + 安裝 + 重啟
########################################

echo "=== 第二次以後部署：更新專案、安裝套件並重啟 app.py ==="

# 啟用虛擬環境
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
fi

# (1) 自動更新專案版本（git pull）
if [ -d ".git" ]; then
    echo "執行 git pull 更新程式 ..."
    git pull
else
    echo "找不到 .git，略過 git pull。"
fi

# (2) 安裝 / 更新 requirements.txt 中套件
echo "安裝 / 更新 requirements.txt 中的套件 ..."
pip install --upgrade pip
pip install -r requirements.txt

# (3) 重啟 app.py
echo "關閉舊的 app.py （如果存在）..."
pkill -f "python3 app.py" 2>/dev/null || true
pkill -f "python app.py"  2>/dev/null || true

echo "重新啟動 app.py ..."
nohup python3 app.py > app.log 2>&1 &

echo "部署流程完成。"
