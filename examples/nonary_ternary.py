#!/usr/bin/env python3
"""元一 · 最小技术种子：九爻三进制（Nonary Ternary）核心

演示：三态(是/否/变) → 9维向量 → 3^9=19683 状态空间
提供：编码 / 解码 / 状态总数 / 三态自检

用法：
    python3 examples/nonary_ternary.py
"""
from itertools import product

# 三态：是(阳+1) / 变(中和0) / 否(阴-1)
STATES = [+1, 0, -1]
DIM = 9
TOTAL = 3 ** DIM  # 19683

def to_base3(value: int, dim: int = DIM) -> list:
    """状态索引 → 九爻三态向量(上爻→下爻)。value ∈ [0, 3^dim)。"""
    assert 0 <= value < 3 ** dim
    digits = []
    v = value
    for _ in range(dim):
        digits.append(v % 3)
        v //= 3
    # 三进制 digit：0→阴(-1), 1→变(0), 2→阳(+1)
    return [{0: -1, 1: 0, 2: +1}[d] for d in digits]

def from_base3(gua: list) -> int:
    """九爻三态向量 → 状态索引。"""
    assert len(gua) == DIM and all(g in STATES for g in gua)
    idx = 0
    for i, g in enumerate(gua):
        digit = {+1: 2, 0: 1, -1: 0}[g]
        idx += digit * (3 ** i)
    return idx

def selftest() -> None:
    """自检：全部 19683 态 编码/解码 往返一致。"""
    total = 3 ** DIM
    for v in range(total):
        gua = to_base3(v)
        assert from_base3(gua) == v, f"往返不一致 @ {v}"
    print(f"✓ 编码/解码往返自检通过：{total} 个状态全部一致")

def main() -> None:
    print("元一 · 九爻三进制核心（Nonary Ternary）")
    print(f"状态空间：3^{DIM} = {TOTAL}")
    print(f"同维度二进制：2^{DIM} = {2 ** DIM}（比值 ~{TOTAL / (2 ** DIM):.1f}×）")
    print()
    print("示例：状态索引 0 / 19682 的九爻向量：")
    print("  to_base3(0)     =", to_base3(0))
    print("  to_base3(19682) =", to_base3(19682))
    print("  from_base3(逆)   =", from_base3(to_base3(19682)))
    print()
    selftest()
    # 全纯阳(是)/全纯阴(否)/全衡(变)三典型态
    pure_yang = [1] * DIM
    pure_yin = [-1] * DIM
    pure_bian = [0] * DIM
    print("\n典型态索引：纯阳(是)=", from_base3(pure_yang),
          "纯阴(否)=", from_base3(pure_yin),
          "纯变(中)=", from_base3(pure_bian))

if __name__ == "__main__":
    main()
