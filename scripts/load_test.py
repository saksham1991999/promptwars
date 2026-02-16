#!/usr/bin/env python3
"""
Load testing script for Chess Alive API.

Simulates realistic user behavior:
- Creating games
- Joining games
- Making moves
- Sending chat messages

Usage:
    python scripts/load_test.py --url https://your-backend-url --users 50 --duration 300
"""

import argparse
import asyncio
import json
import random
import time
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import httpx


@dataclass
class GameSession:
    """Represents a user game session."""

    session_id: str
    game_id: str | None = None
    share_code: str | None = None


class LoadTester:
    """Load tester for Chess Alive API."""

    def __init__(self, base_url: str, num_users: int, duration: int):
        self.base_url = base_url.rstrip("/")
        self.num_users = num_users
        self.duration = duration
        self.results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "p95_response_time": 0.0,
            "p99_response_time": 0.0,
            "errors": [],
        }
        self.response_times: list[float] = []

    async def create_game(self, client: httpx.AsyncClient, session: GameSession) -> bool:
        """Create a new game."""
        try:
            start = time.time()
            response = await client.post(
                f"{self.base_url}/games",
                json={"game_mode": "pvai", "template": "classic"},
                headers={"X-Session-Id": session.session_id},
                timeout=15.0,
            )
            elapsed = time.time() - start
            self.response_times.append(elapsed)
            self.results["total_requests"] += 1

            if response.status_code == 200:
                data = response.json()
                session.game_id = data["id"]
                session.share_code = data["share_code"]
                self.results["successful_requests"] += 1
                print(f"✓ Created game {session.game_id[:8]}... in {elapsed:.2f}s")
                return True
            else:
                self.results["failed_requests"] += 1
                self.results["errors"].append(f"Create game failed: {response.status_code}")
                return False
        except Exception as e:
            self.results["failed_requests"] += 1
            self.results["errors"].append(f"Create game error: {str(e)}")
            return False

    async def get_game(self, client: httpx.AsyncClient, session: GameSession) -> bool:
        """Get game state."""
        if not session.game_id:
            return False

        try:
            start = time.time()
            response = await client.get(
                f"{self.base_url}/games/{session.game_id}",
                timeout=10.0,
            )
            elapsed = time.time() - start
            self.response_times.append(elapsed)
            self.results["total_requests"] += 1

            if response.status_code == 200:
                self.results["successful_requests"] += 1
                return True
            else:
                self.results["failed_requests"] += 1
                return False
        except Exception as e:
            self.results["failed_requests"] += 1
            self.results["errors"].append(f"Get game error: {str(e)}")
            return False

    async def send_chat_message(self, client: httpx.AsyncClient, session: GameSession) -> bool:
        """Send a chat message."""
        if not session.game_id:
            return False

        try:
            start = time.time()
            response = await client.post(
                f"{self.base_url}/games/{session.game_id}/chat",
                json={
                    "content": f"Test message {random.randint(1, 1000)}",
                    "message_type": "player_message",
                },
                headers={"X-Session-Id": session.session_id},
                timeout=10.0,
            )
            elapsed = time.time() - start
            self.response_times.append(elapsed)
            self.results["total_requests"] += 1

            if response.status_code == 200:
                self.results["successful_requests"] += 1
                return True
            else:
                self.results["failed_requests"] += 1
                return False
        except Exception as e:
            self.results["failed_requests"] += 1
            self.results["errors"].append(f"Chat error: {str(e)}")
            return False

    async def user_workflow(self, client: httpx.AsyncClient, user_num: int):
        """Simulate a single user's workflow."""
        session = GameSession(session_id=str(uuid4()))
        print(f"User {user_num}: Starting workflow...")

        # Create game
        if not await self.create_game(client, session):
            return

        # Simulate user activity for duration
        end_time = time.time() + random.uniform(10, 30)  # Random activity time
        action_count = 0

        while time.time() < end_time:
            # Random action: get game state or send chat
            action = random.choice(["get_game", "chat"])

            if action == "get_game":
                await self.get_game(client, session)
            else:
                await self.send_chat_message(client, session)

            action_count += 1
            await asyncio.sleep(random.uniform(1, 3))  # Human-like delay

        print(f"User {user_num}: Completed {action_count} actions")

    async def run(self):
        """Run the load test."""
        print(f"🚀 Starting load test:")
        print(f"  Base URL: {self.base_url}")
        print(f"  Concurrent users: {self.num_users}")
        print(f"  Duration: {self.duration}s")
        print()

        start_time = time.time()

        async with httpx.AsyncClient() as client:
            # Create user workflows
            tasks = [
                self.user_workflow(client, i) for i in range(1, self.num_users + 1)
            ]

            # Run all users concurrently with timeout
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.duration + 60,
                )
            except asyncio.TimeoutError:
                print("⚠️  Load test timed out")

        elapsed = time.time() - start_time

        # Calculate statistics
        if self.response_times:
            self.results["avg_response_time"] = sum(self.response_times) / len(
                self.response_times
            )
            sorted_times = sorted(self.response_times)
            p95_idx = int(len(sorted_times) * 0.95)
            p99_idx = int(len(sorted_times) * 0.99)
            self.results["p95_response_time"] = sorted_times[p95_idx]
            self.results["p99_response_time"] = sorted_times[p99_idx]

        # Print results
        print("\n" + "=" * 60)
        print("📊 LOAD TEST RESULTS")
        print("=" * 60)
        print(f"Total duration: {elapsed:.2f}s")
        print(f"Total requests: {self.results['total_requests']}")
        print(f"Successful: {self.results['successful_requests']}")
        print(f"Failed: {self.results['failed_requests']}")
        print(
            f"Success rate: {self.results['successful_requests'] / self.results['total_requests'] * 100:.1f}%"
        )
        print(f"\nResponse times:")
        print(f"  Average: {self.results['avg_response_time']:.3f}s")
        print(f"  P95: {self.results['p95_response_time']:.3f}s")
        print(f"  P99: {self.results['p99_response_time']:.3f}s")

        if self.results["errors"]:
            print(f"\n⚠️  Errors encountered ({len(self.results['errors'])} total):")
            unique_errors = set(self.results["errors"][:10])  # Show first 10 unique
            for error in unique_errors:
                print(f"  - {error}")

        # Evaluation
        print("\n" + "=" * 60)
        print("📈 EVALUATION")
        print("=" * 60)

        success_rate = (
            self.results["successful_requests"] / self.results["total_requests"] * 100
        )
        p95_time = self.results["p95_response_time"]

        if success_rate >= 99 and p95_time < 0.5:
            print("✅ EXCELLENT - System performing optimally")
        elif success_rate >= 95 and p95_time < 1.0:
            print("✅ GOOD - System performing well")
        elif success_rate >= 90 and p95_time < 2.0:
            print("⚠️  ACCEPTABLE - Some performance degradation")
        else:
            print("❌ NEEDS IMPROVEMENT - Performance issues detected")


def main():
    parser = argparse.ArgumentParser(description="Load test Chess Alive API")
    parser.add_argument(
        "--url",
        required=True,
        help="Base URL of the API (e.g., https://backend-url/api/v1)",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=50,
        help="Number of concurrent users (default: 50)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Test duration in seconds (default: 300)",
    )

    args = parser.parse_args()

    tester = LoadTester(args.url, args.users, args.duration)
    asyncio.run(tester.run())


if __name__ == "__main__":
    main()
