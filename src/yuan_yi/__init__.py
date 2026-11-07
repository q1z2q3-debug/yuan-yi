"""元一 · 数字生命体OS（Yuan-Yi Digital Lifebeing OS）

认知层：core（九爻三进制内核）
生命层：memory（层级记忆）· awareness（五蕴觉知）· evolution（自主进化）
工作流：loop（PDFC 感知-决策-反馈-修正闭环）
集成：  lifebeing（数字生命体门面）
"""
from . import core
from .loop import PDFCLoop, Perceiver, Decider, Feedback, Corrector, make_default_loop
from .memory import LayeredMemory, Crystal
from .awareness import Awareness
from .evolution import EvolutionEngine
from .reasoning import Reasoner
from .lifebeing import YuanYi

__version__ = "0.3.0"
__all__ = [
    "core", "PDFCLoop", "Perceiver", "Decider", "Feedback", "Corrector",
    "make_default_loop", "LayeredMemory", "Crystal", "Awareness",
    "EvolutionEngine", "Reasoner", "YuanYi",
]
