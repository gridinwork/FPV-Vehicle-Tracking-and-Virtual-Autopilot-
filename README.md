![FPV Autonomous Tracking demo](docs/images/main-tracking.png)

# FPV Autonomous Vehicle Tracking & Virtual Autopilot Vision Studio

Advanced local computer-vision application for aerial / FPV vehicle detection, persistent multi-object tracking, target locking, Kalman prediction, target reacquisition, trajectory analysis and virtual autopilot guidance.

The software is designed as an engineering and research desktop tool. It can process drone video files, webcams and RTSP streams, maintain stable vehicle IDs, lock a selected vehicle as the target, estimate image-space motion and size trends, predict short occlusions, and visualize how a **virtual** flight director would correct the camera/drone position.

> **Safety note:** this version is a visual tracking and control-logic simulation. It does **not** send commands to motors, PX4, Pixhawk, MAVLink or MAVSDK. `LEFT`, `RIGHT`, `FORWARD`, `BACK`, `SPEED UP`, `SLOW DOWN`, PID percentages and related outputs are visualization/telemetry only.

## Application interface

![Application interface and loaded FPV source](docs/images/interface.png)

The interface combines source control, detector/model selection, tracker configuration, target state, prediction, virtual autopilot controls, playback, recording and telemetry in one window.

## Highlights

- Vehicle detection for `CAR`, `TRUCK`, `BUS` and `MOTORCYCLE`
- Ultralytics YOLO detector profiles with RT-DETR option
- FAST / BALANCED / ACCURATE model profiles
- CPU / CUDA / automatic device selection
- Multi-object tracking with persistent track IDs
- ByteTrack-style two-stage association implemented in the application
- Click-to-lock target selection
- Automatic center-priority target selection
- Largest-vehicle target mode
- Target loss timeout and automatic reacquisition
- Kalman-based target prediction during temporary occlusion
- Measured and predicted trajectory visualization
- Image-space target velocity and motion state analysis
- Target-size trend and relative-distance trend estimation
- Virtual speed commands: `SPEED UP`, `SLOW DOWN`, `HOLD SPEED`
- Configurable center dead zone
- Target vector and normalized X/Y error
- SIMPLE proportional controller simulation
- Independent horizontal/vertical PID controller simulation
- Virtual camera follow view with automatic zoom
- Real-time and every-frame video processing modes
- Frame-by-frame stepping while paused
- 0.25× to 2× playback speed
- Webcam, local video and RTSP input
- Annotated screenshot and clean-frame export
- Processed MP4 recording with synchronized CSV telemetry
- Session telemetry CSV export
- Runtime performance and GPU information
- Custom `.pt` model discovery

## Tracking pipeline

```text
Video / Webcam / RTSP
        │
        ▼
Vehicle detector
YOLO / RT-DETR
        │
        ▼
Multi-object association
persistent IDs
        │
        ▼
Target manager
click / auto-center / largest
        │
        ├───────────────┐
        ▼               ▼
Motion & size       Kalman prediction
analysis            + reacquisition
        │               │
        └───────┬───────┘
                ▼
         Virtual autopilot
       SIMPLE / PID guidance
                │
                ▼
 Visualization + recording
        + CSV telemetry
```

## Detection backends

The detector layer supports Ultralytics models through a common application backend.

### YOLO

The built-in profiles prefer the latest configured Ultralytics YOLO checkpoints and fall back to compatible YOLO11 / YOLOv8 checkpoints when required.

| Profile | Intended use | Typical input size |
| --- | --- | ---: |
| FAST | highest throughput | 640 |
| BALANCED | aerial vehicle tracking | 960 |
| ACCURATE | small/distant target quality | 1280 |

### RT-DETR

RT-DETR can be selected as an alternative detector for comparison and higher-quality inference scenarios.

Model weights are downloaded locally when needed and are intentionally **not committed** to this repository.

## Multi-object tracking

The tracking layer keeps multiple vehicles alive simultaneously and assigns stable IDs such as `CAR #1` or `TRUCK #4`.

The association strategy follows the main idea of ByteTrack-style matching:

1. high-confidence detections are associated first;
2. lower-confidence detections can recover an existing track;
3. short detection gaps do not immediately destroy track identity;
4. target selection is kept separate from background multi-object tracking.

This implementation is part of this application's tracking layer and does not require a separate MMTracking runtime.

## Target selection

Three target modes are provided:

- **CLICK TARGET** — click a vehicle in the video or select it from the tracking table;
- **AUTO CENTER** — automatically choose a suitable vehicle near the image center;
- **LARGEST VEHICLE** — select the largest visible candidate.

Target states include:

`SEARCHING` · `DETECTED` · `LOCKED` · `CENTERED` · `CORRECTING` · `OCCLUDED` · `PREDICTING` · `REACQUIRED` · `LOST`

## Kalman prediction and reacquisition

A locked vehicle is not immediately discarded when a detector misses it.

During a short occlusion:

- the state changes to `OCCLUDED / PREDICTING`;
- the Kalman predictor estimates the next target position;
- a predicted box/trajectory can be rendered;
- new detections are compared with the predicted position;
- a suitable match restores the previous target identity as `REACQUIRED`.

The lost-target timeout is configurable.

## Motion and relative-distance analysis

Target motion is calculated from image-space position history and can be labeled as moving left/right/forward/back or stable.

The target box area is also monitored:

- `GROWING`
- `SHRINKING`
- `STABLE`

From this trend the interface derives an approximate relative-distance state such as `APPROACHING` or `RECEDING`.

This is **not metric depth**. No physical distance in meters is inferred from a single camera in this module.

## Virtual autopilot / flight director

The target offset from the frame center is converted into simulated visual guidance:

- target left → `LEFT`
- target right → `RIGHT`
- target above → `FORWARD`
- target below → `BACK`
- target inside the dead zone → `HOLD`

Diagonal corrections can be combined, for example `FORWARD + LEFT`.

The interface also shows normalized error, lateral/forward percentages, target vector and virtual speed guidance.

### Controllers

**SIMPLE** uses proportional image-space correction.

**PID** provides independent horizontal and vertical controllers with editable `Kp`, `Ki` and `Kd` coefficients for simulation and tuning experiments.

These values are not calibrated aircraft-control commands.

## Virtual camera follow

The optional follow view creates a separate crop around the currently locked target. Auto Zoom can keep the target at a more consistent apparent size without modifying the original source video.

## Video playback and analysis

Supported local video formats depend on the installed OpenCV codecs and commonly include MP4, AVI, MOV, MKV, M4V and WMV.

Useful analysis controls include:

- play / pause / stop;
- timeline seeking;
- previous/next frame stepping while paused;
- 0.25×, 0.5×, 1×, 1.5× and 2× playback;
- **REALTIME** mode, which may drop frames to remain close to source time;
- **EVERY FRAME** mode for complete frame-by-frame analysis.

## Recording and telemetry

The application can record an annotated demonstration while simultaneously writing telemetry.

Typical outputs:

```text
recordings/
├── drone_tracking_YYYYMMDD_HHMMSS.mp4
└── drone_tracking_YYYYMMDD_HHMMSS.csv
```

The visual recording can include:

- bounding boxes and track IDs;
- locked target state;
- trajectories and predicted trajectory;
- dead zone and center crosshair;
- target vector;
- flight-director visualization;
- virtual guidance command;
- target-size / relative-distance trend;
- performance information.

`EXPORT CSV` can also save telemetry for the current analysis session to `exports/`.

## Sources

### Local video

Use **BROWSE...** to select a video file. Metadata such as resolution, FPS, frame count, duration and codec is shown in the interface.

### Webcam

A local camera can be used for live testing.

### RTSP

RTSP input is available for network-camera / FPV-stream experiments.

## Custom models

Custom Ultralytics-compatible `.pt` weights can be placed in:

```text
custom_models/
```

or the local `models/` folder. Large checkpoint files are excluded from Git.

## Installation

### Requirements

- Windows 10/11
- Python 3.10+
- NVIDIA GPU optional but recommended for higher-resolution aerial detection

Run:

```bat
install.bat
```

The installer:

1. creates `.venv`;
2. installs PyTorch;
3. attempts a CUDA-enabled PyTorch build when an NVIDIA GPU is available;
4. installs the application dependencies;
5. runs the detector/tracker/video self-check.

Start the application with:

```bat
start.bat
```

or manually:

```bat
.venv\Scripts\activate.bat
python main.py
```

## Core dependencies

- Python
- PySide6
- OpenCV
- NumPy
- PyTorch
- Ultralytics

See `requirements.txt` for the direct Python requirements.

## Repository structure

```text
analysis/        motion, velocity and target-size analysis
app/             PySide6 interface and pipeline worker
config/          persistent application settings
control/         proportional / PID virtual autopilot logic
custom_models/   optional custom detector weights
detection/       YOLO / RT-DETR detector abstraction
export/          CSV session export
prediction/      Kalman prediction, trajectory and reacquisition
recording/       video and telemetry recording
sources/         video, webcam and RTSP sources
tracking/        multi-object and target tracking
utils/           paths, settings, logging and GPU helpers
visualization/   boxes, trajectory, vector and flight-director overlays
tests/           acceptance checks
tools/           self-check utilities
```

## Privacy and local operation

After dependencies and model weights are installed, normal video inference can run locally on the computer. The application does not require uploading camera/video frames to a cloud API.

## License

This repository is published under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

The application uses the Ultralytics Python package for YOLO / RT-DETR inference. The public Ultralytics repository is distributed under AGPL-3.0, with separate commercial licensing available from Ultralytics. Third-party components remain under their respective licenses.

See `LICENSE` and `THIRD_PARTY_LICENSES.md`.

## Responsible use

This project is intended for computer-vision research, software engineering demonstrations and simulated tracking/control experiments. Detection and tracking systems can make mistakes, especially with small targets, motion blur, occlusion and unusual camera angles.

Do not use the virtual guidance outputs as direct real-world flight-control commands without an independently engineered and validated safety/control system.