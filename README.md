# Snake Game Workshop

This repository contains the code and resources for the Snake Game Workshop, designed for university-level participants to learn about game programming, distributed systems, and real-time data exchange using RTI Connext DDS.

## Overview

The workshop consists of two main components:
1. **Snake Game Application**: The controller for managing the game, displaying a leaderboard, and placing food items on the game board.
2. **Snake Application**: Individual snake instances that move around the game board, controlled by either user input or as an autonomous bot.

Both applications leverage the [RTI Connext DDS](https://www.rti.com/products/connext-dds-professional) for real-time data communication.

---

## Files in the Repository

### 1. `utils.py`
Defines common data structures used in the game:
- **ShapeFillKind**: Enum defining different fill styles for game shapes.
- **ShapeType** and **ShapeTypeExtended**: Classes representing objects on the game board, such as food and snakes, with attributes like position, color, size, and fill type.

---

### 2. `SnakeGameApplication.py`
Manages the overall game logic, including:
- Placing food on the board using distributed data structures.
- Displaying the leaderboard with player scores.
- Handling updates from all participating snakes via DDS.

#### Key Features:
- **Real-Time Communication**: Uses DDS for exchanging position and score updates between snakes and the game controller.
- **Food Management**: Automatically places food at random positions and detects collisions with snakes.
- **Leaderboard**: Tracks and displays scores based on snake performance.

Run with:
```bash
python SnakeGameApplication.py --domain-id <DDS_DOMAIN_ID>
```

---

### 3. `SnakeApplication.py`
Implements the snake entity for the game. A snake can be:
- **Controlled by a User**: Movement directed using arrow keys.
- **Autonomous Bot**: Calculates its movement based on food position.

#### Key Features:
- **Real-Time Updates**: Continuously publishes its position to the DDS topic.
- **Food Awareness**: Reads food positions and adjusts movement accordingly.
- **Boundary Wrapping**: Ensures the snake wraps around the board edges.

Run with:
```bash
python SnakeApplication.py --snake-id <UNIQUE_ID> [--domain-id <DDS_DOMAIN_ID>] [--is-bot]
```

---

## Workshop Goals

By completing the workshop, participants will:
- Understand the basics of game development, including input handling, object updates, and collision detection.
- Learn how distributed systems communicate using DDS.
- Gain hands-on experience in implementing a real-time multiplayer application.

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- RTI Connext DDS libraries installed
- `curses` library for terminal-based UI

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/MarcosRigal/matchmaking-2024.git
   ```
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Game
1. Start the game controller:
   ```bash
   python SnakeGameApplication.py
   ```
2. Start individual snake applications:
   ```bash
   python SnakeApplication.py --snake-id "Blue"
   python SnakeApplication.py --snake-id "Yellow" --is-bot
   ```

---

