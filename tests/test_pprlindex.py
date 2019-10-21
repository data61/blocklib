import os
from blocklib import PPRLIndex

def test_init():
    """Test constructor for base class PPRLIndex."""
    pprl = PPRLIndex()

    assert pprl.rec_dict = None
    assert pprl.ent_id_col = None
    assert pprl.rec_id_col = None
    assert pprl.revert_index = {}
    assert pprl.attr_select_list = {}
    assert pprl.stats = {}
