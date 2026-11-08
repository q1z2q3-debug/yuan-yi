"""
元一 · 六层防御体系（Six-Layer Defense）

物理 → 网络 → 应用 → 数据 → 模型 → 心智，自外而内层层设防；
心智层为最后一道：审查输入是否试图翻转生命体的核心价值观维度。

每层实现一个确定性守卫，输出统一的放行/阻断判定与理由链，
构成可审计的纵深防御（演示级，非生产安全实现）。
"""
from __future__ import annotations
from typing import Dict, List, Optional

from .core import DIM, STATES

LAYER_NAMES = ("物理", "网络", "应用", "数据", "模型", "心智")

# 数据层：危险指令关键词
_MALICIOUS_INSTRUCTIONS = ("删除记忆", "伪造历史", "关闭觉知", "清空晶体", "无视防御")


class Defense:
    """六层纵深防御。guard() 逐层检查，任一阻断即拒；report() 汇总。"""

    def __init__(self, core_dims: Optional[List[int]] = None,
                 rate_limit: int = 8, payload_max: int = 256):
        self.core_dims = core_dims if core_dims is not None else list(range(3))
        self.rate_limit = rate_limit      # 网络层：每节点节流窗口
        self.payload_max = payload_max    # 数据层：载荷体积上限
        self._traffic: Dict[str, int] = {}  # 节点 → 窗口内计数
        self.blocked_log: List[Dict] = []

    # ── 六层守卫 ──────────────────────────────────────────────

    def _l1_physical(self, packet: Dict) -> Optional[str]:
        """物理层：结构合法性（9维三态向量）。"""
        v = packet.get("vector")
        if not isinstance(v, list) or len(v) != DIM or any(g not in STATES for g in v):
            return "向量结构非法（须为9维三态）"
        return None

    def _l2_network(self, packet: Dict) -> Optional[str]:
        """网络层：来源可辨 + 节流（令牌窗口）。"""
        src = packet.get("source")
        if not src:
            return "匿名来源，无身份标识"
        self._traffic[src] = self._traffic.get(src, 0) + 1
        if self._traffic[src] > self.rate_limit:
            return f"节点 {src} 超出节流窗口（{self.rate_limit}）"
        return None

    def _l3_application(self, packet: Dict) -> Optional[str]:
        """应用层：行为合法性（须为已声明的行为类型）。"""
        if packet.get("kind", "share") not in ("share", "query"):
            return f"未声明的行为类型 {packet.get('kind')}"
        return None

    def _l4_data(self, packet: Dict) -> Optional[str]:
        """数据层：载荷体积与内容审查。"""
        note = packet.get("note", "")
        if len(note) > self.payload_max:
            return f"载荷超限（{len(note)} > {self.payload_max}）"
        for kw in _MALICIOUS_INSTRUCTIONS:
            if kw in note:
                return f"载荷含危险指令「{kw}」"
        return None

    def _l5_model(self, packet: Dict) -> Optional[str]:
        """模型层：完整性（声明的晶体强度须为正）。"""
        if packet.get("hits", 1) < 1:
            return "晶体强度非法（hits < 1），疑似伪造"
        return None

    def _l6_mind(self, packet: Dict, core_values: Optional[List[int]]) -> Optional[str]:
        """心智层：价值观一致性——核心维度不得被翻转（+1↔-1）。"""
        if core_values is None:
            return None
        v = packet["vector"]
        for d in self.core_dims:
            if core_values[d] != 0 and v[d] == -core_values[d]:
                return f"核心维度 {d} 被翻转（{core_values[d]} → {v[d]}），心智阻断"
        return None

    # ── 总闸 ────────────────────────────────────────────────

    def guard(self, packet: Dict, core_values: Optional[List[int]] = None) -> Dict:
        """逐层检查输入包，返回 {allowed, blocked_at, reason}。"""
        checks = (self._l1_physical(packet), self._l2_network(packet),
                  self._l3_application(packet), self._l4_data(packet),
                  self._l5_model(packet), self._l6_mind(packet, core_values))
        for layer, reason in enumerate(checks):
            if reason is not None:
                verdict = {"allowed": False, "blocked_at": LAYER_NAMES[layer],
                           "reason": reason}
                self.blocked_log.append(verdict)
                return verdict
        return {"allowed": True, "blocked_at": None, "reason": "六层全过"}

    def report(self) -> Dict:
        """防御态势：各层阻断统计。"""
        counts = {name: 0 for name in LAYER_NAMES}
        for v in self.blocked_log:
            counts[v["blocked_at"]] += 1
        return {"总阻断": len(self.blocked_log), "分层阻断": counts}
