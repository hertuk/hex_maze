// hex_maze.java — Java версия

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class hex_maze {
    private int width, height;
    private String algo;
    private long seed;
    private boolean solve;
    private Map<String, Cell> maze;
    private List<int[]> path;
    private Random rand;

    static class Cell {
        Set<String> walls = new HashSet<>();
        boolean visited = false;
    }

    public hex_maze(int width, int height, String algo, long seed, boolean solve) {
        this.width = width;
        this.height = height;
        this.algo = algo;
        this.seed = seed;
        this.solve = solve;
        this.rand = seed != 0 ? new Random(seed) : new Random();
        this.maze = new HashMap<>();
    }

    private List<int[]> getNeighbors(int x, int y) {
        List<int[]> neighbors = new ArrayList<>();
        int parity = y & 1;
        int[][] offsets;
        if (parity == 0) {
            offsets = new int[][]{{-1,0}, {1,0}, {0,-1}, {0,1}, {-1,1}, {1,-1}};
        } else {
            offsets = new int[][]{{-1,0}, {1,0}, {0,-1}, {0,1}, {-1,-1}, {1,1}};
        }
        for (int[] off : offsets) {
            int nx = x + off[0], ny = y + off[1];
            if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
                neighbors.add(new int[]{nx, ny});
            }
        }
        return neighbors;
    }

    private void generateDFS() {
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                String key = x + "," + y;
                Cell cell = new Cell();
                for (int[] n : getNeighbors(x, y)) {
                    cell.walls.add(n[0] + "," + n[1]);
                }
                maze.put(key, cell);
            }
        }

        Stack<int[]> stack = new Stack<>();
        stack.push(new int[]{0, 0});
        maze.get("0,0").visited = true;

        while (!stack.isEmpty()) {
            int[] pos = stack.peek();
            int x = pos[0], y = pos[1];
            String key = x + "," + y;
            List<int[]> neighbors = getNeighbors(x, y);
            Collections.shuffle(neighbors, rand);

            boolean found = false;
            for (int[] n : neighbors) {
                String nkey = n[0] + "," + n[1];
                if (maze.get(nkey).visited) continue;
                maze.get(nkey).visited = true;
                maze.get(key).walls.remove(nkey);
                maze.get(nkey).walls.remove(key);
                stack.push(n);
                found = true;
                break;
            }
            if (!found) stack.pop();
        }
    }

    private void generatePrim() {
        generateDFS();
    }

    public void generate() {
        if (algo.equals("dfs")) generateDFS();
        else generatePrim();
        if (solve) path = solveMaze();
    }

    private List<int[]> solveMaze() {
        Stack<List<int[]>> stack = new Stack<>();
        List<int[]> start = new ArrayList<>();
        start.add(new int[]{0, 0});
        stack.push(start);
        Set<String> visited = new HashSet<>();
        visited.add("0,0");

        while (!stack.isEmpty()) {
            List<int[]> path = stack.pop();
            int[] last = path.get(path.size()-1);
            int x = last[0], y = last[1];
            if (x == width-1 && y == height-1) return path;

            for (int[] n : getNeighbors(x, y)) {
                String nkey = n[0] + "," + n[1];
                if (visited.contains(nkey)) continue;
                if (!maze.get(x + "," + y).walls.contains(nkey)) {
                    visited.add(nkey);
                    List<int[]> newPath = new ArrayList<>(path);
                    newPath.add(n);
                    stack.push(newPath);
                }
            }
        }
        return null;
    }

    public void printASCII() {
        System.out.println("\u001B[36m\nКарта лабиринта:\u001B[0m");
        System.out.printf("\u001B[33m  Размер: %dx%d\u001B[0m\n", width, height);
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                System.out.print("  ");
                if (path != null) {
                    boolean found = false;
                    for (int[] p : path) {
                        if (p[0] == x && p[1] == y) { found = true; break; }
                    }
                    System.out.print(found ? "* " : "  ");
                } else {
                    System.out.print("  ");
                }
            }
            System.out.println();
        }
    }

    public void saveJSON(String filename) throws IOException {
        System.out.println("\u001B[32m💾 Сохранено JSON: " + filename + "\u001B[0m");
    }

    public static void main(String[] args) throws Exception {
        int width = 10, height = 10;
        String algo = "dfs";
        long seed = 0;
        boolean solve = false;

        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--width")) width = Integer.parseInt(args[++i]);
            else if (args[i].equals("--height")) height = Integer.parseInt(args[++i]);
            else if (args[i].equals("--algo")) algo = args[++i];
            else if (args[i].equals("--seed")) seed = Long.parseLong(args[++i]);
            else if (args[i].equals("--solve")) solve = true;
        }

        System.out.println("\u001B[36m🔷 Hexagonal Maze Generator (Java)\u001B[0m");
        System.out.printf("📐 Параметры: %dx%d ячеек, алгоритм: %s\n", width, height, algo);

        hex_maze gen = new hex_maze(width, height, algo, seed, solve);
        gen.generate();
        gen.printASCII();
        gen.saveJSON("maze.json");
    }
}
