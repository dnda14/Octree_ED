from direct.showbase.ShowBase import ShowBase
from panda3d.core import LVecBase3, LColor, LineSegs, TextNode
from direct.gui.DirectGui import DirectButton, DirectEntry, DirectDialog
import random


class Point:
    def __init__(self, x=-1, y=-1, z=-1):
        self.x = x
        self.y = y
        self.z = z
    def __eq__(self, other):
        if isinstance(other, Point):
            tolerance = 1e-6  # Small tolerance for floating-point comparison
            return (abs(self.x - other.x) < tolerance and
                    abs(self.y - other.y) < tolerance and
                    abs(self.z - other.z) < tolerance)
        return False

class Octree:
    def __init__(self, x1, y1, z1, x2, y2, z2, capacity=1):
        self.capacity = capacity
        self.boundary_min = Point(x1, y1, z1)
        self.boundary_max = Point(x2, y2, z2)
        self.points = []
        self.children = [None] * 8
        self.divided = False

    def subdivide(self):
        midx = (self.boundary_min.x + self.boundary_max.x) / 2
        midy = (self.boundary_min.y + self.boundary_max.y) / 2
        midz = (self.boundary_min.z + self.boundary_max.z) / 2
        boundaries = [
            (self.boundary_min.x, self.boundary_min.y, self.boundary_min.z, midx, midy, midz),  # TopLeftFront
            (midx, self.boundary_min.y, self.boundary_min.z, self.boundary_max.x, midy, midz),  # TopRightFront
            (midx, midy, self.boundary_min.z, self.boundary_max.x, self.boundary_max.y, midz),  # BottomRightFront
            (self.boundary_min.x, midy, self.boundary_min.z, midx, self.boundary_max.y, midz),  # BottomLeftFront
            (self.boundary_min.x, self.boundary_min.y, midz, midx, midy, self.boundary_max.z),  # TopLeftBottom
            (midx, self.boundary_min.y, midz, self.boundary_max.x, midy, self.boundary_max.z),  # TopRightBottom
            (midx, midy, midz, self.boundary_max.x, self.boundary_max.y, self.boundary_max.z),  # BottomRightBack
            (self.boundary_min.x, midy, midz, midx, self.boundary_max.y, self.boundary_max.z),  # BottomLeftBack
        ]
        for i in range(8):
            self.children[i] = Octree(*boundaries[i], self.capacity)
        self.divided = True

    def insert(self, x, y, z):
        # Check if point is within the node's boundaries
        if not (self.boundary_min.x <= x <= self.boundary_max.x and
                self.boundary_min.y <= y <= self.boundary_max.y and
                self.boundary_min.z <= z <= self.boundary_max.z):
            return False

        # If this node is not divided and has capacity, just add the point
        if not self.divided and len(self.points) < self.capacity:
            self.points.append(Point(x, y, z))
            return True

        # Subdivide if capacity is reached and node is not already divided
        if not self.divided:
            self.subdivide()
            # Move points to children nodes after subdivision
            for p in self.points:
                for child in self.children:
                    if child.insert(p.x, p.y, p.z):
                        break
            self.points = []  # Clear points in the current node as they are now in children

        # Insert new point into one of the children
        for child in self.children:
            if child.insert(x, y, z):
                return True

        return False
    
    def search(self, x, y, z):
        # Check if point is within this node's boundaries
        if not (self.boundary_min.x <= x <= self.boundary_max.x and
                self.boundary_min.y <= y <= self.boundary_max.y and
                self.boundary_min.z <= z <= self.boundary_max.z):
            return False

        # Check if the point exists in this node's points
        for point in self.points:
            if point.x == x and point.y == y and point.z == z:
                return True

        # If divided, recursively search in the children nodes
        if self.divided:
            for child in self.children:
                if child and child.search(x, y, z):
                    return True

        # Point not found in this node or its children
        return False

    def delete(self, x, y, z):
        # Check if the point is within the boundaries of the current node
        if not (self.boundary_min.x <= x <= self.boundary_max.x and
                self.boundary_min.y <= y <= self.boundary_max.y and
                self.boundary_min.z <= z <= self.boundary_max.z):
            return False  # Point is outside this node's boundaries

        # If not divided, check and remove the point from this node
        if not self.divided:
            point_to_delete = Point(x, y, z)
            if point_to_delete in self.points:  # Compare using __eq__ method
                print(f"Point found! Deleting {point_to_delete}")
                self.points.remove(point_to_delete)  # Remove the point
                return True
            print("Point not found in this node")
            return False  # If point is not found in this node

        # If the node is divided, check the children recursively
        for child in self.children:
            if child:  # If child exists
                print(f"Checking child node")
                if child.delete(x, y, z):  # Try deleting from the child
                    print("Point deleted in child node")
                    # After deletion, check if any child can be merged (optional)
                    self._try_merge_children()
                    return True

        return False  # Return False if the point was not found in any child

    def _try_merge_children(self):
        # Check if all children are empty, and if so, merge them back into this node
        all_empty = True
        for child in self.children:
            if len(child.points) > 0 or child.divided:
                all_empty = False
                break

        if all_empty:
            self.children = [None] * 8  # Remove all children
            self.divided = False  # Set the node to undivided

    def find_point(self, x, y, z):
        # Search for the point recursively
        if not (self.boundary_min.x <= x <= self.boundary_max.x and
                self.boundary_min.y <= y <= self.boundary_max.y and
                self.boundary_min.z <= z <= self.boundary_max.z):
            return False

        if not self.divided:
            return Point(x, y, z) in self.points

        for child in self.children:
            if child.find_point(x, y, z):
                return True
        return False
    

class OctreeApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.capacity = 2
        self.size = 10
        self.octree = Octree(-self.size / 2, -self.size / 2, -self.size / 2,
                             self.size / 2, self.size / 2, self.size / 2, self.capacity)

        self.camera.set_pos(20, 30, 20)
        self.camera.look_at(0, 0, 0)

        # Draw initial cube for octree boundary
        self.draw_cube((-self.size / 2, -self.size / 2, -self.size / 2),
                       (self.size / 2, self.size / 2, self.size / 2))

        # Draw XYZ axis lines
        self.draw_axis_lines()
        
        # Button to add random points
        self.add_point_button = DirectButton(text="Add Random Point", scale=0.1, pos=(0, 0, -0.8),
                                             command=self.add_random_point)
        # Button to add point manually
        self.manual_point_button = DirectButton(text="Opera", scale=0.1, pos=(0, 0, -0.6),
                                                command=self.open_input_dialog)
    def draw_axis_lines(self):
        axis_line_segs = LineSegs()
        axis_line_segs.set_thickness(2)

        # X-rojo
        axis_line_segs.set_color(LColor(1, 0, 0, 1))
        axis_line_segs.move_to(-self.size, 0, 0)
        axis_line_segs.draw_to(self.size, 0, 0)

        # Y-verde
        axis_line_segs.set_color(LColor(0, 1, 0, 1))
        axis_line_segs.move_to(0, -self.size, 0)
        axis_line_segs.draw_to(0, self.size, 0)

        # Z-azul
        axis_line_segs.set_color(LColor(0, 0, 1, 1))
        axis_line_segs.move_to(0, 0, -self.size)
        axis_line_segs.draw_to(0, 0, self.size)

        axis_np = self.render.attach_new_node(axis_line_segs.create())
        axis_np.set_tag("axis", "true") 
        
    def open_input_dialog(self):
        
        # Create dialog for manual point input
        self.dialog = DirectDialog(frameSize=(-0.6, 0.6, -0.6, 0.6), fadeScreen=0.5, relief=1)
        self.dialog.setTransparency(True)
        
        # Input fields for X, Y, and Z coordinates
        self.x_entry = DirectEntry(parent=self.dialog, scale=0.1, pos=(-0.4, 0, 0.1), width=5,
                                   text_align=TextNode.ACenter, initialText="X", numLines=1, focus=1)
        self.y_entry = DirectEntry(parent=self.dialog, scale=0.1, pos=(0, 0, 0.1), width=5,
                                   text_align=TextNode.ACenter, initialText="Y", numLines=1)
        self.z_entry = DirectEntry(parent=self.dialog, scale=0.1, pos=(0.4, 0, 0.1), width=5,
                                   text_align=TextNode.ACenter, initialText="Z", numLines=1)
        
        # Confirm button to add point
        confirm_button = DirectButton(parent=self.dialog, text="Add Point", scale=0.07, pos=(0, 0, -0.1),
                                      command=self.add_manual_point)
        # Search button to find point by coordinates
        search_button = DirectButton(parent=self.dialog, text="Search Point", scale=0.07, pos=(0, 0, -0.3),
                                    command=self.search_point)
        
        delete_button = DirectButton(parent=self.dialog, text="Delete Point", scale=0.07, pos=(0, 0, -0.5),
                                    command=self.delete_point)
    def add_manual_point(self):
        # Get values from input fields
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())
        except ValueError:
            print("Please enter valid numbers for X, Y, and Z.")
            return
        
        # Close the dialog
        self.dialog.hide()
        
        # Insert the manually entered point
        if self.octree.insert(x, y, z):
            print(f"Inserted manual point at ({x:.2f}, {y:.2f}, {z:.2f})")
            self.draw_sphere((x, y, z), color=(0, 1, 0, 1))  # Green for manually added points

            for node in self.render.get_children():
                if node.has_tag("octree"):
                    node.remove_node()

            self.visualize_octree()
            
    def search_point(self):
        # Implementation for searching the point
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())
        except ValueError:
            print("Please enter valid numbers for X, Y, and Z.")
            return
        
        # Close the dialog
        self.dialog.hide()
        # Logic for searching the point (e.g., check if the point exists in a structure)
        found = self.octree.search(x, y, z)  # Assume find_point is a method you define
        if found:
            print(f"Point ({x}, {y}, {z}) found!")
        else:
            print(f"Point ({x}, {y}, {z}) not found.")
    
    def delete_point(self):
        # Get values from input fields for deletion
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())
        except ValueError:
            print("Please enter valid numbers for X, Y, and Z.")
            return

        # Close the dialog
        self.dialog.hide()

        # Logic for deleting the point (e.g., remove the point from the octree)
        deleted = self.octree.delete(x, y, z)  # Assume delete method is implemented in Octree
        if deleted:
            print(f"Deleted point ({x}, {y}, {z})")
            for node in self.render.get_children():
                if node.has_tag("octree"):
                    node.remove_node()
            print("hola")
            # Recursively visualize the octree after deletion
            self.visualize_octree()
        else:
            print(f"Point ({x}, {y}, {z}) not found for deletion.")
    
    
    
    def draw_cube(self, min_corner, max_corner):
        line_segs = LineSegs()
        line_segs.set_thickness(2)
        line_segs.set_color(LColor(1, 1, 1, 1))
        x1, y1, z1 = min_corner
        x2, y2, z2 = max_corner

        vertices = [(x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1),
                    (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0),
                (4, 5), (5, 6), (6, 7), (7, 4),
                (0, 4), (1, 5), (2, 6), (3, 7)]

        for start, end in edges:
            line_segs.move_to(vertices[start])
            line_segs.draw_to(vertices[end])

        cube_np = self.render.attach_new_node(line_segs.create())
        cube_np.set_transparency(True)
        cube_np.set_tag("octree", "true")  # Tag the cube for easier removal

    def draw_sphere(self, position, color=(1, 1, 1, 1)):
        sphere = self.loader.load_model("models/misc/sphere")
        sphere.set_scale(0.2)
        sphere.set_pos(*position)
        sphere.set_color(LColor(*color))
        sphere.reparent_to(self.render)

    def add_random_point(self):
        x = random.uniform(-self.size / 2, self.size / 2)
        y = random.uniform(-self.size / 2, self.size / 2)
        z = random.uniform(-self.size / 2, self.size / 2)
        if self.octree.insert(x, y, z):
            print(f"Inserted point at ({x:.2f}, {y:.2f}, {z:.2f})")
            self.draw_sphere((x, y, z), color=(1, 0, 0, 1))  # Red for points

            # Clear previous visualizations of subdivisions
            for node in self.render.get_children():
                if node.has_tag("octree"):
                    node.remove_node()

            # Recursively visualize the octree after insertion
            self.visualize_octree()


    def visualize_octree(self, node=None):
        if node is None:
            node = self.octree
        if not node.divided:
            self.draw_cube((node.boundary_min.x, node.boundary_min.y, node.boundary_min.z),
                           (node.boundary_max.x, node.boundary_max.y, node.boundary_max.z))
        else:
            for child in node.children:
                self.visualize_octree(child)


app = OctreeApp()
app.run()
