from pytest_unordered import unordered

from sismic.io import import_from_yaml


def test_simulator_config(simulator):
    assert simulator.config == {'model_path': 'default',
                                'state_type': 'sismic', 'parser_type': 'sismic'}


def test_sessions(simulator):
    mock_statechart = import_from_yaml(filepath='tests/mocks/mock.yaml')

    assert len(simulator.state_machine.model.sessions) == 6

    for statechart in simulator.state_machine.model.sessions:
        assert statechart.root == mock_statechart.root
        assert statechart.states == mock_statechart.states
        assert statechart.transitions == unordered(mock_statechart.transitions)
