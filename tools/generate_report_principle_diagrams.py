from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch


ROOT = Path(__file__).resolve().parents[1]

TEXT = "#0F172A"
MUTED = "#475569"
EDGE = "#94A3B8"
ARROW = "#64748B"
BLUE = "#DBEAFE"
GREEN = "#DCFCE7"
AMBER = "#FEF3C7"
ORANGE = "#FFEDD5"
PURPLE = "#EDE9FE"
CYAN = "#CFFAFE"
PINK = "#FCE7F3"


def setup_fonts() -> None:
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


def add_box(ax, x, y, w, h, title, body="", fill=BLUE, fontsize=9.5, body_size=7.3, lw=1.15):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.035,rounding_size=0.045",
        linewidth=lw,
        edgecolor=EDGE,
        facecolor=fill,
        zorder=3,
    )
    ax.add_patch(box)
    if body:
        ax.text(x + w / 2, y + h * 0.60, title, ha="center", va="center", fontsize=fontsize, color=TEXT, fontweight="bold", zorder=4)
        ax.text(x + w / 2, y + h * 0.30, body, ha="center", va="center", fontsize=body_size, color=MUTED, linespacing=1.24, zorder=4)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fontsize, color=TEXT, fontweight="bold", zorder=4)
    return (x, y, w, h)


def add_panel(ax, x, y, w, h, title):
    panel = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.05,rounding_size=0.10",
        linewidth=1.05,
        edgecolor="#CBD5E1",
        facecolor="#FFFFFF",
        zorder=1,
    )
    ax.add_patch(panel)
    ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center", fontsize=10.5, color=TEXT, fontweight="bold", zorder=4)


def arrow(ax, start, end, lw=1.1, color=ARROW, dashed=False):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=10.5,
        lw=lw,
        color=color,
        linestyle="--" if dashed else "-",
        shrinkA=1,
        shrinkB=1,
        zorder=2,
    )
    ax.add_patch(patch)


def poly_arrow(ax, points, lw=1.1, color=ARROW, dashed=False):
    for a, b in zip(points[:-2], points[1:-1]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=lw, linestyle="--" if dashed else "-", zorder=2)
    arrow(ax, points[-2], points[-1], lw=lw, color=color, dashed=dashed)


def save(fig, bases: list[Path]) -> None:
    for base in bases:
        base.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
        fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.02)
        fig.savefig(base.with_suffix(".png"), dpi=260, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def transformer_principle() -> None:
    setup_fonts()
    fig, ax = plt.subplots(figsize=(9.6, 5.25), constrained_layout=False)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0.0, 12.0)
    ax.set_ylim(0.0, 6.3)
    ax.set_position([0, 0, 1, 1])
    ax.axis("off")

    add_panel(ax, 0.55, 0.65, 4.85, 5.05, "编码器 Encoder")
    add_panel(ax, 6.60, 0.65, 4.85, 5.05, "解码器 Decoder")
    ax.plot([6.0, 6.0], [0.55, 5.85], color="#CBD5E1", lw=1.1, linestyle="--", zorder=1)

    enc_boxes = [
        add_box(ax, 1.35, 1.00, 3.25, 0.58, "源词嵌入 + 位置编码", "source embedding + PE", AMBER),
        add_box(ax, 1.35, 1.92, 3.25, 0.58, "多头自注意力", "Multi-Head Self-Attention", BLUE),
        add_box(ax, 1.35, 2.84, 3.25, 0.58, "残差连接 + 层归一化", "Add & LayerNorm", PURPLE),
        add_box(ax, 1.35, 3.76, 3.25, 0.58, "位置前馈网络", "Position-wise FFN", GREEN),
        add_box(ax, 1.35, 4.68, 3.25, 0.58, "编码记忆表示", "encoder memory", CYAN),
    ]
    dec_boxes = [
        add_box(ax, 7.40, 1.00, 3.25, 0.58, "目标词嵌入 + 位置编码", "shifted target + PE", AMBER),
        add_box(ax, 7.40, 1.92, 3.25, 0.58, "掩码多头自注意力", "masked self-attention", BLUE),
        add_box(ax, 7.40, 2.84, 3.25, 0.58, "编码器-解码器注意力", "query attends to memory", ORANGE),
        add_box(ax, 7.40, 3.76, 3.25, 0.58, "位置前馈网络", "Position-wise FFN", GREEN),
        add_box(ax, 7.40, 4.68, 3.25, 0.58, "线性层 + Softmax", "target-token distribution", CYAN),
    ]
    for boxes in (enc_boxes, dec_boxes):
        for lower, upper in zip(boxes[:-1], boxes[1:]):
            arrow(ax, (lower[0] + lower[2] / 2, lower[1] + lower[3] + 0.04), (upper[0] + upper[2] / 2, upper[1] - 0.04))

    poly_arrow(ax, [(4.65, 4.97), (5.55, 4.97), (5.55, 3.13), (7.34, 3.13)], color="#94A3B8")
    ax.text(6.10, 3.30, "编码记忆\n作为 K,V", ha="center", va="bottom", fontsize=7.5, color=MUTED)
    ax.text(3.0, 0.38, "源端输入", ha="center", va="center", fontsize=9, color=MUTED)
    ax.text(9.02, 0.38, "已生成目标端", ha="center", va="center", fontsize=9, color=MUTED)
    ax.text(9.02, 5.94, "输出概率", ha="center", va="center", fontsize=9, color=MUTED)

    save(
        fig,
        [
            ROOT / "实验报告/实验4/figures/principle_transformer_architecture",
            ROOT / "code/work4 code/figures/principle_transformer_architecture",
        ],
    )


def segnet_structure() -> None:
    setup_fonts()
    fig, ax = plt.subplots(figsize=(8.9, 4.65), constrained_layout=False)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0.0, 10.2)
    ax.set_ylim(0.0, 5.8)
    ax.set_position([0, 0, 1, 1])
    ax.axis("off")

    ax.text(5.1, 5.35, "SegNet 编码器--解码器结构", ha="center", va="center", fontsize=11.0, color=TEXT, fontweight="bold")
    ax.text(5.1, 5.04, "编码阶段保存最大池化索引，解码阶段用反池化恢复空间位置", ha="center", va="center", fontsize=8.2, color=MUTED)

    top = [
        add_box(ax, 0.55, 3.55, 1.25, 0.74, "输入图像", "3×128×96", AMBER, 8.6),
        add_box(ax, 2.25, 3.55, 1.35, 0.74, "编码块1", "Conv+Pool\n32通道", GREEN, 8.6),
        add_box(ax, 4.00, 3.55, 1.35, 0.74, "编码块2", "Conv+Pool\n64通道", GREEN, 8.6),
        add_box(ax, 5.75, 3.55, 1.35, 0.74, "编码块3", "Conv+Pool\n128通道", GREEN, 8.6),
        add_box(ax, 7.50, 3.55, 1.45, 0.74, "瓶颈特征", "低分辨率语义", CYAN, 8.6),
    ]
    bottom = [
        add_box(ax, 7.50, 1.25, 1.45, 0.74, "解码块3", "MaxUnpool\n128通道", BLUE, 8.6),
        add_box(ax, 5.75, 1.25, 1.35, 0.74, "解码块2", "MaxUnpool\n64通道", BLUE, 8.6),
        add_box(ax, 4.00, 1.25, 1.35, 0.74, "解码块1", "MaxUnpool\n32通道", BLUE, 8.6),
        add_box(ax, 2.25, 1.25, 1.35, 0.74, "像素分类", "1×1 Conv\n32类 logits", ORANGE, 8.4, 6.7),
        add_box(ax, 0.55, 1.25, 1.25, 0.74, "分割结果", "H×W map", PINK, 8.6),
    ]
    for a, b in zip(top[:-1], top[1:]):
        arrow(ax, (a[0] + a[2] + 0.05, a[1] + a[3] / 2), (b[0] - 0.05, b[1] + b[3] / 2))
    poly_arrow(ax, [(8.22, 3.50), (8.22, 2.68), (8.22, 2.04)])
    for a, b in zip(bottom[:-1], bottom[1:]):
        arrow(ax, (a[0] - 0.05, a[1] + a[3] / 2), (b[0] + b[2] + 0.05, b[1] + b[3] / 2))

    index_pairs = [(2.92, 4.42), (4.67, 5.42), (6.42, 7.50)]
    for x_enc, x_dec in index_pairs:
        poly_arrow(ax, [(x_enc, 3.50), (x_enc, 2.72), (x_dec, 2.72), (x_dec, 2.04)], color="#94A3B8", dashed=True)
    ax.text(5.10, 2.96, "池化索引传递", ha="center", va="center", fontsize=8.0, color=MUTED)
    ax.text(5.10, 0.58, "相较直接上采样，池化索引为边界恢复提供位置线索", ha="center", va="center", fontsize=8.3, color=MUTED)

    save(
        fig,
        [
            ROOT / "实验报告/实验6/figures/model_structure",
            ROOT / "code/work6 code/figures/model_structure",
        ],
    )


def lstm_gates() -> None:
    setup_fonts()
    fig, ax = plt.subplots(figsize=(9.4, 4.6), constrained_layout=False)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0.0, 11.0)
    ax.set_ylim(0.0, 5.6)
    ax.set_position([0, 0, 1, 1])
    ax.axis("off")

    add_box(ax, 0.55, 2.30, 1.55, 0.72, "当前输入", "$x_t$", AMBER)
    add_box(ax, 0.55, 1.18, 1.55, 0.72, "上一隐藏态", "$h_{t-1}$", AMBER)
    add_box(ax, 2.65, 1.74, 1.75, 0.82, "拼接特征", "$[x_t, h_{t-1}]$", CYAN)

    gates = [
        add_box(ax, 5.00, 3.84, 1.70, 0.70, "遗忘门", "$f_t=\\sigma(\\cdot)$", BLUE),
        add_box(ax, 5.00, 2.78, 1.70, 0.70, "输入门", "$i_t=\\sigma(\\cdot)$", GREEN),
        add_box(ax, 5.00, 1.72, 1.70, 0.70, "候选记忆", "$\\tilde{c}_t=\\tanh(\\cdot)$", ORANGE),
        add_box(ax, 5.00, 0.66, 1.70, 0.70, "输出门", "$o_t=\\sigma(\\cdot)$", PURPLE),
    ]
    add_box(ax, 8.15, 3.84, 1.65, 0.70, "上一细胞态", "$c_{t-1}$", AMBER)
    add_box(ax, 8.15, 2.42, 1.90, 0.82, "细胞状态更新", "$c_t=f_t\\odot c_{t-1}+i_t\\odot\\tilde{c}_t$", PINK, 8.8, 6.8)
    add_box(ax, 8.15, 0.88, 1.90, 0.82, "当前隐藏态", "$h_t=o_t\\odot\\tanh(c_t)$", CYAN, 8.8, 6.8)

    poly_arrow(ax, [(2.10, 2.66), (2.36, 2.66), (2.36, 2.26), (2.60, 2.26)])
    poly_arrow(ax, [(2.10, 1.54), (2.36, 1.54), (2.36, 2.04), (2.60, 2.04)])
    for gate in gates:
        poly_arrow(ax, [(4.45, 2.15), (4.72, 2.15), (4.72, gate[1] + gate[3] / 2), (gate[0] - 0.06, gate[1] + gate[3] / 2)], dashed=True)
    poly_arrow(ax, [(6.76, 4.19), (7.42, 4.19), (7.42, 2.92), (8.10, 2.92)])
    poly_arrow(ax, [(6.76, 3.13), (7.26, 3.13), (7.26, 2.78), (8.10, 2.78)])
    poly_arrow(ax, [(6.76, 2.07), (7.10, 2.07), (7.10, 2.61), (8.10, 2.61)])
    arrow(ax, (8.98, 3.80), (8.98, 3.28))
    poly_arrow(ax, [(9.10, 2.38), (9.10, 2.04), (9.10, 1.74)])
    poly_arrow(ax, [(6.76, 1.01), (7.22, 1.01), (7.22, 1.29), (8.10, 1.29)])

    ax.text(5.85, 5.05, "LSTM 通过门控选择性保留、写入和输出记忆", ha="center", va="center", fontsize=10.0, color=TEXT, fontweight="bold")
    ax.text(5.85, 4.78, "所有连线表示信息流向，训练时沿时间展开并通过 BPTT 更新参数", ha="center", va="center", fontsize=8.2, color=MUTED)

    save(
        fig,
        [
            ROOT / "实验报告/实验7/figures/principle_lstm_gates",
            ROOT / "code/work7 code/figures/principle_lstm_gates",
        ],
    )


def lstm_model_structure() -> None:
    setup_fonts()
    fig, ax = plt.subplots(figsize=(9.6, 2.85), constrained_layout=False)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0.0, 11.4)
    ax.set_ylim(0.0, 3.3)
    ax.set_position([0, 0, 1, 1])
    ax.axis("off")

    boxes = [
        add_box(ax, 0.35, 1.25, 1.25, 0.72, "Token IDs", "$[T,B]$", AMBER, 8.5),
        add_box(ax, 2.00, 1.25, 1.45, 0.72, "词嵌入", "10000×650", GREEN, 8.8),
        add_box(ax, 3.85, 1.25, 1.50, 0.72, "LSTM 第1层", "hidden=650", BLUE, 8.8),
        add_box(ax, 5.75, 1.25, 1.50, 0.72, "LSTM 第2层", "hidden=650", BLUE, 8.8),
        add_box(ax, 7.65, 1.25, 1.35, 0.72, "Dropout", "p=0.5", PURPLE, 8.8),
        add_box(ax, 9.35, 1.25, 1.65, 0.72, "线性层 + Softmax", "650→10000", ORANGE, 8.4),
    ]
    for a, b in zip(boxes[:-1], boxes[1:]):
        arrow(ax, (a[0] + a[2] + 0.06, a[1] + a[3] / 2), (b[0] - 0.06, b[1] + b[3] / 2))
    arrow(ax, (10.18, 1.20), (10.18, 0.58))
    add_box(ax, 9.46, 0.05, 1.45, 0.50, "PPL 评估", "exp(loss)", CYAN, 8.3, 6.7)

    ax.plot([2.73, 10.18], [2.52, 2.52], color="#94A3B8", lw=1.0, linestyle="--", zorder=2)
    arrow(ax, (2.73, 2.01), (2.73, 2.50), color="#94A3B8", dashed=True)
    arrow(ax, (10.18, 2.50), (10.18, 2.01), color="#94A3B8", dashed=True)
    ax.text(6.45, 2.78, "embedding / decoder 权重绑定以减少参数并改善泛化", ha="center", va="center", fontsize=8.0, color=MUTED)

    save(
        fig,
        [
            ROOT / "实验报告/实验7/figures/model_structure",
            ROOT / "code/work7 code/figures/model_structure",
        ],
    )


def main() -> None:
    transformer_principle()
    segnet_structure()
    lstm_gates()
    lstm_model_structure()


if __name__ == "__main__":
    main()
