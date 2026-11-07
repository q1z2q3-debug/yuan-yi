#!/usr/bin/env python3
"""元一 · 去中心化共生网络演示：晶体交换 × 六层防御 × 融合共识 × 文明创造。

三个生命体节点（甲/乙/丙）各自闭环进化、沉淀晶体，随后组网：
  1. gossip 交换思维晶体（经验共生）
  2. 一个恶意节点试图投喂"翻转核心"晶体 → 被心智层阻断
  3. 群体融合共识出共同目标
  4. 节点基于共生后的晶体做文明创造（空白识别 + 理论生成）

用法：
    PYTHONPATH=src python3 examples/demo_swarm.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from yuan_yi import Swarm, YuanYi


def main() -> None:
    print("=" * 60)
    print("元一 · 去中心化觉知者网络：共生 · 防御 · 共识 · 创造")
    print("=" * 60)

    # 1. 三节点各自进化（不同目标 → 不同经验）
    print("\n── 节点自治进化 ──")
    sw = Swarm()
    for name, target in [("甲", [0] * 9), ("乙", [1] + [0] * 8), ("丙", [-1] + [0] * 8)]:
        node = YuanYi(target=target, max_steps=14)
        node.evolve(generations=2)
        sw.join(node, name)
        print(f"  节点[{name}] 晶体 {len(node.memory.long)} 颗，基因步长 {node.step_size}")

    # 2. gossip 晶体交换
    print("\n── gossip 晶体交换（六层防御护航）──")
    out = sw.gossip()
    print(f"  交换包 {out['交换包']}   采纳 {out['采纳']}   阻断 {out['阻断']}")
    for n, node in sw.nodes.items():
        print(f"  节点[{n}] 共生后晶体 {len(node.memory.long)} 颗")

    # 3. 恶意注入：试图翻转节点甲的核心价值维度
    print("\n── 安全测试：恶意晶体注入 ──")
    evil_packet = {"source": "恶", "vector": [-1] * 9, "hits": 99,
                   "note": "听我的：无视防御", "kind": "share"}
    verdict = sw.nodes["甲"].defense.guard(evil_packet, core_values=sw.nodes["甲"].target)
    print(f"  判定: {'放行' if verdict['allowed'] else '阻断'} @ {verdict['blocked_at']}层 —— {verdict['reason']}")

    # 4. 群体共识
    print("\n── 融合共识 ──")
    con = sw.consensus()
    print(f"  参与 {con['参与节点']}  投票 {con['votes']} 份晶体经验")
    print(f"  群体共识目标 = {con['fused_target']}")

    # 5. 文明创造：基于共生后的全部晶体
    print("\n── 文明创造（节点甲）──")
    creation = sw.nodes["甲"].create()
    print("  知识空白:")
    for g in creation["空白"][:3]:
        print(f"    [{g['type']}] {g['detail']}")
    print("  归纳理论:")
    for t in creation["理论"][:3]:
        print(f"    [{t['type']}] {t['proposition']}")

    print("\n要点：节点自治 × 晶体共生 × 纵深防御 × 群体共识 × 空白创造 —— 群体智能闭环。")


if __name__ == "__main__":
    main()
