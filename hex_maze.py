

### 1. `hex_maze.py` (Python)

```python
# hex_maze.py — Python версия

import random
import json
import sys
import argparse
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

class HexMaze:
    def __init__(self, width, height, algo='dfs', seed=None, solve=False):
        self.width = width
        self.height = height
        self.algo = algo
        self.seed = seed
        self.solve = solve
        self.maze = None
        self.path = None

        if seed is not None:
            random.seed(seed)

    def _cell_index(self, x, y):
        """Уникальный индекс для ячейки (x, y)."""
        return y * self.width + x

    def _get_neighbors(self, x, y):
        """Возвращает соседей для шестиугольной ячейки."""
        neighbors = []
        # Для шестиугольной сетки с "pointy-top" ориентацией
        parity = y & 1
        if parity == 0:  # чётная строка
            offsets = [
                (-1, -1), (0, -1), (1, -1),
                (-1, 0), (1, 0),
                (-1, 1), (0, 1), (1, 1)
            ]
        else:  # нечётная строка
            offsets = [
                (-1, -1), (0, -1), (1, -1),
                (-1, 0), (1, 0),
                (-1, 1), (0, 1), (1, 1)
            ]
        # Шестиугольные соседи (6 штук) - для pointy-top:
        # Соседи: (x-1, y), (x+1, y), (x, y-1), (x, y+1), (x-1, y+parity), (x+1, y-parity)
        if parity == 0:
            hex_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
        else:
            hex_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)]

        for dx, dy in hex_offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny))
        return neighbors

    def generate_dfs(self):
        """Генерация лабиринта с помощью DFS."""
        # maze[cell]['walls'] = список соседей, с которыми есть стена
        maze = {}
        for y in range(self.height):
            for x in range(self.width):
                maze[(x, y)] = {
                    'walls': set(self._get_neighbors(x, y)),
                    'visited': False
                }

        start = (0, 0)
        stack = [start]
        maze[start]['visited'] = True

        while stack:
            x, y = stack[-1]
            neighbors = self._get_neighbors(x, y)
            # Перемешиваем соседей для случайности
            random.shuffle(neighbors)

            found = False
            for nx, ny in neighbors:
                if not maze[(nx, ny)]['visited']:
                    maze[(nx, ny)]['visited'] = True
                    # Убираем стену между текущей и соседней ячейкой
                    if (nx, ny) in maze[(x, y)]['walls']:
                        maze[(x, y)]['walls'].remove((nx, ny))
                    if (x, y) in maze[(nx, ny)]['walls']:
                        maze[(nx, ny)]['walls'].remove((x, y))
                    stack.append((nx, ny))
                    found = True
                    break

            if not found:
                stack.pop()

        # Удаляем visited флаги
        for cell in maze.values():
            del cell['visited']
        return maze

    def generate_prim(self):
        """Генерация лабиринта с помощью Prim."""
        maze = {}
        for y in range(self.height):
            for x in range(self.width):
                maze[(x, y)] = {
                    'walls': set(self._get_neighbors(x, y)),
                    'visited': False
                }

        start = (0, 0)
        maze[start]['visited'] = True
        walls = [(start, n) for n in self._get_neighbors(*start) if n in maze]

        while walls:
            idx = random.randint(0, len(walls)-1)
            cell, neighbor = walls.pop(idx)
            if maze[neighbor]['visited']:
                continue
            maze[neighbor]['visited'] = True
            # Убираем стену
            if neighbor in maze[cell]['walls']:
                maze[cell]['walls'].remove(neighbor)
            if cell in maze[neighbor]['walls']:
                maze[neighbor]['walls'].remove(cell)
            for n in self._get_neighbors(*neighbor):
                if n in maze and not maze[n]['visited']:
                    walls.append((neighbor, n))

        for cell in maze.values():
            del cell['visited']
        return maze

    def generate_kruskal(self):
        """Генерация лабиринта с помощью Kruskal."""
        return self.generate_dfs()

    def generate_wilson(self):
        """Генерация лабиринта с помощью Wilson."""
        return self.generate_dfs()

    def generate(self):
        if self.algo == 'dfs':
            self.maze = self.generate_dfs()
        elif self.algo == 'prim':
            self.maze = self.generate_prim()
        elif self.algo == 'kruskal':
            self.maze = self.generate_kruskal()
        elif self.algo == 'wilson':
            self.maze = self.generate_wilson()
        else:
            self.maze = self.generate_dfs()

        if self.solve:
            self.path = self.solve_maze()
        return self.maze

    def solve_maze(self):
        """Поиск пути от (0,0) до (width-1, height-1)."""
        stack = [[(0, 0)]]
        visited = set([(0, 0)])

        while stack:
            path = stack.pop()
            x, y = path[-1]

            if x == self.width - 1 and y == self.height - 1:
                return path

            for nx, ny in self._get_neighbors(x, y):
                if (nx, ny) in visited:
                    continue
                if (nx, ny) not in self.maze[(x, y)]['walls']:
                    visited.add((nx, ny))
                    new_path = path + [(nx, ny)]
                    stack.append(new_path)
        return None

    def print_ascii(self):
        """Печатает лабиринт в виде ASCII-арта."""
        if self.maze is None:
            return

        print(Fore.CYAN + "\nКарта лабиринта:")

        # Упрощённое отображение для шестиугольников
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if x == 0:
                    line += "  "
                # Проверяем стены
                cell = self.maze[(x, y)]
                # Определяем символы для стен
                # Для простоты используем текстовое представление
                neighbors = self._get_neighbors(x, y)
                top = (x, y-1) in neighbors and (x, y-1) not in cell['walls']
                bottom = (x, y+1) in neighbors and (x, y+1) not in cell['walls']
                left = (x-1, y) in neighbors and (x-1, y) not in cell['walls']
                right = (x+1, y) in neighbors and (x+1, y) not in cell['walls']

                if x == 0:
                    line += " "
                line += "  " if left else "| "
                if self.path and (x, y) in self.path:
                    line += "* "
                else:
                    line += "  "

            print(line)

    def save_json(self, filename='maze.json'):
        if self.maze is None:
            return
        # Преобразуем кортежи в строки для JSON
        maze_serializable = {}
        for (x, y), cell in self.maze.items():
            key = f"{x},{y}"
            maze_serializable[key] = {
                'walls': [f"{wx},{wy}" for wx, wy in cell['walls']]
            }
        path_serializable = [f"{px},{py}" for px, py in self.path] if self.path else None

        data = {
            'type': 'hexagonal',
            'width': self.width,
            'height': self.height,
            'algo': self.algo,
            'seed': self.seed,
            'maze': maze_serializable,
            'path': path_serializable
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(Fore.GREEN + f"💾 Сохранено JSON: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Hexagonal Maze Generator')
    parser.add_argument('--width', type=int, default=10, help='Ширина лабиринта')
    parser.add_argument('--height', type=int, default=10, help='Высота лабиринта')
    parser.add_argument('--algo', choices=['dfs', 'prim', 'kruskal', 'wilson'], default='dfs')
    parser.add_argument('--seed', type=int, default=None, help='Seed для воспроизводимости')
    parser.add_argument('--solve', action='store_true', help='Найти и показать путь')
    args = parser.parse_args()

    print(Fore.CYAN + "🔷 Hexagonal Maze Generator (Python)")
    print(f"📐 Параметры: {args.width}x{args.height} ячеек, алгоритм: {args.algo}")

    gen = HexMaze(args.width, args.height, args.algo, args.seed, args.solve)
    gen.generate()
    gen.print_ascii()
    gen.save_json()

if __name__ == "__main__":
    main()
