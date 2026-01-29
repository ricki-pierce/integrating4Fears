# This code creates an XY plane that mimics a grid placed in front of a subject on a table.
# Users can click anywhere on the grid to define points of interest.
# A reference point is set to represent the location of the subject’s eyes.
# Distances are then calculated from the eyes to each selected point on the board.
# Using these distances, the code computes the physical sizes of points that subtend
# 1°, 2°, and 3° of visual angle at each location.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from matplotlib.patches import Rectangle as Rect2D

class Shape3DPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Shape Plotter - Enhanced")
        self.root.geometry("1400x900")
        
        # Data storage
        self.points = []  # [{pos: (x,y,z), size: float, label: str, artist: obj, text_artist: obj}]
        self.rectangles = []  # [{corners: [...], plane: str, artist: obj, label: str}]
        self.lines = []  # [{start: (x,y,z), end: (x,y,z), artist: obj, label: str}]
        self.selected_object = None
        self.selected_index = None
        self.reference_point = None
        self.reference_artist = None
        
        # Drawing state
        self.drawing_mode = 'select'
        self.current_plane = 'xy'
        self.temp_points = []
        
        # Zoom level
        self.zoom_level = 1.0
        
        # Setup UI
        self.setup_ui()
        self.setup_plot()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        control_frame = ttk.Frame(main_frame, width=250)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        control_frame.pack_propagate(False)
        
        # Drawing Mode Section
        ttk.Label(control_frame, text="Drawing Mode", font=('Arial', 12, 'bold')).pack(pady=(5,5))
        
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, padx=5)
        
        ttk.Button(mode_frame, text="Add Point", command=lambda: self.set_mode('point')).pack(fill=tk.X, pady=2)
        ttk.Button(mode_frame, text="Draw Rectangle", command=lambda: self.set_mode('rectangle')).pack(fill=tk.X, pady=2)
        ttk.Button(mode_frame, text="Draw Line", command=lambda: self.set_mode('line')).pack(fill=tk.X, pady=2)
        ttk.Button(mode_frame, text="Select/Move", command=lambda: self.set_mode('select')).pack(fill=tk.X, pady=2)
        
        # Dimensions Input
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(control_frame, text="Dimensions (cm)", font=('Arial', 12, 'bold')).pack(pady=(5,5))
        
        dim_frame = ttk.Frame(control_frame)
        dim_frame.pack(fill=tk.X, padx=5)
        
        ttk.Label(dim_frame, text="Width:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.width_var = tk.StringVar(value="2.0")
        ttk.Entry(dim_frame, textvariable=self.width_var, width=10).grid(row=0, column=1, pady=2)
        
        ttk.Label(dim_frame, text="Height:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.height_var = tk.StringVar(value="2.0")
        ttk.Entry(dim_frame, textvariable=self.height_var, width=10).grid(row=1, column=1, pady=2)
        
        ttk.Label(dim_frame, text="Point Size:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.point_size_var = tk.StringVar(value="0.3")
        ttk.Entry(dim_frame, textvariable=self.point_size_var, width=10).grid(row=2, column=1, pady=2)
        
        # Object Management
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(control_frame, text="Object Management", font=('Arial', 12, 'bold')).pack(pady=(5,5))
        
        obj_frame = ttk.Frame(control_frame)
        obj_frame.pack(fill=tk.X, padx=5)
        
        ttk.Button(obj_frame, text="Delete Selected", command=self.delete_selected).pack(fill=tk.X, pady=2)
        ttk.Button(obj_frame, text="Clear All", command=self.clear_all).pack(fill=tk.X, pady=2)
        
        # Analysis Section
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(control_frame, text="Analysis", font=('Arial', 12, 'bold')).pack(pady=(5,5))
        
        analysis_frame = ttk.Frame(control_frame)
        analysis_frame.pack(fill=tk.X, padx=5)
        
        ttk.Button(analysis_frame, text="Label Points (Numbers)", 
                  command=self.label_points).pack(fill=tk.X, pady=2)
        ttk.Button(analysis_frame, text="Set Reference Point", 
                  command=self.set_reference_point).pack(fill=tk.X, pady=2)
        ttk.Button(analysis_frame, text="Calculate Distances", 
                  command=self.calculate_distances).pack(fill=tk.X, pady=2)
        
        # Status
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        self.status_label = ttk.Label(control_frame, text="Mode: Select", 
                                      font=('Arial', 10), wraplength=230)
        self.status_label.pack(pady=5)
        
        # Right panel - Plot
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Matplotlib figure - 2D plot
        self.fig = plt.Figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        
        # Zoom controls
        zoom_frame = ttk.Frame(plot_frame)
        zoom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        ttk.Label(zoom_frame, text="Zoom:").pack(side=tk.LEFT, padx=5)
        ttk.Button(zoom_frame, text="➕ Zoom In", command=self.zoom_in, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="➖ Zoom Out", command=self.zoom_out, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="🔄 Reset View", command=self.reset_view, width=12).pack(side=tk.LEFT, padx=2)
        
    def setup_plot(self):
        self.ax.clear()
        
        # Set up 2D grid: -50 to +50 cm on X and Y
        self.ax.set_xlim(-50, 50)
        self.ax.set_ylim(-50, 50)
        
        # Set tick marks at 5cm intervals for better readability
        x_ticks = np.arange(-50, 51, 5)
        y_ticks = np.arange(-50, 51, 5)
        
        self.ax.set_xticks(x_ticks)
        self.ax.set_yticks(y_ticks)
        
        # Add minor ticks for 1cm grid
        self.ax.set_xticks(np.arange(-50, 51, 1), minor=True)
        self.ax.set_yticks(np.arange(-50, 51, 1), minor=True)
        
        self.ax.set_xlabel('X (cm)', fontsize=12)
        self.ax.set_ylabel('Y (cm)', fontsize=12)
        
        self.ax.grid(True, which='major', alpha=0.6, linewidth=1)
        self.ax.grid(True, which='minor', alpha=0.2, linewidth=0.5)
        self.ax.set_aspect('equal')
        
        # Redraw all existing objects
        self.redraw_all_objects()
        
        self.canvas.draw()
        
    def redraw_all_objects(self):
        """Redraw all points, rectangles, and lines after plot reset"""
        # Redraw points
        for point in self.points:
            x, y, z = point['pos']
            point['artist'] = self.ax.scatter(x, y, s=point['size']*100, 
                                             c='red', marker='o', edgecolors='black', linewidths=1)
            if point['label']:
                point['text_artist'] = self.ax.text(x, y, f"  {point['label']}", 
                                                   fontsize=10, color='black')
        
        # Redraw rectangles
        for rect in self.rectangles:
            corners = rect['corners']
            xs = [c[0] for c in corners] + [corners[0][0]]
            ys = [c[1] for c in corners] + [corners[0][1]]
            rect['artist'] = self.ax.fill(xs, ys, alpha=0.3, facecolor='cyan', 
                                          edgecolor='blue', linewidth=2)[0]
        
        # Redraw lines
        for line in self.lines:
            p1, p2 = line['start'], line['end']
            line['artist'] = self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 
                                         'g-', linewidth=2)[0]
        
        # Redraw reference point if it exists
        if self.reference_point:
            x, y, z = self.reference_point
            self.reference_artist = self.ax.scatter(x, y, s=300, 
                                                   c='gold', marker='*', 
                                                   edgecolors='black', linewidths=2)
            self.ax.text(x, y, '  REF', fontsize=12, 
                        color='red', fontweight='bold')
        
    def set_mode(self, mode):
        self.drawing_mode = mode
        self.temp_points = []
        self.selected_object = None
        self.selected_index = None
        status_text = f"Mode: {mode.title()}"
        if mode == 'rectangle':
            status_text += " - Click two corners"
        elif mode == 'line':
            status_text += " - Click start and end points"
        elif mode == 'point':
            status_text += " - Keep clicking to add points"
        elif mode == 'select':
            status_text += " - Click near object to select"
        self.status_label.config(text=status_text)
        
    def on_click(self, event):
        if event.inaxes != self.ax:
            return
            
        if event.button == 1:  # Left click
            if self.drawing_mode == 'point':
                self.add_point(event)
            elif self.drawing_mode == 'rectangle':
                self.add_rectangle_point(event)
            elif self.drawing_mode == 'line':
                self.add_line_point(event)
            elif self.drawing_mode == 'select':
                self.select_object(event)
                
    def get_3d_coords(self, event):
        """Convert 2D click to 3D coordinates - XY from click, Z from user input"""
        if event.xdata is None or event.ydata is None:
            return None
            
        # Round to nearest 0.5cm for precision
        x = round(event.xdata * 2) / 2  # Round to 0.5cm
        y = round(event.ydata * 2) / 2
        
        # Ask for Z coordinate
        z = simpledialog.askfloat("Z Coordinate", 
            f"Point at X={x:.1f}, Y={y:.1f}\nEnter Z coordinate (cm):",
            initialvalue=0.0)
        
        if z is None:
            return None
            
        return (x, y, z)
        
    def add_point(self, event):
        coords = self.get_3d_coords(event)
        if coords is None:
            return
            
        try:
            size = float(self.point_size_var.get())
        except:
            size = 0.3
            
        # Draw point on 2D plane
        x, y, z = coords
        artist = self.ax.scatter(x, y, s=size*100, c='red', marker='o', 
                                edgecolors='black', linewidths=1)
        
        self.points.append({
            'pos': coords,
            'size': size,
            'label': '',
            'artist': artist,
            'text_artist': None
        })
        
        self.canvas.draw()
        
        # Stay in point mode - update status
        self.status_label.config(text=f"Mode: Point (added {len(self.points)} points) - Keep clicking to add more")
        
    def add_rectangle_point(self, event):
        coords = self.get_3d_coords(event)
        if coords is None:
            return
            
        self.temp_points.append(coords)
        
        # Draw temporary point on 2D plane
        x, y, z = coords
        self.ax.scatter(x, y, s=50, c='blue', marker='x')
        self.canvas.draw()
        
        if len(self.temp_points) == 2:
            self.create_rectangle()
            self.temp_points = []
            
    def create_rectangle(self):
        p1, p2 = self.temp_points
        
        try:
            width = float(self.width_var.get())
            height = float(self.height_var.get())
        except:
            width = height = 2.0
        
        # Create rectangle corners in XY plane (Z coordinate from first point)
        x, y, z = p1
        corners = [
            (x, y, z),
            (x + width, y, z),
            (x + width, y + height, z),
            (x, y + height, z)
        ]
        
        # Draw rectangle on 2D plane
        xs = [c[0] for c in corners] + [corners[0][0]]
        ys = [c[1] for c in corners] + [corners[0][1]]
        poly = self.ax.fill(xs, ys, alpha=0.3, facecolor='cyan', 
                           edgecolor='blue', linewidth=2)[0]
        
        self.rectangles.append({
            'corners': corners,
            'plane': 'xy',
            'artist': poly,
            'label': ''
        })
        
        self.canvas.draw()
        
    def add_line_point(self, event):
        coords = self.get_3d_coords(event)
        if coords is None:
            return
            
        self.temp_points.append(coords)
        
        # Draw temporary point on 2D plane
        x, y, z = coords
        self.ax.scatter(x, y, s=50, c='green', marker='x')
        self.canvas.draw()
        
        if len(self.temp_points) == 2:
            self.create_line()
            self.temp_points = []
            
    def create_line(self):
        p1, p2 = self.temp_points
        
        # Draw line on 2D plane
        line = self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 
                           'g-', linewidth=2)[0]
        
        self.lines.append({
            'start': p1,
            'end': p2,
            'artist': line,
            'label': ''
        })
        
        self.canvas.draw()
        
    def select_object(self, event):
        """Select nearest point for moving or deletion"""
        if not self.points:
            return
            
        # Get click coordinates (approximate)
        click_pos = self.get_3d_coords(event)
        if click_pos is None:
            return
        
        # Find nearest point
        min_dist = float('inf')
        nearest_idx = None
        
        for idx, point in enumerate(self.points):
            dist = np.sqrt(sum((a - b)**2 for a, b in zip(point['pos'], click_pos)))
            if dist < min_dist:
                min_dist = dist
                nearest_idx = idx
        
        # Select if close enough (within 2cm)
        if min_dist < 5.0 and nearest_idx is not None:
            self.selected_index = nearest_idx
            self.selected_object = self.points[nearest_idx]
            self.status_label.config(text=f"Selected Point at {self.selected_object['pos']}")
            
            # Ask if user wants to move it
            if messagebox.askyesno("Move Point", "Do you want to move this point?"):
                self.move_selected_point()
        
    def move_selected_point(self):
        """Move the selected point to new coordinates"""
        if self.selected_index is None:
            return
        
        x = simpledialog.askfloat("Move Point", "Enter new X coordinate (cm):",
                                  initialvalue=self.selected_object['pos'][0])
        y = simpledialog.askfloat("Move Point", "Enter new Y coordinate (cm):",
                                  initialvalue=self.selected_object['pos'][1])
        z = simpledialog.askfloat("Move Point", "Enter new Z coordinate (cm):",
                                  initialvalue=self.selected_object['pos'][2])
        
        if x is not None and y is not None and z is not None:
            # Update position
            self.points[self.selected_index]['pos'] = (x, y, z)
            
            # Redraw
            self.setup_plot()
            
    def delete_selected(self):
        """Delete the selected object"""
        if self.selected_index is not None:
            if messagebox.askyesno("Confirm Delete", "Delete selected point?"):
                self.points.pop(self.selected_index)
                self.selected_index = None
                self.selected_object = None
                self.setup_plot()
        else:
            messagebox.showinfo("Info", "No object selected. Use Select/Move mode to select an object.")
            
    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all objects?"):
            self.points = []
            self.rectangles = []
            self.lines = []
            self.reference_point = None
            self.reference_artist = None
            self.setup_plot()
            
    def label_points(self):
        """Label all points with numbers"""
        if not self.points:
            messagebox.showwarning("Warning", "No points to label")
            return
        
        for i, point in enumerate(self.points, 1):
            point['label'] = str(i)
            
        # Redraw to show labels
        self.setup_plot()
        messagebox.showinfo("Success", f"Labeled {len(self.points)} points")
            
    def set_reference_point(self):
        """Set reference point on a specific axis"""
        # Ask user to select axis
        axis_window = tk.Toplevel(self.root)
        axis_window.title("Select Reference Axis")
        axis_window.geometry("300x150")
        
        ttk.Label(axis_window, text="Select the axis for reference point:", 
                 font=('Arial', 11)).pack(pady=10)
        
        axis_var = tk.StringVar(value='Z')
        
        axis_frame = ttk.Frame(axis_window)
        axis_frame.pack(pady=10)
        
        ttk.Radiobutton(axis_frame, text="X Axis", variable=axis_var, value='X').pack(anchor=tk.W)
        ttk.Radiobutton(axis_frame, text="Y Axis", variable=axis_var, value='Y').pack(anchor=tk.W)
        ttk.Radiobutton(axis_frame, text="Z Axis", variable=axis_var, value='Z').pack(anchor=tk.W)
        
        def confirm_axis():
            axis = axis_var.get()
            axis_window.destroy()
            
            # Ask for coordinate value
            coord = simpledialog.askfloat("Reference Point", 
                                         f"Enter {axis} coordinate (cm):",
                                         initialvalue=45.0 if axis == 'Z' else 0.0)
            
            if coord is not None:
                # Set reference point (other coordinates at 0)
                if axis == 'X':
                    self.reference_point = (coord, 0.0, 0.0)
                elif axis == 'Y':
                    self.reference_point = (0.0, coord, 0.0)
                else:  # Z
                    self.reference_point = (0.0, 0.0, coord)
                
                # Redraw to show reference point
                self.setup_plot()
                messagebox.showinfo("Success", 
                    f"Reference point set at {axis}={coord} cm\n{self.reference_point}")
        
        ttk.Button(axis_window, text="Confirm", command=confirm_axis).pack(pady=10)
            
    def calculate_distances(self):
        """Calculate distances from reference point to all labeled points"""
        if self.reference_point is None:
            messagebox.showwarning("Warning", "Please set a reference point first")
            return
            
        if not self.points:
            messagebox.showwarning("Warning", "No points to measure")
            return
        
        # Check if points are labeled
        if not any(p['label'] for p in self.points):
            if messagebox.askyesno("Label Points?", 
                "Points are not labeled. Label them now?"):
                self.label_points()
            else:
                return
            
        # Calculate distances
        results = "DISTANCE CALCULATIONS & VISUAL ANGLES\n"
        results += "=" * 60 + "\n\n"
        results += f"Reference Point: {self.reference_point}\n"
        results += f"  X = {self.reference_point[0]:.2f} cm\n"
        results += f"  Y = {self.reference_point[1]:.2f} cm\n"
        results += f"  Z = {self.reference_point[2]:.2f} cm\n\n"
        results += "=" * 60 + "\n\n"
        
        for point in self.points:
            if point['label']:
                pos = point['pos']
                distance = np.sqrt(
                    (pos[0] - self.reference_point[0])**2 +
                    (pos[1] - self.reference_point[1])**2 +
                    (pos[2] - self.reference_point[2])**2
                )
                
                # Calculate diameters for 1°, 2°, and 3° visual angles
                # Formula: size = 2 * distance * tan(theta / 2)
                # theta in radians
                diameter_1deg = 2 * distance * np.tan(np.radians(1) / 2)
                diameter_2deg = 2 * distance * np.tan(np.radians(2) / 2)
                diameter_3deg = 2 * distance * np.tan(np.radians(3) / 2)
                
                results += f"Point {point['label']}:\n"
                results += f"  Position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}) cm\n"
                results += f"  Distance: {distance:.2f} cm\n"
                results += f"  Diameter for 1° visual angle: {diameter_1deg:.3f} cm\n"
                results += f"  Diameter for 2° visual angle: {diameter_2deg:.3f} cm\n"
                results += f"  Diameter for 3° visual angle: {diameter_3deg:.3f} cm\n\n"
            
        # Show in a new window
        result_window = tk.Toplevel(self.root)
        result_window.title("Distance Calculations & Visual Angles")
        result_window.geometry("600x700")
        
        text = tk.Text(result_window, wrap=tk.WORD, font=('Courier', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert('1.0', results)
        text.config(state=tk.DISABLED)
        
        # Add buttons
        btn_frame = ttk.Frame(result_window)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Close", 
                  command=result_window.destroy).pack(side=tk.LEFT, padx=5)
        
    def on_motion(self, event):
        # Could add preview of shape being drawn
        pass
    
    def on_scroll(self, event):
        """Handle mouse wheel zoom for 2D plot"""
        if event.inaxes != self.ax:
            return
        
        # Zoom factor
        base_scale = 1.1
        
        # Get current axis limits
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # Calculate current ranges
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        
        # Zoom in or out
        if event.button == 'up':
            # Zoom in - decrease range
            scale_factor = 1 / base_scale
        else:
            # Zoom out - increase range
            scale_factor = base_scale
        
        # Calculate new ranges
        new_x_range = max(10, min(200, x_range * scale_factor))
        new_y_range = max(10, min(200, y_range * scale_factor))
        
        # Keep center point the same
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        
        # Apply new limits centered on the same point
        self.ax.set_xlim([x_center - new_x_range/2, x_center + new_x_range/2])
        self.ax.set_ylim([y_center - new_y_range/2, y_center + new_y_range/2])
        
        self.canvas.draw()
    
    def zoom_in(self):
        """Zoom in button handler"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        
        x_range = (xlim[1] - xlim[0]) * 0.8 / 2
        y_range = (ylim[1] - ylim[0]) * 0.8 / 2
        
        self.ax.set_xlim([x_center - x_range, x_center + x_range])
        self.ax.set_ylim([y_center - y_range, y_center + y_range])
        
        self.zoom_level *= 1.25
        self.canvas.draw()
    
    def zoom_out(self):
        """Zoom out button handler"""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        
        x_range = (xlim[1] - xlim[0]) * 1.25 / 2
        y_range = (ylim[1] - ylim[0]) * 1.25 / 2
        
        self.ax.set_xlim([x_center - x_range, x_center + x_range])
        self.ax.set_ylim([y_center - y_range, y_center + y_range])
        
        self.zoom_level *= 0.8
        self.canvas.draw()
    
    def reset_view(self):
        """Reset view to default zoom"""
        self.zoom_level = 1.0
        
        # Reset to default view: -50 to 50 on X and Y
        self.ax.set_xlim(-50, 50)
        self.ax.set_ylim(-50, 50)
        
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = Shape3DPlotter(root)
    root.mainloop()
