#!/usr/bin/env python3
"""元一 · PDFC 闭环演示：模拟飞行滑板姿态自校正收敛。

从"感知端(滑板) + 决策端(手腕) + 耳机反馈 + 执行修正"提炼的闭环，
映射到三元九维认知坐标：姿态 → 9维三态向量 → 偏差决策 → 指导 → 修正 → 回感知。

用法：
    PYTHONPATH=src python3 examples/demo_pdfc_loop.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from yuan_yi.loop import make_default_loop


def main() -> None:
    print("=" * 56)
    print("元一 · PDFC 感知-决策-反馈-修正闭环（飞行姿态自校正）")
    print("=" * 56)
    # 目标态：roll≈0 pitch≈0 throttle≈0，即回到稳定悬停
    target = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    loop, env = make_default_loop(
        target,
        env={"_raw": {"roll": 8.0, "pitch": -5.0, "throttle": 2.0, "stability": 0.0}},
        max_steps=14, tolerance=0.5,
    )

    print("目标态(悬停) =", target)
    print("初始姿态: roll=8.0° pitch=-5.0° throttle=2.0% (明显偏离)\n")
    result = loop.run(env)

    print("\n" + "=" * 56)
    if result["converged"]:
        print(f"✓ 闭环收敛：第 {result['steps']} 步回到目标态（偏差 < 容差）")
    else:
        print(f"✗ 未收敛（{result['steps']} 步），可调大步长或增大容差")
    print("=" * 56)
    print("\n闭环要点：感知/计算分离 · 即时反馈 · 每一步修正都回感知，持续自校正。")


if __name__ == "__main__":
    main()
