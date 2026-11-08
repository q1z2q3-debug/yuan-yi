"""
元一 · 去中心化共生网络 MVP（Awareness P2P Network）

本地仿真多个生命体节点（无中心服务器）：
  gossip 传播 —— 每个节点把自己的思维晶体投递给邻居
  晶体交换前必经六层防御审查（恶意/伪造晶体被阻断）
  融合共识 —— 以各节点晶体为加权投票（权重=晶体强度），
             螺旋融合出群体共识目标

此模块不依赖真实网络栈：Swarm 在同一进程内模拟消息投递，
节点即 YuanYi 生命体，演示"一次部署、群体共生"的最小形态。
"""
from __future__ import annotations
from typing import Dict, List, Optional

from .core import DIM
from .reasoning import Reasoner


class Swarm:
    """觉知者群体：节点注册、gossip 晶体交换、融合共识。"""

    def __init__(self):
        self.nodes: Dict[str, "YuanYi"] = {}   # name → 生命体
        self.reasoner = Reasoner()
        self.exchanged: List[Dict] = []        # 交换日志（可审计）

    def join(self, node: "YuanYi", name: str) -> None:
        self.nodes[name] = node

    def gossip(self) -> Dict:
        """一轮 gossip：每节点向所有邻居广播自己的晶体，邻居经六层防御采纳。"""
        accepted = blocked = 0
        for src_name, src in self.nodes.items():
            for crystal in src.memory.long.values():
                packet = {"source": src_name, "vector": crystal.vector,
                          "hits": crystal.hits, "note": crystal.note, "kind": "share"}
                for dst_name, dst in self.nodes.items():
                    if dst_name == src_name:
                        continue
                    verdict = dst.defense.guard(packet, core_values=dst.target)
                    self.exchanged.append({"from": src_name, "to": dst_name, **verdict})
                    if verdict["allowed"]:
                        before = len(dst.memory.long)
                        for _ in range(dst.memory.crystal_threshold):
                            dst.memory.record(crystal.vector,
                                              note=f"共生:{src_name}·{crystal.note}")
                        if len(dst.memory.long) > before:
                            accepted += 1
                    else:
                        blocked += 1
        return {"交换包": len(self.exchanged), "采纳": accepted, "阻断": blocked}

    def consensus(self) -> Dict:
        """融合共识：全部节点各自晶体的加权（强度）螺旋融合。"""
        votes = []
        for name, node in self.nodes.items():
            for c in node.memory.long.values():
                votes.append((c.vector, float(c.hits)))
        if not votes:
            return {"fused_target": None, "votes": 0}
        fused = self.reasoner.fuse_targets(votes)
        return {"fused_target": fused, "votes": len(votes),
                "参与节点": sorted(self.nodes)}
