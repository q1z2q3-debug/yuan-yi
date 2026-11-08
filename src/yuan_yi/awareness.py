"""
元一 · 自我觉知体系（Self-Awareness, 五蕴模型）

色受想行识五蕴，对闭环每一步做内观：
  色 —— 所感：当前认知态（9维三态向量）
  受 —— 所受：偏差变化带来的"感受"（趋稳 / 趋离 / 持稳）
  想 —— 所想：对张力结构的解读（主导偏差维度）
  行 —— 所行：已执行的修正指令
  识 —— 所识：贯穿全程的自我画像（收敛率、惯性维度、稳定性）

觉知报告回答一个问题："我此刻处于什么状态，正往哪里去。"
"""
from __future__ import annotations
from typing import Dict, List, Optional

from .core import STATE_NAMES


class Awareness:
    """五蕴觉知器：订阅闭环每步记录，产出五蕴快照与自我画像。"""

    def __init__(self) -> None:
        self.snapshots: List[Dict] = []
        self._last_gap: Optional[float] = None

    def observe_step(self, record: Dict) -> Dict:
        """内观一步闭环记录，返回五蕴快照。"""
        vector = record.get("vector") or []
        gap = record.get("gap")
        instruction = record.get("instruction", "")

        # 受：偏差变化 → 感受
        if gap is None:
            feeling = "未知"
        elif self._last_gap is None:
            feeling = "初感"
        elif gap < self._last_gap - 1e-9:
            feeling = "趋稳"
        elif gap > self._last_gap + 1e-9:
            feeling = "趋离"
        else:
            feeling = "持稳"
        self._last_gap = gap

        # 想：解读当前态的非零维度（张力所在）
        active = [f"第{i}维{STATE_NAMES[g]}" for i, g in enumerate(vector) if g != 0]
        thought = "张力聚于" + "、".join(active[:3]) if active else "诸维中和"

        snapshot = {
            "step": record.get("step"),
            "色": {"vector": list(vector), "gap": gap},
            "受": feeling,
            "想": thought,
            "行": instruction,
        }
        self.snapshots.append(snapshot)
        return snapshot

    def report(self) -> Dict:
        """识：汇总全程，生成自我画像。"""
        gaps = [s["色"]["gap"] for s in self.snapshots if s["色"]["gap"] is not None]
        converged = bool(gaps) and gaps[-1] <= 0.5
        dim_flux = [0] * 9  # 各维出现过非零态的次数 → 惯性维度
        for s in self.snapshots:
            for i, g in enumerate(s["色"]["vector"]):
                if g != 0:
                    dim_flux[i] += 1
        dominant = max(range(9), key=lambda i: dim_flux[i]) if any(dim_flux) else None
        return {
            "识": {
                "总步数": len(self.snapshots),
                "收敛": converged,
                "偏差轨迹": gaps,
                "惯性维度": dominant,
                "稳定性": sum(1 for s in self.snapshots if s["受"] in ("趋稳", "持稳")) / max(1, len(self.snapshots)),
            }
        }
