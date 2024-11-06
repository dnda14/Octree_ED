from direct.showbase.ShowBase import ShowBase
from panda3d.core import LVecBase3, LColor, LineSegs, TextNode
from direct.gui.DirectGui import DirectButton, DirectEntry, DirectDialog
import random

sphere_dict = {}
class Point:
    def __init__(self, x=-1, y=-1, z=-1):
        self.x = x
        self.y = y
        self.z = z
    def __eq__(self, other):
        if isinstance(other, Point):
            tolerance = 1e-6  
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
            (self.boundary_min.x, self.boundary_min.y, self.boundary_min.z, midx, midy, midz),  
            (midx, self.boundary_min.y, self.boundary_min.z, self.boundary_max.x, midy, midz),  
            (midx, midy, self.boundary_min.z, self.boundary_max.x, self.boundary_max.y, midz),  
            (self.boundary_min.x, midy, self.boundary_min.z, midx, self.boundary_max.y, midz),  
            (self.boundary_min.x, self.boundary_min.y, midz, midx, midy, self.boundary_max.z),  
            (midx, self.boundary_min.y, midz, self.boundary_max.x, midy, self.boundary_max.z),  
            (midx, midy, midz, self.boundary_max.x, self.boundary_max.y, self.boundary_max.z),  
            (self.boundary_min.x, midy, midz, midx, self.boundary_max.y, self.boundary_max.z),  
        ]
        for i in range(8):
            self.children[i] = Octree(*boundaries[i], self.capacity)
        self.divided = True

    def insert(self, x, y, z):
        if not (self.boundary_min.x <= x <= self.boundary_max.x and
                self.boundary_min.y <= y <= self.boundary_max.y and
                self.boundary_min.z <= z <= self.boundary_max.z):
            return False

        if not self.divided and len(self.points) < self.capacity:
            self.points.append(Point(x, y, z))
            return True

        if not self.divided:
            self.subdivide()
            for p in self.points:
                idx = self.get_child_index(p.x, p.y, p.z)
                self.children[idx].insert(p.x, p.y, p.z)
            self.points = []  

        idx = self.get_child_index(x, y, z)
        return self.children[idx].insert(x, y, z)

    def get_child_index(self, x, y, z):
        midx = (self.boundary_min.x + self.boundary_max.x) / 2
        midy = (self.boundary_min.y + self.boundary_max.y) / 2
        midz = (self.boundary_min.z + self.boundary_max.z) / 2

        if x <= midx:
            if y <= midy:
                if z <= midz:
                    return 0  
                else:
                    return 4 
            else:
                if z <= midz:
                    return 3 
                else:
                    return 7  
        else:
            if y <= midy:
                if z <= midz:
                    return 1  
                else:
                    return 5  
            else:
                if z <= midz:
                    return 2  
                else:
                    return 6  
    
    def search(self, x, y, z):
        
        if not (self.boundary_min.x <= x <= self.boundary_max.x and
                self.boundary_min.y <= y <= self.boundary_max.y and
                self.boundary_min.z <= z <= self.boundary_max.z):
            return False

        
        for point in self.points:
            if point.x == x and point.y == y and point.z == z:
                return True

        
        if self.divided:
            for child in self.children:
                if child and child.search(x, y, z):
                    return True

        
        return False

    def delete(self, x, y, z):
        
        if not (self.boundary_min.x <= x <= self.boundary_max.x and
                self.boundary_min.y <= y <= self.boundary_max.y and
                self.boundary_min.z <= z <= self.boundary_max.z):
            return False  

        
        if not self.divided:
            point_to_delete = Point(x, y, z)
            if point_to_delete in self.points:  
                print(f"Point found! Deleting {point_to_delete}")
                self.points.remove(point_to_delete)  
                print(self.points)
                return True
            print("Point not found in this node")
            return False  

        
        for child in self.children:
            if child:  
                print(f"Checking child node")
                if child.delete(x, y, z):  
                    print("Point deleted in child node")
                    
                    self._try_merge_children()
                    return True

        return False  

    def _try_merge_children(self):
        
        all_empty = True
        for child in self.children:
            if len(child.points) > 0 or child.divided:
                all_empty = False
                break

        if all_empty:
            self.points = []  
            for child in self.children:
                self.points.extend(child.points)  
            self.children = [None] * 8  
            self.divided = False  
    

class OctreeApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.capacity = 1
        self.size = 10
        self.octree = Octree(-self.size / 2, -self.size / 2, -self.size / 2,
                             self.size / 2, self.size / 2, self.size / 2, self.capacity)

        self.camera.set_pos(20, 30, 20)
        self.camera.look_at(0, 0, 0)
        
        
        self.draw_cube((-self.size / 2, -self.size / 2, -self.size / 2),
                       (self.size / 2, self.size / 2, self.size / 2))

        
        self.draw_axis_lines()
        
        
        self.add_point_button = DirectButton(text="Punto random", scale=0.1, pos=(0, 0, -0.8),
                                             command=self.add_random_point)
        
        self.manual_point_button = DirectButton(text="Opera", scale=0.1, pos=(0, 0, -0.6),
                                                command=self.open_input_dialog)
    def draw_axis_lines(self):
        axis_line_segs = LineSegs()
        axis_line_segs.set_thickness(2)

        
        axis_line_segs.set_color(LColor(1, 0, 0, 1))
        axis_line_segs.move_to(-self.size, 0, 0)
        axis_line_segs.draw_to(self.size, 0, 0)

        
        axis_line_segs.set_color(LColor(0, 1, 0, 1))
        axis_line_segs.move_to(0, -self.size, 0)
        axis_line_segs.draw_to(0, self.size, 0)

        
        axis_line_segs.set_color(LColor(0, 0, 1, 1))
        axis_line_segs.move_to(0, 0, -self.size)
        axis_line_segs.draw_to(0, 0, self.size)

        axis_np = self.render.attach_new_node(axis_line_segs.create())
        axis_np.set_tag("axis", "true") 
        
    def open_input_dialog(self):
        
        
        self.dialog = DirectDialog(frameSize=(-0.6, 0.6, -0.6, 0.6), fadeScreen=0.5, relief=1)
        self.dialog.setTransparency(True)
        
        
        self.x_entry = DirectEntry(parent=self.dialog, scale=0.1, pos=(-0.4, 0, 0.1), width=5,
                                   text_align=TextNode.ACenter, initialText="X", numLines=1, focus=1)
        self.y_entry = DirectEntry(parent=self.dialog, scale=0.1, pos=(0, 0, 0.1), width=5,
                                   text_align=TextNode.ACenter, initialText="Y", numLines=1)
        self.z_entry = DirectEntry(parent=self.dialog, scale=0.1, pos=(0.4, 0, 0.1), width=5,
                                   text_align=TextNode.ACenter, initialText="Z", numLines=1)
        
        
        confirm_button = DirectButton(parent=self.dialog, text="Add Point", scale=0.07, pos=(0, 0, -0.1),
                                      command=self.add_manual_point)
        
        search_button = DirectButton(parent=self.dialog, text="Search Point", scale=0.07, pos=(0, 0, -0.3),
                                    command=self.search_point)
        
        
                                    
    def add_manual_point(self):
        
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())
        except ValueError:
            print("Please enter valid numbers for X, Y, and Z.")
            return
        
        
        self.dialog.hide()
        
        
        if self.octree.insert(x, y, z):
            print(f"Inserted manual point at ({x:.2f}, {y:.2f}, {z:.2f})")
            

            for node in self.render.get_children():
                if node.has_tag("octree"):
                    node.remove_node()
            sphere = self.draw_sphere((x, y, z))  
            sphere_dict[(x, y, z)] = sphere
            self.visualize_octree()
            
    def search_point(self):
        
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())
        except ValueError:
            print("Please enter valid numbers for X, Y, and Z.")
            return
        
        
        self.dialog.hide()
        
        found = self.octree.search(x, y, z)  
        if found:
            print(f"Point ({x}, {y}, {z}) found!")
        else:
            print(f"Point ({x}, {y}, {z}) not found.")
    
    def delete_point(self):
        
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())
        except ValueError:
            print("Please enter valid numbers for X, Y, and Z.")
            return

        
        self.dialog.hide()

        
        deleted = self.octree.delete(x, y, z)  
        if deleted:
            
            if (x, y, z) in sphere_dict:
                sphere = sphere_dict.pop((x, y, z))  
                sphere.remove_node()
            print(f"Deleted point ({x}, {y}, {z})")
            for node in self.render.get_children():
                if node.has_tag("octree"):
                    node.remove_node()
            print("hola")
            
            
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
        cube_np.set_tag("octree", "true")  

    def draw_sphere(self, position, color=(1, 1, 1, 1)):
        sphere = self.loader.load_model("models/misc/sphere")
        sphere.set_scale(0.2)
        sphere.set_pos(*position)
        sphere.set_color(LColor(*color))
        sphere.reparent_to(self.render)
        return sphere

    def add_random_point(self):
        x = random.uniform(-self.size / 2, self.size / 2)
        y = random.uniform(-self.size / 2, self.size / 2)
        z = random.uniform(-self.size / 2, self.size / 2)
        if self.octree.insert(x, y, z):
            print(f"Inserted point at ({x:.2f}, {y:.2f}, {z:.2f})")
            

            
            for node in self.render.get_children():
                if node.has_tag("octree"):
                    node.remove_node()

            
            self.visualize_octree()


    def visualize_octree(self, node=None):
        if node is None:
            node = self.octree
        if not node.divided:
            self.draw_cube((node.boundary_min.x, node.boundary_min.y, node.boundary_min.z),
                           (node.boundary_max.x, node.boundary_max.y, node.boundary_max.z))
            #print(node.points)
            for point in node.points:
                self.draw_sphere((point.x, point.y, point.z))
        else:
            for child in node.children:
                self.visualize_octree(child)


app = OctreeApp()
app.run()
