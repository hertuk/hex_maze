<?php
// hex_maze.php — PHP версия

class HexMaze {
    private $width, $height, $algo, $seed, $solve;
    private $maze, $path;

    public function __construct($width, $height, $algo = 'dfs', $seed = null, $solve = false) {
        $this->width = $width;
        $this->height = $height;
        $this->algo = $algo;
        $this->seed = $seed;
        $this->solve = $solve;
        $this->maze = null;
        $this->path = null;
        if ($seed !== null) mt_srand($seed);
    }

    private function getNeighbors($x, $y) {
        $neighbors = [];
        $parity = $y & 1;
        $offsets = $parity == 0 ?
            [[-1,0], [1,0], [0,-1], [0,1], [-1,1], [1,-1]] :
            [[-1,0], [1,0], [0,-1], [0,1], [-1,-1], [1,1]];
        foreach ($offsets as $off) {
            $nx = $x + $off[0];
            $ny = $y + $off[1];
            if ($nx >= 0 && $nx < $this->width && $ny >= 0 && $ny < $this->height) {
                $neighbors[] = [$nx, $ny];
            }
        }
        return $neighbors;
    }

    private function generateDFS() {
        $maze = [];
        for ($y = 0; $y < $this->height; $y++) {
            for ($x = 0; $x < $this->width; $x++) {
                $key = "$x,$y";
                $maze[$key] = ['walls' => [], 'visited' => false];
                foreach ($this->getNeighbors($x, $y) as $n) {
                    $maze[$key]['walls'][] = $n[0] . ',' . $n[1];
                }
                $maze[$key]['walls'] = array_unique($maze[$key]['walls']);
            }
        }

        $stack = [[0, 0]];
        $maze['0,0']['visited'] = true;

        while (!empty($stack)) {
            $pos = end($stack);
            $x = $pos[0]; $y = $pos[1];
            $key = "$x,$y";
            $neighbors = $this->getNeighbors($x, $y);
            shuffle($neighbors);

            $found = false;
            foreach ($neighbors as $n) {
                $nkey = $n[0] . ',' . $n[1];
                if ($maze[$nkey]['visited']) continue;
                $maze[$nkey]['visited'] = true;
                $maze[$key]['walls'] = array_diff($maze[$key]['walls'], [$nkey]);
                $maze[$nkey]['walls'] = array_diff($maze[$nkey]['walls'], [$key]);
                $stack[] = [$n[0], $n[1]];
                $found = true;
                break;
            }
            if (!$found) array_pop($stack);
        }

        foreach ($maze as &$cell) unset($cell['visited']);
        return $maze;
    }

    private function generatePrim() {
        return $this->generateDFS();
    }

    public function generate() {
        $this->maze = $this->algo == 'dfs' ? $this->generateDFS() : $this->generatePrim();
        if ($this->solve) $this->path = $this->solveMaze();
        return $this->maze;
    }

    private function solveMaze() {
        $stack = [[[0, 0]]];
        $visited = ['0,0' => true];

        while (!empty($stack)) {
            $path = array_pop($stack);
            $last = end($path);
            $x = $last[0]; $y = $last[1];
            if ($x == $this->width - 1 && $y == $this->height - 1) return $path;

            foreach ($this->getNeighbors($x, $y) as $n) {
                $nkey = $n[0] . ',' . $n[1];
                if (isset($visited[$nkey])) continue;
                if (!in_array($nkey, $this->maze["$x,$y"]['walls'])) {
                    $visited[$nkey] = true;
                    $newPath = $path;
                    $newPath[] = [$n[0], $n[1]];
                    $stack[] = $newPath;
                }
            }
        }
        return null;
    }

    public function printASCII() {
        echo "\033[36m\nКарта лабиринта:\033[0m\n";
        echo "\033[33m  Размер: {$this->width}x{$this->height}\033[0m\n";
        for ($y = 0; $y < $this->height; $y++) {
            for ($x = 0; $x < $this->width; $x++) {
                echo "  ";
                if ($this->path) {
                    $found = false;
                    foreach ($this->path as $p) {
                        if ($p[0] == $x && $p[1] == $y) { $found = true; break; }
                    }
                    echo $found ? "* " : "  ";
                } else {
                    echo "  ";
                }
            }
            echo "\n";
        }
    }
}

function main($argv) {
    $width = 10;
    $height = 10;
    $algo = 'dfs';
    $seed = null;
    $solve = false;

    for ($i = 1; $i < count($argv); $i++) {
        if ($argv[$i] == '--width') { $width = (int)$argv[++$i]; }
        else if ($argv[$i] == '--height') { $height = (int)$argv[++$i]; }
        else if ($argv[$i] == '--algo') { $algo = $argv[++$i]; }
        else if ($argv[$i] == '--seed') { $seed = (int)$argv[++$i]; }
        else if ($argv[$i] == '--solve') { $solve = true; }
    }

    echo "\033[36m🔷 Hexagonal Maze Generator (PHP)\033[0m\n";
    echo "📐 Параметры: {$width}x{$height} ячеек, алгоритм: {$algo}\n";

    $gen = new HexMaze($width, $height, $algo, $seed, $solve);
    $gen->generate();
    $gen->printASCII();
}

$argc = $_SERVER['argc'] ?? 0;
$argv = $_SERVER['argv'] ?? [];
main($argv);
?>
