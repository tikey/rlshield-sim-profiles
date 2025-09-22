import random
from .state import init_state
from .invariants import compute_invariants
from .disturbances import inject_disturbance
from .policy import choose_action, apply_action

def run_episode(cfg, seed=None, log_steps=False):
    env=cfg["env"]; horizon=cfg.get("horizon",60)
    eps_up=cfg.get("epsilon_up",1.0); eps=cfg.get("epsilon",0.5)
    s=init_state(env, seed=seed)
    for p in s.processes: p.slack=random.choice(env.get("deadlines",[12,18,24]))/2
    s.res_alloc.update(env.get("initial_alloc",{}))
    step_log=[]; active={}; t_rec=None; kept_in_A=True; seen_funnel=False
    for t in range(horizon):
        s.t=t
        for pr in s.processes:
            if s.net_window_open and pr.q>0: pr.q-=1
            pr.age+=0.2; pr.slack-=0.5
        s.net_window_open = random.random() < env.get("net_window_open_prob",0.75)
        active = inject_disturbance(s, cfg.get("disturbances",{}), active)
        compute_invariants(s); B=s.barrier()
        if B<0: kept_in_A=False
        if not seen_funnel and B<=eps: seen_funnel=True
        action=choose_action(s, rho_star=cfg.get("policy",{}).get("rho_star",1))
        apply_action(s, action)
        compute_invariants(s); B=s.barrier()
        if seen_funnel and t_rec is None and B>=eps_up: t_rec=t
        if log_steps:
            step_log.append({"t":t,"B":B,"z_res":s.z_res,"z_temp":s.z_temp,"z_net":s.z_net,"z_order":s.z_order,"z_data":s.z_data,
                             "rho":s.rho,"action":action,"net_open":s.net_window_open,"active_disturbance":active.get("class") if active else None})
    return {"kept_in_A":kept_in_A,"t_rec": t_rec if t_rec is not None else horizon, "rho_max": s.rho, "summary_B": float(B), "steps_log": step_log}
