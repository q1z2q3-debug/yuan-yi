"""
元一 · 九爻三进制内核（Nonary Ternary Core）

第三种计算范式的数学底座：三态(是+1/变0/否-1) × 9维 = 3^9 = 19683 状态空间。

提供：
  - 编码/解码：状态索引 ↔ 9维三态向量（双射，可全空间自检）
  - 度量：欧氏距离 / 逐维张力
  - 结构算子：错(全维相错) / 综(上下颠倒) / 变(单维跃迁) —— 对接 TNE-Core 五算子的核心三算子
  - 邻域检索：单维变易可达的全部邻态
  - 推演：朝目标态的确定性一步推演
"""
from __future__ import annotations
from typing import Dict, List

DIM = 9
STATES = (-1, 0, 1)
TOTAL = 3 ** DIM  # 19683

# 三态语义
STATE_NAMES = {+1: "是(阳)", 0: "变(中和)", -1: "否(阴)"}


def encode(vector: List[int]) -> int:
    """9维三态向量 → 状态索引（三进制位权）。"""
    if len(vector) != DIM or any(g not in STATES for g in vector):
        raise ValueError(f"向量须为 {DIM} 维且每维 ∈ {STATES}")
    idx = 0
    for i, g in enumerate(vector):
        idx += {+1: 2, 0: 1, -1: 0}[g] * (3 ** i)
    return idx


def decode(index: int, dim: int = DIM) -> List[int]:
    """状态索引 → 9维三态向量（下爻在前）。"""
    if not 0 <= index < 3 ** dim:
        raise ValueError(f"索引须 ∈ [0, {3 ** dim})")
    digits, v = [], index
    for _ in range(dim):
        digits.append(v % 3)
        v //= 3
    return [{0: -1, 1: 0, 2: +1}[d] for d in digits]


def distance(a: List[int], b: List[int]) -> float:
    """两认知态的欧氏距离（最大 2√9 = 6）。"""
    return float(sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5)


def tension(current: List[int], target: List[int]) -> List[Dict]:
    """逐维张力：各维偏差方向与强度，按强度降序。张力=变易的驱动力。"""
    items = [
        {"dim": i, "delta": t - c, "strength": abs(t - c) / 2.0,
         "from": STATE_NAMES[c], "to": STATE_NAMES[t]}
        for i, (c, t) in enumerate(zip(current, target)) if c != t
    ]
    items.sort(key=lambda x: -x["strength"])
    return items


# ── 结构算子（认知推演的形式化变换） ──────────────────────────────

def cuo(vector: List[int]) -> List[int]:
    """错：全维阴阳相错（+1↔-1，0 不变）。对立视角推演。"""
    return [-g for g in vector]


def zong(vector: List[int]) -> List[int]:
    """综：上下颠倒（向量逆序）。反向视角推演。"""
    return list(reversed(vector))


def bian(vector: List[int], dim: int) -> List[int]:
    """变：指定一维向对立态跃迁（+1↔-1；0 由中和转向生发 +1）。变易推演。"""
    if not 0 <= dim < len(vector):
        raise ValueError(f"维度须 ∈ [0, {len(vector)})")
    v = list(vector)
    v[dim] = -v[dim] if v[dim] != 0 else +1
    return v


def neighbors(vector: List[int]) -> List[List[int]]:
    """邻域检索：单维变易可达的全部邻态（每维至多 2 个，共 ≤18 个）。"""
    out = []
    for i, g in enumerate(vector):
        for ng in (g - 1, g + 1):
            if ng in STATES:
                v = list(vector)
                v[i] = ng
                out.append(v)
    return out


def step_toward(current: List[int], target: List[int], dims: int = 1) -> List[int]:
    """认知推演：朝目标态确定性走一步（修正张力最大的 dims 维）。"""
    v = list(current)
    for item in tension(current, target)[:dims]:
        i, d = item["dim"], item["delta"]
        v[i] += 1 if d > 0 else -1
    return v
