"""
元一 · 深度逻辑推理（Deep Reasoning）

思维链（CoT）+ 螺旋融合，全程确定性、逐步可审计：
  思维链 —— 从当前认知态到目标态的逐步变易链：
            每步锁定张力最大的一维（推理焦点），变易一次，记录残差变化
  螺旋融合 —— 多目标/多视角冲突下，先逐维加权投票融合出"共识目标"，
             再走思维链逼近；投票→量化→逼近→审计，即一轮螺旋

典型用法：
    from yuan_yi.reasoning import Reasoner
    r = Reasoner()
    r.think(current, target)                        # 单目标思维链
    r.spiral_fuse(current, [(t1, 0.7), (t2, 0.3)])  # 多目标融合决策
"""
from __future__ import annotations
from typing import Dict, List, Sequence, Tuple

from .core import DIM, distance, step_toward, tension


class Reasoner:
    """张力驱动的深度逻辑推理器。"""

    def __init__(self, max_depth: int = 2 * DIM):
        # 最远两态（纯阴→纯阳）需 2 步/维 × 9 维 = 18 步
        self.max_depth = max_depth

    def think(self, current: List[int], target: List[int]) -> Dict:
        """思维链：逐步变易逼近目标，返回可审计的推演轨迹。"""
        v = list(current)
        chain = [list(v)]
        steps = []
        for _ in range(self.max_depth):
            if v == list(target):
                break
            focus = tension(v, target)[0]  # 张力最大维 = 本步推理焦点
            v = step_toward(v, target)
            steps.append({
                "focus_dim": focus["dim"],
                "change": f"第{focus['dim']}维 {focus['from']} → {focus['to']}",
                "residual": round(distance(v, target), 4),
            })
            chain.append(list(v))
        return {
            "start": list(current), "target": list(target),
            "chain": chain, "steps": steps,
            "depth": len(steps), "converged": v == list(target),
            "audit": self._audit(chain, target),
        }

    @staticmethod
    def fuse_targets(weighted_targets: Sequence[Tuple[List[int], float]]) -> List[int]:
        """多目标加权融合 → 共识目标：逐维投票，均值超 ±1/3 阈才定态，否则持"变"。"""
        if not weighted_targets:
            raise ValueError("至少需要一个目标")
        total_w = float(sum(w for _, w in weighted_targets))
        fused = []
        for d in range(DIM):
            s = sum(w * t[d] for t, w in weighted_targets) / total_w
            fused.append(1 if s > 1 / 3 else (-1 if s < -1 / 3 else 0))
        return fused

    def spiral_fuse(self, current: List[int],
                    weighted_targets: Sequence[Tuple[List[int], float]]) -> Dict:
        """螺旋融合决策：加权投票出共识目标 → 思维链逼近 → 残差审计。"""
        fused = self.fuse_targets(weighted_targets)
        cot = self.think(current, fused)
        return {**cot, "fused_target": fused,
                "votes": [(list(t), w) for t, w in weighted_targets]}

    @staticmethod
    def _audit(chain: List[List[int]], target: List[int]) -> Dict:
        """审计推演链：残差单调不增（变易算子保证每步平方残差恰减 1）。"""
        residuals = [distance(v, target) for v in chain]  # 全精度，审计不舍入
        return {"residuals": residuals,
                "monotonic": all(b <= a + 1e-9 for a, b in zip(residuals, residuals[1:]))}
