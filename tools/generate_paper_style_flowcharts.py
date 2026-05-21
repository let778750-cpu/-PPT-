from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]

EDGE = "#8B8B8B"
TEXT = "#2F3437"
MUTED = "#5D6468"
BLUE = "#DDE8F8"
TEAL = "#DCEFF0"
GREEN = "#E7F0DA"
PEACH = "#F4E4D7"
YELLOW = "#F7F1D8"
GRAY = "#E8E6E6"
LAVENDER = "#E4E8F6"
WHITE = "#FFFFFF"


def setup_axes():
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
    fig, ax = plt.subplots(figsize=(9.6, 5.4), constrained_layout=False)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fill=WHITE, dashed=False, fontsize=10, bold=False, radius=0.08):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.025,rounding_size={radius}",
        linewidth=1.25,
        edgecolor=EDGE,
        facecolor=fill,
        linestyle=(0, (4, 2)) if dashed else "solid",
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=TEXT,
        fontweight="bold" if bold else "normal",
        linespacing=1.2,
        zorder=3,
    )
    return patch


def group(ax, x, y, w, h, label, dashed=False):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.06,rounding_size=0.42",
        linewidth=1.35,
        edgecolor="#B8B8B8",
        facecolor="none",
        linestyle=(0, (5, 3)) if dashed else "solid",
        zorder=1,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y - 0.35, label, ha="center", va="top", fontsize=10, color=TEXT)
    return patch


def arrow(ax, x1, y1, x2, y2, dashed=False, lw=1.1, color=EDGE, rad=0.0):
    patch = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>",
        mutation_scale=9.5,
        linewidth=lw,
        linestyle=(0, (4, 3)) if dashed else "solid",
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=1.5,
        shrinkB=1.5,
        zorder=1.5,
    )
    ax.add_patch(patch)


def ortho_arrow(ax, points, dashed=False, lw=1.1, color=EDGE):
    """Draw an orthogonal connector. Every segment must be horizontal or vertical."""
    if len(points) < 2:
        return
    for (x1, y1), (x2, y2) in zip(points[:-2], points[1:-1]):
        if abs(x1 - x2) > 1e-9 and abs(y1 - y2) > 1e-9:
            raise ValueError(f"non-orthogonal segment: {(x1, y1)} -> {(x2, y2)}")
        line(ax, x1, y1, x2, y2, dashed=dashed)
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    if abs(x1 - x2) > 1e-9 and abs(y1 - y2) > 1e-9:
        raise ValueError(f"non-orthogonal segment: {(x1, y1)} -> {(x2, y2)}")
    arrow(ax, x1, y1, x2, y2, dashed=dashed, lw=lw, color=color)


def line(ax, x1, y1, x2, y2, dashed=False):
    ax.plot([x1, x2], [y1, y2], color=EDGE, lw=1.0, linestyle=(0, (4, 3)) if dashed else "solid", zorder=1)


def sine_icon(ax, x, y):
    ax.add_patch(Arc((x, y), 0.58, 0.58, theta1=0, theta2=360, lw=1.1, color=EDGE))
    xs = [x - 0.21, x - 0.07, x + 0.07, x + 0.21]
    ys = [y, y + 0.10, y - 0.10, y]
    ax.plot(xs, ys, color=EDGE, lw=1.1)


def plus_icon(ax, x, y):
    ax.add_patch(Arc((x, y), 0.46, 0.46, theta1=0, theta2=360, lw=1.1, color=EDGE))
    ax.plot([x - 0.14, x + 0.14], [y, y], color=EDGE, lw=1.0)
    ax.plot([x, x], [y - 0.14, y + 0.14], color=EDGE, lw=1.0)


def save(fig, output_bases: list[Path], bounds=None):
    if bounds is not None:
        xmin, ymin, xmax, ymax = bounds
        ax = fig.axes[0]
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ratio = max((xmax - xmin) / max(ymax - ymin, 0.1), 0.8)
        fig.set_size_inches(9.6, max(2.15, min(5.4, 9.6 / ratio)), forward=True)
        ax.set_position([0, 0, 1, 1])
    for outbase in output_bases:
        outbase.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(outbase.with_suffix(".png"), dpi=260, bbox_inches="tight", pad_inches=0.02)
        fig.savefig(outbase.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
        fig.savefig(outbase.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def draw_exp1():
    fig, ax = setup_axes()
    group(ax, 1.48, 3.90, 6.56, 1.72, "特征提取器", dashed=True)
    group(ax, 8.42, 3.90, 4.62, 1.72, "分类器", dashed=True)

    stages = [
        (0.45, 4.48, 1.10, 0.64, "输入图像\n1×28×28", YELLOW, 8.2),
        (1.70, 4.48, 1.36, 0.64, "卷积层\n3×3 / 16", BLUE, 8.1),
        (3.24, 4.48, 1.28, 0.64, "ReLU\n最大池化", GREEN, 8.1),
        (4.70, 4.48, 1.36, 0.64, "卷积层\n3×3 / 32", BLUE, 8.1),
        (6.24, 4.48, 1.28, 0.64, "ReLU\n最大池化", GREEN, 8.1),
        (7.70, 4.48, 1.18, 0.64, "Flatten", GRAY, 8.1),
        (9.05, 4.48, 1.18, 0.64, "Dropout", GRAY, 8.1),
        (10.40, 4.48, 1.18, 0.64, "线性层", LAVENDER, 8.1),
        (11.75, 4.48, 1.18, 0.64, "Softmax", TEAL, 8.1),
        (13.35, 4.42, 1.45, 0.76, "预测数字\n0-9", BLUE, 8.2),
    ]
    for x, y, w, h, label, fill, fontsize in stages:
        box(ax, x, y, w, h, label, fill, fontsize=fontsize, bold=label.startswith("预测"))
    for left, right in zip(stages[:-1], stages[1:]):
        arrow(ax, left[0] + left[2], left[1] + left[3] / 2, right[0], right[1] + right[3] / 2)

    box(ax, 2.15, 1.42, 1.42, 0.66, "真实标签", YELLOW, fontsize=8.2)
    box(ax, 5.00, 1.42, 1.68, 0.66, "交叉熵\n损失", PEACH, fontsize=8.2)
    box(ax, 8.12, 1.42, 1.82, 0.66, "AdamW\n参数更新", PEACH, fontsize=8.2)
    ortho_arrow(ax, [(3.57, 1.75), (5.00, 1.75)])
    ortho_arrow(ax, [(6.68, 1.75), (8.12, 1.75)])

    ortho_arrow(ax, [(14.08, 4.42), (14.08, 2.65), (5.84, 2.65), (5.84, 2.08)])
    ortho_arrow(ax, [(9.03, 2.08), (9.03, 2.98), (12.30, 2.98), (12.30, 3.90)], dashed=True)
    ortho_arrow(ax, [(8.12, 1.75), (1.98, 1.75), (1.98, 3.90)], dashed=True)
    ax.text(5.35, 1.05, "反向传播与参数更新通道", fontsize=7.8, color=MUTED, ha="center")

    outputs = [
        ROOT / "实验报告/实验1/figures/algorithm_flow_20260426_vector",
        ROOT / "实验报告/实验1/figures/algorithm_flow_academic",
        ROOT / "code/work1 code/figures/algorithm_flow_academic",
    ]
    save(fig, outputs, bounds=(0.22, 0.82, 15.08, 5.86))


def draw_exp1_model():
    fig, ax = setup_axes()
    xs = [0.9, 3.0, 5.1, 7.2, 9.3, 11.4, 13.2]
    labels = [
        ("输入\n28×28", YELLOW),
        ("Conv + ReLU\n16通道", BLUE),
        ("MaxPool", GREEN),
        ("Conv + ReLU\n32通道", BLUE),
        ("MaxPool\n+ Flatten", GREEN),
        ("全连接层", LAVENDER),
        ("Softmax\n10类概率", TEAL),
    ]
    for i, (x, (label, fill)) in enumerate(zip(xs, labels)):
        box(ax, x, 4.15, 1.55, 0.85, label, fill, fontsize=8.6, bold=i in {0, 6})
        if i:
            arrow(ax, xs[i - 1] + 1.55, 4.58, x, 4.58)
    group(ax, 2.75, 3.55, 6.35, 2.05, "卷积特征提取 ×2", dashed=True)
    group(ax, 11.1, 3.55, 3.85, 2.05, "分类输出", dashed=True)
    save(fig, [ROOT / "实验报告/实验1/figures/model_structure_20260426_vector"], bounds=(0.55, 3.00, 15.10, 5.92))


def draw_exp1_principle():
    fig, ax = setup_axes()
    ax.text(2.0, 6.92, "局部感受野", fontsize=9.2, color=TEXT, ha="center", fontweight="bold")
    cell = 0.34
    start_x, start_y = 0.95, 4.60
    for i in range(5):
        for j in range(5):
            fill = "#F7F7F7"
            if 1 <= i <= 3 and 1 <= j <= 3:
                fill = "#DDE8F8"
            ax.add_patch(Rectangle((start_x + j * cell, start_y + (4 - i) * cell), cell, cell, facecolor=fill, edgecolor=EDGE, lw=0.8))
    box(ax, 0.72, 3.72, 2.15, 0.48, "输入图像局部区域", YELLOW, fontsize=8.2)
    box(ax, 3.75, 5.18, 1.95, 0.68, "共享卷积核\n3×3", BLUE, fontsize=8.4)
    ortho_arrow(ax, [(2.68, 5.45), (3.75, 5.45)])

    box(ax, 6.72, 5.18, 2.35, 0.68, "加权求和\n+ 非线性激活", GREEN, fontsize=8.4)
    ortho_arrow(ax, [(5.70, 5.52), (6.72, 5.52)])

    ax.text(11.30, 6.92, "特征响应图", fontsize=9.2, color=TEXT, ha="center", fontweight="bold")
    cell2 = 0.34
    sx2, sy2 = 10.55, 4.77
    for i in range(4):
        for j in range(4):
            fill = "#E7F0DA" if (i + j) % 2 == 0 else "#F7F1D8"
            ax.add_patch(Rectangle((sx2 + j * cell2, sy2 + (3 - i) * cell2), cell2, cell2, facecolor=fill, edgecolor=EDGE, lw=0.8))
    ortho_arrow(ax, [(9.07, 5.52), (10.55, 5.52)])
    box(ax, 10.02, 3.66, 2.62, 0.62, "强响应位置\n保留笔画结构", TEAL, fontsize=7.8)

    group(ax, 0.52, 3.30, 12.35, 4.00, "卷积通过局部连接与权值共享提取笔画边缘、交叉和曲率特征", dashed=True)
    save(fig, [ROOT / "实验报告/实验1/figures/principle_cnn_locality"], bounds=(0.34, 2.46, 13.05, 7.45))


def draw_exp2_principle():
    fig, ax = setup_axes()
    box(ax, 0.70, 4.62, 1.90, 0.74, "CIFAR-10 图像\n32×32×3", YELLOW, fontsize=8.2)
    ax.text(3.90, 6.50, "Patch 切分", fontsize=9.2, color=TEXT, ha="center", fontweight="bold")
    sx, sy, c = 3.25, 4.32, 0.34
    for i in range(4):
        for j in range(4):
            fill = [BLUE, GREEN, PEACH, LAVENDER][(i + j) % 4]
            ax.add_patch(Rectangle((sx + j * c, sy + (3 - i) * c), c, c, facecolor=fill, edgecolor=EDGE, lw=0.8))
    ortho_arrow(ax, [(2.60, 4.99), (3.25, 4.99)])

    box(ax, 5.65, 4.62, 2.05, 0.74, "线性投影\nPatch Tokens", BLUE, fontsize=8.3)
    ortho_arrow(ax, [(4.65, 4.99), (5.65, 4.99)])
    box(ax, 8.55, 5.36, 1.52, 0.52, "Class Token", TEAL, fontsize=8.0)
    box(ax, 8.55, 4.10, 1.52, 0.52, "位置编码", GREEN, fontsize=8.0)
    plus_icon(ax, 10.55, 4.99)
    ortho_arrow(ax, [(7.70, 4.99), (10.32, 4.99)])
    ortho_arrow(ax, [(9.31, 5.36), (9.31, 5.18), (10.32, 5.18), (10.32, 5.04)])
    ortho_arrow(ax, [(9.31, 4.62), (9.31, 4.80), (10.32, 4.80), (10.32, 4.94)])

    box(ax, 11.28, 4.62, 2.38, 0.74, "多头自注意力\n全局建模", PEACH, fontsize=8.3)
    ortho_arrow(ax, [(10.78, 4.99), (11.28, 4.99)])
    box(ax, 14.20, 4.62, 1.40, 0.74, "分类\nlogits", LAVENDER, fontsize=8.3)
    ortho_arrow(ax, [(13.66, 4.99), (14.20, 4.99)])
    group(ax, 0.45, 3.48, 15.30, 3.20, "ViT 将二维图像转化为 token 序列，再用自注意力聚合全局上下文", dashed=True)
    save(fig, [ROOT / "实验报告/实验2/figures/principle_vit_patch_attention"], bounds=(0.34, 3.38, 15.85, 6.78))


def draw_exp3_principle():
    fig, ax = setup_axes()
    box(ax, 0.82, 5.34, 1.65, 0.60, "当前输入\nx_t", YELLOW, fontsize=8.3)
    box(ax, 0.82, 3.88, 1.65, 0.60, "上一隐状态\nh_{t-1}", YELLOW, fontsize=8.3)
    box(ax, 3.55, 4.48, 1.72, 0.72, "拼接向量\n[x_t, h_{t-1}]", BLUE, fontsize=8.2)
    ortho_arrow(ax, [(2.47, 5.64), (3.05, 5.64), (3.05, 4.96), (3.55, 4.96)])
    ortho_arrow(ax, [(2.47, 4.18), (3.05, 4.18), (3.05, 4.72), (3.55, 4.72)])

    gates = [
        (6.15, 5.80, "遗忘门\nf_t", PEACH),
        (6.15, 4.80, "输入门\ni_t", GREEN),
        (6.15, 3.80, "候选记忆\nĉ_t", LAVENDER),
        (6.15, 2.80, "输出门\no_t", TEAL),
    ]
    for x, y, label, fill in gates:
        box(ax, x, y, 1.70, 0.58, label, fill, fontsize=8.1)
        ortho_arrow(ax, [(5.27, 4.84), (5.78, 4.84), (5.78, y + 0.29), (x, y + 0.29)])

    box(ax, 9.25, 4.74, 1.95, 0.66, "更新细胞状态\nc_t", BLUE, fontsize=8.2)
    box(ax, 12.20, 4.74, 1.95, 0.66, "输出隐状态\nh_t", GREEN, fontsize=8.2)
    ortho_arrow(ax, [(7.85, 6.09), (8.55, 6.09), (8.55, 5.07), (9.25, 5.07)])
    ortho_arrow(ax, [(7.85, 5.09), (9.25, 5.09)])
    ortho_arrow(ax, [(7.85, 4.09), (8.55, 4.09), (8.55, 4.94), (9.25, 4.94)])
    ortho_arrow(ax, [(11.20, 5.07), (12.20, 5.07)])
    ortho_arrow(ax, [(7.85, 3.09), (11.70, 3.09), (11.70, 4.94), (12.20, 4.94)])

    box(ax, 13.65, 3.42, 1.55, 0.60, "下一字\n概率分布", YELLOW, fontsize=8.2)
    ortho_arrow(ax, [(13.18, 4.74), (13.18, 3.72), (13.65, 3.72)])
    group(ax, 0.50, 2.22, 14.95, 4.62, "LSTM 通过门控机制选择性保留长期上下文并生成下一字符分布", dashed=True)
    save(fig, [ROOT / "实验报告/实验3/figures/principle_lstm_gates"], bounds=(0.35, 2.05, 15.60, 6.95))


def draw_exp2():
    fig, ax = setup_axes()
    box(ax, 0.65, 3.88, 1.65, 0.82, "输入图像\n32×32×3", YELLOW, fontsize=8.8)
    arrow(ax, 2.30, 4.29, 3.15, 4.29)
    box(ax, 3.15, 3.86, 2.0, 0.86, "Patch Embedding\n4×4 → 64 tokens", BLUE, fontsize=8.5)
    plus_icon(ax, 5.80, 4.29)
    arrow(ax, 5.15, 4.29, 5.58, 4.29)
    ax.text(5.80, 3.22, "类别token / 位置向量", fontsize=7.6, ha="center", color=MUTED)
    sine_icon(ax, 5.80, 3.72)
    arrow(ax, 6.02, 4.29, 6.72, 4.29)

    group(ax, 6.72, 1.45, 4.5, 5.7, "Transformer Encoder  N个", dashed=True)
    box(ax, 7.45, 5.85, 3.05, 0.52, "残差连接 & 层归一化", LAVENDER, fontsize=8.4)
    box(ax, 7.45, 5.05, 3.05, 0.52, "多头自注意力", PEACH, fontsize=8.4)
    box(ax, 7.45, 4.25, 3.05, 0.52, "残差连接 & 层归一化", LAVENDER, fontsize=8.4)
    box(ax, 7.45, 3.45, 3.05, 0.52, "前馈神经网络", GREEN, fontsize=8.4)
    box(ax, 7.45, 2.65, 3.05, 0.52, "Class Token 聚合", BLUE, fontsize=8.4)
    for y1, y2 in [(5.85, 5.57), (5.05, 4.77), (4.25, 3.97), (3.45, 3.17)]:
        arrow(ax, 8.98, y1, 8.98, y2)
    line(ax, 7.23, 5.31, 7.23, 4.50)
    arrow(ax, 7.23, 4.50, 7.45, 4.50)
    line(ax, 10.78, 5.31, 10.78, 4.50)
    arrow(ax, 10.78, 4.50, 10.50, 4.50)

    arrow(ax, 11.22, 4.29, 12.0, 4.29)
    box(ax, 12.0, 4.82, 2.15, 0.60, "线性分类头", GRAY, fontsize=8.8)
    arrow(ax, 13.08, 4.82, 13.08, 4.30)
    box(ax, 12.0, 3.70, 2.15, 0.60, "Softmax", TEAL, fontsize=8.8)
    arrow(ax, 13.08, 3.70, 13.08, 3.18)
    box(ax, 12.0, 2.58, 2.15, 0.60, "输出概率\n10类", YELLOW, fontsize=8.6)

    outputs = [
        ROOT / "实验报告/实验2/figures/algorithm_flow_academic",
        ROOT / "code/work2 code/figures/algorithm_flow_academic",
    ]
    save(fig, outputs, bounds=(0.40, 1.25, 14.35, 7.35))


def draw_exp3():
    fig, ax = setup_axes()
    box(ax, 0.70, 4.75, 1.95, 0.72, "唐诗序列\nx1...xt", YELLOW, fontsize=8.8)
    box(ax, 0.70, 2.35, 1.95, 0.72, "起始诗句\n已生成字", YELLOW, fontsize=8.8)
    arrow(ax, 2.65, 5.11, 3.52, 4.36)
    arrow(ax, 2.65, 2.71, 3.52, 3.58)

    box(ax, 3.52, 3.52, 2.0, 0.86, "Embedding\n字向量表示", BLUE, fontsize=8.8)
    arrow(ax, 5.52, 3.95, 6.28, 3.95)

    group(ax, 6.28, 1.62, 3.85, 4.95, "LSTM Stack  N个", dashed=True)
    box(ax, 6.95, 5.28, 2.55, 0.56, "遗忘门 / 输入门 / 输出门", PEACH, fontsize=8.0)
    box(ax, 6.95, 4.44, 2.55, 0.56, "LSTM 层 1", GREEN, fontsize=8.6)
    box(ax, 6.95, 3.60, 2.55, 0.56, "Dropout 正则化", GRAY, fontsize=8.2)
    box(ax, 6.95, 2.76, 2.55, 0.56, "LSTM 层 2", GREEN, fontsize=8.6)
    box(ax, 6.95, 1.92, 2.55, 0.56, "隐状态 h_t", BLUE, fontsize=8.6)
    for y1, y2 in [(5.38, 5.08), (4.52, 4.22), (3.66, 3.36), (2.80, 2.50)]:
        arrow(ax, 8.13, y1, 8.13, y2)

    arrow(ax, 10.13, 3.95, 10.95, 3.95)
    group(ax, 10.95, 2.05, 2.55, 4.35, "输出层")
    box(ax, 11.23, 5.16, 2.0, 0.58, "线性层", GRAY, fontsize=8.7)
    arrow(ax, 12.23, 5.16, 12.23, 4.72)
    box(ax, 11.23, 4.12, 2.0, 0.58, "Softmax", TEAL, fontsize=8.7)
    arrow(ax, 12.23, 4.12, 12.23, 3.68)
    box(ax, 11.23, 3.08, 2.0, 0.58, "温度采样\nTop-k", PEACH, fontsize=8.4)
    arrow(ax, 13.50, 3.37, 14.00, 3.37)
    box(ax, 14.00, 2.97, 1.75, 0.80, "生成下一字\n或诗句", BLUE, fontsize=8.6, bold=True)
    ax.text(13.65, 2.35, "自回归生成时回送输入", fontsize=8.1, color=MUTED, ha="center")

    box(ax, 13.85, 5.35, 1.70, 0.62, "交叉熵损失", LAVENDER, fontsize=8.4)
    arrow(ax, 13.23, 5.45, 13.85, 5.65, dashed=True, rad=0.05)
    ax.text(13.60, 6.20, "训练目标：下一字预测", fontsize=8.2, color=MUTED)

    outputs = [
        ROOT / "实验报告/实验3/figures/algorithm_flow_academic",
        ROOT / "code/work3 code/figures/algorithm_flow_academic",
    ]
    save(fig, outputs, bounds=(0.45, 1.42, 15.95, 6.72))


def draw_exp3_model():
    fig, ax = setup_axes()
    stages = [
        (0.8, "输入索引\nbatch×seq", YELLOW),
        (3.1, "Embedding\n128维", BLUE),
        (5.4, "双层 LSTM\nhidden=256", GREEN),
        (7.9, "Dropout\np=0.3", GRAY),
        (10.1, "Linear\n词表维度", LAVENDER),
        (12.4, "Softmax\n字概率", TEAL),
    ]
    for i, (x, label, fill) in enumerate(stages):
        box(ax, x, 4.12, 1.75, 0.88, label, fill, fontsize=8.7, bold=i in {0, 5})
        if i:
            arrow(ax, stages[i - 1][0] + 1.75, 4.56, x, 4.56)
    group(ax, 5.10, 3.48, 4.65, 2.12, "序列建模核心 ×2", dashed=True)
    box(ax, 12.35, 2.42, 1.85, 0.62, "Top-k / 温度\n采样", PEACH, fontsize=8.2)
    arrow(ax, 13.28, 4.12, 13.28, 3.04)
    save(fig, [ROOT / "实验报告/实验3/figures/model_architecture"], bounds=(0.55, 2.20, 14.45, 5.80))


def main():
    draw_exp1()
    draw_exp1_model()
    draw_exp1_principle()
    draw_exp2_principle()
    draw_exp2()
    draw_exp3_principle()
    draw_exp3()
    draw_exp3_model()


if __name__ == "__main__":
    main()
