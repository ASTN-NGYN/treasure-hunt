import time


def _dist_to_nearest_treasure(pos, treasures):
    if not treasures:
        return 0
    r, c = pos
    return min(abs(r - tr) + abs(c - tc) for tr, tc in treasures)

class Metrics:
    def __init__(self):
        self.nodes_expanded = 0
        self.pruned = 0


def minimax(state, depth, metrics, maximizing=True):
    metrics.nodes_expanded += 1

    if depth == 0 or state.is_terminal():
        from evaluation import evaluate
        return evaluate(state), None

    best_move = None

    if maximizing:
        max_eval = float("-inf")
        for move in state.get_legal_moves():
            child = state.apply_move(move)
            eval_score, _ = minimax(child, depth-1, metrics, False)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            elif eval_score == max_eval and best_move is not None:
                # Tie-break to reduce oscillation and encourage progress.
                prev_a = getattr(state, "prev_agent_a", None)
                cand_key = (
                    1 if prev_a is not None and move == prev_a else 0,
                    _dist_to_nearest_treasure(move, state.treasures),
                )
                best_key = (
                    1 if prev_a is not None and best_move == prev_a else 0,
                    _dist_to_nearest_treasure(best_move, state.treasures),
                )
                if cand_key < best_key:
                    best_move = move
        return max_eval, best_move

    else:
        min_eval = float("inf")
        for move in state.get_legal_moves():
            child = state.apply_move(move)
            eval_score, _ = minimax(child, depth-1, metrics, True)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
        return min_eval, best_move


def alphabeta(state, depth, alpha, beta, metrics, maximizing=True):
    metrics.nodes_expanded += 1

    if depth == 0 or state.is_terminal():
        from evaluation import evaluate
        return evaluate(state), None

    best_move = None

    if maximizing:
        value = float("-inf")
        for move in state.get_legal_moves():
            child = state.apply_move(move)
            eval_score, _ = alphabeta(child, depth-1, alpha, beta, metrics, False)
            if eval_score > value:
                value = eval_score
                best_move = move
            elif eval_score == value and best_move is not None:
                prev_a = getattr(state, "prev_agent_a", None)
                cand_key = (
                    1 if prev_a is not None and move == prev_a else 0,
                    _dist_to_nearest_treasure(move, state.treasures),
                )
                best_key = (
                    1 if prev_a is not None and best_move == prev_a else 0,
                    _dist_to_nearest_treasure(best_move, state.treasures),
                )
                if cand_key < best_key:
                    best_move = move
            alpha = max(alpha, value)
            if beta <= alpha:
                metrics.pruned += 1
                break
        return value, best_move

    else:
        value = float("inf")
        for move in state.get_legal_moves():
            child = state.apply_move(move)
            eval_score, _ = alphabeta(child, depth-1, alpha, beta, metrics, True)
            if eval_score < value:
                value = eval_score
                best_move = move
            beta = min(beta, value)
            if beta <= alpha:
                metrics.pruned += 1
                break
        return value, best_move