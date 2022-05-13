# name                 : Export state mchine information to yaml
# script-type          : Python
# description          : Export state mchine information to yaml
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

# include needed for the Capella modeller API
include('workspace://Python4Capella/simplified_api/capella.py')
if False:
    from simplified_api.capella import *

# Retrieve the Element from the current selection and its aird model path
selected_elem = CapellaElement(CapellaPlatform.getFirstSelectedElement())
aird_path = '/'+ CapellaPlatform.getModelPath(selected_elem)

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

model = CapellaModel()
model.open(aird_path)

class StateMachineSimulator:
    def __init__(self):
        pass

    def state_machine_to_yaml(self):
        pass

    def run_simulation(self):
        state_machine_yaml = self.state_machine_to_yaml()
        for step in steps:
            pass

'''
# Planejamento da classe
- métodos
  - state_machine_to_yaml
  - run_simulation
      - método privado: 
      - 
'''

# gets the SystemEngineering
se = model.get_system_engineering()
logical_architecture = se.get_logical_architecture()
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

print(states_machines)