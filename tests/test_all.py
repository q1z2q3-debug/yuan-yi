#!/usr/bin/env python3
"""元一 · 测试套件：九爻内核 / 层级记忆 / 五蕴觉知 / 进化引擎 / PDFC闭环 / 生命体集成。

用法：
    python3 tests/test_all.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from yuan_yi import core
from yuan_yi.awareness import Awareness
from yuan_yi.evolution import EvolutionEngine
from yuan_yi.lifebeing import YuanYi
from yuan_yi.loop import make_default_loop
from yuan_yi.memory import LayeredMemory
from yuan_yi.reasoning import Reasoner


class TestCore(unittest.TestCase):
    def test_roundtrip_full_space(self):
        for v in range(0, core.TOTAL, 97):  # 抽样 + 边界
            self.assertEqual(core.encode(core.decode(v)), v)
        for v in (0, 1, core.TOTAL // 2, core.TOTAL - 1):
            self.assertEqual(core.encode(core.decode(v)), v)

    def test_encode_invalid(self):
        with self.assertRaises(ValueError):
            core.encode([2] * 9)
        with self.assertRaises(ValueError):
            core.decode(-1)

    def test_operators(self):
        v = [1, 0, -1, 1, 0, -1, 1, 0, -1]
        self.assertEqual(core.cuo(v), [-1, 0, 1, -1, 0, 1, -1, 0, 1])
        self.assertEqual(core.zong(v), list(reversed(v)))
        b = core.bian(v, 0)
        self.assertEqual(b[0], -1)
        self.assertEqual(core.bian(v, 1)[1], 1)  # 0 → +1（中和转向生发）
        self.assertEqual(core.cuo(core.cuo(v)), v)

    def test_neighbors_and_step(self):
        z = [0] * 9
        self.assertEqual(len(core.neighbors(z)), 18)  # 全中和态满邻域
        corner = [1] * 9
        self.assertEqual(len(core.neighbors(corner)), 9)  # 纯阳态只能向下
        target = [1] * 9
        stepped = core.step_toward(z, target, dims=2)
        # 平方距离按修正维数精确递减：9 → 7
        self.assertAlmostEqual(core.distance(stepped, target) ** 2,
                               core.distance(z, target) ** 2 - 2)

    def test_tension_order(self):
        t = core.tension([-1, 0, 1] + [0] * 6, [1, 0, 1] + [0] * 6)
        self.assertEqual(t[0]["dim"], 0)
        self.assertEqual(t[0]["strength"], 1.0)


class TestMemory(unittest.TestCase):
    def test_crystallization(self):
        mem = LayeredMemory(crystal_threshold=3)
        v = [1, 0, -1] + [0] * 6
        self.assertIsNone(mem.record(v, step=1))
        self.assertIsNone(mem.record(v, step=2))
        crystal = mem.record(v, step=3, note="悬停稳定态")
        self.assertIsNotNone(crystal)
        self.assertEqual(crystal.hits, 3)
        self.assertEqual(mem.stats()["晶体"], 1)
        crystal2 = mem.record(v, step=4)
        self.assertIsNone(crystal2)          # 已固化，不再重复生成
        self.assertEqual(mem.long[crystal.index].hits, 4)  # 但强度继续累积

    def test_recall_nearest(self):
        mem = LayeredMemory(crystal_threshold=1)
        mem.record([1] * 9, note="纯阳")
        mem.record([-1] * 9, note="纯阴")
        near = mem.recall([1, 1, 1, -1, -1, -1, 0, 0, 0], top_k=1)
        self.assertEqual(near[0].note, "纯阳")


class TestAwareness(unittest.TestCase):
    def test_feeling_transitions(self):
        aw = Awareness()
        aw.observe_step({"step": 1, "vector": [1] + [0] * 8, "gap": 2.0, "instruction": "调roll -"})
        aw.observe_step({"step": 2, "vector": [0] * 9, "gap": 1.0, "instruction": "调roll -"})
        self.assertEqual(aw.snapshots[0]["受"], "初感")
        self.assertEqual(aw.snapshots[1]["受"], "趋稳")
        rep = aw.report()["识"]
        self.assertEqual(rep["总步数"], 2)
        self.assertIn(0, [rep["惯性维度"]])


class TestEvolution(unittest.TestCase):
    def test_stagnation_grows_step(self):
        ev = EvolutionEngine()
        hist = [{"gap": 3.0}] * 4
        gen = ev.evolve(hist, step_size=1.0, converged=False)
        self.assertEqual(gen["diagnosis"], "停滞")
        self.assertGreater(gen["step_size"], 1.0)

    def test_oscillation_shrinks_step(self):
        ev = EvolutionEngine()
        hist = [{"gap": g} for g in (2.0, 3.0, 2.0, 3.0)]
        gen = ev.evolve(hist, step_size=2.0, converged=False)
        self.assertEqual(gen["diagnosis"], "振荡")
        self.assertLess(gen["step_size"], 2.0)


class TestReasoning(unittest.TestCase):
    def test_think_chain_converges(self):
        r = Reasoner()
        out = r.think([-1] * 9, [1] * 9)
        self.assertTrue(out["converged"])
        self.assertEqual(out["depth"], 18)  # 纯阴→纯阳：2步/维 × 9维
        self.assertTrue(out["audit"]["monotonic"])

    def test_think_already_at_target(self):
        r = Reasoner()
        out = r.think([0] * 9, [0] * 9)
        self.assertTrue(out["converged"])
        self.assertEqual(out["depth"], 0)

    def test_squared_residual_decreases_per_step(self):
        r = Reasoner()
        out = r.think([0] * 9, [1] * 9)
        res = out["audit"]["residuals"]
        for a, b in zip(res, res[1:]):
            self.assertAlmostEqual(a * a - b * b, 1.0)  # 变易算子每步平方残差恰减 1

    def test_fuse_targets_voting(self):
        # 权重 2:1 对冲 → 均值 1/3 未超阈 → 持"变"(0)
        self.assertEqual(Reasoner.fuse_targets([([1] * 9, 2.0), ([-1] * 9, 1.0)]), [0] * 9)
        # 权重 3:1 → 均值 0.5 超阈 → 共识为阳
        self.assertEqual(Reasoner.fuse_targets([([1] * 9, 3.0), ([-1] * 9, 1.0)]), [1] * 9)

    def test_spiral_fuse(self):
        r = Reasoner()
        out = r.spiral_fuse([0] * 9, [([1] * 9, 3.0), ([-1] * 9, 1.0)])
        self.assertEqual(out["fused_target"], [1] * 9)
        self.assertTrue(out["converged"])
        self.assertEqual(len(out["votes"]), 2)

    def test_lifebeing_reason(self):
        life = YuanYi(target=[0] * 9, max_steps=14)
        life.run_once()
        out = life.reason()  # 闭环已收敛至目标 → 链长 0
        self.assertTrue(out["converged"])
        fused = life.reason(weighted_targets=[([1] * 9, 3.0), ([0] * 9, 1.0)])
        self.assertIn("fused_target", fused)


class TestLoopAndLifebeing(unittest.TestCase):
    def test_loop_converges_and_hook_fires(self):
        loop, env = make_default_loop([0] * 9, max_steps=14, log=False)
        seen = []
        loop.on_step = seen.append
        result = loop.run(env)
        self.assertTrue(result["converged"])
        self.assertEqual(len(seen), result["steps"])

    def test_lifebeing_evolve(self):
        life = YuanYi(target=[0] * 9, max_steps=14)
        out = life.evolve(generations=3)
        self.assertEqual(len(out["generations"]), 3)
        report = life.self_report()
        self.assertEqual(report["记忆"]["晶体"] > 0, True)  # 重复路径固化出晶体
        self.assertTrue(report["觉知"]["收敛"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
