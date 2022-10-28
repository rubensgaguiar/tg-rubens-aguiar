import re
import io
import PySimpleGUI as sg

from PIL import Image, ImageTk
from plantweb.render import render


class CommandInterface:
    def __init__(self):
        layout = [
            [sg.Text("State Machine Simulator")],
            [sg.Image(size=(300, 300), key='-IMAGE-')],
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
        images = []
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

                outfile = render(
                    tmp_plantuml,
                    engine='plantuml',
                    format='png',
                    cacheopts={
                        'use_cache': False
                    }
                )

                im = Image.open(io.BytesIO(outfile[0]))
                images.append(im)

            new_im = self._combine_imgs(images)
            tk_im = ImageTk.PhotoImage(image=new_im)
            self.command_interface.window['-IMAGE-'].update(data=tk_im)

            # TODO: Otimizar a geração de imagens, possíveis soluções:
            #       1. Salvar na memória imagens geradas para não ficar gerando novamente caso o usuário clique em voltar
            #       2. Gerar imagens antecipadamente, quando o usuário clicar em next, 
            #          printar a próxima imagem que já estava gerada e depois de printar,
            #          já carregar a próxima imagem.



    def read_session(self):
        # Read capella session
        return self.model.get_system_engineering()

    def _combine_imgs(self, images):
        widths, heights = zip(*(i.size for i in images))

        horizontal, width, height = self._find_aspect(widths, heights)

        new_im = Image.new('RGB', (width, height))

        offset = 10

        if horizontal:
            for im in images:
                new_im.paste(im, (offset, 0))
                offset += im.size[0]
        else:
            for im in images:
                new_im.paste(im, (0, offset))
                offset += im.size[1]

        new_im.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

        return new_im


    def _change_plantuml_color(self, plantuml, state, color):
        pattern = r'"{state}"(.*){{'.format(state=state)

        for m in re.finditer(pattern, plantuml):
            end = m.end() - 1
            tmp_plantuml = plantuml[:end] + color + " " + plantuml[end:]

        return tmp_plantuml

    def _find_aspect(self, widths, heights):
        total_height = sum(heights)
        max_width = max(widths)

        total_width = sum(widths)
        max_height = max(heights)

        is_horizontal = abs(max_width / total_height - 16/9) > abs(total_width / max_height - 16/9)

        if is_horizontal:
            return True, total_width, max_height
        else:
            return False, max_width, total_height
