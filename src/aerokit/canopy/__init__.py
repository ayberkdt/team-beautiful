"""Canopy "not locked" alert retrofit: latch geometry, sensors, warning logic, safety analysis (EASA final 2026).

Modules
-------
mechanism   Extra NG shoot-bolt latch facts (AAIB-28120) and the trip-point tolerance analysis.
sensors     sensor channels with self-checking codes and fault injection.
logic       the alert unit: flight-phase state machine, annunciation, sensor-fault handling, event log.
fta         independent-event fault-tree algebra, minimal cut sets, importance measures.
montecarlo  per-flight Monte Carlo of missed alerts and false alarms vs sensor architecture, with the pilot's response.
barriers    ERCS barrier comparison with / without the system (reuses ``aerokit.investigation.ercs_score``).
fmea        the FMEA table of the recommended installation.

The system detects an unlocked or partially locked canopy. It does **not** detect the bonding defect / fatigue
cracking that AAIB found as the cause of the G-MIIL accident; see ``docs/23_easa_canopy_retrofit.md``.
"""
from aerokit.canopy.logic import AlertLevel, AlertOutput, CanopyAlertUnit, CanopyState, FlightInputs, Phase
from aerokit.canopy.mechanism import EXTRA_NG, LatchMechanism
from aerokit.canopy.sensors import Channel, Reading

__all__ = ["AlertLevel", "AlertOutput", "CanopyAlertUnit", "CanopyState", "Channel", "EXTRA_NG", "FlightInputs",
           "LatchMechanism", "Phase", "Reading"]
