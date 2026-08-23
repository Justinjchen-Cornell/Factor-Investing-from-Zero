"""pytest 根配置：把 src/ 加入模块搜索路径（标准 src 布局）。"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
