# Snake Game Workshop: Reference Solutions

This repository contains completed implementations of the three exercises in the
[participant repository](https://github.com/MarcosRigal/matchmaking-2026).
Use the starter repository when taking the workshop; use this one to compare
answers or prepare a demonstration.

## Documentation route

1. [Participant setup and troubleshooting](https://github.com/MarcosRigal/matchmaking-2026/blob/main/README.md):
   Python, platform dependencies, licensing, and launch commands.
2. [Participant workbook](https://github.com/MarcosRigal/matchmaking-2026/blob/main/WORKSHOP.md):
   DDS concepts, ordered steps, progressive hints, and checkpoints.
3. [Solution walkthrough](SOLUTIONS.md): explanations and answers for each TODO,
   verification cases, and facilitator notes.

The documentation follows the current code, including its limitations; it does
not introduce additional exercises into the starter source.

## Quick start for a reference demonstration

Use supported CPython, preferably **3.11 or 3.12**, and an RTI license.
`rti.connext==7.7.0` requires Python 3.10+ with a matching platform wheel.
See the participant setup for the supported wheel architectures.

```bash
git clone https://github.com/MarcosRigal/solutions-matchmaking-2026.git
cd solutions-matchmaking-2026
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "rti.connext==7.7.0" "keyboard==0.13.5"
export RTI_LICENSE_FILE="/absolute/path/to/rti_license.dat"
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "rti.connext==7.7.0" "keyboard==0.13.5"
$env:RTI_LICENSE_FILE = "C:\absolute\path\to\rti_license.dat"
```

Substitute your license path; do not publish license contents. If PowerShell
blocks activation, invoke `.\.venv\Scripts\python.exe` directly instead of
`python`. Activate the environment and configure the license in each terminal.

The minimal install above covers the imports in the scripts.
[requirements.txt](requirements.txt) also lists packages such as `python-xlib`
that are not portable across all workshop platforms.

Verify that DDS can initialize:

```bash
python -c "import rti.connextdds as dds; participant = dds.DomainParticipant(0); print('DDS participant OK')"
```

Then, in terminal 1, start a bot on your assigned domain (example: `0`):

```bash
python SnakeApplication.py --snake-id YELLOW --domain-id 0 --is-bot
```

On Windows, use [SnakeApplicationWindows.py](SnakeApplicationWindows.py) instead.
For human control, omit `--is-bot`; arrow keys turn and `q` quits.

In terminal 2, after allowing discovery, start one controller:

```bash
python SnakeGameApplication.py --domain-id 0 --initial-food-x 100 --initial-food-y 100
```

The bot should collect food and appear on the text leaderboard. Use `Ctrl+C`
to stop the bot and controller. If the bot never receives food, restart the
controller after discovery: the current controller publishes food only at
startup and after collection, so late readers can miss the initial sample.

## Source map and display expectations

| File | Responsibility |
| --- | --- |
| [utils.py](utils.py) | Shared keyed shape types |
| [SnakeGameApplication.py](SnakeGameApplication.py) | Food publication, collection detection, text leaderboard |
| [SnakeApplication.py](SnakeApplication.py) | Unix keyboard input or bot; DDS snake-head publication |
| [SnakeApplicationWindows.py](SnakeApplicationWindows.py) | Windows keyboard input or bot; same DDS behavior |

The scripts **do not render a game board**. For graphics, use facilitator-provided
RTI Shapes Demo subscribers for `Square` and `Circle` on the same domain, with
compatible types and QoS. Start the food subscriber before the controller.
Do not add Shapes publishers during the basic demo.

Only head positions are published. Growth, snake-to-snake collisions, optimal
pathfinding, and persistent scores are not implemented. See
[the walkthrough](SOLUTIONS.md) for the exact behavior and verification steps.
