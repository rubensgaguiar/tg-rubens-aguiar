import sys
import yaml

from collections import defaultdict
from sismic.io import import_from_yaml

if "pytest" in sys.modules:
    from simulator.parsers.abs_parser import *
else:
    include('workspace://Python4Capella/sample_scripts/simulator/parsers/abs_parser.py')


class SismicParser(AbstractParser):
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
                    owned_state_obj[key].append(element)

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

    def _append_state_machines(self, state_machines, capella_state_machines):
        for state_machine in capella_state_machines:  # Máquina de Estado
            state_machine_obj = self._add_name(state_machine)
            regions = self._build_regions(state_machine)

            state_machine_obj['regions'] = regions
            state_machines.append(state_machine_obj)

        return state_machines

    def _read_capella_state_machines(self, session):
        logical_architecture = session.get_logical_architecture()
        logical_system = logical_architecture.get_logical_system()
        owned_logical_components = logical_system.get_owned_logical_components()  # Inside LC 1

        state_machines = []

        state_machines = self._append_state_machines(
            state_machines, logical_system.get_owned_state_machines())

        for owned_logical_component in owned_logical_components:  # LC 1 Component
            state_machines = self._append_state_machines(
                state_machines, owned_logical_component.get_owned_state_machines())

        return state_machines

    def _dict_to_yaml_str(self, dictonary):
        yaml.dump(dictonary, sys.stdout)  # TODO: colocar isso num logger dps
        return yaml.dump(dictonary)

    def _parse_standard_dict(self, standard_dict):
        statechart_arr = []
        for key, value in standard_dict.items():
            statechart_dict = {}
            if key[1]:
                statechart_dict[key[0]] = key[1]

            statechart_dict.update(value)
            for key_tmp in ['states', 'transitions', 'parallel states']:
                if key_tmp in value:
                    statechart_dict[key_tmp] = self._parse_standard_dict(
                        value[key_tmp])

            statechart_arr.append(statechart_dict)

        return statechart_arr

    def _handle_empty_states(self, states, handle_states):
        # Handle missing states creating a empty state
        for transition in handle_states:
            if ('name', transition) not in states:
                states[('name', transition)] = {}

                # if transition == 'Deep History':
                #     states[('name', transition)]['type'] = 'deep history'

        return states

    def _capella_to_sismic_state_machines(self, state_machines):
        statecharts = []

        for state_machine in state_machines:
            parallel_states = {}
            for region in state_machine['regions']:
                initial = None
                states = {}
                parallels = []
                states_transitions = []

                # Fazer uma busca recursiva começando do primeiro region['states']
                # e ir pegando os próximos estados a partir do outgoing

                for state in region['states']:
                    if initial == None:
                        initial = state['name']

                    transitions = {}
                    has_parallel = len(state['outgoing']) > 1
                    for transition in state['outgoing']:
                        targets = transition.get_target()
                        triggers = [trigger.get_name()
                                    for trigger in transition.get_triggers()]

                        for target in targets:
                            target_name = target if target == None else target.get_name()
                            transitions[('target', target_name)] = {}
                            states_transitions.append(target_name)

                            parallel = {
                                'incoming': state['name'], 'outgoing': target_name}
                            if has_parallel:
                                # Resolve NonDeterministicError: esses estados são paralelos
                                parallels.append(parallel)

                            # if len(triggers) > 0:
                            #     transitions[('target', target_name)] = {'event': triggers[0]}

                    if transitions != {}:
                        states[('name', state['name'])] = {
                            'transitions': transitions
                        }

                states = self._handle_empty_states(states, states_transitions)

                parallel_states[('name', region['name'])] = {
                    'initial': initial,
                    'states': states
                }

            statecharts.append({
                'name': state_machine['name'],
                'root state': {
                    'name': 'root',
                    'parallel states': self._parse_standard_dict(parallel_states)
                }
            })

        return [{
            'statechart': statechart
        } for statechart in statecharts]

    def step(self, step=None):
        # TODO: logar essas informações do print abaixo em um logger

        # Print all steps
        # for attribute in ['event', 'transitions', 'entered_states', 'exited_states', 'sent_events']:
        #     print('{}: {}'.format(attribute, getattr(step, attribute)))

        # TODO: formatar o step para a linguagem do capella
        return step

    def sessions(self, session=None):
        capella_sms = self._read_capella_state_machines(session)
        sismic_sms = self._capella_to_sismic_state_machines(capella_sms)

        simic_yaml_strs = [self._dict_to_yaml_str(
            sismic_sm) for sismic_sm in sismic_sms]

        # TODO: criar um logger e logar o simic_yaml_str

        return [import_from_yaml(simic_yaml_str) for simic_yaml_str in simic_yaml_strs]
