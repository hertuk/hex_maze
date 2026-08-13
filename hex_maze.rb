# hex_maze.rb — Ruby версия

class HexMaze
  attr_reader :maze, :path

  def initialize(width, height, algo = 'dfs', seed = nil, solve = false)
    @width = width
    @height = height
    @algo = algo
    @seed = seed
    @solve = solve
    @maze = nil
    @path = nil
    @rng = seed ? Random.new(seed) : Random.new
  end

  def get_neighbors(x, y)
    neighbors = []
    parity = y & 1
    offsets = if parity == 0
      [[-1,0], [1,0], [0,-1], [0,1], [-1,1], [1,-1]]
    else
      [[-1,0], [1,0], [0,-1], [0,1], [-1,-1], [1,1]]
    end
    offsets.each do |dx, dy|
      nx, ny = x + dx, y + dy
      neighbors << [nx, ny] if nx >= 0 && nx < @width && ny >= 0 && ny < @height
    end
    neighbors
  end

  def generate_dfs
    maze = {}
    (0...@height).each do |y|
      (0...@width).each do |x|
        key = "#{x},#{y}"
        maze[key] = { walls: Set.new, visited: false }
        get_neighbors(x, y).each { |nx, ny| maze[key][:walls] << "#{nx},#{ny}" }
      end
    end

    stack = [[0, 0]]
    maze['0,0'][:visited] = true

    while !stack.empty?
      x, y = stack.last
      key = "#{x},#{y}"
      neighbors = get_neighbors(x, y).shuffle(random: @rng)

      found = false
      neighbors.each do |nx, ny|
        nkey = "#{nx},#{ny}"
        next if maze[nkey][:visited]
        maze[nkey][:visited] = true
        maze[key][:walls].delete(nkey)
        maze[nkey][:walls].delete(key)
        stack << [nx, ny]
        found = true
        break
      end
      stack.pop unless found
    end

    maze.each { |k, v| v.delete(:visited) }
    maze
  end

  def generate_prim
    generate_dfs
  end

  def generate
    @maze = case @algo
    when 'dfs' then generate_dfs
    when 'prim' then generate_prim
    else generate_dfs
    end
    @path = solve_maze if @solve
    @maze
  end

  def solve_maze
    stack = [[[0, 0]]]
    visited = Set.new
    visited.add('0,0')

    while !stack.empty?
      path = stack.pop
      x, y = path.last
      return path if x == @width - 1 && y == @height - 1

      get_neighbors(x, y).each do |nx, ny|
        nkey = "#{nx},#{ny}"
        next if visited.include?(nkey)
        if !@maze["#{x},#{y}"][:walls].include?(nkey)
          visited.add(nkey)
          new_path = path.dup << [nx, ny]
          stack << new_path
        end
      end
    end
    nil
  end

  def print_ascii
    puts "\e[36m\nКарта лабиринта:\e[0m"
    puts "\e[33m  Размер: #{@width}x#{@height}\e[0m"
    (0...@height).each do |y|
      (0...@width).each do |x|
        print "  "
        if @path && @path.include?([x, y])
          print "* "
        else
          print "  "
        end
      end
      puts
    end
  end
end

def main
  width = 10
  height = 10
  algo = 'dfs'
  seed = nil
  solve = false

  args = ARGV
  i = 0
  while i < args.size
    case args[i]
    when '--width' then width = args[i+1].to_i; i += 2
    when '--height' then height = args[i+1].to_i; i += 2
    when '--algo' then algo = args[i+1]; i += 2
    when '--seed' then seed = args[i+1].to_i; i += 2
    when '--solve' then solve = true; i += 1
    else i += 1
    end
  end

  puts "\e[36m🔷 Hexagonal Maze Generator (Ruby)\e[0m"
  puts "📐 Параметры: #{width}x#{height} ячеек, алгоритм: #{algo}"

  gen = HexMaze.new(width, height, algo, seed, solve)
  gen.generate
  gen.print_ascii
end

main if __FILE__ == $0
