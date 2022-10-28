import sys
from sismic.interpreter import Interpreter
from sismic.io import export_to_plantuml

if "pytest" in sys.modules:
    from simulator.sms.abs_sm import *
else:
    include('workspace://Python4Capella/sample_scripts/simulator/sms/abs_sm.py')


MAX_STEPS = 20


class SismicSM(AbstractSM):
    def build_steps(self, session=None):
        steps = []
        interpreter = Interpreter(session)
        plantuml = export_to_plantuml(session)

        for step in interpreter.execute(max_steps=MAX_STEPS):
            for micro_step in step.steps:
                steps.append(micro_step)

        return {
            'steps': steps,
            'name': interpreter.statechart.name,
            'plantuml': plantuml
        }
