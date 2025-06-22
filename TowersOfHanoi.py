import scene
import ui
import random
from typing import List, Tuple
import time

# Type alias for moves
Move = Tuple[int, int, int]

# Scene for animating Tower of Hanoi
class HanoiScene(scene.Scene):
    def __init__(self, n: int, rods: List[List[int]], moves: List[Move], on_complete):
        super().__init__()
        self.n = n
        self.rods = [rod[:] for rod in rods]
        self.moves = moves
        self.current_move_index = -1
        self.disk_nodes = {}
        self.base_node = None
        self.rod_nodes = [None]*len(rods)
        self.rod_positions = [1/len(rods)*(i+0.5) for i in range(len(rods))]
        self.on_complete = on_complete
        # Define distinct RGB/CMY colors, yellow first
        self.disk_colors = [
            (1, 1, 0),      # Yellow
            (1, 0, 0),      # Red
            (0, 0.6, 0.1),      # Green
            (0, 0, 1),      # Blue
            (1, 0.5, 0),    # Orange
            (0.5, 1, 0.25),    # lime
            (1, 0, 1),      # Magenta
            (0, 1, 1),      # Cyan
            (0, 0, 0),      # Black
            (1, 1, 1),      # White
        ]

    def setup(self):
        scene_width = self.size.w or 600
        # Background
        self.background_color = '#f0f0f0'
        # Create disk nodes (only if n > 0)
        if self.n > 0:
            for disk in range(1, self.n + 1):
                width = 50 + disk * 20
                path = ui.Path.rect(-width / 2, 0, width, 20)
                color = self.disk_colors[(disk - 1) % len(self.disk_colors)]
                disk_node = scene.ShapeNode(
                    path,
                    fill_color=color,
                    stroke_color='black'
                )
                disk_node.z_position = 1
                disk_node.anchor_point = (0.5, 0)  # Bottom-center
                self.add_child(disk_node)
                self.disk_nodes[disk] = disk_node
            self.update_disk_positions()
        base_path = ui.Path.rect(0, 0, scene_width, 10)
        self.base_node = scene.ShapeNode(
            base_path,
            fill_color='#8B4513',  # Brown
            stroke_color='black'
        )
        self.base_node.position = (0, 50)  # Top at y=50
        self.base_node.anchor_point = (0, 1)  # Top-left
        self.base_node.z_position = -1
        self.add_child(self.base_node)
        print(f"Base drawn: position=(0, 50), anchor=(0, 1), width={scene_width}, height=10")
        # Draw rods
        self.rod_nodes=[None]*len(self.rods)
        path = ui.Path.rect(-5, 0, 10, 205)
        for i,rod_position in enumerate(self.rod_positions):
            rod_node = scene.ShapeNode(
                path,
                fill_color='#333333',
                stroke_color='black'
            )
            rod_node.position = (rod_position*scene_width, 50)  # Bottom at y=50
            rod_node.anchor_point = (0.5, 0)  # Bottom-center
            rod_node.z_position = 0
            self.add_child(rod_node)
            self.rod_nodes[i]=rod_node
            print(f"Rod {i+1} drawn: {rod_node.position=}, anchor=(0.5, 0), width=10, height=200")
        self.update_rod_positions()
        
        print(f"Setup: scene width={self.size.w}, height={self.size.h}, rods={self.rods}")
        self.needs_display = True

    def update_rod_positions(self):
        # Calculate rod positions
        scene_width = self.size.w or 600
        # Draw base platform
        self.base_node.path = ui.Path.rect(0, 0, scene_width, 10)
        for rod_node,rod_position in zip(self.rod_nodes,self.rod_positions):
          rod_node.position = (rod_position*scene_width, 50)  # Bottom at y=50
        print(f"Rods drawn at {self.rod_positions}")
        self.needs_display = True

    def did_change_size(self):
        if not self.base_node: return #return if not yet initialized
        self.update_rod_positions()
        self.update_disk_positions()
        print(f"Size changed: width={self.size.w}, height={self.size.h}")
        self.needs_display = True

    def update_disk_positions(self):
        scene_width = self.size.w or 600
        for rod_position, rod in zip(self.rod_positions,self.rods):
            for i, disk in enumerate(rod):  # Largest disk first
                y = 50 + 20 * i
                x = rod_position*scene_width
                x = min(max(x, 0), self.size.w or 600)
                y = min(max(y, 50), (self.size.h or 300) - 20)
                #if disk in self.disk_nodes:
                self.disk_nodes[disk].position = (x, y)
        self.needs_display = True

    def did_start(self):
        if self.moves:
            delay_action = scene.Action.wait(1.0)
            animate_action = scene.Action.call(self.animate_next_move)
            self.run_action(scene.Action.sequence([delay_action, animate_action]))
            print(f"did_start: Starting animation with {len(self.moves)} moves after 1s delay")
        else:
            self.run_action(scene.Action.call(self.on_complete))
            print("did_start: No moves to animate")
        self.needs_display = True

    def animate_next_move(self):
        scene_width = self.size.w or 600
        if self.current_move_index + 1 >= len(self.moves):
            print("Animation complete, calling on_complete")
            self.run_action(scene.Action.call(self.on_complete))
            return
        self.current_move_index += 1
        disk, from_rod, to_rod = self.moves[self.current_move_index]
        if disk in self.rods[from_rod]:
            self.rods[from_rod].remove(disk)
            self.rods[to_rod].append(disk)
        rod_counts = [len(rod) for rod in self.rods]
        target_y = 50 + 20 * (rod_counts[to_rod] - 1)
        target_x = self.rod_positions[to_rod]*scene_width
        target_x = min(max(target_x, 0), self.size.w or 600)
        target_y = min(max(target_y, 50), (self.size.h or 300) - 20)
        # Three-step animation: lift, move, descend
        source_x = self.rod_positions[from_rod]*scene_width
        source_x = min(max(source_x, 0), self.size.w or 600)
        lift_y = 260  # Above rods
        lift_action = scene.Action.move_to(source_x, lift_y, 0.5, 2)  # 0.5s up
        move_action = scene.Action.move_to(target_x, lift_y, 0.5, 2)  # 0.5s across
        descend_action = scene.Action.move_to(target_x, target_y, 0.5, 2)  # 0.5s down
        def adjust_disk_position():
            target_x=self.rod_positions[to_rod]*self.size.w #re-calculate position in case of resize
            self.disk_nodes[disk].position=(target_x,target_y)
        adjust_action = scene.Action.call(adjust_disk_position)
        wait_action = scene.Action.wait(0.3)  # Pause before next move
        next_action = scene.Action.call(self.animate_next_move)
        print(f"Animating move {disk} from rod {from_rod} to {to_rod}: lift to ({source_x}, {lift_y}), move to ({target_x}, {lift_y}), descend to ({target_x}, {target_y})")
        self.disk_nodes[disk].run_action(
            scene.Action.sequence([lift_action, move_action, descend_action, adjust_action, wait_action, next_action])
        )
        self.needs_display = True

# Main UI view
class HanoiView(ui.View):
    def __init__(self):
        super().__init__()
        self.name = 'Tower of Hanoi Solver'
        self.background_color = 'white'
        self.n = 0
        self.rods = [[], [], []]
        self.moves = []
        self.scene_view = None
        self.output_view = None
        self.n_input = None
        self.classic_button = None
        self.random_button = None
        self.setup_ui()
    
    def setup_ui(self):
        self.scene_view = scene.SceneView(frame=(0, 50, self.bounds.w or 600, 300))
        self.scene_view.flex = 'WH'
        self.scene_view.scene = HanoiScene(0, [[], [], []], [], self.animation_complete)
#        self.scene_view.scene.setup()
        self.scene_view.scene.did_change_size()  # Force initial rod draw
        self.add_subview(self.scene_view)
        self.n_input = ui.TextField(frame=(150, 10, 100, 32))
        self.n_input.placeholder = 'Enter n (1-10)'
        try:
            self.n_input.keyboard_type = ui.UIKeyboardTypeNumberPad
        except AttributeError:
            pass
        self.n_input.text = '10'
        self.add_subview(self.n_input)
        n_label = ui.Label(frame=(10, 10, 130, 32))
        n_label.text = 'Number of disks:'
        self.add_subview(n_label)
        self.classic_button = ui.Button(frame=(10, 360, 100, 32))
        self.classic_button.title = 'Classic'
        self.classic_button.background_color = 'blue'
        self.classic_button.tint_color = 'white'
        self.classic_button.action = self.start_classic
        self.add_subview(self.classic_button)
        self.random_button = ui.Button(frame=(120, 360, 100, 32))
        self.random_button.title = 'Random'
        self.random_button.background_color = 'green'
        self.random_button.tint_color = 'white'
        self.random_button.action = self.start_random
        self.add_subview(self.random_button)
        self.output_view = ui.TextView(frame=(10, 400, 600, 300))
        self.output_view.flex = 'WH'
        self.output_view.font = ('Menlo', 12)
        self.output_view.editable = False
        self.add_subview(self.output_view)
    
    def layout(self):
        self.scene_view.frame = (0, 50, self.bounds.w, 300)
        self.output_view.frame = (10, 400, self.bounds.w - 20, self.bounds.h - 410)
        if self.scene_view.scene:
            self.scene_view.scene.did_change_size()
            self.scene_view.scene.needs_display = True
    
    def start_classic(self, sender):
        self.start_solver(is_random=False)
    
    def start_random(self, sender):
        self.start_solver(is_random=True)
    
    def start_solver(self, is_random: bool):
        try:
            n = int(self.n_input.text)
            if not (1 <= n <= 10):
                raise ValueError
        except ValueError:
            self.output_view.text = "Please enter a valid number of disks (1-10)."
            return
        self.n = n
        start_time = time.time()
        self.rods = generate_random_start(n) if is_random else generate_classic_start(n)
        initial_rods = [rod[:] for rod in self.rods]
        self.moves = list(solve_tower_recursive(self.rods, n, goal_rod=2))
        end_time = time.time()
        output = "Random start configuration:\n" if is_random else "Classic configuration (all disks on A):\n"
        output += print_solution(initial_rods, self.moves, n)
        output += f"\nExecution time: {end_time - start_time:.3f} seconds\n"
        self.output_view.text = output
        self.classic_button.enabled = False
        self.random_button.enabled = False
        self.scene_view.scene = HanoiScene(n, initial_rods, self.moves, self.animation_complete)
        self.scene_view.scene.setup()
        self.scene_view.scene.did_change_size()
        self.scene_view.scene.did_start()
        self.scene_view.scene.needs_display = True
        print(f"Start solver: {len(self.moves)} moves generated")

    def animation_complete(self):
        self.classic_button.enabled = True
        self.random_button.enabled = True
        print("animation_complete called")

# Solver functions
def generate_random_start(n: int) -> List[List[int]]:
    rods = [[], [], []]
    rods[0].append(n)
    for disk in range(1, n):
        rod = random.randint(0, 2)
        rods[rod].append(disk)
    for rod in rods:
        rod.sort(reverse=True)
    return rods

def generate_classic_start(n: int) -> List[List[int]]:
    rods = [[], [], []]
    rods[0] = list(range(n, 0, -1))
    return rods

def solve_tower_recursive(rods: List[List[int]], n: int, goal_rod: int):
    if n == 0:
        return
    largest_disk = n
    source_rod = -1
    for rod_idx, rod in enumerate(rods):
        if largest_disk in rod:
            source_rod = rod_idx
            break
    if source_rod == goal_rod:
        yield from solve_tower_recursive(rods, n-1, goal_rod)
        return
    #auxiliary_rod = (set([0, 1, 2]) - {source_rod, goal_rod}).pop()
    #auxiliary_rod= (7 & ~((1<<source_rod)|(1<<goal_rod))).bit_length()-1
    auxiliary_rod=3-source_rod-goal_rod
    yield from solve_tower_recursive(rods, n-1, auxiliary_rod)
    rods[source_rod].pop()
    rods[goal_rod].append(largest_disk)
    yield (largest_disk, source_rod, goal_rod)
    #yield from solve_tower_recursive(rods, n-1, goal_rod)
    yield from solve_classic_recursive(n-1, auxiliary_rod, source_rod, goal_rod)
  
def solve_classic_recursive(n: int, source: int, auxiliary: int, goal: int):
    if n == 0:
        return
    yield from solve_classic_recursive(n-1, source, goal, auxiliary)
    yield (n, source, goal)
    yield from solve_classic_recursive(n-1, auxiliary, source, goal)

def print_solution(rods: List[List[int]], moves: List[Tuple[int, int, int]], n: int):
    rod_names = {0: 'A', 1: 'B', 2: 'C'}
    result = f"Starting configuration (disk 1=smallest, {n}=largest):\n"
    for i, rod in enumerate(rods):
        result += f"Rod {rod_names[i]}: {rod if rod else 'empty'}\n"
    result += "\nMove sequence:\n"
    for i, (disk, from_rod, to_rod) in enumerate(moves, 1):
        result += f"Move {i}: Disk {disk} from rod {rod_names[from_rod]} to rod {rod_names[to_rod]}\n"
    result += f"Total moves: {len(moves)}\n"
    return result

# Run the app
view = HanoiView()
view.present(style='full_screen',orientations=['landscape'])


