# Solution Walkthrough

[Reference setup](README.md) |
[Participant workbook](https://github.com/MarcosRigal/matchmaking-2026/blob/main/WORKSHOP.md)

This guide explains the existing answers rather than changing the exercise
requirements. Attempt the participant checkpoints before opening the answers.

## Exercise map

The starter contains six TODO comments: three in each platform file. They
represent **three exercises**, not six separate assignments.

| Starter TODO | Reference location | Used by |
| --- | --- | --- |
| Implement DDS initialization | Constructor in [Unix player](SnakeApplication.py) and [Windows player](SnakeApplicationWindows.py) | Both human and bot modes |
| Implement user input handling for controlling the snake | `handle_input()` in [Unix player](SnakeApplication.py) and [Windows player](SnakeApplicationWindows.py) | Human mode |
| Implement bot logic to calculate the next move | `calculate_bot_direction()` in [Unix player](SnakeApplication.py) and [Windows player](SnakeApplicationWindows.py) | Bot mode |

Choose the file for your platform. The
[controller](SnakeGameApplication.py) and [shared types](utils.py) have no
exercise TODOs.

## 1. DDS initialization

Insert the following at the DDS TODO inside the starter constructor, keeping
the constructor's indentation:

```python
self.participant = dds.DomainParticipant(domain_id)
self.snake_topic = dds.Topic(self.participant, "Square", ShapeTypeExtended)
self.food_topic = dds.Topic(self.participant, "Circle", ShapeTypeExtended)
self.snake_writer = dds.DataWriter(
    self.participant.implicit_publisher, self.snake_topic
)
self.snake_reader = dds.DataReader(
    self.participant.implicit_subscriber, self.snake_topic
)
self.food_reader = dds.DataReader(
    self.participant.implicit_subscriber, self.food_topic
)
```

### Why it works

1. `domain_id` keeps group selection in the command line rather than hard-coded.
2. The topic names and `ShapeTypeExtended` match the controller. `Square` carries
   snake heads; `Circle` carries food.
3. Implicit publishers/subscribers let the participant own the endpoint groups
   without extra explicit publisher/subscriber objects.
4. The attributes match existing calls: `self.snake_writer.write(...)` publishes
   movement, while `self.food_reader.read()` retrieves food.
5. `self.snake_reader` matches the reference setup but is **not used** by the
   current snake loop. It is not responsible for food or scoring.

The `color` field is marked as the DDS key in [utils.py](utils.py). Separate
player IDs produce distinct instances on Square. Reusing an ID also makes the
controller group those position updates under one player.

### Verify

Run human mode before implementing the other TODOs. The player should move
right and publish without missing-attribute errors. Observe Square in Shapes
Demo or inspect received samples in the controller with a debugger. Stop with
`Ctrl+C`, since `q` is not implemented until exercise 2.

To check food, start the snake first, allow discovery, and then start the
controller. A valid Circle sample should populate `self.food_position`.
Do not test the unfinished bot yet: it returns `None`.

## 2. Keyboard controls

The important convention is **position `(x, y)` but direction `(dy, dx)`**.
The movement method adds `dx` to `head_x` and `dy` to `head_y`.

| Key | New direction | Reject when current direction is |
| --- | --- | --- |
| Left | `(0, -5)` | `(0, 5)` |
| Right | `(0, 5)` | `(0, -5)` |
| Up | `(-5, 0)` | `(5, 0)` |
| Down | `(5, 0)` | `(-5, 0)` |

### Linux/macOS answer

Replace the starter method with:

```python
def handle_input(self):
    try:
        key = self.screen.getch()
        if key != -1:
            if key == curses.KEY_LEFT and self.direction != (0, 5):
                self.direction = (0, -5)
            elif key == curses.KEY_RIGHT and self.direction != (0, -5):
                self.direction = (0, 5)
            elif key == curses.KEY_UP and self.direction != (5, 0):
                self.direction = (-5, 0)
            elif key == curses.KEY_DOWN and self.direction != (-5, 0):
                self.direction = (5, 0)
            elif key == ord("q"):
                self.running = False
    except Exception as e:
        self.running = False
        print(f"Input error: {e}")
```

The constructor already sets `nodelay(True)`. `getch()` returns `-1` instead
of blocking when there is no input, so movement and DDS updates continue.

### Windows answer

Replace the starter method with:

```python
def handle_input(self):
    try:
        if keyboard.is_pressed('left') and self.direction != (0, 5):
            self.direction = (0, -5)
        elif keyboard.is_pressed('right') and self.direction != (0, -5):
            self.direction = (0, 5)
        elif keyboard.is_pressed('up') and self.direction != (5, 0):
            self.direction = (-5, 0)
        elif keyboard.is_pressed('down') and self.direction != (-5, 0):
            self.direction = (5, 0)
        elif keyboard.is_pressed('q'):
            self.running = False
    except Exception as e:
        self.running = False
        print(f"Input error: {e}")
```

This polls key state rather than reading terminal key codes. With multiple
keys held, the first satisfied branch wins. Release arrows before pressing `q`.

Both snippets reflect the existing reference's broad exception handler:
it reports an input error and requests shutdown. This is not a recommendation
to catch every exception in new code; more narrowly scoped error handling and
explicit resource cleanup are possible follow-up improvements.

### Verify

Start moving right. Left must be ignored; down must turn; up must then be
ignored; left must now turn. No input and unrelated keys preserve direction.
`q` requests shutdown.

One final movement can occur after `q` or an input error: the existing loop
still calls `update_snake()` before checking `self.running` again. The Unix
entry point restores the terminal in its `finally` block; `stty sane` is a
recovery option if the terminal is left in an unusual state.

## 3. Greedy bot direction

The answer is identical in both platform files:

```python
def calculate_bot_direction(self):
    if self.food_position is None:
        return self.direction

    head_x, head_y = self.snake[0]
    delta_y = self.food_position.y - head_y
    delta_x = self.food_position.x - head_x

    if abs(delta_y) > abs(delta_x):
        return (5, 0) if delta_y > 0 else (-5, 0)
    else:
        return (0, 5) if delta_x > 0 else (0, -5)
```

### Why it works

1. No food is a normal state, particularly before discovery. Preserving the
   direction also prevents `None` from reaching the movement unpacking.
2. Absolute distances choose an axis; the sign chooses movement on that axis.
3. The step remains five, matching manual movement.
4. Strict `>` makes ties horizontal. At exact overlap, the reference returns
   left because `delta_x > 0` is false.
5. The method returns a direction; the loop moves and publishes the head.
   Collection is detected separately by the controller.

This is a greedy baseline, not an optimal pathfinder. Unlike human input, it
does not reject reversals. It does not account for shorter wrapped routes.

### Deterministic verification

The following optional check runs the reference direction method without
starting DDS participants, keyboard hooks, or a terminal UI. Run it from the
repository root using `python` in the activated environment (paste it into the
Python REPL or save it locally as a scratch script). Run the same check from
the starter repository after implementing exercise 3.

It checks both files because the expected bot behavior is platform-independent.
The small loader extracts only the method; this is a logic check, **not** a DDS
integration or platform-input test.

```python
import ast
from collections import deque
from pathlib import Path
from types import SimpleNamespace

cases = [
    (None, (0, 5)),
    ((50, 40), (0, 5)),
    ((10, 40), (0, -5)),
    ((30, 60), (5, 0)),
    ((30, 20), (-5, 0)),
    ((50, 60), (0, 5)),
    ((10, 20), (0, -5)),
    ((30, 40), (0, -5)),
]

for filename in ("SnakeApplication.py", "SnakeApplicationWindows.py"):
    tree = ast.parse(Path(filename).read_text())
    player_class = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "SnakeApplication"
    )
    method = next(
        node for node in player_class.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "calculate_bot_direction"
    )
    namespace = {}
    module = ast.Module(body=[method], type_ignores=[])
    exec(compile(module, filename, "exec"), namespace)
    for food, expected in cases:
        player = SimpleNamespace(
            snake=deque([(30, 40)]),
            direction=(0, 5),
            food_position=(
                None if food is None
                else SimpleNamespace(x=food[0], y=food[1])
            ),
        )
        actual = namespace["calculate_bot_direction"](player)
        assert actual == expected, (filename, food, actual, expected)
    print(f"{filename}: {len(cases)} direction cases passed")
```

If you implemented only one starter file, change the filename tuple to contain
only that file. Otherwise the untouched platform's TODO will fail the check.

## End-to-end verification and facilitator notes

1. Complete the [setup checks](README.md) before the workshop. Test the actual
   student platform, interpreter, license, keyboard access, and network.
2. Allocate one domain per group and unique player IDs within each group.
3. Start a completed bot first, then Shapes subscribers if using them.
4. Allow discovery, then start **one** controller with a predictable target:

   ```bash
   python SnakeGameApplication.py --domain-id 0 --initial-food-x 100 --initial-food-y 100
   ```

5. Expect a score after food collection, followed by a new Circle position.
   If the bot never turns, inspect food reception and restart the controller
   after discovery. Do not diagnose a missing sample as a bot algorithm error.
6. Check a human player using the direction/reversal sequence in exercise 2.
7. Add a second player with a distinct ID. First verify locally, then across
   machines on an approved network. A new bot can miss the current food sample.
8. Stop participants with `Ctrl+C`; human players also support `q`.

### Existing behavior to explain, not silently promise away

| Detail | Consequence for the workshop |
| --- | --- |
| Food is published at startup and after collection only | Late readers may miss it with default QoS; restart the controller after discovery |
| Controller scores only when both coordinate differences are `< 5` | A difference of exactly five does not score |
| Leaderboard entries are created on collection | No entry on join is expected |
| Direction selection precedes food reading | A new food sample affects a later iteration |
| Only the head is published | A graphical snake body is not part of the exercise |
| Controller and snake use `read()`, not `take()` | Samples may remain in reader history; this is not a consume-once event queue |
| Random food coordinates include the upper bounds | Edge placement can interact with wrapping; use `(100, 100)` for the first demo |
| Scores and position histories are in memory | Restart resets scores; stopped players are not explicitly removed |
| No explicit QoS configuration is provided | Do not promise late-join delivery or identical behavior under arbitrary external QoS |

Keep optional improvements separate from grading the three TODOs. A participant
has completed the core when DDS exchange works, manual input meets its checks,
the bot passes its direction cases, and an end-to-end run earns a point.
