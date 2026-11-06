
# Introduction

A Precision Approach Radar (PAR) shows a controller the distance, lateral offset and height offset of an aircraft on final
approach. The controller reads these values and talks the pilot down in low visibility . FAA Order
JO 7110.65BB asks for one transmission about every 5 s . Advionics asks us to automate this chain: radar data in,
heading and glidepath corrections out, and a clear cue to the pilot, with no controller .

We chose the HYBRID direction (Figure). A display updates with every radar plot. Voice speaks only for
important changes. A 5 s voice rhythm is a limit of the human talk-down. A display can update each second and does not
block the radio. The words are FAA words, so a pilot who knows a PAR talk-down can read them at once.

We assume a working radar, an aircraft established on final and a decision height (DH) of 200 ft. This is an educational
concept on simulated and recorded data. It is not approved or ready for operational flight use.


Radar to pilot flow. The link from the ground to the cockpit is assumed.



# Synthetic data


# Purpose and limits

We found no measured PAR plots. A recorded track also cannot test the cue, because a recorded aircraft does not react to it.
So we built a closed loop: radar plots feed the cue, a pilot model flies the cue, and the aircraft moves. Faults start at a
known time and repeat with the same seed. The model tests the logic. It does not predict how a real pilot performs.


# Basic equations

Radar error uses the ICAO Annex 10 limits . X is the distance from the antenna; X and X are the lateral and
vertical deviation. We assume that X is half of the limit:



The aircraft is a point mass with airspeed X, heading X, sink rate X, crosswind X and vertical gust X:



Wind grows with height X from its 20 ft value X (X and X in ft). Gusts follow the low-altitude Dryden form
with turbulence level X, 15 kt when light :





The model covers the full chain at low order. Simulation results hold only inside this scope.



# Closed-loop result

The test follows the brief: start at 5 NM, 150 m right and 30 m high, 3 m/s crosswind, light turbulence, 100 seeds. The first
pilot model flies a rounded heading target that changes at most every 5 s, as a controller's heading does. The second flies
the marker into the display ring (Section 4).


Both cue laws remove the start offset. The ring also removes the overshoot. Lines are medians and bands are 5 to 95 % of 100 runs. The no-cue line ends where most runs leave the limits.


With the heading target, 99 of 100 runs reach DH, with a 95 % error of 37 m lateral and 11 m vertical. With the ring, 99 of 100
reach DH with 11 m and 9 m. That ring pilot reads drift from the marker with no error, so 11 m is a best case. With no cue, 1 of
100 reaches DH. For the heading target, a 4 s reaction gives 95 of 100, 90 % detection gives 96, a radar twice as good gives 100
and moderate turbulence gives 77 (ring: 76). A 300 m start at 5 m/s crosswind gives 65.


# Test on recorded data


# Agreement with Zurich

We used 1000 recorded tracks on Zurich runway 14 (ADS-B, October and November 2019) . They are the first 1000 tracks
that passed our filter, not a random sample. For this comparison the simulation starts on the path, with no steady wind, at A320
speed. Speed is an input (137 kt; recorded median 141 kt). Sink rate is a result: 726 ft/min against 747 ft/min recorded, with 5 to
95 % ranges of 640--849 and 667--842 ft/min.


Simulated scatter is wider than real scatter. (a, b) Scatter between flights: 1000 recorded tracks, 100 simulated runs and published ILS data . (c) Smolensk 2010: track from 13 report points, X0.5° limit, the five radio position calls (circles) and the first limit call of the cue in replay (diamond).


With the ring, simulated lateral scatter is 1.3 to 1.6 times the recorded value, and vertical scatter 1.3 to 2.1 times. With the
heading target, lateral scatter is 2.1 to 3.7 times the recorded value. A perfect radar does not reduce it (13 to 18 m), so the cause
is the heading steps. A perfect radar does reduce vertical scatter to 4 to 5 m, so PAR accuracy sets the vertical result. These
aircraft flew ILS, and the simulated aircraft flew the cue, so the two scatters are not a like-for-like test. We also removed one
height constant per flight, because ADS-B height differs by aircraft. Recorded vertical scatter is therefore a lower bound.


# Replay of the cue

Each track went through the Annex 10 radar model and the cue. The aircraft did not react to the cue. No pilot saw it. Of 1000
tracks, 985 stayed quiet, 5 reached advise, 4 caution and 6 warning. On 98.5 % of tracks the cue gave no guidance voice, and 275
tracks ended before DH. We did not check whether the 6 warnings were real excursions. At 90 % detection, 8 tracks ended in a false
RADAR LOST.

Recorded data changed the design. With no noise margin and no frame count, the closure flag fired on 397 of 1000 tracks. Simulation
had not shown this. With both it fires on 6. This is not an independent result, because we tuned the flag on the first 300 of these
tracks and on the Smolensk track. Of 66 go-arounds labelled on this runway , we could cut 22 out of the tracks. The cue
spoke before the climb in 11, with a median lead of 15 s.


# A radar talk-down: Smolensk 2010

This is the one event we found with a radar talk-down and stated deviations . We use deviations and calls only, with no
finding on blame. The radio said "on course, on glide path" five times outside the on-path band. The first correction came 5.5 s
before the first tree strike. In replay, our limit call would have come 88.5 s before it (median, 200 of 200 noisy runs). With the
limit switched off, "Coming down rapidly" would have come 16.5 s before it, in 167 of 200 runs. If the radar itself was wrong, as
the report suspects, the cue would inherit the error.


# The cue on the display


# Marker logic

ICAO treats the axes differently: in azimuth the pilot gets a heading, and in elevation the pilot corrects from position
information . The law follows this and uses radar position only. Three designs with a radar-derived rate failed
(0 of 100 runs reached DH), because a rate from 1 Hz plots is too noisy. With ground speed X, range X and path angle X,
the look-ahead time X, the aim track X and the aim sink rate X are:



Corrections are capped at 10° (5° inside 3 NM) and 1.2 m/s. We use symbols that pilots already know (Figure):

- Diamonds: where the path is. Scales as on an ILS, 1 dot = 1.25° lateral and 0.35° vertical.
- Marker: where you go. Real track and flight path angle from aircraft sensors, not from the radar. Wind needs no term.
- Ring: where to go. The point on the path X seconds ahead, at X and X. It turns green with the marker inside.

With the marker in the ring, X, so the offset decays with time constant X. An aircraft with no flight path marker cannot
use the ring. It can use the diamonds, the heading and the FAA words.


The symbols show the state before the pilot reads any text. (a) Off path: marker outside the ring. (b) On path: marker in the green ring. (c) Data 4 s old: hollow diamonds, no ring. (d) Radar lost: no diamonds, no ring. Replay frames; horizon position is schematic.



# Alert levels and voice

Below 1 dot the level is quiet. At 1 dot it is advise (stable approach limit ), at 1.3 dots caution (EGPWS Mode 5 soft alert
), and in a missed approach state warning. The limits X0.5° and X2° come from one report . The FAA
prints no number, and a real system takes them per runway. A call repeats only for 20 % more deviation. The cue ranks below every
aircraft alert . With an aircraft alert sounding, the cue is silent and a warning waits. With a transmission on, a routine
call is dropped. The display never waits. Voice repeats the display words .


# When data goes wrong

With no valid data, the cue gives no new guidance and no extrapolation (Table). A missed approach call is the reason,
then the condition . The pilot decides. The short GO AROUND flag on the mock-up points to that call. None of these calls applies
after DH.


Each fault has one display state and one call. The pilot never sees old data without a mark.


In 100 seeded runs, a 4 s delay and a radar stop were each told after 3 s in all runs, and a 400 m jump after 1 s in 90 runs. No frame
showed guidance without valid data. The weak point is a wrong but plausible plot. Far out, a jump below 200 m was not caught. Near the
runway, a jump below 150 m was mostly not caught. Such a jump moved the aircraft by up to 66 m (95 %).


# Limits and next step

No real pilot has flown this cue, so we claim no drop in workload. Voice less often than every 5 s departs from the FAA rhythm and needs
a pilot trial. Radar to cockpit needles is not new: Navy ACLS Mode II does this . Our work is the logic behind the display:
FAA fault rules, a silent path and a voice that yields to aircraft alerts, tested in a replay of 1000 recorded tracks.

For Advionics the airborne change is one display page and one data link, and the radar stays. The work fits its RF, embedded software and
test skills . The next steps are a pilot-in-the-loop simulator trial, recorded PAR plots to replace the assumed error
model, link latency tests and an independent height check against wrong plots.

% ---- references: extra pages, outside the 5-page limit -----------------
