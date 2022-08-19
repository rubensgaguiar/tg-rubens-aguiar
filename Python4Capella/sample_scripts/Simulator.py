# name                 : Simulator
# script-type          : Python
# description          : Simulator
# popup                : enableFor(org.polarsys.capella.core.data.capellacore.CapellaElement)
#
# This script loads the Capella model passed as first argument and list its root LogicalFunction.
# To run it:
#  - enable Developer capabilities if not already done (see documentation in the help menu)
#  - you can run this script by launching the contextual menu "Run As / EASE Script..."
#    on this script.
#    - By default, the model selected is IFE sample (aird path of the model written below)

#  - you can also run this script according to a configuration (script selected, arguments)
#    and modify the configuration by launching the contextual menu "Run As / Run configurations..."
#    on this script.
#    - create a new "EASE Script" configuration
#    - define the name of the configuration: "list_logical_functions_in_console.py" (for instance)
#    - define the Script Source path: "workspace://Python4Capella/sample_scripts/List_logical_functions_in_console.py"
#    - define the path to the aird file as first argument in "Script arguments" area: "/In-Flight Entertainment System/In-Flight Entertainment System.aird" (for instance)

from sismic.interpreter import Interpreter
from sismic.model import Statechart
from sismic.io import import_from_yaml
from typing_extensions import Self
from collections import defaultdict
from abc import ABC
import yaml
import time
import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install("pyyaml")

# include needed for the Capella modeller API
include('workspace://Python4Capella/simplified_api/capella.py')
if False:
    from simplified_api.capella import *

# Retrieve the Element from the current selection and its aird model path
selected_elem = CapellaElement(CapellaPlatform.getFirstSelectedElement())
aird_path = '/' + CapellaPlatform.getModelPath(selected_elem)

'''
# change this path to execute the script on your model (here is the IFE sample). 
# Uncomment it if you want to use the "Run configuration" instead
aird_path = '/In-Flight Entertainment System/In-Flight Entertainment System.aird'
'''
'''
#Here is the "Run Configuration" part to uncomment if you want to use this functionality :

#check parameter numbers
if len(argv) != 1:
    # use IFE default values
    aird_path = "/In-Flight Entertainment System/In-Flight Entertainment System.aird"
else:
    # Load the Capella model from the first argument of the script
    aird_path = argv[0]
'''


MAX_STEPS = 10


class Parser(ABC):
    """
      Abstração de um parser
    """

    def session(self):
        # abstract
        pass

    def state(self):
        # abstract
        pass


class SM(ABC):
    """
      Abstração de uma máquina de estados
    """

    def build_steps(self):
        # abstract
        pass


class SismicParser(Parser):
    """
      Traduz sessões do capella para o modelo
      Traduz estados do modelo para o capella
    """

    def __init__(self):
        self.sismic_to_capella = defaultdict(lambda: None)

    def _add_name(self, state):
        return {
            'name': state.get_name()
        }

    def _method_by_name(self, method, name: str):
        return getattr(method, name)

    def _build_state(self, owned_region):
        states = []
        for owned_state in owned_region.get_owned_states():  # Estado ou Modo
            owned_state_obj = {
                'incoming': [],
                'outgoing': [],
                'realized_states': [],
                'realizing_states': []
            }

            for key in owned_state_obj:
                method_to_call = self._method_by_name(
                    owned_state, 'get_' + key)
                for element in method_to_call():
                    owned_state_obj[key].append(self._add_name(element))

            owned_state_obj['name'] = owned_state.get_name()
            states.append(owned_state_obj)

            # Mapeio o nome do estado para o elemento do capella
            # e suas transiçoes. Para acessar depois, se necessario.
            self.sismic_to_capella[owned_state_obj['name']] = {
                'state': owned_state
            }

        return states

    def _build_regions(self, state_machine):
        regions = []
        for owned_region in state_machine.get_owned_regions():  # Região da máquina
            owned_region_obj = self._add_name(owned_region)

            states = self._build_state(owned_region)

            owned_region_obj['states'] = states
            regions.append(owned_region_obj)

        return regions

    def _read_capella_state_machines(self, session):
        logical_architecture = session.get_logical_architecture()
        logical_system = logical_architecture.get_logical_system()
        owned_logical_components = logical_system.get_owned_logical_components()  # Inside LC 1

        state_machines = []
        for owned_logical_component in owned_logical_components:  # LC 1 Component
            for state_machine in owned_logical_component.get_owned_state_machines():  # Máquina de Estado
                state_machine_obj = self._add_name(state_machine)
                regions = self._build_regions(state_machine)

                state_machine_obj['regions'] = regions
                state_machines.append(state_machine_obj)
        return state_machines

    def _dict_to_yaml_str(self, dictonary):
        return yaml.dump(dictonary)

    def _capella_to_sismic_state_machines(self, state_machines):
        # TODO: convert from capella to sismic
        state_machine_sismics = []

        # TODO: só suporta uma state_machine, se tiver mais de uma, resolve somente a primeira
        for state_machine in state_machines:
            parallel_states = []
            for region in state_machine['regions']:
                states = []
                for state in region['states']:
                    transitions = []
                    for transition in state['incoming']:
                        transitions.append({
                            'target': transition.get_target(),
                            'guard': transition.get_guard(),
                            'action': transition.get_effects()
                        })

                    states.append({
                        'name': state['name'],
                        'transitions': transitions
                    })

                parallel_states.append({
                    'name': region['name'],
                    'states': states
                })
            state_machine_sismics.append({
                'name': state_machine['name'],
                'root state': {
                    'name': 'root',
                    'parallel states': states
                }
            })

        statechart = {}
        if len(state_machine_sismics) > 0:
            statechart = state_machine_sismics[0]

        return {
            'statechart': statechart
        }

    def step(self, step=None):
        # TODO: logar essas informações do print abaixo em um logger

        # Print all steps
        # for attribute in ['event', 'transitions', 'entered_states', 'exited_states', 'sent_events']:
        #     print('{}: {}'.format(attribute, getattr(step, attribute)))

        # TODO: formatar o step para a linguagem do capella
        return step

    def session(self, session=None):
        capella_sms = self._read_capella_state_machines(session)
        sismic_sms = self._capella_to_sismic_state_machines(capella_sms)
        simic_yaml_str = self._dict_to_yaml_str(sismic_sms)

        # TODO: criar um logger e logar o simic_yaml_str

        return import_from_yaml(simic_yaml_str)  # algo assim...


class SismicSM(SM):
    def build_steps(self, session=None):
        steps = []
        interpreter = Interpreter(session)
        for step in interpreter.execute(max_steps=MAX_STEPS):
            steps.append(step)
        return steps


class Factory(ABC):
    """
      Abstração da fabricação de modelos
    """

    def __init__(self, type, products):
        self.type = type
        self.products = products

    def __new__(cls):
        return cls.products[cls.type]


class ParserFactory:
    """
      Fábrica de Parser
    """

    def __new__(cls, type) -> Self:
        # Fabrica o modelo solicitado
        products = {
            'sismic': SismicParser
        }
        return products[type]()


class SMFactory:
    """
      Fábrica de Máquina de Estados
    """

    def __new__(cls, type) -> Self:
        # Fabrica o modelo solicitado
        products = {
            'sismic': SismicSM
        }
        return products[type]()


class StateMachineModel:
    """
      Construção de um modelo de máquina de estados
    """

    def __init__(self, session, state_type, parser_type):
        # Inicializa a máquina de estados, parser e sessão
        self.sm = SMFactory(type=state_type)
        self.parser = ParserFactory(type=parser_type)
        self.session = self.parser.session(session=session)

    def build_steps(self):
        # Chama método de construção de estados
        steps = self.sm.build_steps(session=self.session)

        # Traduz os estados para a linguagem do capella
        return [self.parser.step(step) for step in steps]


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

    def start(self):
        # Constrói todos os estados do modelo
        self.states = self.model.build_steps()

    def next_step(self):
        # Vai para o próximo estado do modelo, se houver
        if len(self.states) > self.step + 1:
            self.step = self.step + 1

            print("----> Step", self.step)
            return self.states[self.step]

        # Se não, a simulacao termina
        return None

    def automatic(self):
        if self.states == None:
            self.start()

        return self.next_step()


class CapellaModelAPI:
    def __init__(self):
        self.model = CapellaModel()
        self.model.open(aird_path)

    def build_command_interface(self):
        """
            Constrói no capella uma interface de comando
            para que o usuário gerencie os steps da simulação.

            Obs: enquanto ela não for construída, executaremos
            cada step da simulação de 1 em 1 segundo.
        """

        # TODO: create command board in capella

        pass

    def listen(self):
        """
            Fica escutando caso ocorra uma
            interação entre o usuário e a interface de comando.
            Se ocorrer, exibe o step requisitado pelo usuário.

        """

        # TODO: be always waiting for some command

        return 'automatic'

    def render_state(self, state=None):
        # TODO: render state in capella
        print(state)

    def read_session(self):
        # Read capella session
        return self.model.get_system_engineering()


class Simulator:
    """
    Essa classe interage em alto nível com o capella e a SM
    """

    def __init__(self, config):
        # Carrega configurações
        self.state = None
        self.config = self._parse_config(config=config)

        # Inicializa o capella
        self.capella = CapellaModelAPI()

        # Inicializa capella e máquina de estados
        self.state_machine = self._load_state_machine()

    def run(self):
        # Constrói a interface de comando
        self._build_command_interface()

        # Escuta comandos enviados
        while True:
            self._command_handler()
            time.sleep(5)

            if self.state == None:
                print("End of simulation!")
                return

    def _build_command_interface(self):
        self.capella.build_command_interface()

    def _command_handler(self):
        """
            Escuta e executa comandos.
        """
        command = self.capella.listen()  # be awaiting for a new command
        self._command_to_state(command)
        self._render_state()

    def _command_to_state(self, command):
        self.state = self._map_commands(command)()

    def _render_state(self):
        if self.state:
            self.capella.render_state(state=self.state)

    def _map_commands(self, command):
        # Mapeia strings a comandos
        commands = {
            'start': self.state_machine.start,
            'next_step': self.state_machine.next_step,
            'automatic': self.state_machine.automatic
        }
        return commands[command]

    def _get_session(self):
        return self.capella.read_session()

    def _load_state_machine(self):
        # Carrega a state machine
        session = self._get_session()
        state_type = self.config['state_type']
        parser_type = self.config['parser_type']

        return SM(
            session=session,
            state_type=state_type,
            parser_type=parser_type
        )

    @staticmethod
    def _parse_config(config):
        # Cria configurações válidas
        parsed_config = {
            'model_path': 'default',
            'state_type': 'sismic',
            'parser_type': 'sismic'
        }

        for key, value in config.items():
            parsed_config[key] = value if key in parsed_config else None

        return parsed_config


simulator = Simulator(config={
    'model_path': 'default',
    'state_type': 'sismic',
    'parser_type': 'sismic'
})

simulator.run()
