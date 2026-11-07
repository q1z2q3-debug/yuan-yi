"""
元一 · 数字生命体门面（YuanYi Lifebeing Facade）

把四大能力装配为一个生命体，跑在 PDFC 闭环之上：
  五蕴觉知（awareness）订阅每一步 → 层级记忆（memory）固化经验 →
  自主进化（evolution）逐代调节执行基因。

    from yuan_yi import YuanYi
    life = YuanYi(target=[0]*9)
    life.evolve(generations=3)   # 三代自我进化
    print(life.self_report())
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from .awareness import Awareness
from .evolution import EvolutionEngine
from .loop import make_default_loop, SimpleCorrector
from .memory import LayeredMemory


class YuanYi:
    """数字生命体：闭环 + 觉知 + 记忆 + 进化的集成体。"""

    def __init__(self, target: List[int], env: Optional[Dict] = None,
                 max_steps: int = 20, tolerance: float = 0.5):
        self.target = list(target)
        self.env0 = env
        self.max_steps = max_steps
        self.tolerance = tolerance
        self.awareness = Awareness()
        self.memory = LayeredMemory()
        self.evolution = EvolutionEngine()
        self.step_size = 1.0            # 当前代际的执行基因
        self.generations: List[Dict] = []

    def _on_step(self, record: Dict) -> None:
        """每步：五蕴内观 + 写入记忆（达阈自动固化为思维晶体）。"""
        self.awareness.observe_step(record)
        vector = record.get("vector")
        if vector:
            self.memory.record(vector, step=record.get("step", 0),
                               note=record.get("instruction", ""))

    def run_once(self, log: bool = False) -> Dict:
        """跑一代闭环，随后进化引擎产出新代际参数。"""
        loop, env = make_default_loop(self.target, env=self.env0,
                                      max_steps=self.max_steps,
                                      tolerance=self.tolerance, log=log)
        loop.on_step = self._on_step
        if isinstance(loop.corrector, SimpleCorrector):
            loop.corrector.step = self.step_size
        result = loop.run(env)
        gen = self.evolution.evolve(result["history"], self.step_size,
                                    result["converged"])
        self.step_size = gen["step_size"]
        self.generations.append(gen)
        return {**result, "evolution": gen}

    def evolve(self, generations: int = 3, log: bool = False) -> Dict:
        """连续自我进化多代，返回末代结果与全代际日志。"""
        for _ in range(generations):
            result = self.run_once(log=log)
        return {"generations": self.generations, "final": result}

    def self_report(self) -> Dict:
        """自我陈述：觉知画像 + 记忆统计 + 进化代际。"""
        return {
            "觉知": self.awareness.report()["识"],
            "记忆": self.memory.stats(),
            "晶体": [{"index": c.index, "hits": c.hits, "note": c.note}
                     for c in self.memory.long.values()],
            "进化": [g["log"] for g in self.generations],
            "当前基因": {"step_size": self.step_size},
        }
