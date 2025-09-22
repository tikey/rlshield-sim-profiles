import random
from .state import SystemState
def inject_disturbance(s:SystemState,cfg,active):
    prob=cfg.get("prob",0.5); dur_lo,dur_hi=cfg.get("dur_range",[2,5])
    sev=cfg.get("severity",{"cpu":[10,30],"latency":[1,3],"age":[2,4],"queue":[2,5]})
    classes=cfg.get("classes",["net_drop","res_spike","temp_jitter","order_swap","data_stale","ctl_stall"])
    if not active and random.random()<prob:
        cls=random.choice(classes); dur=random.randint(dur_lo,dur_hi); p={}
        if cls=="res_spike": p={"cpu_up":random.uniform(*sev["cpu"]),"queue_up":random.randint(*sev["queue"])}
        elif cls=="temp_jitter": p={"slack_down":random.uniform(*sev["latency"])}
        elif cls=="net_drop": p={"drop":True}
        elif cls=="order_swap": p={"bad_order":True}
        elif cls=="data_stale": p={"age_up":random.uniform(*sev["age"])}
        elif cls=="ctl_stall": p={"stall":True}
        active={"class":cls,"remaining":dur,"params":p}
    if active:
        cls=active["class"]; p=active["params"]
        if cls=="res_spike":
            s.res_alloc["cpu"]=min(s.res_cap["cpu"], s.res_alloc["cpu"]+p.get("cpu_up",5.0))
            for pr in s.processes: pr.q=min(s.queue_cap, pr.q+p.get("queue_up",1)); s.rho=min(s.rho+1,5)
        elif cls=="temp_jitter":
            for pr in s.processes: pr.slack-=p.get("slack_down",1.0); s.rho=min(s.rho+1,5)
        elif cls=="net_drop": s.net_window_open=False; s.rho=min(s.rho+1,5)
        elif cls=="order_swap":
            if s.processes: s.processes[random.randrange(len(s.processes))].order_ok=False; s.rho=min(s.rho+1,5)
        elif cls=="data_stale":
            for pr in s.processes: pr.age+=p.get("age_up",1.0); s.rho=min(s.rho+1,5)
        elif cls=="ctl_stall":
            if s.processes: s.processes[random.randrange(len(s.processes))].busy=True; s.rho=min(s.rho+1,5)
        active["remaining"]-=1
        if active["remaining"]<=0: active={}
    return active
