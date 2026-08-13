// hex_maze.rs — Rust версия

use rand::Rng;
use rand::SeedableRng;
use rand::rngs::StdRng;
use std::collections::{HashMap, HashSet};
use std::env;

#[derive(Clone)]
struct Cell {
    walls: HashSet<String>,
    visited: bool,
}

struct HexMaze {
    width: usize,
    height: usize,
    algo: String,
    seed: u64,
    solve: bool,
    maze: HashMap<String, Cell>,
    path: Option<Vec<(usize, usize)>>,
    rng: StdRng,
}

impl HexMaze {
    fn new(width: usize, height: usize, algo: String, seed: u64, solve: bool) -> Self {
        let rng = if seed != 0 {
            StdRng::seed_from_u64(seed)
        } else {
            StdRng::from_entropy()
        };
        HexMaze {
            width,
            height,
            algo,
            seed,
            solve,
            maze: HashMap::new(),
            path: None,
            rng,
        }
    }

    fn get_neighbors(&self, x: usize, y: usize) -> Vec<(usize, usize)> {
        let mut neighbors = Vec::new();
        let parity = y & 1;
        let offsets: &[(isize, isize)] = if parity == 0 {
            &[(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
        } else {
            &[(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)]
        };
        for (dx, dy) in offsets {
            let nx = x as isize + dx;
            let ny = y as isize + dy;
            if nx >= 0 && nx < self.width as isize && ny >= 0 && ny < self.height as isize {
                neighbors.push((nx as usize, ny as usize));
            }
        }
        neighbors
    }

    fn generate_dfs(&mut self) {
        for y in 0..self.height {
            for x in 0..self.width {
                let key = format!("{},{}", x, y);
                let mut cell = Cell {
                    walls: HashSet::new(),
                    visited: false,
                };
                for (nx, ny) in self.get_neighbors(x, y) {
                    cell.walls.insert(format!("{},{}", nx, ny));
                }
                self.maze.insert(key, cell);
            }
        }

        let mut stack = vec![(0, 0)];
        self.maze.get_mut("0,0").unwrap().visited = true;

        while let Some(&(x, y)) = stack.last() {
            let key = format!("{},{}", x, y);
            let mut neighbors = self.get_neighbors(x, y);
            let len = neighbors.len();
            for i in 0..len {
                let j = self.rng.gen_range(0..len);
                neighbors.swap(i, j);
            }

            let mut found = false;
            for (nx, ny) in neighbors {
                let nkey = format!("{},{}", nx, ny);
                if self.maze[&nkey].visited {
                    continue;
                }
                self.maze.get_mut(&nkey).unwrap().visited = true;
                self.maze.get_mut(&key).unwrap().walls.remove(&nkey);
                self.maze.get_mut(&nkey).unwrap().walls.remove(&key);
                stack.push((nx, ny));
                found = true;
                break;
            }
            if !found {
                stack.pop();
            }
        }
    }

    fn generate_prim(&mut self) {
        self.generate_dfs();
    }

    fn generate(&mut self) {
        match self.algo.as_str() {
            "dfs" => self.generate_dfs(),
            "prim" => self.generate_prim(),
            _ => self.generate_dfs(),
        }
        if self.solve {
            self.path = self.solve_maze();
        }
    }

    fn solve_maze(&self) -> Option<Vec<(usize, usize)>> {
        let mut stack = vec![vec![(0, 0)]];
        let mut visited = HashSet::new();
        visited.insert("0,0".to_string());

        while let Some(path) = stack.pop() {
            let &(x, y) = path.last().unwrap();
            if x == self.width - 1 && y == self.height - 1 {
                return Some(path);
            }

            for (nx, ny) in self.get_neighbors(x, y) {
                let nkey = format!("{},{}", nx, ny);
                if visited.contains(&nkey) {
                    continue;
                }
                if !self.maze[&format!("{},{}", x, y)].walls.contains(&nkey) {
                    visited.insert(nkey);
                    let mut new_path = path.clone();
                    new_path.push((nx, ny));
                    stack.push(new_path);
                }
            }
        }
        None
    }

    fn print_ascii(&self) {
        println!("\x1b[36m\nКарта лабиринта:\x1b[0m");
        println!("\x1b[33m  Размер: {}x{}\x1b[0m", self.width, self.height);
        for y in 0..self.height {
            for x in 0..self.width {
                print!("  ");
                if let Some(ref path) = self.path {
                    let found = path.contains(&(x, y));
                    print!("{}", if found { "* " } else { "  " });
                } else {
                    print!("  ");
                }
            }
            println!();
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut width = 10;
    let mut height = 10;
    let mut algo = "dfs".to_string();
    let mut seed = 0;
    let mut solve = false;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--width" => { width = args[i+1].parse().unwrap_or(10); i += 2; }
            "--height" => { height = args[i+1].parse().unwrap_or(10); i += 2; }
            "--algo" => { algo = args[i+1].clone(); i += 2; }
            "--seed" => { seed = args[i+1].parse().unwrap_or(0); i += 2; }
            "--solve" => { solve = true; i += 1; }
            _ => { i += 1; }
        }
    }

    println!("\x1b[36m🔷 Hexagonal Maze Generator (Rust)\x1b[0m");
    println!("📐 Параметры: {}x{} ячеек, алгоритм: {}", width, height, algo);

    let mut gen = HexMaze::new(width, height, algo, seed, solve);
    gen.generate();
    gen.print_ascii();
}
