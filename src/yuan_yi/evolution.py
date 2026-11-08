"""
元一 · 自主进化引擎 MVP（Evolution Engine）

从闭环历史中学习，自调节执行参数——自编程的最小可行形态：
  停滞检测 —— 偏差连续多步不降 → 增大修正步长（自我强化）
  振荡检测 —— 偏差上下往复 → 减小修正步长（自我收敛）
  经验固化 —— 收敛路径写入层级记忆（自我获取的沉淀）

每轮运行结束产出一次"代际"：参数即基因，历史即选择压力。
"""
from __future__ import annotations
from typing import Dict, List, Optional


class EvolutionEngine:
    """依据 PDFC 闭环历史调节执行参数的进化引擎。"""

    def __init__(self, stagnation_window: int = 3, grow: float = 1.5, shrink: float = 0.7,
                 min_step: float = 0.2, max_step: float = 4.0):
        self.stagnation_window = stagnation_window
        self.grow = grow
        self.shrink = shrink
        self.min_step = min_step
        self.max_step = max_step
        self.generation = 0

    @staticmethod
    def _gaps(history: List[Dict]) -> List[float]:
        return [r["gap"] for r in history if r.get("gap") is not None]

    def diagnose(self, history: List[Dict]) -> str:
        """诊断运行历史：收敛 / 停滞 / 振荡 / 探索中。"""
        gaps = self._gaps(history)
        if len(gaps) < 2:
            return "探索中"
        tail = gaps[-self.stagnation_window:]
        if len(tail) >= self.stagnation_window and len(set(tail)) == 1:
            return "停滞"
        ups = sum(1 for a, b in zip(gaps, gaps[1:]) if b > a)
        if ups >= max(2, len(gaps) // 2):
            return "振荡"
        if gaps[-1] < gaps[0]:
            return "收敛"
        return "探索中"

    def evolve(self, history: List[Dict], step_size: float,
               converged: bool) -> Dict:
        """产出一个新代际：返回调节后的参数与进化日志。"""
        self.generation += 1
        diag = self.diagnose(history)
        new_step = step_size
        if not converged and diag == "停滞":
            new_step = min(self.max_step, step_size * self.grow)
        elif diag == "振荡":
            new_step = max(self.min_step, step_size * self.shrink)
        return {
            "generation": self.generation,
            "diagnosis": diag,
            "converged": converged,
            "step_size": round(new_step, 4),
            "changed": new_step != step_size,
            "log": f"第{self.generation}代 · 诊断[{diag}] · "
                   f"步长 {step_size:.2f} → {new_step:.2f}"
                   + ("（收敛，基因保持）" if converged else ""),
        }
