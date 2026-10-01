![FPV Autonomous Tracking demo](docs/images/tracking-demo.png)

# FPV Autonomous Vehicle Tracking & Virtual Autopilot Vision Studio

Advanced local computer-vision application for detecting, tracking and following road vehicles in aerial / FPV video. The project combines multi-object detection, persistent IDs, click-to-lock target selection, ByteTrack-style association, Kalman prediction, automatic target reacquisition, motion/size analysis, trajectory visualization and a virtual autopilot guidance layer in one Windows desktop interface.

> **Simulation only:** this software does not command a real aircraft, Pixhawk, PX4, MAVLink or MAVSDK. Flight-direction and speed outputs are visualization and control-logic simulations only.

## Application interface

![FPV Tracker V2 interface](docs/images/interface.png)

The interface provides direct access to the source, detector, model profile, tracker, compute device, processing mode, target-selection mode, target telemetry, virtual-autopilot controls, PID parameters, trajectory display, virtual camera follow, recording and export tools.

## Project overview

This second-generation tracker was designed as a more capable engineering platform than the first FPV tracker. It is built around a modular pipeline so detector, tracking, prediction, target management, guidance logic, visualization and recording are separated into independent components.

The application can process recorded drone footage, webcams and RTSP streams. Multiple vehicles are detected and tracked simultaneously, while one vehicle can be selected as the active target. The target can remain locked through short occlusions using motion prediction and can be reacquired when it reappears near the predicted position.

## Main features

- Aerial / FPV vehicle detection
- Multi-object tracking with persistent IDs
- CAR, TRUCK, BUS and MOTORCYCLE classes
- Click-to-select target
- AUTO CENTER target mode
- LARGEST VEHICLE target mode
- ByteTrack-style two-stage association
- Kalman-filter target prediction during temporary occlusion
- Automatic target reacquisition
- Target trajectory history and predicted trajectory
- Target motion estimation
- Target-size trend analysis
- Relative-distance trend estimation from apparent target size
- Virtual camera follow window
- Automatic follow-view zoom
- Configurable dead zone
- Virtual lateral / forward guidance output
- SIMPLE proportional controller
- Separate horizontal / vertical PID controller
- Configurable Kp / Ki / Kd values
- Virtual speed commands: SPEED UP / SLOW DOWN / HOLD SPEED
- Video-file, webcam and RTSP input
- REALTIME and EVERY FRAME processing modes
- Single-frame stepping when paused
- Video playback speed control
- Processed video recording
- Screenshot and clean-frame export
- Session telemetry CSV export
- CPU / CUDA / AUTO execution
- Runtime FPS and processing-status display
- Custom Ultralytics model discovery

## Detection backends

The detector layer supports Ultralytics models through two selectable families:

### YOLO

Profiles map to progressively larger checkpoints:

| Profile | Preferred model | Input size | Use case |
| --- | --- | ---: | --- |
| FAST | YOLO nano | 640 | maximum speed |
| BALANCED | YOLO small | 960 | general aerial tracking |
| ACCURATE | YOLO medium | 1280 | small / distant vehicles |

The application prefers current YOLO checkpoints and retains fallback support for earlier Ultralytics generations when the preferred checkpoint is unavailable.

### RT-DETR

RT-DETR is available as an alternative detector for higher-quality experiments where more compute is acceptable.

Model weights are downloaded separately and are intentionally not committed to this repository.

## Tracking architecture

The tracker maintains a separate state for each detected object and uses a ByteTrack-style strategy:

1. high-confidence detections are associated first;
2. lower-confidence detections can recover existing tracks;
3. motion prediction helps preserve IDs through short misses;
4. track age and lost duration are maintained independently;
5. one track can be promoted to the active target without stopping the other tracks.

Persistent labels such as `CAR #1` allow the same object to be followed across consecutive frames.

## Target selection and states

Available target-selection modes include:

- **CLICK TARGET** — click a vehicle directly in the video;
- **AUTO CENTER** — choose the vehicle closest to frame center;
- **LARGEST VEHICLE** — choose the visually largest candidate.

Target states include:

`SEARCHING` · `DETECTED` · `LOCKED` · `CENTERED` · `CORRECTING` · `OCCLUDED` · `PREDICTING` · `REACQUIRED` · `LOST`

The right-side target panel reports class, track ID, confidence, tracking mode, track age, lost duration, target motion, speed, target size, size trend and relative-distance trend.

## Occlusion prediction and reacquisition

When the target temporarily disappears, the application does not immediately discard it. A Kalman predictor estimates its next position and a predicted target box can be rendered while the target is occluded.

If a compatible detection appears close enough to the predicted position before the configurable timeout expires, the target is reacquired and tracking continues with the existing target identity.

This behavior is useful in aerial footage where vehicles can briefly pass behind trees, buildings, shadows or other traffic.

## Motion and target-size analysis

The analysis layer derives additional state from image-space movement:

- movement direction from target-center velocity;
- target speed in image coordinates;
- target area relative to the frame;
- `GROWING`, `SHRINKING` or `STABLE` size trend;
- `APPROACHING`, `RECEDING` or `STABLE` relative-distance trend.

Relative distance is a visual trend only. It is not a metric distance measurement because the application does not use a depth sensor.

## Virtual autopilot

The guidance system converts the selected target's offset from frame center into simulated control output.

Typical commands include:

- `LEFT`
- `RIGHT`
- `FORWARD`
- `BACK`
- `HOLD`
- combined diagonal commands such as `FORWARD + LEFT`

The dead zone can be adjusted so small target movement around the center does not produce continuous correction commands.

The panel also displays normalized lateral/forward percentages and X/Y tracking error.

### SIMPLE controller

A proportional mapping converts target displacement directly to virtual guidance output.

### PID controller

Independent horizontal and vertical PID controllers provide adjustable:

- `Kp`
- `Ki`
- `Kd`

PID output is visualized only and is not connected to physical flight hardware.

## Virtual speed command

Target-size history is used to produce an additional simulated speed command:

- apparent target shrinking → `SPEED UP`
- apparent target growing quickly → `SLOW DOWN`
- otherwise → `HOLD SPEED`

This is intended for control-logic visualization and experimentation rather than direct vehicle control.

## Virtual camera follow

**VIRTUAL CAMERA FOLLOW** opens a separate cropped follow view around the selected target. **Auto Zoom** adjusts the crop to keep the tracked object at a more consistent visual size.

The follow view does not alter the original input frame.

## Sources and playback

Supported source types:

- video files;
- webcam;
- RTSP stream.

Video-file mode provides:

- timeline seeking;
- pause / resume;
- single-frame stepping;
- playback-speed selection;
- source metadata such as resolution, FPS, frame count, duration and codec.

### Processing modes

**REALTIME** prioritizes keeping playback close to the source timing and may drop frames when inference cannot keep up.

**EVERY FRAME** processes every frame and is intended for detailed tracking review, even when playback becomes slower than real time.

## Recording and export

The recording pipeline can save an annotated MP4 together with a telemetry CSV containing synchronized tracking and guidance information.

Additional output tools include:

- **SAVE SCREENSHOT** — annotated frame;
- **SAVE CLEAN FRAME** — original frame without overlays;
- **EXPORT CSV** — session telemetry export.

Generated recordings, screenshots and exports are excluded from version control by default.

## GPU and CPU support

Available execution modes:

- **AUTO** — use CUDA when a working NVIDIA device is available;
- **CUDA** — request GPU execution;
- **CPU** — force CPU inference.

The GPU-selection helper can choose between multiple installed NVIDIA GPUs based on available runtime information.

## Custom models

Custom `.pt` detector weights can be placed in `custom_models/` or `models/`. The model registry discovers additional checkpoints while keeping standard profiles separate.

Model files are excluded from this repository because they are large third-party assets and can have their own licensing terms.

## Project structure

```text
app/             PySide6 GUI, source/target/controller panels and video widgets
analysis/        motion, velocity and target-size analysis
control/         proportional and PID virtual-autopilot logic
detection/       detector backend, worker, manager and model registry
export/          CSV export
prediction/      Kalman prediction, trajectory and reacquisition
recording/       video and telemetry recording
sources/         video, webcam and RTSP sources
tracking/        track manager, target manager and ByteTrack-style association
utils/           GPU info, settings, logging, datatypes and timing
visualization/   boxes, trajectories, target vector and flight-director overlays
custom_models/   optional user-provided model weights
models/          downloaded detector checkpoints
```

## Installation

Recommended environment:

- Windows 10 / 11
- Python 3.10+
- NVIDIA GPU optional

Run:

```text
install.bat
```

Then launch:

```text
start.bat
```

Main Python dependencies:

- NumPy
- OpenCV
- PySide6
- Ultralytics

## Privacy and local processing

After packages and model weights are installed, normal video, camera and RTSP processing runs locally on the machine. The application does not require cloud inference for its tracking pipeline.

## License and third-party software

This repository is distributed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See `LICENSE`.

The project uses third-party software that remains subject to its own licensing terms, including:

- **Ultralytics** — AGPL-3.0 for the open-source distribution, with separate commercial licensing available from Ultralytics;
- **OpenCV** — Apache License 2.0;
- **NumPy** — BSD-3-Clause;
- **PySide6 / Qt for Python** — LGPLv3 / GPLv3 / commercial licensing options.

See `THIRD_PARTY_LICENSES.md` for additional notes.

## Safety note

This repository implements computer-vision tracking and a virtual guidance simulation. It is not a certified navigation, collision-avoidance or flight-control system. Do not connect its simulated guidance percentages directly to a real aircraft without a separately engineered and validated flight-control architecture, safety layer, geofencing, fail-safes and appropriate testing.
