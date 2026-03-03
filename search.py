import time
import random
from config import ACTIONS, GRID_SIZE


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def evaluate(state):
    """
    Heuristic score from A's perspective (A = maximizer, B = minimizer).

    Factors:
    - Score differential: A collected vs B collected (weighted heavily)
    - Distance to nearest treasure: A closer is better, B farther is better
    - Trap proximity: penalize A near traps, reward B near traps
    """
    score = 0
    treasures = state["treasures"]
    traps = state["traps"]

    # Collected treasure score differential (most important factor)
    score += (state.get("a_score", 0) - state.get("b_score", 0)) * 20

    # Distance to nearest treasure
    if treasures:
        dist_a = min(manhattan(state["a_pos"], t) for t in treasures)
        dist_b = min(manhattan(state["b_pos"], t) for t in treasures)
        score -= dist_a * 3   # A closer → better for A
        score += dist_b * 2   # B farther → better for A

    # Trap proximity (danger zone = within 2 cells)
    for trap in traps:
        d_a = manhattan(state["a_pos"], trap)
        d_b = manhattan(state["b_pos"], trap)
        if d_a <= 2:
            score -= (3 - d_a) * 5   # A near trap → bad for A
        if d_b <= 2:
            score += (3 - d_b) * 3   # B near trap → good for A

    return score


def get_valid_moves(state, player):
    pos = state["a_pos"] if player == "A" else state["b_pos"]
    walls = state["walls"]

    moves = []
    for move in ACTIONS:
        nr = pos[0] + move[0]
        nc = pos[1] + move[1]
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            if (nr, nc) not in walls:
                moves.append(move)
    return moves


def apply_move(state, move):
    new_state = {
        "a_pos": state["a_pos"],
        "b_pos": state["b_pos"],
        "treasures": set(state["treasures"]),
        "traps": state["traps"],
        "walls": state["walls"],
        "turn": state["turn"],
        "a_score": state.get("a_score", 0),
        "b_score": state.get("b_score", 0),
    }

    if state["turn"] == "A":
        new_pos = (
            state["a_pos"][0] + move[0],
            state["a_pos"][1] + move[1]
        )
        new_state["a_pos"] = new_pos
        if new_pos in new_state["treasures"]:
            new_state["treasures"].discard(new_pos)
            new_state["a_score"] += 1
        new_state["turn"] = "B"
    else:
        new_pos = (
            state["b_pos"][0] + move[0],
            state["b_pos"][1] + move[1]
        )
        new_state["b_pos"] = new_pos
        if new_pos in new_state["treasures"]:
            new_state["treasures"].discard(new_pos)
            new_state["b_score"] += 1
        new_state["turn"] = "A"

    return new_state


# ── Minimax ──────────────────────────────────────────────────────────────────

def minimax(state, depth):
    """
    Minimax search.
    A is always the maximizer; B is always the minimizer.
    maximizing/minimizing is derived from s["turn"] — NOT from an external bool —
    to prevent the parameter from going out of sync with the actual game turn.
    Returns (best_move, nodes_expanded, runtime_seconds).
    """
    nodes = 0

    def recurse(s, d):
        nonlocal nodes
        nodes += 1

        if d == 0 or not s["treasures"]:
            return evaluate(s)

        moves = get_valid_moves(s, s["turn"])
        if not moves:               # agent is fully blocked → treat as terminal
            return evaluate(s)

        if s["turn"] == "A":        # maximizer
            value = -float("inf")
            for m in moves:
                child = apply_move(s, m)
                value = max(value, recurse(child, d - 1))
            return value
        else:                       # minimizer
            value = float("inf")
            for m in moves:
                child = apply_move(s, m)
                value = min(value, recurse(child, d - 1))
            return value

    start = time.time()
    best_move = None
    current_turn = state["turn"]

    # Initialise best_val in the correct direction for the current player
    best_val = -float("inf") if current_turn == "A" else float("inf")

    for m in get_valid_moves(state, current_turn):
        child = apply_move(state, m)
        val = recurse(child, depth - 1)

        if current_turn == "A" and val > best_val:
            best_val = val
            best_move = m
        elif current_turn == "B" and val < best_val:
            best_val = val
            best_move = m

    runtime = time.time() - start
    return best_move, nodes, runtime


# ── Alpha-Beta Pruning ────────────────────────────────────────────────────────

def alphabeta(state, depth):
    """
    Alpha-Beta Pruning (extension of Minimax).
    Same turn-derivation fix as minimax().
    Returns (best_move, nodes_expanded, pruned_count, runtime_seconds).
    """
    nodes = 0
    pruned = 0

    def recurse(s, d, alpha, beta):
        nonlocal nodes, pruned
        nodes += 1

        if d == 0 or not s["treasures"]:
            return evaluate(s)

        moves = get_valid_moves(s, s["turn"])
        if not moves:
            return evaluate(s)

        if s["turn"] == "A":        # maximizer
            value = -float("inf")
            for m in moves:
                child = apply_move(s, m)
                value = max(value, recurse(child, d - 1, alpha, beta))
                alpha = max(alpha, value)
                if beta <= alpha:
                    pruned += 1
                    break
            return value
        else:                       # minimizer
            value = float("inf")
            for m in moves:
                child = apply_move(s, m)
                value = min(value, recurse(child, d - 1, alpha, beta))
                beta = min(beta, value)
                if beta <= alpha:
                    pruned += 1
                    break
            return value

    start = time.time()
    best_move = None
    current_turn = state["turn"]
    best_val = -float("inf") if current_turn == "A" else float("inf")
    alpha = -float("inf")
    beta = float("inf")

    for m in get_valid_moves(state, current_turn):
        child = apply_move(state, m)
        val = recurse(child, depth - 1, alpha, beta)

        if current_turn == "A":
            if val > best_val:
                best_val = val
                best_move = m
            alpha = max(alpha, best_val)
        else:
            if val < best_val:
                best_val = val
                best_move = m
            beta = min(beta, best_val)

    runtime = time.time() - start
    return best_move, nodes, pruned, runtime


# ── Random agent (used for B in easy mode) ───────────────────────────────────

def random_move(state):
    moves = get_valid_moves(state, state["turn"])
    return random.choice(moves) if moves else None
