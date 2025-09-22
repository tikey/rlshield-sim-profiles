from dataclasses import dataclass, field
from typing import Dict, List
import random
@dataclass
class Process:
    q:int=0; age:float=0.0; slack:float=10.0; order_ok:bool=True; busy:bool=False
@dataclass
class SystemState:
    t:int=0; processes:List[Process]=field(default_factory=list)
    res_cap:Dict[str,float]=field(default_factory=lambda:{"cpu":100.0,"mem":256.0,"energy":100.0})
    res_alloc:Dict[str,float]=field(default_factory=lambda:{"cpu":0.0,"mem":0.0,"energy":0.0})
    queue_cap:int=20; data_staleness:float=10.0; deadlines:List[int]=field(default_factory=lambda:[12,18,24])
    net_window_open:bool=True; rho:int=0; z_res:float=0.0; z_temp:float=0.0; z_net:float=0.0; z_order:float=0.0; z_data:float=0.0
    def barrier(self)->float: return min(self.z_res,self.z_temp,self.z_net,self.z_order,self.z_data)
def init_state(env_cfg, seed=None)->SystemState:
    if seed is not None: random.seed(seed)
    n=env_cfg.get("processes",3)
    st=SystemState(processes=[Process() for _ in range(n)],
                   res_cap=env_cfg.get("resource_cap",{"cpu":100.0,"mem":256.0,"energy":100.0}),
                   res_alloc=env_cfg.get("initial_alloc",{"cpu":30.0,"mem":64.0,"energy":0.0}),
                   queue_cap=env_cfg.get("queue_cap",20),
                   data_staleness=env_cfg.get("data_staleness",10),
                   deadlines=env_cfg.get("deadlines",[12,18,24]),
                   net_window_open=True,rho=0)
    return st
