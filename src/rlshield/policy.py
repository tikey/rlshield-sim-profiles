from .state import SystemState
def predict_barrier_after_action(s:SystemState, action:str)->float:
    z_res,z_temp,z_net,z_order,z_data=s.z_res,s.z_temp,s.z_net,s.z_order,s.z_data; rho=s.rho
    if action=="isolate": rho=max(0,rho-1)
    elif action=="throttle": z_res+=2.0; [setattr(pr,'q',max(0,pr.q-1)) for pr in s.processes]
    elif action=="retime": z_temp+=1.0; [setattr(pr,'slack',pr.slack+1.0) for pr in s.processes]
    elif action=="rebind": z_res+=1.5; s.res_alloc["cpu"]=max(0.0,s.res_alloc["cpu"]-5.0)
    elif action=="rollback": z_order=max(z_order,0.5); z_data+=1.0; [ (setattr(pr,'order_ok',True), setattr(pr,'age',max(0.0,pr.age-2.0))) for pr in s.processes ]
    elif action=="degrade": z_temp+=0.5; z_res+=0.5
    elif action=="fence": z_order=1.0
    elif action=="sanitize": [setattr(pr,'q',max(0,pr.q-2)) for pr in s.processes]; z_res+=1.0
    return min(z_res,z_temp,z_net,z_order,z_data)
def clone_state(s:SystemState)->SystemState:
    from .state import SystemState, Process
    ns=SystemState(t=s.t, processes=[Process(q=p.q,age=p.age,slack=p.slack,order_ok=p.order_ok,busy=p.busy) for p in s.processes],
                   res_cap=dict(s.res_cap), res_alloc=dict(s.res_alloc), queue_cap=s.queue_cap,
                   data_staleness=s.data_staleness, deadlines=list(s.deadlines), net_window_open=s.net_window_open,
                   rho=s.rho, z_res=s.z_res, z_temp=s.z_temp, z_net=s.z_net, z_order=s.z_order, z_data=s.z_data)
    return ns
def choose_action(s:SystemState, rho_star:int=1)->str:
    actions=["isolate","throttle","retime","rebind","rollback","degrade","fence","sanitize"]
    if s.rho>rho_star: return "isolate"
    current=s.barrier(); best_a=None; best_gain=-1e9
    for a in actions:
        pred=predict_barrier_after_action(clone_state(s),a); gain=pred-current
        if gain>best_gain: best_gain, best_a=gain, a
    return best_a or "retime"
def apply_action(s:SystemState, action:str)->None:
    if action=="isolate": s.rho=max(0,s.rho-1); s.net_window_open=True
    elif action=="throttle":
        for pr in s.processes: pr.q=max(0,pr.q-1)
        s.res_alloc["cpu"]=max(0.0,s.res_alloc["cpu"]-2.0)
    elif action=="retime":
        for pr in s.processes: pr.slack+=1.0
    elif action=="rebind":
        s.res_alloc["cpu"]=max(0.0,s.res_alloc["cpu"]-5.0)
    elif action=="rollback":
        for pr in s.processes: pr.order_ok=True; pr.age=max(0.0, pr.age-2.0)
    elif action=="degrade":
        for pr in s.processes: pr.slack+=0.5
    elif action=="fence":
        for pr in s.processes: pr.order_ok=True
    elif action=="sanitize":
        for pr in s.processes: pr.q=max(0, pr.q-2)
