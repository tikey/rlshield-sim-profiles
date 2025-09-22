from .state import SystemState
def compute_invariants(s:SystemState):
    res_margins=[s.res_cap[k]-s.res_alloc.get(k,0.0) for k in s.res_cap]
    q_margin=min((s.queue_cap-p.q) for p in s.processes) if s.processes else 0.0
    z_res=min(min(res_margins) if res_margins else 0.0, q_margin)
    z_temp=min(p.slack for p in s.processes) if s.processes else 0.0
    z_net=1.0 if s.net_window_open else -1.0
    z_order=1.0 if all(p.order_ok for p in s.processes) else -1.0
    z_data=min((s.data_staleness-p.age) for p in s.processes) if s.processes else 0.0
    s.z_res,s.z_temp,s.z_net,s.z_order,s.z_data=z_res,z_temp,z_net,z_order,z_data
    return z_res,z_temp,z_net,z_order,z_data
