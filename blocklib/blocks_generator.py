"""Class that implement final block generations."""
from .configuration import get_config


def generate_blocks(reversed_indices, config):
    """
    Generate final blocks given list of reversed indices from mutliparty data providers.
    :param reversed_indices: List of dictionaries
    :param config: dictionary
    :return: filtered_reversed_indices: List of dictionaries
    """
    algorithm = get_config(config, 'type')
    assert len(reversed_indices) >= 2

    if algorithm in {'lambda-fold'}:
        # decide final blocks keys - intersection of all reversed index keys
        block_keys = set(reversed_indices[0].keys())
        for reversed_index in reversed_indices[1:]:
            block_keys = block_keys.intersection(set(reversed_index.keys()))
        # filter reversed indices if keys not in block_keys
        filtered_reversed_indices = []
        for reversed_index in reversed_indices:
            reversed_index = {k: v for k, v in reversed_index.items() if k in block_keys}
            filtered_reversed_indices.append(reversed_index)
    else:
        raise NotImplementedError("Algorithm {} is not supported yet!".format(algorithm))
    return filtered_reversed_indices
