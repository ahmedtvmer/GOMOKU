# Gomoku AI

A high-performance Gomoku (Five-in-a-Row) game featuring an intelligent AI opponent, built with Python and Pygame.

## 🎮 How to Play

1.  **Run the Game**:
    ```bash
    ./venv/bin/python gomoku.py
    ```
2.  **Controls**:
    *   **Mouse Click**: Place your stone (White).
    *   **'R' Key**: Restart the game instantly.
3.  **Objective**: Be the first to get **5 stones in a row** (horizontally, vertically, or diagonally).

## 🧠 AI Architecture

The AI uses a combination of classical game theory algorithms and heuristic evaluation to play at a competitive level.

### 1. Minimax Algorithm
The core decision-making engine is the **Minimax** algorithm. The AI looks ahead several moves into the future, simulating every possible response from the player. It assumes the player will always play perfectly (minimizing the AI's score), and chooses the move that maximizes its own potential score.

### 2. Alpha-Beta Pruning
To make the search faster, **Alpha-Beta Pruning** is implemented. This optimization allows the AI to stop analyzing a specific sequence of moves as soon as it finds a move that is worse than a previously examined option. This significantly reduces the number of board states the AI needs to evaluate, allowing it to search deeper in the same amount of time.

### 3. Heuristic Evaluation (The "Brain")
Since the AI cannot calculate every move until the end of the game, it uses a **Heuristic Function** to estimate how "good" a specific board state is.
The evaluation logic uses **Pattern Matching** to identify dangerous or winning shapes:

*   **Open 4 (`.XXXX.`)**: **100,000 pts** (Guaranteed Win - Unstoppable)
*   **Closed 4 (`OXXXX.`)**: **50,000 pts** (Must Block immediately)
*   **Open 3 (`.XXX.`)**: **10,000 pts** (Creates a double threat)
*   **Closed 3 (`OXXX.`)**: **500 pts** (Strategic build-up)
*   **Open 2 (`.XX.`)**: **100 pts**

The AI also prioritizes **Blocking** the opponent's threats by giving a slightly higher weight (1.5x) to defensive moves when the opponent has a strong shape.

### 4. Efficient Move Generation
Instead of checking every empty spot on the 15x15 board (225 possibilities), the AI only considers **Candidate Moves** that are within a 2-cell radius of existing stones. This focuses the calculation on the active area of play, making the AI much faster and more responsive.

## 🛠️ Requirements

*   Python 3.x
*   Pygame
*   Numpy

## 🚀 Installation

1.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install pygame numpy
    ```
