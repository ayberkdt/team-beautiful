# EASA kit · 05 — Aircraft Flight Manual Supplement (draft) + pilot checklist card

**Status: competition draft.** Structure and wording are ours [Y]; the Extra NG POH and its canopy-opening procedure
were **not** read (doc 23 §5), so every abnormal/emergency action below must be agreed with the TC holder. The
supplement is listed among the change documents in CS-SC110a §5 [D] and in `retrofit_plan.md` step 11. Legend texts
are the four used everywhere in the kit (mock-up, logic, requirements R-7/R-8): **CANOPY LOCKED · CANOPY UNLOCKED ·
CANOPY OPEN · CANOPY SENS**.

---

## AFMS — LOCK-SENSE canopy lock alert system (Extra NG)

### 1. General

This supplement applies when LOCK-SENSE is installed. It supplements, and does not replace, the basic AFM/POH. The
system senses that the canopy is seated and that each of the three shoot bolts is fully engaged, and it alerts the pilot
when it is not. **The pilot's handle check remains the primary means of verifying that the canopy is locked**; the green
light is an independent second confirmation.

### 2. Limitations

- No change to the operating limitations of the basic AFM.
- The system is non-required equipment. With the system inoperative the aircraft may be flown as before the
  modification, after the defect has been deferred and the placard **CANOPY WARN INOP** fitted (Part-ML ML.A.403(b)(1),
  (d); research note R3 [D-ag]).
- Placard near the annunciator: **"CANOPY — GREEN = LOCKED. NO GREEN, NO TAKE-OFF."** [Y]

### 3. Emergency procedures

**CANOPY (red, flashing) + voice "CANOPY" in flight**
1. Fly the aeroplane; reduce speed (target to be set with the TC holder) [Y].
2. **Do not** attempt to close or re-latch the canopy in flight (BFU 21-0469 fatal case, doc 23 §6b Q5 [D]).
3. Land as soon as practicable.
4. After landing: report in the technical log; the event log will be downloaded (ICA task T4).

Canopy separation and bail-out: **unchanged**, follow the basic AFM. The system does not obstruct emergency opening or
jettison (requirement R-9).

### 4. Abnormal procedures

**CANOPY UNLOCKED (amber + one chime) during taxi**
1. Stop the aeroplane, throttle idle.
2. Canopy — re-lock: handle fully aft to the end stop, LOCK legend visible.
3. Confirm **green CANOPY LOCKED** before continuing.

**CANOPY (red, flashing) + voice at take-off power, on the ground**
1. Reject the take-off if it is safe to do so [Y; the reject rule needs the TC holder's procedure].
2. Re-lock as above; do not take off without green.

**CANOPY SENS (amber on the ground)**
1. The system cannot confirm the lock state. Treat the canopy as **not locked**.
2. Perform the handle check; if the light remains, the system is inoperative → defer (§2), fit the placard, report.
3. At take-off power a SENS indication turns red: "unconfirmed is not locked" (fault demo, doc 23 §3).

**No green after locking (light dark)**
1. Lamp test (power-up test). If the lamps work, re-lock and check again.
2. If still dark: system inoperative → as CANOPY SENS step 2.

### 5. Normal procedures

**Before engine start / pre-flight**
- MASTER ON → power-up test: all legends and the voice for 3 s [R-11].
- Canopy closed and locked: handle fully aft to the end stop, LOCK legend visible, **green CANOPY LOCKED ON**.

**Before take-off (line-up check)**
- **CANOPY — GREEN** (call it aloud in two-crew operation).

**After landing**
- Canopy may be opened for taxi only where the basic AFM allows it; an open canopy in taxi shows the white OPEN
  advisory, not an alert.

### 6. Performance

No change.

### 7. Weight and balance

Add the installed equipment to the equipment list: mass 0.45–0.82 kg as estimated (kit `07`), to be replaced by the
weighed value after installation; arm per the installation drawing.

### 8. Systems description

Four inductive proximity sensors on the fuselage rim (one per shoot-bolt lug, one seated) feed an alert unit on its own
circuit breaker. Green CANOPY LOCKED lights only when all four confirm (hardware AND). Alert levels depend on the phase
(parked / taxi / take-off power / airborne), detected from the throttle position and the indicated airspeed. The unit
logs every state change with a time stamp. Annunciator: rear-seat glareshield, repeater in the front cockpit.

---

## Pilot checklist card (A6, laminated) [Y]

| When | Item | Expected |
|---|---|---|
| Master on | Power-up test | all legends + voice, 3 s |
| Before start | Canopy handle | fully aft, LOCK legend visible |
| Before start | Canopy light | **GREEN — LOCKED** |
| Line-up | Canopy | **GREEN** (call out) |
| Any amber / red / SENS on the ground | Stop, re-lock | green, or defer + placard |
| Red + voice in flight | Fly, slow down, do not touch the canopy | land as soon as practicable |
