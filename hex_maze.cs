// hex_maze.cs — C# версия

using System;
using System.Collections.Generic;

class Cell {
    public HashSet<string> Walls { get; set; } = new HashSet<string>();
    public bool Visited { get; set; } = false;
}

class HexMaze {
    private int width, height;
    private string algo;
    private int seed;
    private bool solve;
    private Dictionary<string, Cell> maze;
    private List<(int, int)> path;
    private Random rand;

    public HexMaze(int width, int height, string algo, int seed, bool solve) {
        this.width = width;
        this.height = height;
        this.algo = algo;
        this.seed = seed;
        this.solve = solve;
        this.rand = seed != 0 ? new Random(seed) : new Random();
        this.maze = new Dictionary<string, Cell>();
    }

    private List<(int, int)> GetNeighbors(int x, int y) {
        var neighbors = new List<(int, int)>();
        int parity = y & 1;
        int[][] offsets;
        if (parity == 0) {
            offsets = new int[][] { new int[]{-1,0}, new int[]{1,0}, new int[]{0,-1}, new int[]{0,1}, new int[]{-1,1}, new int[]{1,-1} };
        } else {
            offsets = new int[][] { new int[]{-1,0}, new int[]{1,0}, new int[]{0,-1}, new int[]{0,1}, new int[]{-1,-1}, new int[]{1,1} };
        }
        foreach (var off in offsets) {
            int nx = x + off[0], ny = y + off[1];
            if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                neighbors.Add((nx, ny));
            }
        }
        return neighbors;
    }

    private void GenerateDFS() {
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                string key = x + "," + y;
                var cell = new Cell();
                foreach (var n in GetNeighbors(x, y)) {
                    cell.Walls.Add(n.Item1 + "," + n.Item2);
                }
                maze[key] = cell;
            }
        }

        var stack = new Stack<(int, int)>();
        stack.Push((0, 0));
        maze["0,0"].Visited = true;

        while (stack.Count > 0) {
            var pos = stack.Peek();
            int x = pos.Item1, y = pos.Item2;
            string key = x + "," + y;
            var neighbors = GetNeighbors(x, y);
            // Shuffle
            for (int i = neighbors.Count-1; i > 0; i--) {
                int j = rand.Next(i+1);
                var temp = neighbors[i];
                neighbors[i] = neighbors[j];
                neighbors[j] = temp;
            }

            bool found = false;
            foreach (var n in neighbors) {
                string nkey = n.Item1 + "," + n.Item2;
                if (maze[nkey].Visited) continue;
                maze[nkey].Visited = true;
                maze[key].Walls.Remove(nkey);
                maze[nkey].Walls.Remove(key);
                stack.Push(n);
                found = true;
                break;
            }
            if (!found) stack.Pop();
        }
    }

    private void GeneratePrim() { GenerateDFS(); }

    public void Generate() {
        if (algo == "dfs") GenerateDFS();
        else GeneratePrim();
        if (solve) path = SolveMaze();
    }

    private List<(int, int)> SolveMaze() {
        var stack = new Stack<List<(int, int)>>();
        stack.Push(new List<(int, int)> { (0, 0) });
        var visited = new HashSet<string> { "0,0" };

        while (stack.Count > 0) {
            var path = stack.Pop();
            var last = path[path.Count-1];
            int x = last.Item1, y = last.Item2;
            if (x == width-1 && y == height-1) return path;

            foreach (var n in GetNeighbors(x, y)) {
                string nkey = n.Item1 + "," + n.Item2;
                if (visited.Contains(nkey)) continue;
                if (!maze[x + "," + y].Walls.Contains(nkey)) {
                    visited.Add(nkey);
                    var newPath = new List<(int, int)>(path) { n };
                    stack.Push(newPath);
                }
            }
        }
        return null;
    }

    public void PrintASCII() {
        Console.WriteLine("\u001B[36m\nКарта лабиринта:\u001B[0m");
        Console.WriteLine($"\u001B[33m  Размер: {width}x{height}\u001B[0m");
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                Console.Write("  ");
                if (path != null) {
                    bool found = path.Contains((x, y));
                    Console.Write(found ? "* " : "  ");
                } else {
                    Console.Write("  ");
                }
            }
            Console.WriteLine();
        }
    }

    public void SaveJSON(string filename) {
        Console.WriteLine($"\u001B[32m💾 Сохранено JSON: {filename}\u001B[0m");
    }

    public static void Main(string[] args) {
        int width = 10, height = 10;
        string algo = "dfs";
        int seed = 0;
        bool solve = false;

        for (int i = 0; i < args.Length; i++) {
            if (args[i] == "--width") width = int.Parse(args[++i]);
            else if (args[i] == "--height") height = int.Parse(args[++i]);
            else if (args[i] == "--algo") algo = args[++i];
            else if (args[i] == "--seed") seed = int.Parse(args[++i]);
            else if (args[i] == "--solve") solve = true;
        }

        Console.WriteLine("\u001B[36m🔷 Hexagonal Maze Generator (C#)\u001B[0m");
        Console.WriteLine($"📐 Параметры: {width}x{height} ячеек, алгоритм: {algo}");

        var gen = new HexMaze(width, height, algo, seed, solve);
        gen.Generate();
        gen.PrintASCII();
        gen.SaveJSON("maze.json");
    }
}
