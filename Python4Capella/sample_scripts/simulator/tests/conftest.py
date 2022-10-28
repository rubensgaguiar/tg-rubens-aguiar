import pytest

from simulator.simulator import Simulator
from simulator.tests.mocks.mock_cappela import MockCapellaModel


@pytest.fixture
def simulator():
    model = MockCapellaModel()
    return Simulator(model, config={
        'model_path': 'default',
        'state_type': 'sismic',
        'parser_type': 'sismic'
    })
