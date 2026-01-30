# HVsaccades
Testing if the HV illusion affects the second of two saccades

## Overview

This repository contains a PsychoPy experiment to test whether the horizontal-vertical (HV) illusion affects the accuracy of the second saccade in a double-saccade task.

## Experiment Design

### Task Structure

Participants perform a double-saccade task where:

1. **First Saccade**: A diagonal saccade (45°) from the center to one of 4 corner positions
   - Northeast (NE)
   - Northwest (NW)
   - Southwest (SW)
   - Southeast (SE)

2. **Second Saccade**: A horizontal or vertical saccade to an adjacent corner
   - From each corner, participants saccade either horizontally or vertically
   - This creates 8 unique conditions (4 corners × 2 directions)

### Key Features

- **Perfect Square Configuration**: All 4 target positions form a perfect square
- **Equal Length**: All second saccades have equal length (√2 × distance)
- **Counterbalancing**: Endpoints of second saccades can serve as starting points in other trials
- **Randomization**: Trial order is randomized across repetitions

### Visual Layout

```
        NW (-,+) ←─────→ NE (+,+)
            ↑              ↑
            │              │
            ↓              ↓
        SW (-,-) ←─────→ SE (+,-)
```

From each corner, there are two possible second saccades:
- Horizontal (←→): moves to opposite x-coordinate, same y
- Vertical (↑↓): moves to same x-coordinate, opposite y

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Visualizing the Task

To see a diagram of the task configuration:

```bash
python visualize_task.py
```

This generates `task_visualization.png` showing:
- Left panel: First saccades (diagonal) from fixation to each corner
- Right panel: Second saccades (horizontal/vertical) between corners

![Task Visualization](task_visualization.png)

### Running the Experiment

```bash
python experiment.py
```

This will:
1. Show a dialog to enter participant information
2. Display instructions
3. Run the experiment trials
4. Save data to the `data/` directory

### Testing the Configuration

To verify the mathematical correctness of the trial configuration without running the full experiment:

```bash
python test_configuration.py
```

This validates:
- Square formation (4 targets equidistant from center)
- First saccades are perfect diagonals (45°)
- Second saccades are horizontal or vertical
- All second saccades have equal length
- Endpoints can serve as starting points

## Parameters

Default parameters can be adjusted in the dialog:
- **Participant ID**: Identifier for data files
- **Distance**: Distance from center to each target (degrees of visual angle, default: 10)
- **Repetitions**: Number of repetitions per condition (default: 5)

Total trials = 4 corners × 2 directions × repetitions = 40 trials (with defaults)

## Data Output

Data is saved to `data/<participant_id>_<timestamp>.csv` with columns:
- `trial_num`: Trial number
- `start_x`, `start_y`: Starting position (fixation)
- `target1_x`, `target1_y`: First target position (diagonal)
- `target2_x`, `target2_y`: Second target position (H/V)
- `first_direction`: Cardinal direction of first saccade (NE, NW, SW, SE)
- `second_direction`: Direction type of second saccade (horizontal, vertical)

## Requirements

- Python 3.7+
- PsychoPy 2023.1.0+
- NumPy 1.20.0+

## License

See LICENSE file for details.
