import sys

if "pytest" in sys.modules:
    from simulator.core.capella_api import *
    from simulator.core.state_machine import *
else:
    # CapellaModelAPI
    include('workspace://Python4Capella/sample_scripts/simulator/core/capella_api.py')
    include(
        'workspace://Python4Capella/sample_scripts/simulator/core/state_machine.py')  # SM


class Simulator:
    """
    Essa classe interage em alto nível com o capella e a SM
    """

    def __init__(self, model, config):
        # Carrega configurações
        self.states = None
        self.config = self._parse_config(config=config)

        # Inicializa o capella
        self.capella = CapellaModelAPI(model=model)

        # Inicializa capella e máquina de estados
        self.state_machine = self._load_state_machine()

    def run(self):
        # Constrói a interface de comando
        self._build_command_interface()

        # Escuta comandos enviados
        while True:
            self._command_handler()

            if self.states == None:
                print("Simulation finalized!")
                return

    def _build_command_interface(self):
        sm_buttons = [state['name'] for state in self.state_machine.states]
        self.capella.build_command_interface(sm_buttons)

    def _command_handler(self):
        """
            Escuta e executa comandos.
        """
        command = self.capella.listen()  # be awaiting for a new command
        if command:
            self._command_to_state(command)
            self._render_states()

    def _command_to_state(self, command):
        self.states = self._map_commands(command)()

    def _render_states(self):
        if self.states:
            self.capella.render_states(states=self.states)

    def _map_commands(self, command):
        # Mapeia strings a comandos
        commands = {
            'next_step': self.state_machine.next_step,
            'previous_step': self.state_machine.previous_step,
            'finalize': self.state_machine.finalize,
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
