"""Case 2 — "if communication with the tower is lost": comm-state machine, what reaches the display, SERA.14083.

    python 03_Advionics/cases/case_2_lost_comms/run.py [--set rule_set=ICAO_EUR_LEGACY] [--set rx_lost_from_s=120]

Reuses ``aerokit.atc.commhealth`` (CommHealthMonitor, AdvisoryDisplay), ``clearance.parse``, ``datalink`` (CPDLC as
the independent alternate) and ``aerokit.atc.lostcomm`` (rule-set timeline, display policy).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import Case, figure_set, md_table, save_figure  # noqa: E402

from aerokit.atc import clearance as CL  # noqa: E402
from aerokit.atc import lostcomm as LC  # noqa: E402
from aerokit.atc.commhealth import AdvisoryDisplay, AltLink, CommHealthMonitor, CommInputs, States  # noqa: E402
from aerokit.atc.datalink import Uplink, uplink_to_clearance  # noqa: E402

LOSS = (States.RX_LOST, States.TX_LOST, States.ALL_COMMS_LOST, States.ALTERNATE_AVAILABLE)


def build_ticks(p: dict) -> list[CommInputs]:
    cpdlc = AltLink("CPDLC (VDL Mode 2)", True, bus="BUS2", antenna="ANT3", authorised_for="datalink, non-urgent")
    down = AltLink(cpdlc.name, False, cpdlc.bus, cpdlc.antenna, cpdlc.authorised_for)
    msg_t = {int(m[0]) for m in p["messages"]}
    ticks = []
    for t in range(0, int(p["duration_s"]) + 1):
        tt = float(t)
        alt = (cpdlc,) if p["alt_up_from_s"] <= t < p["alt_down_from_s"] else \
            (down,) if p["alt_down_from_s"] <= t < p["recovered_from_s"] else ()
        we = t in p["our_calls_s"]
        to_us = t in msg_t and t != 45
        if t < p["degraded_from_s"]:
            x = CommInputs(tt, True, p["snr_good_db"], 0.92, heard_traffic=t % 7 == 0 or t in msg_t,
                           atc_to_us=to_us or t == 40, we_transmitted=we)
        elif t < p["rx_lost_from_s"]:
            x = CommInputs(tt, True, p["snr_degraded_db_level"], 0.55, dropout_fraction=0.2,
                           heard_traffic=t % 9 == 0 or t in msg_t, atc_to_us=to_us, we_transmitted=we)
        elif t < p["recovered_from_s"]:
            x = CommInputs(tt, False, None, None, we_transmitted=we, alt_links=alt)
        else:
            asks = t in p["if_read_calls_s"]
            x = CommInputs(tt, True, p["snr_good_db"], 0.9, heard_traffic=t % 5 == 0 or asks or t in msg_t,
                           atc_to_us=to_us or asks, atc_asks_if_read=asks, we_transmitted=we)
        ticks.append(x)
    return ticks


def parse_messages(p: dict) -> dict[float, CL.Clearance]:
    out, mid = {}, 0
    for t, text, flag in p["messages"]:
        mid += 1
        words: object = text
        if flag.startswith("low:"):
            k = int(flag.split(":")[1])
            words = [(w, 0.35 if i == k else 0.9) for i, w in enumerate(text.split())]
        out[float(t)] = CL.parse(words, own_callsign=p["own_callsign"], t_received=float(t), msg_id=mid,
                                 partial=(flag == "partial"))
    return out


def main(argv: list[str] | None = None) -> dict:
    c = Case(__file__, argv, "comm-state machine + display + lost-comm rule set")
    p = c.p
    mon = CommHealthMonitor(snr_degraded_db=p["snr_degraded_db"], conf_degraded=p["conf_degraded"],
                            dropout_degraded=p["dropout_degraded"], answer_timeout_s=p["answer_timeout_s"],
                            unanswered_for_loss=int(p["unanswered_for_loss"]),
                            silence_for_loss_s=p["silence_for_loss_s"], recover_ticks=int(p["recover_ticks"]),
                            no_signal_after_s=p["no_signal_after_s"])
    disp = AdvisoryDisplay(stale_after_s=p["stale_after_s"])
    msgs = parse_messages(p)
    ups = {float(t): Uplink(int(um), v, p["own_callsign"], float(t), 100 + i)
           for i, (t, um, v) in enumerate(p["cpdlc_uplinks"])}
    views, received_at = [], {}
    for x in build_ticks(p):
        st = mon.step(x)
        if x.t in msgs and x.carrier:                       # no carrier -> nothing received, nothing shown
            disp.receive(msgs[x.t])
            received_at[msgs[x.t].msg_id] = x.t
        if x.t in ups and any(a.up for a in x.alt_links):
            disp.receive(uplink_to_clearance(ups[x.t], p["own_callsign"]))
            received_at[ups[x.t].msg_id] = x.t
        v = disp.view(x.t, st, mon.no_signal_s if st == States.NO_SIGNAL else None)
        v["reasons"] = list(mon.reasons)
        v["carrier"] = x.carrier
        views.append(v)
    # invariants: shown ⊆ received-before-now; in loss states every voice item is STALE
    viol = sum(1 for v in views for it in v["items"]
               if it["msg_id"] not in received_at or received_at[it["msg_id"]] > v["t"])
    not_stale = sum(1 for v in views if v["state"] in (States.RX_LOST, States.ALL_COMMS_LOST, States.TX_LOST)
                    for it in v["items"] if not it["tag"].startswith("STALE"))
    first = {}
    for v in views:
        first.setdefault(v["state"], v["t"])
    loss_t = next((v["t"] for v in views if v["t"] >= p["rx_lost_from_s"] and v["state"] in LOSS), None)
    nosig_t = next((v["t"] for v in views if v["t"] >= p["rx_lost_from_s"] and v["state"] == States.NO_SIGNAL), None)
    ok_without_carrier = sum(1 for v in views if not v["carrier"] and v["banner"] == "VHF VOICE OK")
    changes = [views[0]] + [b for a, b in zip(views, views[1:]) if a["state"] != b["state"]]
    rows = [{"t": int(v["t"]), "state": v["state"], "banner": v["banner"],
             "shown": "; ".join(f"{it['text']} [{it['tag']}]" for it in v["items"]) or "-",
             "why": "; ".join(v["reasons"])[:110] or "-"} for v in changes]
    tl = LC.timeline(p["rule_set"], eat_min=p["eat_min"], eta_min=p["eta_min"])
    rs = LC.RULE_SETS[p["rule_set"]]
    hold = f"{rs.hold_min:g} min" if rs.hold_min is not None else "no fixed hold"
    key = [("carrier stops -> NO SIGNAL -> loss declared",
            (f"NO SIGNAL (amber, age counter) from {nosig_t:.0f} s = first second without carrier, " if nosig_t is not None
             else "") + (f"loss declared after {loss_t - p['rx_lost_from_s']:.0f} s" if loss_t is not None
                         else "loss not declared") + f"; 'VHF VOICE OK' shown without carrier: {ok_without_carrier} s"),
           ("items shown that were not received", f"{viol} (and {not_stale} non-STALE items in loss states)"),
           (f"rule set {p['rule_set']}", f"hold {hold}; squawk {'/'.join(rs.squawks)}; land within "
                                         f"{rs.land_within_min if rs.land_within_min is not None else '-'} min "
                                         f"after ETA/EAT")]
    body = ["## State changes and what the display showed", "",
            md_table(rows, ["t", "state", "banner", "shown", "why"]), "",
            f"States reached: {', '.join(f'{k} at {v:.0f} s' for k, v in first.items())}.", "",
            f"## Reminder timeline after the trigger — {rs.title}", "",
            md_table([{"t_min": "-" if m.t_min is None else f"{m.t_min:g}", "who": m.who, "text": m.text,
                       "source": m.source} for m in tl], ["t_min", "who", "text", "source"]), "",
            "## What may reach the display in each state (aerokit.atc.lostcomm.DISPLAY_POLICY)", "",
            md_table([{"state": s, **r} for s, r in LC.DISPLAY_POLICY.items()],
                     ["state", "new_voice_items", "old_items", "never"]), "",
            "Rule: a message lost on the channel cannot be reconstructed — not by ASR, not by AI. The display shows "
            "the last received item with its age (STALE) and the rule-set reminders; the crew decides."]
    figs = []
    if not c.args.no_fig:
        dw, S = figure_set(c)
        S.nicelik("t", "Time", "s", eksen="x")
        S.nicelik("state", "Communication state", None, eksen="y")
        S.varlik("State", renk="#3b3b3b", degistir=True)
        fig, ax = S.figur(oran=0.55)
        order = list(States.ALL)
        ax.step([v["t"] for v in views], [order.index(v["state"]) for v in views], where="post", **S.stil("State"))
        ax.set_yticks(range(len(order)), [s.replace("_", " ") for s in order])
        S.eksen(ax, x="t", y="state")
        figs.append(save_figure(S, fig, c.out, "C2_comm_state_timeline"))
    c.finish("Case 2 — lost communication", key, "\n".join(body), figs)
    return {"views": views, "violations": viol, "not_stale": not_stale, "first": first, "key": key,
            "ok_without_carrier": ok_without_carrier, "nosig_t": nosig_t, "loss_t": loss_t}


if __name__ == "__main__":
    main()
