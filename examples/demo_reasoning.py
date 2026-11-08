#!/usr/bin/env python3
"""元一 · 深度逻辑推理演示：思维链 + 螺旋融合。

场景：三方"顾问"对同一决策给出冲突的九维目标态 ——
  激进派(权重0.5)全阳、保守派(权重0.3)全阴、稳妥派(权重0.2)全中和。
螺旋融合先投票出共识目标，再由思维链逐步推演到达路径，全程可审计。

用法：
    PYTHONPATH=src python3 examples/demo_reasoning.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from yuan_yi import Reasoner


def main() -> None:
    print("=" * 60)
    print("元一 · 深度逻辑推理：多目标冲突的螺旋融合决策")
    print("=" * 60)

    r = Reasoner()
    votes = [([1] * 9, 0.5), ([-1] * 9, 0.3), ([0] * 9, 0.2)]
    print("\n投票（目标态, 权重）：")
    for name, (t, w) in zip(["激进派", "保守派", "稳妥派"], votes):
        print(f"  {name}: 权重 {w}  首三维 {t[:3]}…")

    out = r.spiral_fuse([-1] * 9, votes)
    print("\n融合共识目标 =", out["fused_target"])
    print(f"思维链深度 = {out['depth']} 步   收敛 = {out['converged']}")

    print("\n推演链（前 5 步）：")
    for i, s in enumerate(out["steps"][:5], 1):
        print(f"  [{i:2d}] 焦点 {s['change']}   残差 {s['residual']}")
    print("   …")

    print("\n审计：残差序列单调不增 =", out["audit"]["monotonic"])
    print("残差轨迹:", [round(x, 4) for x in out["audit"]["residuals"][:9]], "…")
    print("\n要点：每一步变易都可定位、可解释、可审计 —— 确定性符号推理。")


if __name__ == "__main__":
    main()
