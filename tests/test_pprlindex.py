import PPRLIndex

def test_init(self):
    """Test constructor for base class PPRLIndex."""
    pprl = PPRLIndex(nparty=2)

    assert pprl.nparty == 2
    assert pprl.rec_dict == {}
    assert pprl.rec_id_cols == {}
    assert pprl.ent_id_cols == {}
