"""
元一 · 文明创造引擎 MVP（Civilization Creation）

从已有思维晶体出发，做两件"创造"：
  知识空白识别 —— 统计晶体在 19683 空间中的分布，找出覆盖最稀疏的
                 维度/区域（未探索的认知空白）
  理论归纳生成 —— 在晶体间寻找对称/守恒/渐进等不变结构，
                 将不变性陈述为一条可检验的"理论命题"

创造的定义：发现空白 + 提出假说。验证交给后续的闭环实验（自验证）。
"""
from __future__ import annotations
from typing import Dict, List

from .core import DIM, cuo, encode, step_toward, tension


class CreationEngine:
    """基于思维晶体的空白识别与理论生成。"""

    def find_gaps(self, crystals: List, top_k: int = 3) -> List[Dict]:
        """识别知识空白：晶体分布最稀疏的维度，以及尚无晶体的结构性区域。"""
        gaps = []
        if not crystals:
            return [{"type": "全域空白", "detail": "尚无思维晶体，全空间待探索"}]
        # 维度覆盖度：各维在晶体中非零的次数
        coverage = [0] * DIM
        for c in crystals:
            for d, g in enumerate(c.vector):
                if g != 0:
                    coverage[d] += 1
        ranked = sorted(range(DIM), key=lambda d: coverage[d])
        for d in ranked[:top_k]:
            gaps.append({"type": "维度空白", "dim": d,
                         "detail": f"第{d}维仅 {coverage[d]}/{len(crystals)} 颗晶体涉及"})
        # 结构区域：任一维度的三态符号是否从未被探索
        for d in range(DIM):
            for g in (-1, 0, 1):
                if all(c.vector[d] != g for c in crystals):
                    gaps.append({"type": "区域空白", "dim": d,
                                 "detail": f"第{d}维从未出现过「{g}」态"})
        return gaps[:top_k + DIM] if len(gaps) > top_k else gaps

    def induce(self, crystals: List) -> List[Dict]:
        """理论生成：从晶体集合归纳不变性命题。"""
        theories = []
        vecs = [c.vector for c in crystals]
        if len(vecs) < 2:
            return theories
        # 守恒命题：某维在所有晶体中恒定
        for d in range(DIM):
            vals = {v[d] for v in vecs}
            if len(vals) == 1:
                theories.append({"type": "守恒",
                                 "proposition": f"第{d}维恒为 {vals.pop()}（{len(vecs)} 颗晶体无一例外）",
                                 "evidence": len(vecs)})
        # 对称命题：存在互错（cuo）晶体对
        idx = {encode(v) for v in vecs}
        for v in vecs:
            if encode(cuo(v)) in idx:
                theories.append({"type": "对称",
                                 "proposition": "存在互错晶体对：认知结构呈阴阳对称",
                                 "evidence": 2})
                break
        # 渐进命题：晶体间存在"一步可达"的变易链（演化路径）
        for i, a in enumerate(vecs):
            for b in vecs[i + 1:]:
                if step_toward(a, b) == b or (len(tension(a, b)) == 1):
                    theories.append({"type": "渐进",
                                     "proposition": "晶体间存在单维变易链：知识可逐级演化",
                                     "evidence": 2})
                    return theories  # 各类型至多一条，避免重复
        return theories
