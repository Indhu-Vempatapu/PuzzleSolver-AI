from collections import deque
import heapq
import numpy as np
import random
import math
import copy

class PuzzleState:
    def __init__(self, board, zero_pos, moves, cost=0):
        self.board = board
        self.zero_pos = zero_pos
        self.moves = moves
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost

    def get_possible_moves(self):
        x, y = self.zero_pos
        possible_moves = []
        if x > 0: possible_moves.append((x - 1, y))  # Up
        if x < 2: possible_moves.append((x + 1, y))  # Down
        if y > 0: possible_moves.append((x, y - 1))  # Left
        if y < 2: possible_moves.append((x, y + 1))  # Right
        return possible_moves

    def move(self, new_zero_pos):
        new_board = self.board.copy()
        x, y = self.zero_pos
        new_x, new_y = new_zero_pos
        new_board[x][y], new_board[new_x][new_y] = new_board[new_x][new_y], new_board[x][y]
        new_moves = self.moves + [new_board]
        return PuzzleState(new_board, new_zero_pos, new_moves, self.cost + 1)

def manhattan_distance(board, goal):
    distance = 0
    for num in range(1, 9):
        x1, y1 = np.argwhere(board == num)[0]
        x2, y2 = np.argwhere(goal == num)[0]
        distance += abs(x1 - x2) + abs(y1 - y2)
    return distance

def bfs(start, goal):
    start_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    queue = deque([start_state])
    visited = {tuple(start.flatten())}
    print(f"BFS Kích thước hàng đợi ban đầu: {len(queue)}, Đã thăm: {len(visited)}")

    while queue:
        current_state = queue.popleft()
        if np.array_equal(current_state.board, goal):
            return current_state.moves

        for move in current_state.get_possible_moves():
            new_state = current_state.move(move)
            state_tuple = tuple(new_state.board.flatten())
            if state_tuple not in visited:
                visited.add(state_tuple)
                queue.append(new_state)
        print(f"BFS Kích thước hàng đợi: {len(queue)}, Đã thăm: {len(visited)}")

    print("Hàng đợi rỗng, không tìm thấy giải pháp")
    return None

def dfs(start, goal, max_depth=50000):
    start_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    stack = [start_state]
    visited = {tuple(start.flatten())}
    depth_limit = max_depth
    print(f"DFS Kích thước ngăn xếp ban đầu: {len(stack)}, Đã thăm: {len(visited)}")

    while stack:
        current_state = stack.pop()
        if len(current_state.moves) > depth_limit:
            print(f"DFS Bỏ qua: Vượt giới hạn độ sâu {depth_limit}")
            continue
        if np.array_equal(current_state.board, goal):
            return current_state.moves

        for move in current_state.get_possible_moves():
            new_state = current_state.move(move)
            state_tuple = tuple(new_state.board.flatten())
            if state_tuple not in visited:
                visited.add(state_tuple)
                stack.append(new_state)
        print(f"DFS Kích thước ngăn xếp: {len(stack)}, Đã thăm: {len(visited)}")

    print("Ngăn xếp rỗng, không tìm thấy giải pháp")
    return None

def ucs(start, goal):
    start_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start], cost=0)
    pq = [(0, start_state)]
    visited = {}
    print(f"UCS Kích thước hàng đợi ưu tiên ban đầu: {len(pq)}, Đã thăm: {len(visited)}")

    while pq:
        cost, current_state = heapq.heappop(pq)
        state_tuple = tuple(current_state.board.flatten())
        print(f"Chi phí: {cost}")

        if state_tuple in visited and visited[state_tuple] <= cost:
            print(f"UCS Bỏ qua: Trạng thái đã thăm với chi phí thấp hơn {visited[state_tuple]}")
            continue
        visited[state_tuple] = cost

        if np.array_equal(current_state.board, goal):
            return current_state.moves

        for move in current_state.get_possible_moves():
            new_state = current_state.move(move)
            heapq.heappush(pq, (new_state.cost, new_state))
        print(f"UCS Kích thước hàng đợi ưu tiên: {len(pq)}, Đã thăm: {len(visited)}")

    print("Hàng đợi ưu tiên rỗng, không tìm thấy giải pháp")
    return None

def dls(state, goal, depth, visited):
    print(f"DLS Độ sâu: {depth}, Trạng thái:\n{state.board}")
    if np.array_equal(state.board, goal):
        return state.moves
    if depth == 0:
        return None

    for move in state.get_possible_moves():
        new_state = state.move(move)
        new_board_tuple = tuple(new_state.board.flatten())
        if new_board_tuple not in visited:
            visited.add(new_board_tuple)
            result = dls(new_state, goal, depth - 1, visited)
            if result is not None:
                return result
    print(f"Không có nước đi hợp lệ ở độ sâu {depth}")
    return None

def ids(start, goal, max_depth=500):
    start_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    for depth in range(max_depth):
        visited = {tuple(start.flatten())}
        print(f"IDS Giới hạn độ sâu: {depth}, Đã thăm: {len(visited)}")
        result = dls(start_state, goal, depth, visited)
        if result is not None:
            print(f"IDS Tìm thấy giải pháp ở độ sâu {depth}")
            return result
    print(f"Đạt độ sâu tối đa {max_depth}, không tìm thấy giải pháp")
    return None

def gs(start, goal):
    start_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    pq = [(manhattan_distance(start, goal), start_state)]
    visited = {tuple(start.flatten())}
    print(f"GS Kích thước hàng đợi ưu tiên ban đầu: {len(pq)}, Đã thăm: {len(visited)}")

    while pq:
        _, current_state = heapq.heappop(pq)
        print(f"GS Trạng thái hiện tại:\n{current_state.board}\nManhattan: {manhattan_distance(current_state.board, goal)}")
        if np.array_equal(current_state.board, goal):
            return current_state.moves

        for move in current_state.get_possible_moves():
            new_state = current_state.move(move)
            state_tuple = tuple(new_state.board.flatten())
            if state_tuple not in visited:
                visited.add(state_tuple)
                heapq.heappush(pq, (manhattan_distance(new_state.board, goal), new_state))
        print(f"GS Kích thước hàng đợi ưu tiên: {len(pq)}, Đã thăm: {len(visited)}")

    print("Hàng đợi ưu tiên rỗng, không tìm thấy giải pháp")
    return None

def a_star(start, goal):
    start_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start], cost=0)
    pq = [(manhattan_distance(start, goal), 0, start_state)]
    visited = {}
    print(f"A* Kích thước hàng đợi ưu tiên ban đầu: {len(pq)}, Đã thăm: {len(visited)}")

    while pq:
        _, g, current_state = heapq.heappop(pq)
        state_tuple = tuple(current_state.board.flatten())
        print(f"A* Trạng thái hiện tại:\n{current_state.board}\nChi phí g: {g}, f: {g + manhattan_distance(current_state.board, goal)}")

        if state_tuple in visited and visited[state_tuple] <= g:
            print(f"A* Bỏ qua: Trạng thái đã thăm với chi phí thấp hơn {visited[state_tuple]}")
            continue
        visited[state_tuple] = g

        if np.array_equal(current_state.board, goal):
            return current_state.moves

        for move in current_state.get_possible_moves():
            new_state = current_state.move(move)
            new_g = g + 1
            new_f = new_g + manhattan_distance(new_state.board, goal)
            heapq.heappush(pq, (new_f, new_g, new_state))
        print(f"A* Kích thước hàng đợi ưu tiên: {len(pq)}, Đã thăm: {len(visited)}")

    print("Hàng đợi ưu tiên rỗng, không tìm thấy giải pháp")
    return None

def ida_star_dls(state, goal, threshold):
    f = state.cost + manhattan_distance(state.board, goal)
    print(f"IDA* DLS Trạng thái:\n{state.board}\nf: {f}, Ngưỡng: {threshold}")
    if f > threshold:
        print(f"IDA* DLS Vượt ngưỡng: {f} > {threshold}")
        return f, None
    if np.array_equal(state.board, goal):
        return f, state.moves

    min_threshold = float('inf')
    for move in state.get_possible_moves():
        new_state = state.move(move)
        new_threshold, result = ida_star_dls(new_state, goal, threshold)
        if result is not None:
            return new_threshold, result
        min_threshold = min(min_threshold, new_threshold)

    print(f"IDA* DLS Không còn nước đi, ngưỡng tối thiểu: {min_threshold}")
    return min_threshold, None

def ida_star(start, goal):
    start_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start], cost=0)
    threshold = manhattan_distance(start, goal)
    print(f"IDA* Ngưỡng ban đầu: {threshold}")

    while True:
        new_threshold, result = ida_star_dls(start_state, goal, threshold)
        if result is not None:
            return result
        if new_threshold == float('inf'):
            print("Ngưỡng vô cực, không tìm thấy giải pháp")
            return None
        threshold = new_threshold
        print(f"IDA* Ngưỡng mới: {threshold}")

def shc(start, goal):
    current_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    while not np.array_equal(current_state.board, goal):
        neighbors = [current_state.move(move) for move in current_state.get_possible_moves()]
        print(f"SHC Trạng thái hiện tại:\n{current_state.board}\nSố lân cận: {len(neighbors)}")
        if not neighbors:
            print("Không có lân cận")
            return None
        next_state = min(neighbors, key=lambda state: manhattan_distance(state.board, goal))
        if manhattan_distance(next_state.board, goal) >= manhattan_distance(current_state.board, goal):
            print(f"Không có lân cận tốt hơn, khoảng cách hiện tại: {manhattan_distance(current_state.board, goal)}")
            return None
        current_state = next_state
    return current_state.moves

def sahc(start, goal):
    current_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    while not np.array_equal(current_state.board, goal):
        neighbors = [current_state.move(move) for move in current_state.get_possible_moves()]
        print(f"SAHC Trạng thái hiện tại:\n{current_state.board}\nSố lân cận: {len(neighbors)}")
        if not neighbors:
            print("Không có lân cận")
            return None
        next_state = min(neighbors, key=lambda state: manhattan_distance(state.board, goal))
        if manhattan_distance(next_state.board, goal) >= manhattan_distance(current_state.board, goal):
            print(f"Không có lân cận tốt hơn, khoảng cách hiện tại: {manhattan_distance(current_state.board, goal)}")
            return None
        current_state = next_state
    return current_state.moves

def sthc(start, goal, max_attempts=1000):
    current_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    attempts = 0
    while not np.array_equal(current_state.board, goal) and attempts < max_attempts:
        neighbors = [current_state.move(move) for move in current_state.get_possible_moves()]
        print(f"STHC Trạng thái hiện tại:\n{current_state.board}\nLượt: {attempts}, Số lân cận: {len(neighbors)}")
        if not neighbors:
            print("Không có lân cận")
            return None
        valid_neighbors = [n for n in neighbors if manhattan_distance(n.board, goal) <= manhattan_distance(current_state.board, goal)]
        if not valid_neighbors:
            print("Không có lân cận hợp lệ")
            return None
        current_state = random.choice(valid_neighbors)
        attempts += 1
    if np.array_equal(current_state.board, goal):
        return current_state.moves
    print(f"Đạt số lượt tối đa {max_attempts}")
    return None

def simulated_annealing(start, goal, initial_temp=1000, cooling_rate=0.99, min_temp=1):
    current_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    temp = initial_temp
    while temp > min_temp:
        print(f"SA Trạng thái hiện tại:\n{current_state.board}\nNhiệt độ: {temp:.2f}")
        if np.array_equal(current_state.board, goal):
            return current_state.moves
        neighbors = [current_state.move(move) for move in current_state.get_possible_moves()]
        if not neighbors:
            print("Không có lân cận")
            break
        next_state = random.choice(neighbors)
        delta_e = manhattan_distance(next_state.board, goal) - manhattan_distance(current_state.board, goal)
        print(f"SA Delta E: {delta_e}, Xác suất: {math.exp(-delta_e / temp) if delta_e > 0 else 1.0}")
        if delta_e < 0 or random.random() < math.exp(-delta_e / temp):
            current_state = next_state
        temp *= cooling_rate
    print("Đạt nhiệt độ tối thiểu, không tìm thấy giải pháp")
    return None

def beam(start, goal, beam_width=3):
    start_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    frontier = [start_state]
    visited = {tuple(start.flatten())}
    print(f"Beam Kích thước miền khám phá ban đầu: {len(frontier)}, Đã thăm: {len(visited)}")

    while frontier:
        next_frontier = []
        for state in frontier:
            print(f"Beam Trạng thái hiện tại:\n{state.board}\nManhattan: {manhattan_distance(state.board, goal)}")
            if np.array_equal(state.board, goal):
                return state.moves
            for move in state.get_possible_moves():
                new_state = state.move(move)
                state_tuple = tuple(new_state.board.flatten())
                if state_tuple not in visited:
                    visited.add(state_tuple)
                    next_frontier.append(new_state)
        if not next_frontier:
            print("Miền khám phá rỗng, không tìm thấy giải pháp")
            return None
        next_frontier.sort(key=lambda s: manhattan_distance(s.board, goal))
        frontier = next_frontier[:beam_width]
        print(f"Beam Kích thước miền khám phá: {len(frontier)}, Đã thăm: {len(visited)}")
    return None

def ga(start, goal, population_size=50, generations=100, mutation_rate=0.1):
    def generate_individual():
        state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
        moves = [start.copy()]
        for _ in range(random.randint(5, 20)):
            possible_moves = state.get_possible_moves()
            if not possible_moves:
                break
            move = random.choice(possible_moves)
            state = state.move(move)
            moves.append(state.board)
        return moves

    def fitness(individual):
        distance = manhattan_distance(individual[-1], goal)
        return 1 / (1 + distance)

    def crossover(parent1, parent2):
        cp = random.randint(1, min(len(parent1), len(parent2)) - 1)
        child1 = parent1[:cp] + parent2[cp:]
        child2 = parent2[:cp] + parent1[cp:]
        return child1 if is_valid_individual(child1) else parent1, child2 if is_valid_individual(child2) else parent2    

    def mutate(individual):
        if random.random() < mutation_rate:
            idx = random.randint(0, len(individual) - 1)
            state = PuzzleState(individual[idx], tuple(np.argwhere(individual[idx] == 0)[0]), individual[:idx + 1])
            moves = state.get_possible_moves()
            if moves:
                new_state = state.move(random.choice(moves))
                individual[idx] = new_state.board.copy()
        return individual if is_valid_individual(individual) else generate_individual()

    def is_valid_individual(individual):
        if not individual or not isinstance(individual, list):
            return False
        for board in individual:
            if not isinstance(board, np.ndarray) or board.shape != (3, 3):
                return False
        return True

    population = [generate_individual() for _ in range(population_size)]
    print(f"GA Kích thước quần thể ban đầu: {len(population)}")
    for gen in range(generations):
        fitness_scores = [fitness(ind) for ind in population]
        print(f"GA Thế hệ {gen}, Độ thích nghi tốt nhất: {max(fitness_scores)}")
        if max(fitness_scores) >= 1:  # Đạt mục tiêu
            best = population[fitness_scores.index(max(fitness_scores))]
            return best
        new_population = []
        for _ in range(population_size // 2):
            parents = random.choices(population, weights=fitness_scores, k=2)
            child1, child2 = crossover(parents[0], parents[1])
            new_population.extend([mutate(child1), mutate(child2)])
        population = new_population[:population_size]
    print("Đạt số thế hệ tối đa, không tìm thấy giải pháp")
    return None

def and_or_search(start, goal):
    start_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    visited = {tuple(start.flatten())}

    def or_search(state, path):
        print(f"And-Or OR Trạng thái:\n{state.board}")
        if np.array_equal(state.board, goal):
            return state.moves
        if tuple(state.board.flatten()) in visited:
            print("Trạng thái đã thăm")
            return None
        visited.add(tuple(state.board.flatten()))
        for move in state.get_possible_moves():
            new_state = state.move(move)
            plan = and_search([new_state], path + [state])
            if plan is not None:
                return state.moves[:-1] + plan
        print("Không có nước đi hợp lệ")
        return None

    def and_search(states, path):
        print(f"And-Or AND Số trạng thái: {len(states)}")
        if not states:
            return []
        plans = []
        for state in states:
            plan = or_search(state, path)
            if plan is None:
                print("Không có kế hoạch cho trạng thái")
                return None
            plans.extend(plan[1:] if plans else plan)
        return plans

    result = or_search(start_state, [])
    return result

class BeliefState:
    def __init__(self, boards, moves):
        self.boards = boards  # Tập hợp các bảng có thể
        self.moves = moves

def bs(start, goal):
    start_state = BeliefState({tuple(start.flatten())}, [start])
    queue = deque([start_state])
    visited = set()
    print(f"BS Kích thước hàng đợi ban đầu: {len(queue)}, Đã thăm: {len(visited)}")

    while queue:
        current_state = queue.popleft()
        print(f"BS Số bảng hiện tại: {len(current_state.boards)}")
        if any(np.array_equal(np.array(b).reshape(3, 3), goal) for b in current_state.boards):
            return current_state.moves

        next_boards = set()
        for board_tuple in current_state.boards:
            board = np.array(board_tuple).reshape(3, 3)
            state = PuzzleState(board, tuple(np.argwhere(board == 0)[0]), [])
            for move in state.get_possible_moves():
                new_state = state.move(move)
                next_boards.add(tuple(new_state.board.flatten()))

        next_state = BeliefState(next_boards, current_state.moves + [np.array(list(next_boards)[0]).reshape(3, 3)])
        state_tuple = frozenset(next_boards)
        if state_tuple not in visited:
            visited.add(state_tuple)
            queue.append(next_state)
        print(f"BS Kích thước hàng đợi: {len(queue)}, Đã thăm: {len(visited)}")

    print("Hàng đợi rỗng, không tìm thấy giải pháp")
    return None

def swpo(start, goal):
    start_state = PuzzleState(start, tuple(np.argwhere(start == 0)[0]), [start])
    queue = deque([start_state])
    visited = {tuple(start.flatten())}
    print(f"SWPO Kích thước hàng đợi ban đầu: {len(queue)}, Đã thăm: {len(visited)}")

    while queue:
        current_state = queue.popleft()
        print(f"SWPO Trạng thái hiện tại:\n{current_state.board}")
        if np.array_equal(current_state.board, goal):
            return current_state.moves

        for move in current_state.get_possible_moves():
            new_state = current_state.move(move)
            state_tuple = tuple(new_state.board.flatten())
            if state_tuple not in visited:
                visited.add(state_tuple)
                queue.append(new_state)
        print(f"SWPO Kích thước hàng đợi: {len(queue)}, Đã thăm: {len(visited)}")

    print("Hàng đợi rỗng, không tìm thấy giải pháp")
    return None

def ac_3(start, goal):
    variables = list(range(9))  # Ô 0-8
    domains = {v: list(range(9)) for v in variables}  # Vị trí 0-8
    constraints = [(i, j) for i in variables for j in variables if i < j]  # Tất cả khác nhau

    def revise(xi, xj):
        revised = False
        for x in domains[xi][:]:
            if all(x == y for y in domains[xj]):
                domains[xi].remove(x)
                revised = True
        return revised

    queue = deque(constraints)
    print(f"AC-3 Số ràng buộc ban đầu: {len(queue)}")
    while queue:
        xi, xj = queue.popleft()
        if revise(xi, xj):
            if not domains[xi]:
                print("Miền rỗng cho biến")
                return None
            for xk in [v for v in variables if v != xj and (xk, xi) in constraints]:
                queue.append((xk, xi))
        print(f"AC-3 Số ràng buộc còn lại: {len(queue)}")

    assignment = {}
    for v in variables:
        if not domains[v]:
            print("Không có miền hợp lệ cho biến")
            return None
        assignment[v] = domains[v][0]
    board = np.zeros((3, 3), dtype=int)
    for tile, pos in assignment.items():
        board[pos // 3][pos % 3] = tile
    if np.array_equal(board, goal):
        return [board]
    print("Bảng tạo ra không khớp mục tiêu")
    return None

def backtracking(start, goal):
    def consistent(assignment, var, value):
        for v, val in assignment.items():
            if val == value:
                return False
        return True

    def backtrack(assignment, variables, domains):
        if len(assignment) == len(variables):
            board = np.zeros((3, 3), dtype=int)
            for tile, pos in assignment.items():
                board[pos // 3][pos % 3] = tile
            if np.array_equal(board, goal):
                return [board]
            print("Gán không khớp mục tiêu")
            return None
        var = variables[len(assignment)]
        for value in domains[var]:
            if consistent(assignment, var, value):
                assignment[var] = value
                result = backtrack(assignment.copy(), variables, domains)
                if result is not None:
                    return result
        print(f"Không có giá trị hợp lệ cho biến {var}")
        return None

    variables = list(range(9))
    domains = {v: list(range(9)) for v in variables}
    result = backtrack({}, variables, domains)
    return result

def backtracking_fc(start, goal):
    print(f"Backtracking FC Bắt đầu:\n{start}\nMục tiêu:\n{goal}")
    def forward_check(assignment, var, value, domains):
        new_domains = copy.deepcopy(domains)
        for v in variables:
            if v not in assignment and value in new_domains[v]:
                new_domains[v].remove(value)
                if not new_domains[v]:
                    return None
        return new_domains

    def backtrack(assignment, variables, domains):
        if len(assignment) == len(variables):
            board = np.zeros((3, 3), dtype=int)
            for tile, pos in assignment.items():
                board[pos // 3][pos % 3] = tile
            if np.array_equal(board, goal):
                return [board]
            print("Gán không khớp mục tiêu")
            return None
        var = variables[len(assignment)]
        for value in domains[var]:
            new_domains = forward_check(assignment, var, value, domains)
            if new_domains is not None:
                assignment[var] = value
                result = backtrack(assignment.copy(), variables, new_domains)
                if result is not None:
                    return result
        print(f"Không có giá trị hợp lệ cho biến {var}")
        return None

    variables = list(range(9))
    domains = {v: list(range(9)) for v in variables}
    result = backtrack({}, variables, domains)
    return result

def q_learning(start, goal_state, episodes=100, alpha=0.1, gamma=0.9, epsilon=0.3):
    def state_to_str(state):
        return str(state.tolist())

    def get_neighbors(state):
        neighbors = []
        row, col = np.argwhere(state == 0)[0]
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_state = state.copy()
                new_state[row, col], new_state[new_row, new_col] = new_state[new_row, new_col], new_state[row, col]
                neighbors.append(new_state)
        return neighbors

    def is_goal(state, goal_state):
        return np.array_equal(state, goal_state)

    def find_action_index(action, possible_actions):
        for idx, pa in enumerate(possible_actions):
            if np.array_equal(pa, action):
                return idx
        raise ValueError("Hành động không có trong possible_actions")

    q_table = {}
    consecutive_successes = 0
    success_threshold = 10  # Dừng nếu đạt mục tiêu 10 lần liên tiếp

    def choose_action(state_str, possible_actions):
        if random.uniform(0, 1) < epsilon:
            return random.choice(possible_actions)
        q_values = q_table.get(state_str, {})
        if not q_values:
            return random.choice(possible_actions)
        max_q = max(q_values.values())
        best_indices = [idx for idx, q in q_values.items() if q == max_q]
        return possible_actions[random.choice(best_indices)]

    for episode in range(episodes):
        current_state = start.copy()
        current_state_str = state_to_str(current_state)
        steps = 0
        max_steps = 500
        print(f"Q-Learning Lượt {episode}, Trạng thái ban đầu:\n{current_state}")

        while steps < max_steps:
            possible_actions = get_neighbors(current_state)
            if not possible_actions:
                print(f"Q-Learning Lượt {episode} Thất bại: Không có hành động khả thi")
                break

            action = choose_action(current_state_str, possible_actions)
            action_idx = find_action_index(action, possible_actions)

            reward = -1
            manhattan_dist = sum(abs(np.argwhere(action == num)[0][0] - np.argwhere(goal_state == num)[0][0]) +
                                 abs(np.argwhere(action == num)[0][1] - np.argwhere(goal_state == num)[0][1])
                                 for num in range(1, 9))
            if is_goal(action, goal_state):
                reward = 200
                next_state = action
            else:
                reward = -1 - manhattan_dist * 0.1
                next_state = action

            next_state_str = state_to_str(next_state)
            if current_state_str not in q_table:
                q_table[current_state_str] = {}
            old_q = q_table[current_state_str].get(action_idx, 0.0)
            future_q = max(q_table.get(next_state_str, {}).values(), default=0) if q_table.get(next_state_str) else 0
            new_q = old_q + alpha * (reward + gamma * future_q - old_q)
            q_table[current_state_str][action_idx] = new_q

            current_state = next_state.copy()
            current_state_str = next_state_str
            steps += 1

            if is_goal(current_state, goal_state):
                print(f"Q-Learning Lượt {episode} Thành công: Đạt mục tiêu")
                consecutive_successes += 1
                if consecutive_successes >= success_threshold:
                    print(f"Q-Learning Dừng sớm: Đạt {success_threshold} lần thành công liên tiếp")
                    break
                break
            else:
                consecutive_successes = 0

        if steps >= max_steps:
            print(f"Q-Learning Lượt {episode} Thất bại: Đạt số bước tối đa {max_steps}")
            
        if consecutive_successes >= success_threshold:
            break

    print(f"Q-Learning Q-table cho trạng thái bắt đầu: {q_table.get(state_to_str(start), {})}")
    path = [start.copy()]
    current_state = start.copy()
    current_state_str = state_to_str(current_state)
    visited = set()
    visited.add(current_state_str)
    max_steps = 100

    for step in range(max_steps):
        possible_actions = get_neighbors(current_state)
        if not possible_actions:
            print(f"Không có hành động ở bước {step}")
            break

        q_values = q_table.get(current_state_str, {})
        if not q_values:
            print(f"Không có Q-value cho trạng thái:\n{current_state}")
            break

        max_q = max(q_values.values(), default=0)
        best_indices = [idx for idx, q in q_values.items() if q == max_q]
        if not best_indices:
            print(f"Không có chỉ số tốt nhất cho trạng thái:\n{current_state}")
            break

        chosen_idx = random.choice(best_indices)
        next_state = possible_actions[chosen_idx]
        print(f"Q-Learning Đường đi Bước {step}: Chọn hành động với Q={max_q}\n{next_state}")

        next_state_str = state_to_str(next_state)
        path.append(next_state.copy())
        current_state = next_state.copy()
        current_state_str = next_state_str

        if is_goal(current_state, goal_state):
            return path

        if next_state_str in visited:
            print(f"Phát hiện vòng lặp ở bước {step}")
            break
        visited.add(next_state_str)

    print(f"Không tìm thấy giải pháp sau {max_steps} bước")
    return None
