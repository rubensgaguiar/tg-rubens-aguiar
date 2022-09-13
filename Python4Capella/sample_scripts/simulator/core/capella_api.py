import PySimpleGUI as sg


class CommandInterface:
    def __init__(self):
        layout = [
            [sg.Text("State Machine Simulator")],
            [sg.Button("NEXT")],
            [sg.Button("PREVIOUS")],
            [sg.Button("FINALIZE")]
        ]
        self.window = sg.Window("Demo", layout, location=(50, 50))


class CapellaModelAPI:
    def __init__(self, model):
        self.model = model
        self.command_interface = None

    def build_command_interface(self):
        """
            Constrói no capella uma interface de comando
            para que o usuário gerencie os steps da simulação.

            Obs: enquanto ela não for construída, executaremos
            cada step da simulação de 1 em 1 segundo.
        """

        # TODO: create command board in capella
        self.command_interface = CommandInterface()

    def listen(self):
        """
            Fica escutando caso ocorra uma
            interação entre o usuário e a interface de comando.
            Se ocorrer, exibe o step requisitado pelo usuário.

        """

        if self.command_interface:
            event, _ = self.command_interface.window.read()

            if event == "NEXT":
                return 'next_step'

            if event == "PREVIOUS":
                return 'previous_step'

            if event == sg.WIN_CLOSED or event == "FINALIZE":
                return 'finalize'

        return 'finalize'

    def render_states(self, states=None):
        # TODO: render state in capella
        for state in states:
            print("-->> MicroStep", state[1])
            print('event:', state[0].event)
            print('transition:', state[0].transition)
            print('entered_states:', state[0].entered_states)
            print('exited_states:', state[0].exited_states)
            print('sent_events:', state[0].sent_events)

    def read_session(self):
        # Read capella session
        return self.model.get_system_engineering()
