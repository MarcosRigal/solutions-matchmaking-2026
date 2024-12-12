import time
import curses
import argparse
import rti.connextdds as dds
from collections import deque
from utils import ShapeTypeExtended


class SnakeApplication:
    def __init__(self, snake_id, domain_id=0, is_bot=False):
        self.running = True
        self.dds_width = 230
        self.dds_height = 265

        # Initialize curses for input handling
        if not is_bot:
            self.screen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.screen.keypad(True)
            self.screen.nodelay(True)

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

        self.snake_id = snake_id
        self.is_bot = is_bot

        # Initialize snake with DDS coordinates
        self.snake = deque([(30, 40), (30, 35), (30, 30)])  # DDS coordinates
        self.direction = (0, 5)  # DDS coordinate movement
        self.food_position = None

    def handle_input(self):
        try:
            key = self.screen.getch()
            if key != -1:  # -1 means no key pressed
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

    def update_snake(self):
        head_x, head_y = self.snake[0]
        dy, dx = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Handle wrapping in DDS coordinates
        new_head = (new_head[0] % self.dds_width, new_head[1] % self.dds_height)

        self.snake.appendleft(new_head)
        self.snake.pop()

        # Publish snake position to DDS
        self.snake_writer.write(
            ShapeTypeExtended(
                color=self.snake_id, x=new_head[0], y=new_head[1], shapesize=10
            )
        )

    def check_food_updates(self):
        for sample in self.food_reader.read():
            if sample.info.valid:
                self.food_position = sample.data

    def run(self):
        while self.running:
            if self.is_bot:
                self.direction = self.calculate_bot_direction()
            else:
                self.handle_input()
            self.update_snake()
            self.check_food_updates()  # Check for food updates more frequently
            time.sleep(0.1)

    def __del__(self):
        if not self.is_bot:
            # Cleanup curses
            curses.nocbreak()
            self.screen.keypad(False)
            curses.echo()
            curses.endwin()


def parse_args():
    parser = argparse.ArgumentParser(description="Snake Game")
    parser.add_argument(
        "--snake-id", required=True, help="Unique identifier for the snake"
    )
    parser.add_argument("--domain-id", type=int, default=0, help="DDS Domain ID")
    parser.add_argument("--is-bot", action="store_true", help="Run as a bot")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        app = SnakeApplication(
            args.snake_id, domain_id=args.domain_id, is_bot=args.is_bot
        )
        app.run()
    except KeyboardInterrupt:
        print(f"\nSnake {args.snake_id} has stopped.")
    finally:
        if not args.is_bot:
            curses.endwin()  # Ensure proper cleanup


if __name__ == "__main__":
    main()
