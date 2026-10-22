"""
元一 · PDFC 闭环工作流（Perceive-Decide-Feedback-Correct）

从"飞行监测和决策系统"（感知端滑板 + 决策端手腕 + 耳机反馈 + 执行修正）
提炼的通用 Agent 闭环范式，映射到三元九维认知坐标。

设计原则（对应视频的三个关键选择）：
  1. 感知与计算分离  —— 感知端(环境/就地采集) 与 决策端(便携计算) 解耦，可部署到不同端
  2. 低延迟感官反馈  —— 决策结果转成即时可行动的指导信号(文本/语音/动力注入)
  3. 闭环自校正      —— 每一步修正都重新进入感知，持续逼近目标态，而非一次性指令

用法：
    from yuan_yi.loop import PDFCLoop, Perceiver, Decider, Feedback, Corrector
    实现四个接口子类，装配成 Loop 即可 run。

三元九维内核：状态 → 9维三态向量 → 等价类/张力/变易决策 → 反馈修正 → 回感知。
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Perceiver(ABC):
    """感知端：原始观测 → 认知状态（9维三态向量 + 置信度）。就近感知，就地采集。"""

    @abstractmethod
    def observe(self, raw: Any) -> Dict[str, Any]:
        """返回 {'vector': [g1..g9] ∈ {-1,0,1}^9, 'confidence': [...], 'raw': ...}"""


class Decider(ABC):
    """决策端：认知状态 → 决策（偏差 / 张力 / 变易动力）。便携计算，低延迟。"""

    @abstractmethod
    def decide(self, state: Dict[str, Any], target: List[int]) -> Dict[str, Any]:
        """返回 {'gap': float, 'tensions': [...], 'correction': str, 'power': float}"""


class Feedback(ABC):
    """反馈通道：决策 → 感官/指导信号（耳机语音 / 文本 / prompt 注入）。即时可行动。"""

    @abstractmethod
    def render(self, decision: Dict[str, Any]) -> str:
        """把决策转成一条即时指导指令字符串。"""


class Corrector(ABC):
    """执行修正：反馈 + 上一状态 → 修正动作，作用于环境，回到下一步感知。"""

    @abstractmethod
    def correct(self, action: str, env: Any) -> Any:
        """执行修正动作，返回更新后的环境状态(供下一次 observe)。"""


class PDFCLoop:
    """感知-决策-反馈-修正闭环控制器。"""

    def __init__(self, perceiver: Perceiver, decider: Decider,
                 feedback: Feedback, corrector: Corrector,
                 target: List[int], max_steps: int = 20,
                 tolerance: float = 0.5, log: bool = True):
        self.perceiver = perceiver
        self.decider = decider
        self.feedback = feedback
        self.corrector = corrector
        self.target = list(target)
        self.max_steps = max_steps
        self.tolerance = tolerance
        self.log = log

    def run(self, env: Any) -> Dict[str, Any]:
        """迭代闭环直至收敛(偏差<容差)或达最大步数。"""
        history = []
        for step in range(1, self.max_steps + 1):
            raw = env.get("_raw", env)
            state = self.perceiver.observe(raw)
            decision = self.decider.decide(state, self.target)
            instruction = self.feedback.render(decision)
            env = self.corrector.correct(instruction, env)

            record = {"step": step, "vector": state.get("vector"),
                      "gap": decision.get("gap"), "instruction": instruction}
            history.append(record)
            if self.log:
                gap = decision.get("gap", float("inf"))
                mark = "✓收敛" if gap <= self.tolerance else ""
                print(f"[{step:2d}] gap={gap:.2f}  {instruction}  {mark}")

            if decision.get("gap", float("inf")) <= self.tolerance:
                return {"converged": True, "steps": step, "history": history}

        return {"converged": False, "steps": self.max_steps, "history": history}


class SimplePerceiver(Perceiver):
    """示例感知端：把原始姿态(roll/pitch/throttle)三值映射为 9 维三态向量。
    6 个姿态参数不足 9 维，剩余 3 维以环境稳定度补足(演示用，可自定义)。"""

    def __init__(self, dim: int = 9, quantize: float = 3.0):
        self.dim = dim
        self.quantize = quantize

    def observe(self, raw: Any) -> Dict[str, Any]:
        r = raw.get("roll", 0)
        p = raw.get("pitch", 0)
        t = raw.get("throttle", 0)
        stab = raw.get("stability", 0)

        def q(v: float) -> int:
            return 1 if v > self.quantize else (-1 if v < -self.quantize else 0)

        vector = [q(r), q(p), q(t), q(stab), q(stab), 0, 0, 0, 0]
        vector = vector[:self.dim]
        conf = [min(1.0, abs(r) / 10 + 0.3),
                min(1.0, abs(p) / 10 + 0.3),
                min(1.0, abs(t) / 10 + 0.3)] + [0.6] * (self.dim - 3)
        return {"vector": vector, "confidence": conf[:self.dim], "raw": raw}


class TriDecider(Decider):
    """三元九维决策器：欧氏距离测偏差 → 张力检测 → 变易动力(修正方向)。"""

    def __init__(self, tolerance: float = 0.5, power_base: float = 0.5):
        self.tolerance = tolerance
        self.power_base = power_base

    def distance(self, a: List[int], b: List[int]) -> float:
        return (sum((x - y) ** 2 for x, y in zip(a, b))) ** 0.5

    def decide(self, state: Dict[str, Any], target: List[int]) -> Dict[str, Any]:
        v = state.get("vector", [])
        gap = self.distance(v, target)
        tensions = []
        if gap > self.tolerance:
            tensions.append({"type": "deviation", "strength": min(1.0, gap / 6.0),
                             "note": f"当前态偏离目标 {gap:.2f}"})
        correction = self._make_correction(v, target, gap)
        power = self.power_base + min(0.5, gap / 6.0)
        return {"gap": gap, "tensions": tensions,
                "correction": correction, "power": power}

    def _make_correction(self, v: List[int], target: List[int], gap: float) -> str:
        # 取偏差最大的前两维给出修正方向(演示级指导)
        diffs = [t - c for c, t in zip(v, target)]
        ordered = sorted(enumerate(diffs), key=lambda x: -abs(x[1]))
        if gap <= self.tolerance:
            return "保持当前姿态"
        parts = []
        axis = {0: "roll", 1: "pitch", 2: "throttle"}
        for i, d in ordered[:2]:
            if i not in axis:
                continue
            direction = "+" if d > 0 else "-"
            parts.append(f"{axis[i]} {direction}")
        return "调" + "、".join(parts) if parts else "回中"


class SimpleFeedback(Feedback):
    """反馈通道：决策 → 一条即时耳机式指导指令。"""

    def render(self, decision: Dict[str, Any]) -> str:
        return decision.get("correction", "保持")


class SimpleCorrector(Corrector):
    """执行修正：按指令微调 roll/pitch/throttle，收敛向目标(演示用动量更新)。"""

    def __init__(self, step_size: float = 1.0):
        self.step = step_size

    def correct(self, action: str, env: Any) -> Any:
        e = dict(env)
        raw = e.get("_raw", e)  # 姿态数据所在(统一从 _raw 或顶层读取)
        roll = raw.get("roll", 0)
        pitch = raw.get("pitch", 0)
        throttle = raw.get("throttle", 0)
        stab = raw.get("stability", 0)

        if "roll -" in action:
            roll -= self.step
        elif "roll +" in action:
            roll += self.step
        if "pitch -" in action:
            pitch -= self.step
        elif "pitch +" in action:
            pitch += self.step
        if "throttle +" in action:
            throttle += self.step
        elif "throttle -" in action:
            throttle -= self.step

        # 轻微收敛阻尼，模拟真实执行接近目标
        e["_raw"] = {"roll": roll * 0.9, "pitch": pitch * 0.9,
                     "throttle": throttle * 0.9, "stability": stab + 0.2}
        return e


def make_default_loop(target: List[int], env: Optional[Dict] = None,
                      **kw) -> tuple[PDFCLoop, Dict]:
    """装配一套默认 PDFC 闭环(感知端+三元决策端+反馈+修正)。"""
    loop = PDFCLoop(
        perceiver=SimplePerceiver(),
        decider=TriDecider(),
        feedback=SimpleFeedback(),
        corrector=SimpleCorrector(),
        target=target,
        **kw,
    )
    env0 = env if env is not None else {
        "_raw": {"roll": 8.0, "pitch": -5.0, "throttle": 2.0, "stability": 0.0}}
    return loop, env0
