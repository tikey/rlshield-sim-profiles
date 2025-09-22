import json
from rlshield.sim import run_episode
def test_smoke():
    cfg = json.load(open('experiments/configs/hard.json','r',encoding='utf-8'))
    r = run_episode(cfg, seed=1, log_steps=False)
    assert 'kept_in_A' in r and 't_rec' in r
