from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]

TEXT = "#253038"
MUTED = "#5D676E"
EDGE = "#8F9AA3"
PANEL = "#FDFEFE"
LINE = "#7D8790"

BLUE = "#DCE8F8"
TEAL = "#DCEFF0"
GREEN = "#E6F0DD"
PEACH = "#F3E3D7"
YELLOW = "#F7F1D8"
LAVENDER = "#E5E8F6"
PINK = "#F7E4EF"


def setup() -> tuple[plt.Figure, plt.Axes]:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "axes.unicode_minus": False,
        }
    )
    fig, ax = plt.subplots(figsize=(10.2, 4.45), constrained_layout=False)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 13.8)
    ax.set_ylim(0, 5.7)
    ax.set_position([0, 0, 1, 1])
    ax.axis("off")
    return fig, ax


def panel(ax: plt.Axes, x: float, y: float, w: float, h: float, title: str) -> None:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.055,rounding_size=0.16",
        linewidth=1.15,
        edgecolor="#C7CDD2",
        facecolor=PANEL,
        zorder=1,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center", fontsize=9.7, color=TEXT, fontweight="bold", zorder=4)


def block(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body: str,
    fill: str,
    title_size: float = 8.6,
    body_size: float = 6.8,
) -> tuple[float, float, float, float]:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.035,rounding_size=0.055",
        linewidth=1.15,
        edgecolor=EDGE,
        facecolor=fill,
        zorder=3,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center", fontsize=title_size, color=TEXT, fontweight="bold", zorder=4)
    ax.text(x + w / 2, y + h * 0.29, body, ha="center", va="center", fontsize=body_size, color=MUTED, linespacing=1.18, zorder=4)
    return (x, y, w, h)


def center_right(b: tuple[float, float, float, float]) -> tuple[float, float]:
    x, y, w, h = b
    return (x + w, y + h / 2)


def center_left(b: tuple[float, float, float, float]) -> tuple[float, float]:
    x, y, _w, h = b
    return (x, y + h / 2)


def center_top(b: tuple[float, float, float, float]) -> tuple[float, float]:
    x, y, w, h = b
    return (x + w / 2, y + h)


def center_bottom(b: tuple[float, float, float, float]) -> tuple[float, float]:
    x, y, w, _h = b
    return (x + w / 2, y)


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], dashed: bool = False) -> None:
    if abs(start[0] - end[0]) > 1e-9 and abs(start[1] - end[1]) > 1e-9:
        raise ValueError(f"non-orthogonal arrow: {start} -> {end}")
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=9.5,
        linewidth=1.05,
        color=LINE,
        linestyle=(0, (4, 3)) if dashed else "solid",
        shrinkA=1.2,
        shrinkB=1.2,
        zorder=2,
    )
    ax.add_patch(patch)


def ortho(ax: plt.Axes, points: list[tuple[float, float]], dashed: bool = False) -> None:
    for a, b in zip(points[:-2], points[1:-1]):
        if abs(a[0] - b[0]) > 1e-9 and abs(a[1] - b[1]) > 1e-9:
            raise ValueError(f"non-orthogonal segment: {a} -> {b}")
        ax.plot([a[0], b[0]], [a[1], b[1]], color=LINE, lw=1.05, linestyle=(0, (4, 3)) if dashed else "solid", zorder=2)
    arrow(ax, points[-2], points[-1], dashed=dashed)


def vertical(ax: plt.Axes, upper: tuple[float, float, float, float], lower: tuple[float, float, float, float]) -> None:
    arrow(ax, center_bottom(upper), center_top(lower))


def save(fig: plt.Figure, bases: list[Path]) -> None:
    for base in bases:
        base.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
        fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.02)
        fig.savefig(base.with_suffix(".png"), dpi=280, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def draw_common(
    data: list[tuple[str, str, str]],
    train: list[tuple[str, str, str]],
    evals: list[tuple[str, str, str]],
    note: str,
    bases: list[Path],
) -> None:
    fig, ax = setup()

    panel(ax, 0.45, 0.55, 3.25, 4.72, "数据准备")
    panel(ax, 4.05, 0.55, 5.25, 4.72, "训练闭环")
    panel(ax, 9.65, 0.55, 3.65, 4.72, "评估归档")

    data_boxes = [
        block(ax, 0.92, 3.86 - i * 1.28, 2.30, 0.72, title, body, fill)
        for i, (title, body, fill) in enumerate(data)
    ]
    train_boxes = [
        block(ax, 4.55, 3.86 - i * 1.28, 2.24, 0.72, title, body, fill)
        for i, (title, body, fill) in enumerate(train)
    ]
    eval_boxes = [
        block(ax, 10.13, 3.86 - i * 1.28, 2.30, 0.72, title, body, fill)
        for i, (title, body, fill) in enumerate(evals)
    ]

    for upper, lower in zip(data_boxes, data_boxes[1:]):
        vertical(ax, upper, lower)
    for upper, lower in zip(train_boxes, train_boxes[1:]):
        vertical(ax, upper, lower)
    for upper, lower in zip(eval_boxes, eval_boxes[1:]):
        vertical(ax, upper, lower)

    ortho(ax, [center_right(data_boxes[-1]), (3.72, center_right(data_boxes[-1])[1]), (3.72, center_left(train_boxes[0])[1]), center_left(train_boxes[0])])
    ortho(ax, [center_right(train_boxes[0]), (9.42, center_right(train_boxes[0])[1]), (9.42, center_left(eval_boxes[0])[1]), center_left(eval_boxes[0])])

    # Feedback loop: optimizer/loss updates the model. The route stays outside nodes.
    opt = train_boxes[-1]
    model = train_boxes[0]
    loop_y = 1.02
    loop_x = 8.75
    ortho(
        ax,
        [
            center_right(opt),
            (loop_x, center_right(opt)[1]),
            (loop_x, loop_y),
            (4.34, loop_y),
            (4.34, center_left(model)[1]),
            center_left(model),
        ],
        dashed=True,
    )
    ax.text(6.55, 0.82, "参数更新反馈", ha="center", va="center", fontsize=7.1, color=MUTED)

    ax.text(6.88, 5.48, note, ha="center", va="center", fontsize=8.0, color=MUTED)
    save(fig, bases)


def exp4() -> None:
    draw_common(
        data=[
            ("平行语料", "NiuTrans\n中英句对", YELLOW),
            ("文本预处理", "分词 / 词表\npadding 与 mask", GREEN),
            ("批量加载", "source / target\nDataLoader", BLUE),
        ],
        train=[
            ("Transformer", "Encoder-Decoder\nMHA + FFN", BLUE),
            ("训练目标", "label smoothing\n交叉熵损失", PEACH),
            ("优化更新", "Adam 调度\n梯度回传", LAVENDER),
        ],
        evals=[
            ("最优权重", "保存 checkpoint\n加载推理", TEAL),
            ("束搜索解码", "Beam Search\n生成译文", GREEN),
            ("BLEU4 评估", "测试集指标\n曲线与样例归档", PINK),
        ],
        note="Transformer 机器翻译训练、推理与指标归档流程",
        bases=[
            ROOT / "实验报告/实验4/figures/algorithm_flow_academic",
            ROOT / "code/work4 code/figures/algorithm_flow_academic",
        ],
    )


def exp6() -> None:
    draw_common(
        data=[
            ("图像与标签", "CamVid Tiny\nRGB / mask", YELLOW),
            ("空间规整", "resize 128x96\n类别索引保持", GREEN),
            ("固定划分", "train / val / test\n70 / 15 / 15", BLUE),
        ],
        train=[
            ("SegNet 前向", "Encoder-Decoder\npool indices", BLUE),
            ("像素级监督", "Cross Entropy\n忽略无效区域", PEACH),
            ("优化更新", "AdamW\n权重衰减", LAVENDER),
        ],
        evals=[
            ("最优权重", "验证集选择\n保存 checkpoint", TEAL),
            ("测试评估", "PA / MPA\nmIoU", GREEN),
            ("结果可视化", "预测 mask\n图表与样例", PINK),
        ],
        note="SegNet 街景语义分割数据、训练与测试流程",
        bases=[
            ROOT / "实验报告/实验6/figures/algorithm_flow_academic",
            ROOT / "code/work6 code/figures/algorithm_flow_academic",
        ],
    )


def exp7() -> None:
    draw_common(
        data=[
            ("PTB 语料", "train / valid / test\nsimple-examples", YELLOW),
            ("词表构建", "10k vocab\nword to id", GREEN),
            ("BPTT 批处理", "batchify\nseq_len = 35", BLUE),
        ],
        train=[
            ("LSTM 语言模型", "Embedding + 2层\nweight tying", BLUE),
            ("序列损失", "next-token CE\n困惑度 PPL", PEACH),
            ("优化更新", "SGD + 裁剪\n学习率衰减", LAVENDER),
        ],
        evals=[
            ("验证选择", "valid PPL 最低\n保存 checkpoint", TEAL),
            ("独立测试", "加载最优权重\ntest PPL", GREEN),
            ("结果归档", "曲线 / 指标\n调参记录", PINK),
        ],
        note="PTB LSTM 语言模型训练、验证选择与测试流程",
        bases=[
            ROOT / "实验报告/实验7/figures/algorithm_flow",
            ROOT / "实验报告/实验7/figures/algorithm_flow_academic",
            ROOT / "code/work7 code/figures/algorithm_flow",
            ROOT / "code/work7 code/figures/algorithm_flow_academic",
        ],
    )


def main() -> None:
    exp4()
    exp6()
    exp7()


if __name__ == "__main__":
    main()
