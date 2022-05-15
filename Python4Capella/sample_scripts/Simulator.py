from abc import ABC
from typing_extensions import Self


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
  def build_states(self):
    # abstract
    pass


class SismicParser(Parser):
  """
    Traduz sessões do capella para o modelo
    Traduz estados do modelo para o capella
  """
  def session(self, session=None):
    logical_architecture = session.get_logical_architecture()
    logical_system = logical_architecture.get_logical_system()
    owned_logical_components = logical_system.get_owned_logical_components() # Inside LC 1

    states_machines = []

    for owned_logical_component in owned_logical_components: # LC 1 Component
        for state_machine in owned_logical_component.get_owned_state_machines(): # Máquina de Estado
            state_machine_obj = {
                'name': state_machine.get_name(),
            }
            regions = []
            for owned_region in state_machine.get_owned_regions(): # Região da máquina
                print(owned_region.get_name())
                owned_region_obj = {
                    'name': owned_region.get_name()
                }
                
                states = []
                for owned_state in owned_region.get_owned_states(): # Estado ou Modo
                    print(owned_state.get_name())
                    owned_state_obj = {
                        'name': owned_state.get_name(),
                        'incoming': [],
                        'outgoing': [],
                        'realized_states': [],
                        'realizing_states': []
                    }

                    for incoming in owned_state.get_incoming(): # Entradas
                        print(incoming.get_name())
                        owned_state_obj['incoming'].append({
                            'name': incoming.get_name()
                        })
                    for outgoing in owned_state.get_outgoing(): # Saídas
                        print(outgoing.get_name())
                        owned_state_obj['outgoing'].append({
                            'name': outgoing.get_name()
                        })
                    for realized_states in owned_state.get_realized_states(): # Estados Realizados
                        print(realized_states.get_name())
                        owned_state_obj['realized_states'].append({
                            'name': realized_states.get_name()
                        })
                    for realizing_states in owned_state.get_realizing_states(): # Estados em Realização
                        print(realizing_states.get_name())
                        owned_state_obj['realizing_states'].append({
                            'name': realizing_states.get_name()
                        })

                    states.append(owned_state_obj)

                owned_region_obj['states'] = states
                regions.append(owned_region_obj)
            state_machine_obj['regions'] = regions
            states_machines.append(state_machine_obj)

    return sismic.import_from_yaml(states_machines) # algo assim...


class SismicSM(SM):
  def build_states(self, session):
    # TODO: build states in sismic
    pass


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
  def __init__(self, type) -> None:
    # Possíveis modelos de parser
    products = {
      'sismic': SismicParser
    }
    super().__init__(type, products)

  def __new__(cls: type[Self]) -> Self:
    # Fabrica o modelo solicitado
    return super().__new__()


class SMFactory:
  """
    Fábrica de Máquina de Estados
  """
  def __init__(self, type) -> None:
    # Possíveis modelos de parser
    products = {
      'sismic': SismicSM
    }
    super().__init__(type, products)

  def __new__(cls: type[Self]) -> Self:
    # Fabrica o modelo solicitado
    return super().__new__()


class StateMachineModel:
  """
    Construção de um modelo de máquina de estados
  """
  def __init__(self, session, sm_type, parser_type):
    # Inicializa a máquina de estados, parser e sessão
    self.sm = SMFactory(sm_type=sm_type)
    self.parser = ParserFactory(parser_type=parser_type)
    self.session = self.parser.session(session=session)

  def build_states(self):
    # Chama método de construção de estados
    states = self.sm.build_states(session=self.session)

    # Traduz os estados para a linguagem do capella
    return [self.parser.state(state) for state in states]


class StateMachine:
  """
  Abstração da lógica de máquinas de estado.
  """
  def __init__(self, session, state_type, parser_type):
    # Inicializa os estados, o step e o modelo
    self.step = 0
    self.states = []

    self.model = StateMachineModel(
      session=session,
      state_type=state_type,
      parser=parser_type
    )

  def start(self):
    # Constrói todos os estados do modelo
    self.states = self.model.build_states()

  def next_step(self):
    # Vai para o próximo estado do modelo, se houver
    if len(self.steps) > self.step + 1:
      self.step = self.step + 1
    return self.states[self.step]


class Simulator:
  """
  Essa classe interage em alto nível com o capella e a SM
  """
  def __init__(self, config):
    # Carrega configurações
    self.state = None
    self.config = self._parse_config(config=config)

    # Inicializa capella e máquina de estados
    self.model = CapellaModel()
    self.state_machine = self._load_state_machine()

  def run(self):
    # Constrói a interface de comando
    self._build_command_interface()

    # Escuta comandos enviados
    self._command_listener()

  def _build_command_interface(self):
    # TODO: create command board in capella
    pass

  def _render_state(self):
    # TODO: render state in capella
    pass

  def _get_session(self):
    # Get capella session
    return self.model.get_system_engineering()

  def _command_listener(self):
    # TODO: be always waiting for some command
    command = None
    self.state = self.map_commands(command)()
    self.render_state()

  def _map_commands(self, command):
    # Mapeia strings a comandos
    commands = {
      'start': self.state_machine.start,
      'next_step': self.state_machine.next_step
    }
    return commands[command]

  @staticmethod
  def _parse_config(config):
    # Cria configurações válidas
    parsed_config = {
      'model_path': 'default',
      'state_type': 'sismic',
      'parser_type': 'sismic'
    }

    for key, value in config:
      parsed_config[key] = value if key in parsed_config else None

    return parsed_config

  def _load_state_machine(self):
    # Carrega a state machine
    session = self._get_session()
    state_type=self.config['state_type']
    parser_type=self.config['parser_type']

    return StateMachine(
      session=session,
      state_type=state_type,
      parser_type=parser_type
    )

simulator = Simulator({
  'model_path': 'default',
  'state_type': 'sismic',
  'parser_type': 'sismic'
})

simulator.run()
