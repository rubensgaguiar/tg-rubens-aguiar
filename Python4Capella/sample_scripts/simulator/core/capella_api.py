import re
import io
import PySimpleGUI as sg

from PIL import Image, ImageTk
from plantweb.render import render


class CommandInterface:
    def __init__(self, buttons):
        layout = [
            [sg.Text("State Machine Simulator")],
            [sg.Image(key='-IMAGE-' + button) for button in buttons],
            [sg.Button(button) for button in buttons],
            [sg.Button("NEXT"), sg.Button("PREVIOUS"), sg.Button("FINALIZE")],
        ]
        self.window = sg.Window("Simulator", layout, location=(50, 50))


class CapellaModelAPI:
    def __init__(self, model):
        self.model = model
        self.command_interface = None
        self.images = {}
        self.buttons = []
        self.button = None

    def build_command_interface(self, buttons):
        """
            Constrói no capella uma interface de comando
            para que o usuário gerencie os steps da simulação.

            Obs: enquanto ela não for construída, executaremos
            cada step da simulação de 1 em 1 segundo.
        """

        self.buttons = buttons
        if len(buttons) > 0:
            self.button = buttons[0]

        self.command_interface = CommandInterface(buttons)

    def listen(self):
        """
            Fica escutando caso ocorra uma
            interação entre o usuário e a interface de comando.
            Se ocorrer, exibe o step requisitado pelo usuário.

        """

        if self.command_interface:
            event, _ = self.command_interface.window.read()

            if event in self.buttons:
                self.button = event
                for key in self.buttons:
                    self.command_interface.window['-IMAGE-' +
                                                  key].update(visible=key == self.button)
                return None

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
            step = state['step']
            name = state['name']
            plantuml = state['plantuml']

            print("-->> MicroStep", name)
            print('event:', step.event)
            print('transition:', step.transition)
            print('entered_states:', step.entered_states)
            print('exited_states:', step.exited_states)
            print('sent_events:', step.sent_events)

            for entered in step.entered_states:
                tmp_plantuml = self._change_plantuml_color(plantuml, entered, "#FFEE75")

            for exited in step.exited_states:
                tmp_plantuml = self._change_plantuml_color(tmp_plantuml, exited, "#84B1E4")

            print('plantuml', tmp_plantuml)

            outfile = render(
                tmp_plantuml,
                engine='plantuml',
                format='png',
                cacheopts={
                    'use_cache': False
                }
            )

            im = Image.open(io.BytesIO(outfile[0]))
            im.thumbnail((1024, 728), Image.Resampling.LANCZOS)
            self.images[name] = ImageTk.PhotoImage(image=im)

            for key in self.images:
                self.command_interface.window['-IMAGE-' + key].update(
                    data=self.images[key], visible=key == self.button)

            # TODO: Otimizar a geração de imagens, possíveis soluções:
            #       1. Salvar na memória imagens geradas para não ficar gerando novamente caso o usuário clique em voltar
            #       2. Gerar imagens antecipadamente, quando o usuário clicar em next,
            #          printar a próxima imagem que já estava gerada e depois de printar,
            #          já carregar a próxima imagem.

    def read_session(self):
        # Read capella session
        return self.model.get_system_engineering()

    def _change_plantuml_color(self, plantuml, state, color):
        pattern = r'"{state}"(.*){{'.format(state=state)

        for m in re.finditer(pattern, plantuml):
            end = m.end() - 1
            tmp_plantuml = plantuml[:end] + color + " " + plantuml[end:]

        return tmp_plantuml
