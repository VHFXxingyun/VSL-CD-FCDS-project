
---

## `test_report.md`

```md
# Version 1.0 Test Report

## Test Objective

The purpose of this test was to verify that Version 1.0 can complete the full single-target visual tracking loop:

- detect a red target
- track the target with the pan-tilt system
- remain stable near the center
- trigger `OUT` after stable lock
- return home after prolonged target loss

---

## Test Environment

### Hardware
- Raspberry Pi 5
- CSI camera
- ESP32-based servo expansion board
- two serial servos
- LED/output indicator connected to ESP32 output pin

### Software
- Raspberry Pi Python vision and control program
- ESP32 Arduino servo control firmware
- USB serial communication at `115200`

---

## Verified Functions

| Function | Result |
|---|---|
| CSI camera image acquisition | Pass |
| Red target detection | Pass |
| Target center extraction | Pass |
| Real-time pan-tilt tracking | Pass |
| Stable-zone anti-jitter logic | Pass |
| Stable hold timing | Pass |
| Automatic `OUT` trigger | Pass |
| Lost target waiting | Pass |
| Automatic `HOME` after long loss | Pass |

---

## Motion Convention Verification

| Command | Expected Motion | Result |
|---|---|---|
| `+10,0` | Right | Pass |
| `-10,0` | Left | Pass |
| `0,+10` | Down | Pass |
| `0,-10` | Up | Pass |
| `HOME` | Return to home position | Pass |
| `OUT` | Trigger output pin | Pass |

---

## Stable Lock Trigger Verification

### Test description
A red target was placed in front of the camera and manually aligned into the center area.

### Expected result
When the target remained stable within the stable region for at least `2.0 s`, the Raspberry Pi should send `OUT`, and the ESP32 should trigger the output pin.

### Result
Pass

---

## Lost Target Recovery Verification

### Test description
The target was removed from the field of view.

### Expected result
- short-term loss → `LOST_WAIT`
- prolonged loss → `LOST_HOME`
- Raspberry Pi sends `HOME`
- ESP32 returns the pan-tilt to the predefined home position

### Result
Pass

---

## Notes

- Target center smoothing significantly reduced oscillation during stable aiming.
- Hysteresis-based stable-zone thresholds improved lock stability near the image center.
- The current Version 1.0 is suitable for single-target demonstrations.
- Multi-target mission logic is reserved for the next version.
