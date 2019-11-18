from typing import Dict


def get_config(config: Dict, arg_name: str):
    """Get arg value if arg_name exists in the config.

    Arguments
    ---------
    config: dict
    arg_name: str

    """
    value = config.get(arg_name, 'not specified')
    if value == 'not specified':
        raise ValueError(f'Argument "{arg_name}" was not specified\n\n{config}')
    return value
