from typing import Any, Callable, Dict, List, Sequence, Optional, cast

from metaphone import doublemetaphone

from blocklib.validation import PSigSignatureModel
from blocklib.validation.psig_validation import PSigCharsAtSignatureSpec


def generate_by_feature_value(attr_ind: int, dtuple: Sequence):
    """Generate signatures by simply return original feature at attr_ind."""
    return dtuple[attr_ind]


def generate_by_char_at(attr_ind: int, dtuple: Sequence, pos: List[Any]):
    """ Generate signatures by select subset of characters in original features.

    >>> res = generate_by_char_at(2, ('harry potter', '4 Privet Drive', 'Little Whinging', 'Surrey'), [0, 3])
    >>> assert res == 'Lt'
    >>> res = generate_by_char_at(2, ('harry potter', '4 Privet Drive', 'Little Whinging', 'Surrey'), [":4"])
    >>> assert res == 'Litt'

    """
    sig = []
    feature = dtuple[attr_ind]

    # missing value
    if feature == '':
        return None

    max_ind = len(feature)
    for p in pos:
        if type(p) == int:
            p = min(p, max_ind - 1)
            sig.append(feature[p])
        elif ':' not in p:
            p = int(p)
            p = min(p, max_ind - 1)
            sig.append(feature[p])
        else:
            start_ind, end_ind = p.split(":")
            if start_ind != '' and end_ind != '':
                start_ind = int(start_ind)
                end_ind = int(end_ind)
                assert start_ind < end_ind, "Start index should be less than End index in {}".format(p)
                start_ind = min(start_ind, max_ind - 1)
                end_ind = min(end_ind, max_ind)
                c = feature[start_ind: end_ind]
            elif start_ind == '' and end_ind != '':
                end_ind = int(end_ind)
                end_ind = min(end_ind, max_ind)
                c = feature[:end_ind]
            elif start_ind != '' and end_ind == '':
                start_ind = int(start_ind)
                start_ind = min(start_ind, max_ind)
                c = feature[start_ind:]
            else:
                raise ValueError('Invalid pos argument: {}'.format(p))
            sig.append(c)

    return ''.join(sig)


def generate_by_metaphone(attr_ind: int, dtuple: Sequence):
    """Generate a phonetic encoding of features using metaphone.

    >>> generate_by_metaphone(0, ('Smith', 'Schmidt', 2134))
    'SM0XMT'

    """
    feature = dtuple[attr_ind]
    phonetic_encoding = doublemetaphone(feature)
    return ''.join(phonetic_encoding)


#################################################
########## Add strategy here ####################
#################################################
SIGNATURE_STRATEGIES = {
    'feature-value': generate_by_feature_value,
    "characters-at": generate_by_char_at,
    "characters_at": generate_by_char_at,
    'metaphone': generate_by_metaphone,
}  # type: Dict[str, Callable[..., str]]


def generate_signatures(signature_strategies: List[PSigSignatureModel],
                        dtuple: Sequence,
                        feature_to_index: Optional[Dict[str, int]] = None):
    """Generate signatures for one record.

    :param signature_strategies:
        A list of PSigSignatureModel instances each describing a strategy to generate signatures.

    :param dtuple:
        Raw data to generate signatures from

    :param feature_to_index:
        Mapping from feature name to feature index

    :return signatures: set of str
    """
    # signatures to return
    signatures = []

    # loop through each strategy

    for i, strategy in enumerate(signature_strategies):
        sig = []
        for spec in strategy:
            # arguments that we need to pass for any strategy
            attr = spec.feature
            if type(attr) == str:
                attr_name: str = cast(str, attr)
                assert feature_to_index, "Missing information to map from feature name to index"
                attr_ind = feature_to_index.get(attr_name, None)
                if attr_ind is None:
                    raise ValueError(f'Feature {attr} is not in the dataset')
            else:
                attr_ind = cast(int, attr)
            args = dict(attr_ind=attr_ind, dtuple=[str(x) for x in dtuple])

            # find the correct strategy function to call
            func = SIGNATURE_STRATEGIES.get(spec.type, None)

            if func is None:
                raise NotImplementedError(f'Strategy {spec.type} is not implemented yet!')
            else:
                if hasattr(spec, 'config'):
                    # For now that means it must be a PSigCharsAtSignatureSpec
                    args.update(cast(PSigCharsAtSignatureSpec, spec).config)
                s = func(**args)
                sig.append(s)
        signatures.append('{}_{}'.format(i, "_".join([x for x in sig if x is not None])))

    return signatures
