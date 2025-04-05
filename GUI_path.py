import tkinter as tk
import time
import threading


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stingray Maze - Lab 5")

        # Maze dimensions
        self.rows = 6   # 6 rows
        self.cols = 12   # 12 columns
        self.tile_size = 50

        # Create the Canvas
        width = self.cols * self.tile_size
        height = self.rows * self.tile_size
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg="white")
        self.canvas.pack()

        # Approximate grey blocks from the figure:
        # (row, col) for each grey tile
        GREY_CELLS = [
            # All grey blocks
            (1,10),(2,10),(3,10),
            (3,9),
            (0,8),(1,8),(3,8),
            (0,7),(1,7),(3,7),
            (0,6),(1,6),(3,6),
            (1,5),(0,5),
            (3,4),(4,4),
            (1,3),
            (1,2),(2,2),
            (4,1),
               
        ]

        # Draw the 6×12 grid
        self.draw_grid()

        # Shade the cells for obstacles/walls
        for (r,c) in GREY_CELLS:
            self.shade_cell(r, c, color="#c0c0c0")

        # Label S (start) at top-right: row=0, col=11
        sx = (11.5 * self.tile_size)
        sy = (5.5  * self.tile_size)
        self.canvas.create_text(sx, sy, text="S", font=("Arial",16,"bold"), fill="black")

        # Label F (finish) at bottom-left: row=5, col=0
        fx = (0.5 * self.tile_size)
        fy = (0.5 * self.tile_size)
        self.canvas.create_text(fx, fy, text="F", font=("Arial",16,"bold"), fill="black")

        # Robot default position/heading
        self.robot_row = 5
        self.robot_col = 11
        self.robot_heading = 0
        self.robot_marker = None
        self.draw_robot(self.robot_row, self.robot_col, self.robot_heading)

    def draw_grid(self):
        """Draw horizontal and vertical lines for a 6×12 grid."""
        for r in range(self.rows + 1):
            y = r * self.tile_size
            self.canvas.create_line(0, y, self.cols*self.tile_size, y)
        for c in range(self.cols + 1):
            x = c * self.tile_size
            self.canvas.create_line(x, 0, x, self.rows*self.tile_size)

    def shade_cell(self, row, col, color="#c0c0c0"):
        """Shade a specific cell at (row, col)."""
        x1 = col * self.tile_size
        y1 = row * self.tile_size
        x2 = x1 + self.tile_size
        y2 = y1 + self.tile_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def draw_robot(self, row, col, heading):
        """
        Draws or updates the robot marker at (row, col).
        heading in degrees (0 = up).
        Adjust to show direction if you like.
        """
        # Convert row,col -> pixel coords
        px = (col + 0.5) * self.tile_size
        py = (row + 0.5) * self.tile_size

        # If there's already a marker, remove it
        if self.robot_marker is not None:
            self.canvas.delete(self.robot_marker)

        # Draw a simple triangle to indicate heading
        # heading=0 => facing upward => rotate triangle accordingly
        size = 10
        # Basic triangle points for heading=0
        points = [
            (px, py - size),      # tip
            (px - size, py + size),
            (px + size, py + size)
        ]
        # If you want to rotate the points according to heading, do so. (Optional)

        self.robot_marker = self.canvas.create_polygon(
            points, fill="blue"
        )

    def update_robot_position(self, new_row, new_col, new_heading):
        """Call whenever the robot moves or rotates to update the GUI."""
        self.robot_row = new_row
        self.robot_col = new_col
        self.robot_heading = new_heading
        self.draw_robot(self.robot_row, self.robot_col, self.robot_heading)
        

# Run the GUI simulation
# Shared GUI instance to update from logic thread
gui_app = None

def run_gui():
    global gui_app
    root = tk.Tk()
    gui_app = GUI(root)
    root.mainloop()

def simulate_maze_movement():
    """
    Simulate the Stingray bot moving along a path.
    Replace this with your real movement logic.
    """
    path = [
        (5, 11), (4, 11), (3, 11), (2, 11), (1, 11),
        (0, 11), (0, 10), (0, 9), (1, 9), (2, 9),
        (2, 8), (2,7), (2,6), (2,5),(3,5),(4,5),
        (4,5),(4,6),(4,7),(4,8),(4,9),(4,10),
        (5,10),(5,9),(5,8),(5,7),(5,6),(5,5),(5,4),(5,3),
        (4,3),(3,3),(2,3),
        (2,4),(1,4),(0,4),
        (0,3),(0,2),(0,1),
        (1,1),(2,1),(3,1),
        (3,2),(4,2),(5,2),
        (5,1),(5,0),
        (4,0),(3,0),(2,0),(1,0),(0,0),

    ]

    heading = 0  # Can rotate this if you want arrow direction
    for (row, col) in path:
        if gui_app:
            gui_app.update_robot_position(row, col, heading)
        time.sleep(0.3)  # Simulate movement delay

def main():
    # Start GUI in its own thread
    gui_thread = threading.Thread(target=run_gui, daemon=True)
    gui_thread.start()

    # Wait a moment to make sure GUI is initialized
    time.sleep(1)

    # Start maze navigation simulation
    simulate_maze_movement()

    # Optional: Wait for GUI thread to finish (usually runs forever)
    gui_thread.join()
    
    
    
    
    


if __name__ == "__main__":
    main()
