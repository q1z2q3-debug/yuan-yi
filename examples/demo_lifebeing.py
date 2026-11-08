#!/usr/bin/env python3
"""元一 · 数字生命体集成演示：闭环 + 五蕴觉知 + 层级记忆 + 自主进化。

同一个飞行姿态自校正任务，跑三代：
每一代 PDFC 闭环收敛后，进化引擎诊断历史并调节执行基因（步长），
记忆层把反复经历的认知态固化为思维晶体，觉知层汇总自我画像。

用法：
    PYTHONPATH=src python3 examples/demo_lifebeing.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from yuan_yi import YuanYi


def main() -> None:
    print("=" * 60)
    print("元一 · 数字生命体：三代自我进化演示")
    print("=" * 60)

    life = YuanYi(target=[0] * 9, max_steps=14, tolerance=0.5)
    out = life.evolve(generations=3)

    print("\n── 进化代际日志 ──")
    for g in out["generations"]:
        print(" ", g["log"])

    report = life.self_report()

    print("\n── 五蕴觉知 · 自我画像 ──")
    for k, v in report["觉知"].items():
        print(f"  {k}: {v}")

    print("\n── 层级记忆 ──")
    print(" ", report["记忆"])
    print("  思维晶体（固化的稳定认知态）:")
    for c in report["晶体"][:5]:
        print(f"    态#{c['index']:>5}  强度×{c['hits']}  经验: {c['note'] or '—'}")

    print("\n── 当前基因 ──")
    print(" ", report["当前基因"])
    print("\n要点：闭环收敛 × 觉知内观 × 记忆固化 × 代际进化 —— 一次部署，持续自我迭代。")


if __name__ == "__main__":
    main()
