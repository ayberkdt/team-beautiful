"""ATC communications and surveillance: from signal to display information (Advionics 2026 challenge).

Modules: ``modes`` (Mode S / ADS-B decode and encode), ``modeac`` (SSR Mode A/C pulse trains), ``radar`` (PSR/SSR link
budgets, detection probability, coverage), ``tracker`` (alpha-beta / Kalman / IMM multi-sensor tracking),
``asterix`` (CAT048 monoradar target reports), ``clearance`` (ATC text -> structured clearance, readback check,
callsign correlation), ``channel`` (synthetic radio channel), ``commhealth`` (comm-state machine and advisory display
model), ``datalink`` (CPDLC uplinks as an alternate source), ``par`` (precision approach radar talk-down),
``ils`` (90/150 Hz DDM receiver with flag), ``asr_sapi`` (Windows speech in the loop), ``traffic`` (synthetic
scenario for the scope).
Everything here is an advisory prototype: it never creates a clearance and never commands the aircraft.
"""
