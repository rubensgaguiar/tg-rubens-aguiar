class MockTarget:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


class MockTransition:
    def __init__(self, name):
        self.name = name

    def get_target(self):
        return [
            MockTarget(self.name),
            MockTarget(self.name)
        ]

    def get_triggers(self):
        return []


class MockOwnedState:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_incoming(self):
        return [
            MockTransition(self.name + 'transition'),
            MockTransition(self.name + 'transition2')
        ]

    def get_outgoing(self):
        return [
            MockTransition(self.name + 'transition3'),
            MockTransition(self.name + 'transition4')
        ]

    def get_realized_states(self):
        return []

    def get_realizing_states(self):
        return []


class MockOwnedRegion:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_owned_states(self):
        return [
            MockOwnedState(self.name + 'ownedstate1'),
            MockOwnedState(self.name + 'ownedstate2')
        ]


class MockStateMachine:
    def __init__(self, name='sm'):
        self.name = name

    def get_name(self):
        return self.name

    def get_owned_regions(self):
        return [
            MockOwnedRegion(self.name + 'ownedregion1'),
            MockOwnedRegion(self.name + 'ownedregion2')
        ]


class MockLogicalComponent:
    def get_owned_state_machines(self):
        return [
            MockStateMachine(),
            MockStateMachine()
        ]


class MockLogicalSystem:
    def get_owned_logical_components(self):
        return [
            MockLogicalComponent(),
            MockLogicalComponent()
        ]

    def get_owned_state_machines(self):
        return [
            MockStateMachine(),
            MockStateMachine()
        ]


class MockLogicalArchitecture:
    def get_logical_system(self):
        return MockLogicalSystem()


class MockSystemEngineering:
    def get_logical_architecture(self):
        return MockLogicalArchitecture()


class MockCapellaModel:
    def get_system_engineering(self):
        return MockSystemEngineering()
