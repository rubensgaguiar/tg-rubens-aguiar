# Capella Statecharts Simulation 
###### Originally forked from rubensgaguiar/tg-rubens-aguiar

## Overview
The behavior of complex reactive event-based systems can be modeled with Statecharts. Statecharts support hierarchical structures of states, parallel execution, guarded transitions and actions.
This particular approach should (will) take as input a set of Mode State Machine diagrams (MSM) from Capella, translate them into the YAML structure and then feed them into the [Sismic](https://sismic.readthedocs.io/en/latest/) library, going back through this route to show the results of the simulation. 
The transition is done with [Python4Capella](https://github.com/labs4capella/python4capella), with future plans to show visually the execution of the simulation within Capella.

## YAML (_YAML Ain't Markup Language_)
The YAML specification is available [here](https://yaml.org/spec/1.2.2/). While Sismic statecharts can be defined entirely in Python code, defining them using YAML is preferable since it abstracts the coding language used.

The following YAML description defines an Elevator. A Statechart object can be created from it within Sismic (using the *import_from_yaml* method): 
```yaml
statechart:
  name: Elevator
  preamble: |
    current = 0
    destination = 0
    doors_open = True
  root state:
    name: active
    parallel states:
      - name: movingElevator
        initial: doorsOpen
        states:
          - name: doorsOpen
            transitions:
              - target: doorsClosed
                guard: destination != current
                action: doors_open = False
              - target: doorsClosed
                guard: after(10) and current > 0
                action: |
                  destination = 0
                  doors_open = False
          - name: doorsClosed
            transitions:
              - target: movingUp
                guard: destination > current
              - target: movingDown
                guard: destination < current and destination >= 0
          - name: moving
            transitions:
              - target: doorsOpen
                guard: destination == current
                action: doors_open = True
            states:
              - name: movingUp
                on entry: current = current + 1
                transitions:
                  - target: movingUp
                    guard: destination > current
              - name: movingDown
                on entry: current = current - 1
                transitions:
                  - target: movingDown
                    guard: destination < current
      - name: floorListener
        initial: floorSelecting
        states:
          - name: floorSelecting
            transitions:
              - target: floorSelecting
                event: floorSelected
                action: destination = event.floor
```
Which can then be visually described using PlantUML:

![image](https://user-images.githubusercontent.com/20509814/188492090-2f1c9478-3710-47e1-91b1-67e874eea4e5.png)


## Sismic (_Sismic Interactive Statechart Model Interpreter and Checker_)
Sismic is a statechart library for Python providing a set of tools to **define, validate, simulate, execute and test statecharts**. Here are some of its features:
  - A statechart interpreter offering a discrete, step-by-step, and fully observable simulation engine
  - Fully controllable simulation clock, with support for real and simulated time
  - Built-in support for expressing actions and guards using regular Python code, can be easily extended to other programming languages
  
Among other features. 
One feature of particular interest arises from the interpreter when executing transitions that are triggered simultaneously. In those cases, instead of executing using the document order, Sismic raises a ```NonDeterminismError```, indicating that there is no clear order of transitioning.
The execution starts with a Statechart object, which can be used to create an interpreter object:
```python
from sismic.io import import_from_yaml
from sismic.interpreter import Interpreter

# Load statechart from yaml file
elevator = import_from_yaml(filepath='examples/elevator/elevator.yaml')

# Create an interpreter for this statechart
interpreter = Interpreter(elevator)
```
When constructing the interpreter one single ```execute_once()``` call is needed to set the initial configuration:
```python
print('Before:', interpreter.configuration)

step = interpreter.execute_once()

print('After:', interpreter.configuration)
```

```
Before: []
After: ['active', 'floorListener', 'movingElevator', 'doorsOpen', 'floorSelecting']
```

The ```execute_once()``` method is similar to a "tick" or "run" method, returning simulation information (transitions processed, event consumed, entered/exited states).
Events can be externally sent to the simulation using the ```queue('event')``` method, and then processed using ```execute_once()```:
```python
interpreter.queue('click')
interpreter.execute_once()  # Process the "click" event

interpreter.queue('clack')  # An event name can be provided as well
interpreter.execute_once()  # Process the "clack" event

interpreter.queue('click', 'clack')
interpreter.execute_once()  # Process "click"
interpreter.execute_once()  # Process "clack"
```

Sismic runs synchronously by default, meaning that ```execute_once()``` calls are blocking operations. Thus, the simulation cannot proceed until all events are processed by calling the method in a loop or in another thread.
Sismic can alternatively be executed asynchronously using ```AsyncRunner```, that provides basic support for continuous async execution of statecharts.

## To-do

- [ ] https://github.com/CentroEspacialITA/capella-sim/issues/1
- [ ] #2
- #2

- Continue development of the capella state machine to YAML converter (must cover all relations between State Machines - this can be tested by converting to YAML, generating a graphical view with PlantUML and comparing both diagrams).
- Continue development of the Simulator class (essentially a wrapper around Sismic, but must communicate with Capella somehow)
- Check simulation visualization methods for Capella: graphical interfaces, mainly.
- Check validation/model checking techniques (can simulation logs/outputs from Sismic be used to validate the architecture automagically?)




