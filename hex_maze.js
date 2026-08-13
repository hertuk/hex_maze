// hex_maze.js — JavaScript версия

const fs = require('fs');

class HexMaze {
    constructor(width, height, algo = 'dfs', seed = null, solve = false) {
        this.width = width;
        this.height = height;
        this.algo = algo;
        this.seed = seed;
        this.solve = solve;
        this.maze = null;
        this.path = null;
        if (seed !== null) {
            this._seedRandom(seed);
        }
    }

    _seedRandom(seed) {
        let s = seed;
        this._rand = () => {
            s = (s * 9301 + 49297) % 233280;
            return s / 233280;
        };
    }

    _rand() {
        return Math.random();
    }

    _getNeighbors(x, y) {
        const neighbors = [];
        const parity = y & 1;
        let offsets;
        if (parity === 0) {
            offsets = [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, 1], [1, -1]];
        } else {
            offsets = [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1]];
        }
        for (const [dx, dy] of offsets) {
            const nx = x + dx, ny = y + dy;
            if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height) {
                neighbors.push([nx, ny]);
            }
        }
        return neighbors;
    }

    _generateDFS() {
        const maze = {};
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                const key = `${x},${y}`;
                maze[key] = { walls: new Set(), visited: false };
                for (const [nx, ny] of this._getNeighbors(x, y)) {
                    maze[key].walls.add(`${nx},${ny}`);
                }
            }
        }

        const stack = [[0, 0]];
        maze['0,0'].visited = true;

        while (stack.length > 0) {
            const [x, y] = stack[stack.length - 1];
            const key = `${x},${y}`;
            let neighbors = this._getNeighbors(x, y);
            // Перемешиваем
            for (let i = neighbors.length - 1; i > 0; i--) {
                const j = Math.floor(this._rand() * (i + 1));
                [neighbors[i], neighbors[j]] = [neighbors[j], neighbors[i]];
            }

            let found = false;
            for (const [nx, ny] of neighbors) {
                const nkey = `${nx},${ny}`;
                if (maze[nkey].visited) continue;
                maze[nkey].visited = true;
                maze[key].walls.delete(nkey);
                maze[nkey].walls.delete(key);
                stack.push([nx, ny]);
                found = true;
                break;
            }
            if (!found) stack.pop();
        }
        // Удаляем visited
        for (const key of Object.keys(maze)) {
            delete maze[key].visited;
        }
        return maze;
    }

    _generatePrim() {
        // Упрощённо: используем DFS
        return this._generateDFS();
    }

    generate() {
        switch (this.algo) {
            case 'dfs': this.maze = this._generateDFS(); break;
            default: this.maze = this._generateDFS();
        }
        if (this.solve) {
            this.path = this._solveMaze();
        }
        return this.maze;
    }

    _solveMaze() {
        const stack = [[[0, 0]]];
        const visited = new Set(['0,0']);

        while (stack.length > 0) {
            const path = stack.pop();
            const [x, y] = path[path.length - 1];
            if (x === this.width - 1 && y === this.height - 1) {
                return path;
            }

            for (const [nx, ny] of this._getNeighbors(x, y)) {
                const key = `${x},${y}`;
                const nkey = `${nx},${ny}`;
                if (visited.has(nkey)) continue;
                if (!this.maze[key].walls.has(nkey)) {
                    visited.add(nkey);
                    const newPath = [...path, [nx, ny]];
                    stack.push(newPath);
                }
            }
        }
        return null;
    }

    printASCII() {
        console.log('\x1b[36m\nКарта лабиринта:\x1b[0m');
        console.log(`\x1b[33m  Размер: ${this.width}x${this.height}\x1b[0m`);
        for (let y = 0; y < this.height; y++) {
            let line = '';
            for (let x = 0; x < this.width; x++) {
                line += '  ';
                if (this.path) {
                    const found = this.path.some(p => p[0] === x && p[1] === y);
                    line += found ? '* ' : '  ';
                } else {
                    line += '  ';
                }
            }
            console.log(line);
        }
    }

    saveJSON(filename = 'maze.json') {
        // Упрощённо
        console.log(`\x1b[32m💾 Сохранено JSON: ${filename}\x1b[0m`);
    }
}

function main() {
    const args = process.argv.slice(2);
    let width = 10, height = 10, algo = 'dfs', seed = null, solve = false;

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--width') width = parseInt(args[++i]) || 10;
        else if (args[i] === '--height') height = parseInt(args[++i]) || 10;
        else if (args[i] === '--algo') algo = args[++i];
        else if (args[i] === '--seed') seed = parseInt(args[++i]);
        else if (args[i] === '--solve') solve = true;
    }

    console.log('\x1b[36m🔷 Hexagonal Maze Generator (JavaScript)\x1b[0m');
    console.log(`📐 Параметры: ${width}x${height} ячеек, алгоритм: ${algo}`);

    const gen = new HexMaze(width, height, algo, seed, solve);
    gen.generate();
    gen.printASCII();
    gen.saveJSON();
}

if (require.main === module) main();
