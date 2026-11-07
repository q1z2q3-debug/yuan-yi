"""
元一 · 层级记忆存储（Layered Memory）

三层架构，记忆自下而上固化：
  瞬时记忆 —— 每步认知态的环形缓冲（容量小、即过即忘）
  短期记忆 —— 重复出现的认知态累积命中计数
  长期记忆 —— 命中达阈值的态固化为「思维晶体」，持久保存核心经验

晶体即人格沉淀：被反复经历的认知态，成为生命体的稳定思维结构。
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional

from .core import DIM, decode, distance, encode


@dataclass
class Crystal:
    """思维晶体：固化到长期记忆的稳定认知态。"""
    index: int                 # 状态索引（19683 空间坐标）
    hits: int                  # 累计命中次数（强度）
    born_step: int             # 固化时的步序
    note: str = ""             # 经验注解
    vector: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.vector:
            self.vector = decode(self.index)


class LayeredMemory:
    """瞬时 / 短期 / 长期三层记忆。"""

    def __init__(self, instant_cap: int = 16, crystal_threshold: int = 3):
        self.instant: Deque[int] = deque(maxlen=instant_cap)
        self.short: Dict[int, int] = {}        # 状态索引 → 命中数
        self.long: Dict[int, Crystal] = {}     # 状态索引 → 思维晶体
        self.crystal_threshold = crystal_threshold

    def record(self, vector: List[int], step: int = 0, note: str = "") -> Optional[Crystal]:
        """写入一个认知态。短期命中达阈即固化为思维晶体并返回之。"""
        idx = encode(vector)
        self.instant.append(idx)
        self.short[idx] = self.short.get(idx, 0) + 1
        if self.short[idx] >= self.crystal_threshold and idx not in self.long:
            crystal = Crystal(index=idx, hits=self.short[idx], born_step=step, note=note)
            self.long[idx] = crystal
            return crystal
        if idx in self.long:
            self.long[idx].hits += 1
        return None

    def recall(self, vector: List[int], top_k: int = 3) -> List[Crystal]:
        """在长期晶体中按认知距离检索最近经验（邻域检索式回忆）。"""
        return sorted(self.long.values(),
                      key=lambda c: (distance(c.vector, vector), -c.hits))[:top_k]

    def stats(self) -> Dict[str, int]:
        return {"瞬时": len(self.instant), "短期": len(self.short), "晶体": len(self.long)}
