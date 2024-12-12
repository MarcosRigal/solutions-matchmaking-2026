import time
import random
import argparse
import rti.connextdds as dds
from collections import deque, defaultdict
import os
import keyboard

from utils import (
    ShapeTypeExtended,
    ShapeFillKind,
)


class SnakeGameApplication:
    def __init__(self, domain_id=0, initial_food_position=None):
        self.running = True
        self.dds_width = 230
        self.dds_height = 265

        self.participant = dds.DomainParticipant(domain_id)
        self.snake_topic = dds.Topic(self.participant, "Square", ShapeTypeExtended)
        self.food_topic = dds.Topic(self.participant, "Circle", ShapeTypeExtended)
        self.food_writer = dds.DataWriter(
            self.participant.implicit_publisher, self.food_topic
        )
        self.snake_reader = dds.DataReader(
            self.participant.implicit_subscriber, self.snake_topic
        )

        self.snake_positions = defaultdict(deque)
        self.food_position = initial_food_position
        self.leaderboard = defaultdict(int)
        self.screen = None

    def place_food(self):
        if self.food_position is None:
            # Place food in DDS coordinates directly
            dds_x = random.randint(0, self.dds_width)
            dds_y = random.randint(0, self.dds_height)
            self.food_position = ShapeTypeExtended(
                color="RED",
                x=dds_x,
                y=dds_y,
                shapesize=10,
                fillKind=ShapeFillKind.SOLID_FILL,
            )
        self.food_writer.write(self.food_position)

    def handle_snake_updates(self):
        for sample in self.snake_reader.read():
            if sample.info.valid:
                snake_id = sample.data.color
                if snake_id not in self.snake_positions:
                    self.snake_positions[snake_id] = deque([(sample.data.x, sample.data.y)])
                else:
                    self.snake_positions[snake_id].appendleft((sample.data.x, sample.data.y))
                    if len(self.snake_positions[snake_id]) > 10:
                        self.snake_positions[snake_id].pop()

    def detect_collisions(self):
        for snake_id, positions in self.snake_positions.items():
            if not positions:
                continue
            head_x, head_y = positions[0]

            if self.food_position:
                food_x, food_y = self.food_position.x, self.food_position.y
                if abs(head_x - food_x) < 5 and abs(head_y - food_y) < 5:  # Increase collision area
                    self.leaderboard[snake_id] += 1
                    self.food_position = None
                    self.place_food()

    def display_leaderboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Leaderboard:")
        for idx, (snake_id, score) in enumerate(sorted(self.leaderboard.items(), key=lambda item: item[1], reverse=True), start=1):
            print(f"{snake_id}: {score}")

    def run(self):
        self.place_food()
        while self.running:
            self.handle_snake_updates()
            self.detect_collisions()
            self.display_leaderboard()
            time.sleep(0.1)

    def __del__(self):
        pass


def parse_args():
    parser = argparse.ArgumentParser(description="Snake Game Controller")
    parser.add_argument("--domain-id", type=int, default=0, help="DDS Domain ID")
    parser.add_argument(
        "--initial-food-x", type=int, help="Initial food X position", default=None
    )
    parser.add_argument(
        "--initial-food-y", type=int, help="Initial food Y position", default=None
    )
    return parser.parse_args()


def main():
    args = parse_args()
    initial_food_position = None
    if args.initial_food_x is not None and args.initial_food_y is not None:
        initial_food_position = ShapeTypeExtended(
            color="RED",
            x=args.initial_food_x,
            y=args.initial_food_y,
            shapesize=10,
            fillKind=ShapeFillKind.SOLID_FILL,
        )
    try:
        app = SnakeGameApplication(args.domain_id, initial_food_position)
        app.run()
    except KeyboardInterrupt:
        print("\nGame controller stopped.")


if __name__ == "__main__":
    main()
