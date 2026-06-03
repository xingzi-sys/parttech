#!/bin/bash

# PartTech 启停脚本
# 用法: ./parttech.sh [start|stop|restart|status]

PROJECT_DIR="/opt/PartTech"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
}

check_node() {
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
}

start_backend() {
    log_info "启动后端服务..."
    cd "$BACKEND_DIR"

    # 检查依赖
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv --copies
    fi

    # 激活虚拟环境并安装依赖
    source venv/bin/activate
    pip install -r requirements.txt -q

    # 检查数据库是否初始化
    if [ ! -f "instance/parttech.db" ]; then
        log_info "初始化数据库..."
        python seed.py
    fi

    # 启动后端（使用虚拟环境中的python）
    nohup python run.py > "$PROJECT_DIR/logs/backend.log" 2>&1 &
    echo $! > "$PROJECT_DIR/logs/backend.pid"

    log_info "后端服务已启动 (PID: $(cat $PROJECT_DIR/logs/backend.pid))"
    deactivate
}

start_frontend() {
    log_info "启动前端服务..."
    cd "$FRONTEND_DIR"

    # 检查node_modules
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install
    fi

    # 启动前端
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    echo $! > ../logs/frontend.pid

    log_info "前端服务已启动 (PID: $(cat ../logs/frontend.pid))"
}

stop_backend() {
    if [ -f "$PROJECT_DIR/logs/backend.pid" ]; then
        PID=$(cat "$PROJECT_DIR/logs/backend.pid")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            log_info "后端服务已停止 (PID: $PID)"
        else
            log_warn "后端进程不存在"
        fi
        rm -f "$PROJECT_DIR/logs/backend.pid"
    else
        log_warn "未找到后端PID文件"
    fi
}

stop_frontend() {
    if [ -f "$PROJECT_DIR/logs/frontend.pid" ]; then
        PID=$(cat "$PROJECT_DIR/logs/frontend.pid")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            log_info "前端服务已停止 (PID: $PID)"
        else
            log_warn "前端进程不存在"
        fi
        rm -f "$PROJECT_DIR/logs/frontend.pid"
    else
        log_warn "未找到前端PID文件"
    fi
}

check_status() {
    echo "=== PartTech 服务状态 ==="

    # 检查后端
    if [ -f "$PROJECT_DIR/logs/backend.pid" ]; then
        PID=$(cat "$PROJECT_DIR/logs/backend.pid")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "后端服务: ${GREEN}运行中${NC} (PID: $PID)"
        else
            echo -e "后端服务: ${RED}已停止${NC} (过期PID)"
        fi
    else
        echo -e "后端服务: ${RED}未运行${NC}"
    fi

    # 检查前端
    if [ -f "$PROJECT_DIR/logs/frontend.pid" ]; then
        PID=$(cat "$PROJECT_DIR/logs/frontend.pid")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "前端服务: ${GREEN}运行中${NC} (PID: $PID)"
        else
            echo -e "前端服务: ${RED}已停止${NC} (过期PID)"
        fi
    else
        echo -e "前端服务: ${RED}未运行${NC}"
    fi

    echo ""
    echo "访问地址:"
    echo "  前端: http://localhost:5173"
    echo "  后端: http://localhost:5000"
    echo "  健康检查: http://localhost:5000/api/health"
}

case "$1" in
    start)
        check_python
        check_node

        # 创建日志目录
        mkdir -p "$PROJECT_DIR/logs"

        start_backend
        sleep 2
        start_frontend

        echo ""
        log_info "PartTech 启动完成!"
        check_status
        ;;

    stop)
        log_info "停止服务..."
        stop_frontend
        stop_backend
        log_info "PartTech 已停止"
        ;;

    restart)
        $0 stop
        sleep 2
        $0 start
        ;;

    status)
        check_status
        ;;

    *)
        echo "用法: $0 {start|stop|restart|status}"
        echo ""
        echo "  start   - 启动所有服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  status  - 查看服务状态"
        exit 1
        ;;
esac

exit 0
