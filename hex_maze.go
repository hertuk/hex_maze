// hex_maze.go — Go версия

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math/rand"
	"time"
)

type Cell struct {
	Walls   map[string]bool `json:"walls"`
	Visited bool            `json:"-"`
}

type HexMaze struct {
	Width  int
	Height int
	Algo   string
	Seed   int64
	Solve  bool
	Maze   map[string]*Cell
	Path   [][2]int
	rand   *rand.Rand
}

func NewHexMaze(width, height int, algo string, seed int64, solve bool) *HexMaze {
	var rng *rand.Rand
	if seed != 0 {
		rng = rand.New(rand.NewSource(seed))
	} else {
		rng = rand.New(rand.NewSource(time.Now().UnixNano()))
	}
	return &HexMaze{
		Width:  width,
		Height: height,
		Algo:   algo,
		Seed:   seed,
		Solve:  solve,
		rand:   rng,
		Maze:   make(map[string]*Cell),
	}
}

func (m *HexMaze) getNeighbors(x, y int) [][2]int {
	neighbors := [][2]int{}
	parity := y & 1
	var offsets [][2]int
	if parity == 0 {
		offsets = [][2]int{{-1, 0}, {1, 0}, {0, -1}, {0, 1}, {-1, 1}, {1, -1}}
	} else {
		offsets = [][2]int{{-1, 0}, {1, 0}, {0, -1}, {0, 1}, {-1, -1}, {1, 1}}
	}
	for _, offset := range offsets {
		nx, ny := x+offset[0], y+offset[1]
		if nx >= 0 && nx < m.Width && ny >= 0 && ny < m.Height {
			neighbors = append(neighbors, [2]int{nx, ny})
		}
	}
	return neighbors
}

func (m *HexMaze) generateDFS() {
	for y := 0; y < m.Height; y++ {
		for x := 0; x < m.Width; x++ {
			key := fmt.Sprintf("%d,%d", x, y)
			m.Maze[key] = &Cell{
				Walls:   make(map[string]bool),
				Visited: false,
			}
			for _, n := range m.getNeighbors(x, y) {
				nkey := fmt.Sprintf("%d,%d", n[0], n[1])
				m.Maze[key].Walls[nkey] = true
			}
		}
	}

	stack := [][2]int{{0, 0}}
	m.Maze["0,0"].Visited = true

	for len(stack) > 0 {
		x, y := stack[len(stack)-1][0], stack[len(stack)-1][1]
		key := fmt.Sprintf("%d,%d", x, y)
		neighbors := m.getNeighbors(x, y)
		m.rand.Shuffle(len(neighbors), func(i, j int) {
			neighbors[i], neighbors[j] = neighbors[j], neighbors[i]
		})

		found := false
		for _, n := range neighbors {
			nkey := fmt.Sprintf("%d,%d", n[0], n[1])
			if m.Maze[nkey].Visited {
				continue
			}
			m.Maze[nkey].Visited = true
			delete(m.Maze[key].Walls, nkey)
			delete(m.Maze[nkey].Walls, key)
			stack = append(stack, n)
			found = true
			break
		}
		if !found {
			stack = stack[:len(stack)-1]
		}
	}
}

func (m *HexMaze) generatePrim() {
	for y := 0; y < m.Height; y++ {
		for x := 0; x < m.Width; x++ {
			key := fmt.Sprintf("%d,%d", x, y)
			m.Maze[key] = &Cell{
				Walls:   make(map[string]bool),
				Visited: false,
			}
			for _, n := range m.getNeighbors(x, y) {
				nkey := fmt.Sprintf("%d,%d", n[0], n[1])
				m.Maze[key].Walls[nkey] = true
			}
		}
	}

	m.Maze["0,0"].Visited = true
	wallList := [][2][2]int{}
	for _, n := range m.getNeighbors(0, 0) {
		wallList = append(wallList, [2][2]int{{0, 0}, {n[0], n[1]}})
	}

	for len(wallList) > 0 {
		idx := m.rand.Intn(len(wallList))
		wall := wallList[idx]
		wallList = append(wallList[:idx], wallList[idx+1:]...)
		cell, neighbor := wall[0], wall[1]
		cellKey := fmt.Sprintf("%d,%d", cell[0], cell[1])
		neighborKey := fmt.Sprintf("%d,%d", neighbor[0], neighbor[1])
		if m.Maze[neighborKey].Visited {
			continue
		}
		m.Maze[neighborKey].Visited = true
		delete(m.Maze[cellKey].Walls, neighborKey)
		delete(m.Maze[neighborKey].Walls, cellKey)
		for _, n := range m.getNeighbors(neighbor[0], neighbor[1]) {
			nkey := fmt.Sprintf("%d,%d", n[0], n[1])
			if !m.Maze[nkey].Visited {
				wallList = append(wallList, [2][2]int{{neighbor[0], neighbor[1]}, {n[0], n[1]}})
			}
		}
	}
}

func (m *HexMaze) generate() {
	switch m.Algo {
	case "dfs":
		m.generateDFS()
	case "prim":
		m.generatePrim()
	default:
		m.generateDFS()
	}
	if m.Solve {
		m.Path = m.solveMaze()
	}
}

func (m *HexMaze) solveMaze() [][2]int {
	stack := [][][2]int{{{0, 0}}}
	visited := map[[2]int]bool{{0, 0}: true}

	for len(stack) > 0 {
		path := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		x, y := path[len(path)-1][0], path[len(path)-1][1]

		if x == m.Width-1 && y == m.Height-1 {
			return path
		}

		for _, n := range m.getNeighbors(x, y) {
			nx, ny := n[0], n[1]
			if visited[[2]int{nx, ny}] {
				continue
			}
			nkey := fmt.Sprintf("%d,%d", nx, ny)
			if _, ok := m.Maze[fmt.Sprintf("%d,%d", x, y)].Walls[nkey]; !ok {
				visited[[2]int{nx, ny}] = true
				newPath := make([][2]int, len(path))
				copy(newPath, path)
				newPath = append(newPath, [2]int{nx, ny})
				stack = append(stack, newPath)
			}
		}
	}
	return nil
}

func (m *HexMaze) printASCII() {
	fmt.Println("\x1b[36m\nКарта лабиринта:\x1b[0m")
	fmt.Printf("\x1b[33m  Размер: %dx%d\x1b[0m\n", m.Width, m.Height)
	for y := 0; y < m.Height; y++ {
		line := ""
		for x := 0; x < m.Width; x++ {
			key := fmt.Sprintf("%d,%d", x, y)
			line += "  "
			if m.Path != nil {
				found := false
				for _, p := range m.Path {
					if p[0] == x && p[1] == y {
						found = true
						break
					}
				}
				if found {
					line += "* "
				} else {
					line += "  "
				}
			} else {
				line += "  "
			}
		}
		fmt.Println(line)
	}
}

func (m *HexMaze) saveJSON(filename string) {
	data := map[string]interface{}{
		"type":   "hexagonal",
		"width":  m.Width,
		"height": m.Height,
		"algo":   m.Algo,
		"seed":   m.Seed,
		"maze":   m.Maze,
		"path":   m.Path,
	}
	jsonData, _ := json.MarshalIndent(data, "", "  ")
	// ...
	fmt.Printf("\x1b[32m💾 Сохранено JSON: %s\x1b[0m\n", filename)
}

func main() {
	width := flag.Int("width", 10, "Ширина лабиринта")
	height := flag.Int("height", 10, "Высота лабиринта")
	algo := flag.String("algo", "dfs", "Алгоритм (dfs, prim)")
	seed := flag.Int64("seed", 0, "Seed для воспроизводимости")
	solve := flag.Bool("solve", false, "Найти и показать путь")
	flag.Parse()

	fmt.Println("\x1b[36m🔷 Hexagonal Maze Generator (Go)\x1b[0m")
	fmt.Printf("📐 Параметры: %dx%d ячеек, алгоритм: %s\n", *width, *height, *algo)

	gen := NewHexMaze(*width, *height, *algo, *seed, *solve)
	gen.generate()
	gen.printASCII()
	gen.saveJSON("maze.json")
}
