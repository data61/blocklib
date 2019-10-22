

def generate_signature(signature_strategy, attr_ind, dtuple,
                       signature_strategy_config):
    """Generate signature for one record.

    Parameters
    ----------
    signature_strategy: str
        It specifies which strategy to generate signatures.

    attr_ind: list of integer
        It specifies the positions of attributes used to get signatures

    dtuple: tuple
        It contains raw record

    signature_strategy_config: dict
        It specifies the configuration for signature strategy

    Return
    ------
    signatures: list of str

    """
    # arguments that we need to pass for any strategy
    args = dict(attr_ind=attr_ind, dtuple=dtuple)
    args.update(signature_strategy_config)

    if signature_strategy == 'feature-value':
        signatures = generate_by_feature_value(**args)

    elif signature_strategy == 'n-gram':
        signatures = generate_by_n_gram(**args)

    else:
        raise NotImplementedError('Strategy {} is not implemented yet!')

    return signatures

def generate_by_feature_value(attr_ind, dtuple):
    """Generate signatures by concatenate original features."""
    return set([''.join([dtuple[ind] for ind in attr_ind])])


def generate_by_n_gram(attr_ind, dtuple, n):
    """Generate signatures by constructing n-grams."""
    # concatenate all attributes as 1 string
    attribute = ''.join([dtuple[x] for x in attr_ind])

    # generate ngrams
    signatures = set()
    for i in range(len(attribute) - n + 1):
        gram = attribute[i: i + n]
        signatures.add(gram)
    return signatures
