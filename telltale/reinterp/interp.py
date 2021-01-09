from .ast import Stage


def interp(stage, states):
    assert isinstance(stage, Stage)
    stage.exec(states)
