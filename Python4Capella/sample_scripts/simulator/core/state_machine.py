import sys

if "pytest" in sys.modules:
    from simulator.parsers.factory_parser import *
    from simulator.sms.factory_sm import *
else:
    # ParserFactory
    include(
        'workspace://Python4Capella/sample_scripts/simulator/parsers/factory_parser.py')
    # SMFactory
    include('workspace://Python4Capella/sample_scripts/simulator/sms/factory_sm.py')


class StateMachineModel:
    """
      Construção de um modelo de máquina de estados
    """

    def __init__(self, session, state_type, parser_type):
        # Inicializa a máquina de estados, parser e sessão
        self.sm = SMFactory(type=state_type)
        self.parser = ParserFactory(type=parser_type)
        self.sessions = self.parser.sessions(session=session)

    def build_steps(self):
        # Chama método de construção de estados
        steps_sms = [self.sm.build_steps(session=s) for s in self.sessions]

        # Traduz os estados para a linguagem do capella
        return [{
            'name': steps['name'],
            'steps': [self.parser.step(step) for step in steps['steps']]
        } for steps in steps_sms]


class SM:
    """
    Abstração da lógica de máquinas de estado.
    """

    def __init__(self, session=None, state_type=None, parser_type=None):
        # Inicializa os estados, o step e o modelo
        self.step = -1
        self.states = None

        self.model = StateMachineModel(
            session=session,
            state_type=state_type,
            parser_type=parser_type
        )

    def next_step(self):
        if self.states == None:
            self.start()

        # Vai para o próximo estado do modelo, se houver
        self.step = self.step + 1

        return [self.get_step(steps) for steps in self.states]

    def get_step(self, steps):
        stepslen = len(steps['steps'])
        if stepslen <= self.step and stepslen > 0:
            self.step = stepslen - 1

        return steps['steps'][self.step], steps['name']

    def previous_step(self):
        # Vai para o próximo estado do modelo, se houver
        if self.states == None:
            self.start()

        if self.step < 1:
            self.step = 0
        else:
            self.step = self.step - 1

        return [self.get_step(steps) for steps in self.states]

    def start(self):
        # Constrói todos os estados do modelo
        self.states = self.model.build_steps()

    def automatic(self):
        if self.states == None:
            return self.start()

        return self.next_step()

    def finalize(self):
        return None