def evaluate(state):
    # Terminal state: no treasures remaining.
    # If it's B's turn, A just moved and likely collected the last treasure.
    if state.is_terminal():
        return 1000 if state.current_player == "B" else -1000

    score = 0

    # Reward states with fewer remaining treasures.
    max_treasures = 5
    remaining = len(state.treasures)
    score += (max_treasures - remaining) * 25

    ax, ay = state.agent_a
    bx, by = state.agent_b

    # Distance to nearest treasure: prefer A closer than B.
    if state.treasures:
        min_a = min(
            abs(ax - tx) + abs(ay - ty)
            for tx, ty in state.treasures
        )

        min_b = min(
            abs(bx - tx) + abs(by - ty)
            for tx, ty in state.treasures
        )

        score += (min_b - min_a) * 3

    # Traps: prefer A farther from traps than B.
    traps = []
    for r, row in enumerate(state.grid):
        for c, cell in enumerate(row):
            if cell == 2:
                traps.append((r, c))

    if traps:
        min_trap_a = min(
            abs(ax - tx) + abs(ay - ty)
            for tx, ty in traps
        )
        min_trap_b = min(
            abs(bx - tx) + abs(by - ty)
            for tx, ty in traps
        )
        score += (min_trap_a - min_trap_b) * 2

    # Discourage 2-cell oscillation (A: p0->p1->p0).
    if getattr(state, "prev2_agent_a", None) is not None and state.agent_a == state.prev2_agent_a:
        score -= 60
    if getattr(state, "prev2_agent_b", None) is not None and state.agent_b == state.prev2_agent_b:
        score += 30  # Opponent oscillating is mildly good for A.

    return score