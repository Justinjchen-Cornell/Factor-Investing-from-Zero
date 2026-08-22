"""Notebook 执行护栏：仓库内所有 notebook 必须能从头跑到尾（课程完成标准之一）。"""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def _all_notebooks():
    return sorted((ROOT / "chapters").glob("*/notebooks/*.ipynb"))


def test_at_least_one_notebook():
    assert _all_notebooks(), "chapters 下还没有任何 notebook"


def test_all_notebooks_execute():
    for nb_path in _all_notebooks():
        nb = nbformat.read(nb_path, as_version=4)
        client = NotebookClient(nb, timeout=300, kernel_name="python3",
                                resources={"metadata": {"path": str(ROOT)}})
        client.execute()
        # nbclient 遇到异常会直接抛出，走到这里即视为执行成功
