import pytest
from yaclipy_tools.config import Config, ConfigTargetUnset, InvalidTarget


v1 = Config.var('v1 docs', 3)
v2 = Config.var('v2 docs', [1,2,3])

@Config.target(mutex='targetB targetC')
def targetA():
    v1(4)

@Config.target(mutex='targetC targetA')
def targetB():
    v1(5)

@Config.target(mutex='targetB targetA')
def targetC():
    v1(6)

@targetC.override()
def targetC():
    v1(60)

@Config.target(after='targetB targetA')
def postBA():
    v2([3,4,5])

@Config.target(before='postBA', after='targetB')
def interB_BA():
    v1(42)



def test_config_targets():
    assert(Config.targets.keys() == {'targeta', 'targetb', 'targetc', 'postba', 'interb-ba'})
    assert(Config.valid_targets() == {'targetA', 'targetB', 'targetC', 'targetB.postBA', 'targetA.postBA', 'targetB.interB-BA.postBA'})  
    @postBA.override(after='targetB targetC')
    def postBC():
        v2([1])
    assert(Config.valid_targets() == {'targetA', 'targetB', 'targetC', 'targetB.postBC', 'targetC.postBC', 'targetB.interB-BA.postBC'})
    assert(Config.is_valid_target('targetb.interB-ba.postBC'))
    assert(not Config.is_valid_target('targetb.interB-ba.postba'))

    with pytest.raises(ConfigTargetUnset):
        v1()
    with pytest.raises(InvalidTarget):
        Config.set_target('targeta.interb-ba.postba')
    Config.set_target('targetb.interb-ba.postbc')
    assert(v1() == 42)
    Config.set_target('targeta')
    assert(v1() == 4)
