"""生成《困境资产中的因子思维》30 分钟分享 PPTX。"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "articles" / "assets"
OUT = ASSETS / "困境资产中的因子思维-30分钟分享.pptx"

CREAM = RGBColor(255, 248, 236)
INK = RGBColor(62, 44, 35)
MUTED = RGBColor(122, 106, 95)
ORANGE = RGBColor(242, 140, 40)
GREEN = RGBColor(91, 140, 90)
BLUE = RGBColor(91, 127, 166)
RED = RGBColor(217, 93, 57)
PURPLE = RGBColor(123, 106, 168)
LINE = RGBColor(234, 220, 200)
WHITE = RGBColor(255, 255, 255)

FONT = "Microsoft YaHei"


def set_bg(slide, color=CREAM):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text(slide, text, left, top, width, height, size=18, bold=False,
             color=INK, align=PP_ALIGN.LEFT, font=FONT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_bullets(slide, items, left, top, width, height, size=18, color=INK,
                line_spacing=1.35):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            text, level = item
        else:
            text, level = item, 0
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = level
        p.line_spacing = line_spacing
        p.space_after = Pt(6)
        run = p.add_run()
        prefix = "• " if level == 0 else "– "
        run.text = prefix + text
        run.font.name = FONT
        run.font.size = Pt(size if level == 0 else size - 2)
        run.font.color.rgb = color if level == 0 else MUTED
    return box


def add_rect(slide, left, top, width, height, fill=WHITE, line=LINE,
             radius=False, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    shp = slide.shapes.add_shape(shape if radius else MSO_SHAPE.RECTANGLE,
                                 Inches(left), Inches(top), Inches(width), Inches(height))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.color.rgb = line
    shp.line.width = Pt(1.2)
    if radius:
        try:
            shp.adjustments[0] = 0.08
        except Exception:
            pass
    return shp


def add_footer(slide, page):
    add_text(slide, "困境资产中的因子思维 ｜ 内部交流", 0.6, 7.12, 8.0, 0.3,
             size=10, color=MUTED)
    add_text(slide, str(page), 12.45, 7.12, 0.4, 0.3, size=10, color=MUTED,
             align=PP_ALIGN.RIGHT)


def add_title(slide, kicker, title, subtitle=None):
    add_text(slide, kicker, 0.6, 0.42, 12.0, 0.3, size=12, bold=True, color=ORANGE)
    add_text(slide, title, 0.6, 0.78, 12.0, 0.8, size=30, bold=True, color=INK)
    if subtitle:
        add_text(slide, subtitle, 0.6, 1.52, 12.0, 0.45, size=15, color=MUTED)
    # top-right small tag
    add_text(slide, "从故事 → 证据", 10.9, 0.42, 1.9, 0.3, size=11,
             bold=True, color=GREEN, align=PP_ALIGN.RIGHT)


def add_key_message(slide, text, top=6.25):
    add_rect(slide, 0.6, top, 12.13, 0.62, fill=WHITE, line=LINE, radius=True)
    add_text(slide, text, 0.85, top + 0.12, 11.6, 0.4, size=17, bold=True,
             color=INK, align=PP_ALIGN.CENTER)


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def slide_1(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    # decorative blocks
    add_rect(s, 10.1, 0.0, 3.2, 0.18, fill=ORANGE, line=ORANGE, shape=MSO_SHAPE.RECTANGLE)
    add_rect(s, 0.0, 6.9, 4.2, 0.18, fill=GREEN, line=GREEN, shape=MSO_SHAPE.RECTANGLE)
    add_text(s, "内部交流 ｜ 投资方法论", 0.8, 1.0, 8.0, 0.4, size=14, bold=True, color=ORANGE)
    add_text(s, "困境资产中的\n因子思维", 0.8, 1.6, 10.5, 2.2, size=48, bold=True, color=INK)
    add_text(s, "从“故事”到“可检验的证据”", 0.8, 4.0, 10.0, 0.6, size=24, color=MUTED)
    add_text(s, "一套可复现的研究工作流 ｜ 30 分钟", 0.8, 4.7, 10.0, 0.4, size=16, color=MUTED)
    add_text(s, "2026-11-22", 0.8, 6.2, 4.0, 0.4, size=13, color=MUTED)
    add_notes(s, "0:00–0:01 开场。不要急着讲公式，先让听众进入“故事 vs 证据”的语境。")
    return s


def slide_2(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "开场", "你听到的是故事，还是证据？")
    quotes = [
        ("“核心地段，只是股东流动性问题。”", ORANGE),
        ("“三折买入，闭着眼都不会亏。”", RED),
        ("“上一轮周期我就是这么赚的。”", BLUE),
        ("“基本面没问题，只是被抽贷了。”", GREEN),
    ]
    for i, (q, color) in enumerate(quotes):
        x = 0.7 + (i % 2) * 6.2
        y = 1.95 + (i // 2) * 1.55
        add_rect(s, x, y, 5.8, 1.25, fill=WHITE, line=color, radius=True)
        add_text(s, q, x + 0.3, y + 0.28, 5.2, 0.7, size=17, color=INK)
    add_text(s, "互动：哪一句最像你听过的？", 0.7, 5.35, 10.0, 0.4, size=16, bold=True, color=ORANGE)
    add_key_message(s, "故事不一定错，但故事不是证据。")
    add_notes(s, "0:01–0:03 让听众选一句，建立共鸣。不要否定故事，强调“故事是起点，证据是终点”。")
    return s


def slide_3(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "为什么困境资产特别难", "五个特殊性",
              "样本少 + 反馈慢 + 叙事强 = 最容易把 β 当 α")
    items = [
        ("样本少：一年看几十个，真正成交个位数", 0),
        ("周期长：3~7 年才反馈，错了也很难立刻知道", 0),
        ("异质性强：法律、资产、区域、债务人各不同", 0),
        ("幸存者偏差：失败者不再发声，成功者反复被引用", 0),
        ("叙事驱动：越便宜，故事越动人，越容易忽略风险", 0),
    ]
    add_bullets(s, items, 0.8, 2.15, 11.8, 3.6, size=20)
    add_key_message(s, "所以需要的不是更多故事，而是一套“把故事拆成可检验问题”的方法。")
    add_notes(s, "0:03–0:05 五个特殊性逐个讲，每个配一个你见过的例子。")
    return s


def slide_4(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "统一语言", "一个公式：E[R] = βλ + α",
              "把收益拆成“共同原因”和“个体能力”")
    add_text(s, "E[R] = βλ + α", 0.8, 2.15, 11.8, 0.9, size=40, bold=True,
             color=ORANGE, align=PP_ALIGN.CENTER, font="Cambria Math")
    parts = [
        ("β", "暴露", "你对共同风险敞开多少", BLUE),
        ("λ", "溢价", "市场为承担风险支付多少", GREEN),
        ("α", "定价误差", "模型解释不了的超额收益", RED),
    ]
    for i, (sym, name, desc, color) in enumerate(parts):
        x = 0.8 + i * 4.2
        add_rect(s, x, 3.35, 3.8, 1.65, fill=WHITE, line=color, radius=True)
        add_text(s, sym, x + 0.25, 3.55, 0.8, 0.6, size=30, bold=True, color=color,
                 font="Cambria Math")
        add_text(s, name, x + 1.0, 3.55, 2.5, 0.4, size=18, bold=True, color=INK)
        add_text(s, desc, x + 0.25, 4.15, 3.3, 0.6, size=13, color=MUTED)
    add_bullets(s, [
        "周期底部买什么都能赚 → 是 β",
        "信用利差高位买债 → 是 β",
        "高杠杆放大收益 → 还是 β",
    ], 0.9, 5.25, 11.8, 0.9, size=15)
    add_key_message(s, "扣掉 β 之后，你的 α 还在不在？")
    add_notes(s, "0:05–0:08 用三个“β 伪装成 α”的例子，让听众意识到公式不是学术，是防自欺。")
    return s


def slide_5(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "翻译", "把公式翻译到困境资产", "因子不是没有，只是藏得更深")
    data = [
        ("因子投资", "困境资产"),
        ("市场 / 行业 / 风格因子", "利率、信用利差、地产周期、区域流动性、法律/监管"),
        ("β（暴露）", "项目对共同风险的敏感度"),
        ("λ（溢价）", "市场为承担风险要求的折价/回报"),
        ("α（定价误差）", "项目选择、重组、法律执行、运营改善、退出时机"),
    ]
    table = s.shapes.add_table(len(data), 2, Inches(0.7), Inches(1.95),
                               Inches(11.9), Inches(3.9)).table
    table.columns[0].width = Inches(4.0)
    table.columns[1].width = Inches(7.9)
    for r, (a, b) in enumerate(data):
        for c, text in enumerate((a, b)):
            cell = table.cell(r, c)
            cell.text = text
            cell.fill.solid()
            cell.fill.fore_color.rgb = ORANGE if r == 0 else (WHITE if r % 2 else CREAM)
            for p in cell.text_frame.paragraphs:
                p.alignment = PP_ALIGN.LEFT
                for run in p.runs:
                    run.font.name = FONT
                    run.font.size = Pt(15 if r else 16)
                    run.font.bold = (r == 0)
                    run.font.color.rgb = WHITE if r == 0 else INK
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = Inches(0.12)
            cell.margin_right = Inches(0.12)
    add_key_message(s, "先问“这是哪个因子”，再问“这个项目有什么特别”。")
    add_notes(s, "0:08–0:10 逐行翻译。强调 λ 是市场定价，不是你的能力；α 才是你要证明的东西。")
    return s


def slide_6(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "第2章方法", "把“感觉”变成“证据”", "五个工具，一套语法")
    cards = [
        ("排序法", "先排队，再分组比较", "高组 − 低组 = 因子收益", ORANGE),
        ("时序回归", "每个项目对共同因子的 β、α", "r = α + βf + ε", BLUE),
        ("截面 / FM", "市场为哪类风险付钱", "每期回归再平均", GREEN),
        ("NW / GRS", "标准误与联合检验", "别被“显著”骗了", RED),
        ("正交化", "剔除重复信息", "残差 = 纯增量", PURPLE),
    ]
    for i, (title, line1, line2, color) in enumerate(cards):
        x = 0.55 + i * 2.48
        add_rect(s, x, 1.95, 2.3, 3.55, fill=WHITE, line=color, radius=True)
        add_rect(s, x, 1.95, 2.3, 0.12, fill=color, line=color, shape=MSO_SHAPE.RECTANGLE)
        add_text(s, title, x + 0.18, 2.25, 1.95, 0.4, size=17, bold=True, color=color)
        add_text(s, line1, x + 0.18, 2.8, 1.95, 0.9, size=13, color=INK)
        add_text(s, line2, x + 0.18, 3.75, 1.95, 0.8, size=12, color=MUTED)
    add_bullets(s, [
        "先分组，再回归；先控制，再解释。",
        "单变量排序 → 双重排序 → 时序 α → FM 加控制变量。",
    ], 0.8, 5.65, 11.8, 0.7, size=15)
    add_key_message(s, "方法不是量化专利，是任何项目都能用的研究语法。")
    add_notes(s, "0:10–0:16 重点讲排序法、FM、NW/GRS、正交化。每个工具配一个困境资产例子。")
    return s


def slide_7(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "工作流", "六步：从定义到复盘", "一页图，贴在投委会桌上")
    img = ASSETS / "distressed-factor-workflow.png"
    if img.exists():
        s.shapes.add_picture(str(img), Inches(2.17), Inches(1.72), width=Inches(9.0))
    add_text(s, "复盘不是终点，是下一轮的 Step 1。", 0.8, 7.05, 8.0, 0.3,
             size=11, color=ORANGE, bold=True)
    add_notes(s, "0:16–0:18 展示工作流图，强调六步不是线性结束，6→1 的复盘回路才是核心。")
    return s


def slide_8(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "第6章警告", "别让“研究”变成“数据窥探”", "试得够多，总能“显著”")
    cols = [
        ("p-hacking 的三个动作", [
            "只讲成功案例，不讲失败",
            "只挑好年份 / 好区域",
            "先看项目，再编投资逻辑",
        ], RED),
        ("策略动物园", [
            "每个策略都有成功案例",
            "跨周期、跨区域还成立吗？",
            "扣掉成本、容量还剩多少？",
        ], ORANGE),
        ("三个必问", [
            "样本外还成立吗？",
            "换了口径还成立吗？",
            "有经济逻辑吗？",
        ], GREEN),
    ]
    for i, (title, items, color) in enumerate(cols):
        x = 0.7 + i * 4.15
        add_rect(s, x, 1.95, 3.85, 3.9, fill=WHITE, line=color, radius=True)
        add_text(s, title, x + 0.25, 2.2, 3.35, 0.45, size=18, bold=True, color=color)
        add_bullets(s, items, x + 0.25, 2.9, 3.35, 2.6, size=15)
    add_key_message(s, "先怀疑，再验证；先看完整样本，再谈成功经验。")
    add_notes(s, "0:18–0:20 把学术的 p-hacking 翻译成尽调里的“只挑成功案例”。")
    return s


def slide_9(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "行为金融", "错误定价从哪里来？", "错误定价 = 偏差 + 套利限制")
    cells = [
        ("套利限制", "资金久期、牌照、法律程序、资产不可分割", BLUE),
        ("预期偏差", "过度悲观 / 过度乐观、锚定原估值", ORANGE),
        ("风险偏好偏差", "损失厌恶、处置效应、彩票偏好", RED),
        ("认知限制", "注意力有限、只看熟悉区域/资产", GREEN),
    ]
    for i, (title, desc, color) in enumerate(cells):
        x = 0.7 + (i % 2) * 6.2
        y = 1.95 + (i // 2) * 1.75
        add_rect(s, x, y, 5.8, 1.45, fill=WHITE, line=color, radius=True)
        add_text(s, title, x + 0.25, y + 0.18, 5.2, 0.4, size=18, bold=True, color=color)
        add_text(s, desc, x + 0.25, y + 0.7, 5.2, 0.55, size=14, color=MUTED)
    add_key_message(s, "两者同时存在，才是机会；只有偏差、没有套利限制，价格会被纠回来。")
    add_notes(s, "0:20–0:22 四个来源各举一个困境资产例子，强调“套利限制”是困境资产的核心。")
    return s


def slide_10(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "第7章落地", "风险、组合、归因", "从“看对”到“做对”")
    cards = [
        ("风险模型", "Σ = BΣ_fB' + D", "真分散，还是假分散？", BLUE),
        ("组合优化", "max w'μ − λ/2·w'Σw", "小心“误差最大化器”", ORANGE),
        ("Smart Beta", "规则化：分数 → 选股 → 加权", "把策略变成可检验的规则", GREEN),
        ("归因", "收益 = 因子贡献 + α", "钱从哪里来？", PURPLE),
    ]
    for i, (title, formula, desc, color) in enumerate(cards):
        x = 0.7 + (i % 2) * 6.2
        y = 1.95 + (i // 2) * 1.85
        add_rect(s, x, y, 5.8, 1.55, fill=WHITE, line=color, radius=True)
        add_text(s, title, x + 0.25, y + 0.16, 5.2, 0.4, size=18, bold=True, color=color)
        add_text(s, formula, x + 0.25, y + 0.62, 5.2, 0.35, size=14, bold=True,
                 color=INK, font="Cambria Math")
        add_text(s, desc, x + 0.25, y + 1.05, 5.2, 0.35, size=13, color=MUTED)
    add_key_message(s, "收益模型决定偏不偏，风险模型决定稳不稳，归因决定知不知。")
    add_notes(s, "0:22–0:25 四块各一句话：风险模型防假分散，优化防误差最大化，Smart Beta 规则化，归因回答钱从哪来。")
    return s


def slide_11(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "三个误区", "最容易犯的三个错", "每一个都能让好项目变成坏投资")
    rows = [
        ("01", "把 β 当 α", "周期底部买什么都能赚；高杠杆放大收益", "扣掉共同因子，再看 α 是否显著", RED),
        ("02", "把样本内当样本外", "用 2016–2021 的经验套 2022–2024；只总结成功案例", "时间切分、完整样本、预注册", ORANGE),
        ("03", "把模型当真相", "风险模型说“分散”，压力下相关性飙升", "压力测试、稳健性、人工复核", BLUE),
    ]
    for i, (num, title, symptom, fix, color) in enumerate(rows):
        y = 1.95 + i * 1.45
        add_rect(s, 0.7, y, 11.9, 1.22, fill=WHITE, line=color, radius=True)
        add_text(s, num, 0.95, y + 0.28, 0.8, 0.5, size=24, bold=True, color=color)
        add_text(s, title, 1.8, y + 0.18, 3.0, 0.4, size=18, bold=True, color=INK)
        add_text(s, symptom, 1.8, y + 0.66, 4.8, 0.4, size=13, color=MUTED)
        add_text(s, "解法：" + fix, 7.0, y + 0.45, 5.3, 0.45, size=14, bold=True, color=GREEN)
    add_key_message(s, "模型是地图，不是领土；先写“什么证明我错了”，再写“为什么买”。")
    add_notes(s, "0:25–0:27 三个误区各讲一个真实场景，重点在“解法”。")
    return s


def slide_12(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "随身清单", "尽调十问", "投前问一遍，投后少后悔")
    left = [
        "1. 收益里多少来自周期/区域/流动性？",
        "2. 我的 β 是什么？",
        "3. 信用利差走阔 200bp，回收率怎么变？",
        "4. “便宜”是不是“质量差/法律复杂”的代理？",
        "5. 成功案例的完整样本是什么？",
    ]
    right = [
        "6. 我试了多少种退出假设？",
        "7. 交易对手/债权人/开发商是否重叠？",
        "8. 压力情景下，组合相关性会怎样？",
        "9. 扣掉 β/成本后，α 还显著吗？",
        "10. 什么证据会证明我错了？",
    ]
    add_bullets(s, left, 0.8, 2.0, 5.9, 3.8, size=16, line_spacing=1.5)
    add_bullets(s, right, 6.9, 2.0, 5.9, 3.8, size=16, line_spacing=1.5)
    add_key_message(s, "把这十问打印出来，放在投决会桌上。")
    add_notes(s, "0:27–0:28 不逐条念，挑 3 条最容易被忽略的：β、完整样本、证明我错了。")
    return s


def slide_13(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_title(s, "结语", "四句话", "因子思维是一种“反叙事”的纪律")
    lines = [
        ("收益 = βλ + α", ORANGE),
        ("先分清共同原因，再谈个体能力", INK),
        ("先看样本外，再信样本内", INK),
        ("先做归因，再谈成功", INK),
    ]
    for i, (text, color) in enumerate(lines):
        add_text(s, text, 1.0, 2.0 + i * 0.85, 11.3, 0.6, size=26, bold=True,
                 color=color)
    add_text(s, "因子研究不是寻找圣杯，而是用证据保护判断，用归因持续学习。",
             1.0, 5.75, 11.3, 0.5, size=17, color=MUTED)
    add_notes(s, "0:28–0:30 放慢语速，四句话逐句停顿。最后一句作为收束。")
    return s


def slide_14(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s)
    add_text(s, "Q&A", 0.8, 0.7, 4.0, 0.9, size=44, bold=True, color=ORANGE)
    add_text(s, "预设问题", 0.8, 1.8, 4.0, 0.4, size=16, bold=True, color=MUTED)
    questions = [
        "困境资产样本这么少，怎么做统计？",
        "β 怎么定义？宏观因子怎么选？",
        "这套方法能直接指导投决吗？",
        "怎么说服投委会/老板？",
    ]
    add_bullets(s, questions, 0.8, 2.3, 7.0, 3.0, size=18, line_spacing=1.6)
    add_rect(s, 8.4, 1.8, 4.2, 4.4, fill=WHITE, line=LINE, radius=True)
    add_text(s, "回答原则", 8.65, 2.0, 3.7, 0.4, size=16, bold=True, color=GREEN)
    add_bullets(s, [
        "先讲经济逻辑，再讲统计",
        "先讲局限，再讲结论",
        "先讲样本外，再讲样本内",
        "先讲成本，再讲收益",
    ], 8.65, 2.5, 3.7, 3.2, size=14, line_spacing=1.4)
    add_text(s, "谢谢", 0.8, 6.2, 4.0, 0.5, size=20, bold=True, color=INK)
    add_notes(s, "留 2 分钟 Q&A。回答时先讲经济逻辑和局限，不要急着证明方法“能赚钱”。")
    return s


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    for fn in [slide_1, slide_2, slide_3, slide_4, slide_5, slide_6,
               slide_7, slide_8, slide_9, slide_10, slide_11, slide_12,
               slide_13, slide_14]:
        fn(prs)
    for i, slide in enumerate(prs.slides, start=1):
        if i not in (1, 7):
            add_footer(slide, i)
    prs.save(str(OUT))
    print("saved", OUT)


if __name__ == "__main__":
    main()
