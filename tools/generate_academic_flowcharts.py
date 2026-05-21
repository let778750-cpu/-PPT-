from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle


ROOT = Path(__file__).resolve().parents[1]

BOX_FILL = "#F8FAFC"
BOX_EDGE = "#334155"
ACCENT = "#2563EB"
TEXT = "#0F172A"
MUTED = "#475569"
ARROW = "#64748B"


CHARTS = {
    "exp1": {
        "stages": [
            ("数据来源", "MNIST 本地数据\n60k train / 10k test"),
            ("预处理", "张量转换、归一化\nDataLoader 批处理"),
            ("模型前向", "两层卷积特征提取\n全连接分类器"),
            ("参数学习", "交叉熵损失\nAdamW 反向更新"),
            ("独立评估", "测试集 loss / acc\n保存最佳权重"),
            ("结果归档", "训练曲线\n混淆矩阵与日志"),
        ],
        "outputs": [
            "实验报告/实验1/figures/algorithm_flow_20260426_vector",
            "实验报告/实验1/figures/algorithm_flow_academic",
            "code/work1 code/figures/algorithm_flow_academic",
        ],
    },
    "exp2": {
        "stages": [
            ("数据来源", "CIFAR-10 本地数据\n50k train / 10k test"),
            ("图像编码", "增强、4×4 patch\n位置编码与 token"),
            ("ViT 主干", "Transformer Encoder\nMSA + MLP blocks"),
            ("训练优化", "CE + AdamW\nCosine LR 调度"),
            ("验证复评", "测试准确率\n选择 best checkpoint"),
            ("结果归档", "训练历史 JSON\nloss / acc / lr 曲线"),
        ],
        "outputs": [
            "实验报告/实验2/figures/algorithm_flow_academic",
            "code/work2 code/figures/algorithm_flow_academic",
        ],
    },
    "exp3": {
        "stages": [
            ("语料输入", "tang.npz 唐诗语料\n57,580 首诗"),
            ("序列样本", "字表映射\nx[0:124] → x[1:125]"),
            ("LSTM 建模", "Embedding + 2-layer LSTM\nDropout 正则化"),
            ("训练优化", "CE + Adam\n学习率调度与梯度裁剪"),
            ("文本生成", "温度采样\n续写诗与藏头诗"),
            ("结果归档", "best checkpoint\nloss 曲线与示例"),
        ],
        "outputs": [
            "实验报告/实验3/figures/algorithm_flow_academic",
            "实验报告和PPT（新）/实验3/figures/algorithm_flow_academic",
            "code/work3 code/figures/algorithm_flow_academic",
        ],
    },
    "exp4": {
        "stages": [
            ("平行语料", "NiuTrans 中英语料\n约 10 万句对"),
            ("文本预处理", "词表构建、padding\n源端/目标端 mask"),
            ("翻译模型", "Transformer Enc-Dec\nMHA + FFN ×3"),
            ("训练优化", "Label smoothing CE\nAdam 与学习率调度"),
            ("解码评估", "Beam Search 译文生成\nBLEU4 自动评测"),
            ("结果归档", "test BLEU4 = 25.84\n曲线与指标表"),
        ],
        "outputs": [
            "实验报告/实验4/figures/algorithm_flow_academic",
            "code/work4 code/figures/algorithm_flow_academic",
        ],
    },
    "exp6": {
        "stages": [
            ("数据来源", "CamVid Tiny 子集\n100 组图像/标签"),
            ("像素标注", "128×96 resize\n70/15/15 固定划分"),
            ("SegNet 主干", "Encoder-Decoder\npool indices / unpool"),
            ("训练优化", "像素级 CE\nAdamW 小规模验证"),
            ("测试评估", "PA / MPA / mIoU\n独立 test split"),
            ("结果归档", "曲线、样例预测\n来源与哈希记录"),
        ],
        "outputs": [
            "实验报告/实验6/figures/algorithm_flow_academic",
            "code/work6 code/figures/algorithm_flow_academic",
        ],
    },
    "exp7": {
        "stages": [
            ("语料输入", "PTB simple-examples\ntrain / valid / test"),
            ("序列批处理", "10k 词表\nbatchify + BPTT=35"),
            ("语言模型", "Embedding + 2-layer LSTM\nweight tying"),
            ("训练优化", "SGD + LR decay\nDropout 与梯度裁剪"),
            ("模型选择", "valid PPL 最低\n保存 best checkpoint"),
            ("独立测试", "加载最佳权重\ntest PPL = 75.77"),
        ],
        "outputs": [
            "实验报告/实验7/figures/algorithm_flow",
            "实验报告/实验7/figures/algorithm_flow_academic",
            "code/work7 code/figures/algorithm_flow",
            "code/work7 code/figures/algorithm_flow_academic",
        ],
    },
}


POSITIONS = [
    (1.45, 4.25),
    (4.80, 4.25),
    (8.15, 4.25),
    (8.15, 1.75),
    (4.80, 1.75),
    (1.45, 1.75),
]


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


def add_stage(ax, idx: int, x: float, y: float, title: str, subtitle: str) -> None:
    width = 2.38
    height = 1.08
    box = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.035,rounding_size=0.035",
        linewidth=1.25,
        edgecolor=BOX_EDGE,
        facecolor=BOX_FILL,
        zorder=3,
    )
    ax.add_patch(box)

    circle = Circle((x - width / 2 + 0.28, y + height / 2 - 0.25), 0.16, facecolor=ACCENT, edgecolor=ACCENT, zorder=4)
    ax.add_patch(circle)
    ax.text(
        x - width / 2 + 0.28,
        y + height / 2 - 0.25,
        str(idx + 1),
        ha="center",
        va="center",
        fontsize=7.2,
        color="white",
        fontweight="bold",
        zorder=5,
    )
    ax.text(
        x,
        y + 0.14,
        title,
        ha="center",
        va="center",
        fontsize=10.2,
        color=TEXT,
        fontweight="bold",
        zorder=5,
    )
    ax.text(
        x,
        y - 0.20,
        subtitle,
        ha="center",
        va="center",
        fontsize=7.5,
        color=MUTED,
        linespacing=1.35,
        zorder=5,
    )


def add_arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=11.5,
        lw=1.25,
        color=ARROW,
        shrinkA=2,
        shrinkB=2,
        zorder=2,
    )
    ax.add_patch(patch)


def draw_chart(chart: dict[str, object], outbase: Path) -> None:
    setup_fonts()
    fig, ax = plt.subplots(figsize=(9.6, 4.25), constrained_layout=False)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0.05, 9.55)
    ax.set_ylim(0.95, 4.95)
    ax.set_position([0, 0, 1, 1])
    ax.axis("off")

    for i, (title, subtitle) in enumerate(chart["stages"]):
        add_stage(ax, i, *POSITIONS[i], title, subtitle)

    w = 2.38
    h = 1.08
    add_arrow(ax, (POSITIONS[0][0] + w / 2 + 0.08, POSITIONS[0][1]), (POSITIONS[1][0] - w / 2 - 0.08, POSITIONS[1][1]))
    add_arrow(ax, (POSITIONS[1][0] + w / 2 + 0.08, POSITIONS[1][1]), (POSITIONS[2][0] - w / 2 - 0.08, POSITIONS[2][1]))
    add_arrow(ax, (POSITIONS[2][0], POSITIONS[2][1] - h / 2 - 0.08), (POSITIONS[3][0], POSITIONS[3][1] + h / 2 + 0.08))
    add_arrow(ax, (POSITIONS[3][0] - w / 2 - 0.08, POSITIONS[3][1]), (POSITIONS[4][0] + w / 2 + 0.08, POSITIONS[4][1]))
    add_arrow(ax, (POSITIONS[4][0] - w / 2 - 0.08, POSITIONS[4][1]), (POSITIONS[5][0] + w / 2 + 0.08, POSITIONS[5][1]))

    outbase.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outbase.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(outbase.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(outbase.with_suffix(".png"), dpi=260, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def main() -> None:
    requested = set(sys.argv[1:]) if len(sys.argv) > 1 else set(CHARTS)
    unknown = requested.difference(CHARTS)
    if unknown:
        raise SystemExit(f"Unknown chart keys: {', '.join(sorted(unknown))}")
    for key, chart in CHARTS.items():
        if key not in requested:
            continue
        for output in chart["outputs"]:
            draw_chart(chart, ROOT / output)


if __name__ == "__main__":
    main()
