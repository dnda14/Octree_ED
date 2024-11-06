from direct.showbase.ShowBase import ShowBase
from panda3d.core import LVecBase3, LColor, LineSegs
from direct.gui.DirectGui import DirectButton  

from algo_octree import Octree
import random

class CubeApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.c_color=1
        
        self.camera.set_pos(500, 1000, 5)
        self.camera.look_at(0, 0, 0)

        
        

        self.tam_cubo = 1
        self.cube = self.create_wireframe_cube(0, 0, 0, self.tam_cubo)
        self.octree = Octree((-self.tam_cubo / 2, -self.tam_cubo / 2, -self.tam_cubo / 2,
                              self.tam_cubo / 2, self.tam_cubo / 2, self.tam_cubo / 2), 2)
        



        
        
                                         

        self.add_point_button = DirectButton(text="Agregar Punto", scale=0.1, pos=(0, 0, -0.8),
                                             command=self.insertar_random)
        self.draw_axes()
    def insertar_random(self): 
        """Agrega un punto aleatorio al octree."""
        point = (random.uniform(-self.tam_cubo / 2, self.tam_cubo / 2),
                 random.uniform(-self.tam_cubo / 2, self.tam_cubo / 2),
                 random.uniform(-self.tam_cubo / 2, self.tam_cubo / 2))
        if self.octree.insert(point):
            print(f"Punto {point} agregado al octree.")
            self.draw_esfera(point)
            self.octree.visualizar(self.render)
        else:
            print(f"Punto {point} fuera de los límites del octree.")
        
    def draw_esfera(self, posicion):
        """Dibuja una esfera en la posición dada."""
        sphere = self.loader.load_model("sphere3D/scene.gltf")
        sphere.set_scale(0.02)  
        sphere.set_pos(LVecBase3(*posicion))
        sphere.reparent_to(self.render)
        sphere.set_color(LColor(1, 1, 1, 0.1))  
        
    def create_wireframe_cube(self, x, y, z, size):
        """Crea un cubo con aristas visibles y caras transparentes."""
        
        cube = self.loader.load_model("scene.gltf")
        cube.reparent_to(self.render)
        cube.set_scale(size)
        cube.set_pos(LVecBase3(x, y, z))
        cube.set_transparency(True)
        cube.set_color(LColor(1, 1, 1, 0.1))  

        
        line_segs = LineSegs()
        
        

        
        vertices = [
            (-size / 2, -size / 2, -size / 2), (size / 2, -size / 2, -size / 2),
            (size / 2, size / 2, -size / 2), (-size / 2, size / 2, -size / 2),
            (-size / 2, -size / 2, size / 2), (size / 2, -size / 2, size / 2),
            (size / 2, size / 2, size / 2), (-size / 2, size / 2, size / 2)
        ]

        
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  
            (4, 5), (5, 6), (6, 7), (7, 4),  
            (0, 4), (1, 5), (2, 6), (3, 7)   
        ]

        
        for edge in edges:
            start, end = edge
            line_segs.move_to(vertices[start])
            line_segs.draw_to(vertices[end])

        
        wireframe = line_segs.create()
        wireframe_node = self.render.attach_new_node(wireframe)
        

        return cube
    def draw_axes(self):
        """Dibuja los ejes X, Y y Z con diferentes colores."""
        line_segs = LineSegs()

        
        origin = (0, 0, 0)
        x_axis_end = (1, 0, 0)
        y_axis_end = (0, 1, 0)
        z_axis_end = (0, 0, 1)

        
        line_segs.set_color(LColor(1, 0, 0, 1))  
        line_segs.move_to(origin)
        line_segs.draw_to(x_axis_end)

        line_segs.set_color(LColor(0, 1, 0, 1))  
        line_segs.move_to(origin)
        line_segs.draw_to(y_axis_end)

        line_segs.set_color(LColor(0, 0, 1, 1))  
        line_segs.move_to(origin)
        line_segs.draw_to(z_axis_end)

        
        axes = line_segs.create()
        axes_node = self.render.attach_new_node(axes)
        
        
    def change_cube_color(self):
        """Cambia el color del cubo transparente a verde."""
        if self.c_color ==1:
            self.cube.set_color(LColor(0, 1, 0, 0.1))
            self.c_color=0
        elif self.c_color ==0:
            self.cube.set_color(LColor(1, 1, 0, 0.1))  
            self.c_color=1
            

app = CubeApp()
app.run()
