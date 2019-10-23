from typing import List, Dict, Sequence

import fuzzy


def generate_by_feature_value(attr_ind, dtuple, list_substrings_indices=[[0]]):
    """ Generate signatures by simply concatenating original features and selecting a substring (useful for dates for
     example).
    >>> res = generate_by_feature_value([2, 3], ('harry potter', '4 Privet Drive', 'Little Whinging', 'Surrey'))
    >>> assert res == {'Little WhingingSurrey'}
    >>> res = generate_by_feature_value([2, 3], ('harry potter', '4 Privet Drive', 'Little Whinging', 'Surrey'), list_substrings_indices=[[2,4], [5]])
    >>> assert res == {'tt', 'e WhingingSurrey'}
    """

    return set([''.join([dtuple[ind] for ind in attr_ind])[x[0]: x[1] if len(x) > 1 else None] for x in list_substrings_indices])


def generate_by_n_gram(attr_ind, dtuple, n):
    """Generate signatures by constructing n-grams.
    >>> res = generate_by_n_gram([0, 3], ('harry potter', '4 Privet Drive', 'Little Whinging', 'Surrey'), 2)
    >>> assert res == {'y ', 'ot', 'rS', 'Su', 'ry', 'er', 'ur', 'po', 're', 'ha', 'te', 'ar', 'tt', 'rr', ' p', 'ey'}
    """
    # concatenate all attributes as 1 string
    attribute = ''.join([dtuple[x] for x in attr_ind])

    # generate ngrams
    signatures = set()
    for i in range(len(attribute) - n + 1):
        gram = attribute[i: i + n]
        signatures.add(gram)
    return signatures


def generate_by_soundex(attr_ind, dtuple):
    """Generate a phonetic encoding of features using soundex.

    >>> sigs = generate_by_soundex([0, 1], ('Joyce', 'Wang', 2134))
    >>> assert sigs == {'W52', 'J2'}

    """
    features = tuple(dtuple[i] for i in attr_ind)
    soundex = fuzzy.Soundex(4)
    return {soundex(feature) for feature in features}


def generate_by_metaphone(attr_ind, dtuple):
    """Generate a phonetic encoding of features using metaphone.

    >>> sorted(generate_by_metaphone([0, 1], ('Smith', 'Schmidt', 2134)))
    ['SM0XMT', 'XMTSMT']

    """
    features = tuple(dtuple[i] for i in attr_ind)
    metaphone = fuzzy.DMetaphone()
    sigs = []
    for feature in features:
        phonetic_encoding = metaphone(feature)

        sigs.append(''.join(p.decode() for p in phonetic_encoding if p is not None))
    return set(sigs)


#################################################
########## Add strategy here ####################
#################################################
SIGNATURE_STRATEGIES = {
    'feature-value': generate_by_feature_value,
    'n-gram': generate_by_n_gram,
    'soundex': generate_by_soundex,
    'metaphone': generate_by_metaphone
}


def generate_signatures(signature_strategies: List[Dict],
                        attr_ind: List[int],
                        dtuple: Sequence):
    """Generate signatures for one record.

    :param signature_strategies:
        A list of dicts each describing a strategy to generate signatures.

    :param attr_ind:
        Specifies the positions of attributes used to get signatures

    :param dtuple:
        Raw data to generate signatures from

    :return signatures: set of str
    """
    # arguments that we need to pass for any strategy
    args = dict(attr_ind=attr_ind, dtuple=dtuple)

    # signatures to return
    signatures = set()

    # loop through each strategy

    for strategy in signature_strategies:
        config = strategy.get('config', {})

        # find the correct strategy function to call
        func = SIGNATURE_STRATEGIES.get(strategy['type'], None)

        if func is None:
            raise NotImplementedError(f'Strategy {strategy} is not implemented yet!')
        else:
            config.update(args)
            signatures = signatures.union(func(**config))

    return signatures
