"""课程结构冒烟测试：保证仓库骨架与每章「三件套」模板不退化。

这是本项目的常驻护栏——任何里程碑都不得破坏它。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_repo_skeleton_files_exist():
    for name in [".gitignore", ".gitattributes", "requirements.txt", "LICENSE", "README.md"]:
        assert (ROOT / name).exists(), f"缺少顶层文件 {name}"


def test_requirements_pins_versions():
    reqs = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    pinned = [ln for ln in reqs.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    assert pinned, "requirements.txt 不应为空"
    assert all("==" in ln for ln in pinned), "所有依赖必须锁定版本 (==)"


def test_readme_has_required_sections():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for marker in ["TL;DR", "学习路径", "章节导航", "快速开始", "延伸阅读", "版权"]:
        assert marker in readme, f"README 缺少「{marker}」"


def test_chapters_dir_exists():
    assert (ROOT / "chapters").is_dir(), "缺少 chapters/ 目录"


def test_each_existing_chapter_has_three_part_template():
    chapters = sorted((ROOT / "chapters").glob("0*/"))
    if not chapters:
        return  # M0 阶段尚无章节；M1 起由 test_chapter_01_present 强制至少一章
    for ch in chapters:
        assert (ch / "README.md").exists(), f"{ch.name} 缺讲义 README.md"
        assert (ch / "notebooks").is_dir(), f"{ch.name} 缺 notebooks/"
        assert (ch / "exercises").is_dir(), f"{ch.name} 缺 exercises/"
        assert (ch / "exercises" / "solutions").is_dir(), f"{ch.name} 缺 exercises/solutions/"


def test_chapter_01_present():
    ch01 = ROOT / "chapters" / "01-factor-basics"
    assert ch01.is_dir(), "第1章 chapters/01-factor-basics/ 尚未创建"


def test_chapter_lecture_has_template_markers():
    ch01 = ROOT / "chapters" / "01-factor-basics"
    readme = (ch01 / "README.md").read_text(encoding="utf-8")
    for marker in ["🎯", "📚", "📖", "📋", "✅"]:
        assert marker in readme, f"第1章讲义缺少模板标记 {marker}"


def test_chapter_02_present_and_complete():
    ch02 = ROOT / "chapters" / "02-methodology"
    assert ch02.is_dir(), "第2章 chapters/02-methodology/ 尚未创建"
    readme = (ch02 / "README.md").read_text(encoding="utf-8")
    for marker in ["🎯", "📚", "📖", "📋", "✅"]:
        assert marker in readme, f"第2章讲义缺少模板标记 {marker}"
    for name in [
        "02.1-portfolio-sorting.ipynb",
        "02.2-regression-methods.ipynb",
        "02.3-anomaly-and-grs.ipynb",
    ]:
        assert (ch02 / "notebooks" / name).exists(), f"第2章缺少 notebook {name}"
    assert (ch02 / "exercises" / "EXERCISES.md").exists(), "第2章缺少练习"
    assert (ch02 / "exercises" / "solutions" / "SOLUTIONS.md").exists(), "第2章缺少练习答案"


def test_chapter_03_present_and_complete():
    ch03 = ROOT / "chapters" / "03-mainstream-factors"
    assert ch03.is_dir(), "第3章 chapters/03-mainstream-factors/ 尚未创建"
    readme = (ch03 / "README.md").read_text(encoding="utf-8")
    for marker in ["🎯", "📚", "📖", "📋", "✅"]:
        assert marker in readme, f"第3章讲义缺少模板标记 {marker}"
    for name in [
        "03.1-data-and-factors.ipynb",
        "03.2-factor-sorting.ipynb",
        "03.3-performance-and-robustness.ipynb",
    ]:
        assert (ch03 / "notebooks" / name).exists(), f"第3章缺少 notebook {name}"
    assert (ch03 / "exercises" / "EXERCISES.md").exists(), "第3章缺少练习"
    assert (ch03 / "exercises" / "solutions" / "SOLUTIONS.md").exists(), "第3章缺少练习答案"


def test_chapter_04_present_and_complete():
    ch04 = ROOT / "chapters" / "04-multi-factor-models"
    assert ch04.is_dir(), "第4章 chapters/04-multi-factor-models/ 尚未创建"
    readme = (ch04 / "README.md").read_text(encoding="utf-8")
    for marker in ["🎯", "📚", "📖", "📋", "✅"]:
        assert marker in readme, f"第4章讲义缺少模板标记 {marker}"
    for name in [
        "04.1-seven-models.ipynb",
        "04.2-model-comparison.ipynb",
        "04.3-priced-factors-and-parsimony.ipynb",
    ]:
        assert (ch04 / "notebooks" / name).exists(), f"第4章缺少 notebook {name}"
    assert (ch04 / "exercises" / "EXERCISES.md").exists(), "第4章缺少练习"
    assert (ch04 / "exercises" / "solutions" / "SOLUTIONS.md").exists(), "第4章缺少练习答案"
