from direct.showbase.ShowBase import ShowBase
from panda3d.core import LVecBase3, LColor, LineSegs
from direct.gui.DirectGui import DirectButton  # Importa DirectButton para crear el botón

from algo_octree import Octree
import random

class CubeApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.c_color=1
        # Posición de la cámara
        self.camera.set_pos(500, 1000, 5)
        self.camera.look_at(0, 0, 0)

        # Crear el cubo transparente con aristas visibles
        #self.cube = self.create_wireframe_cube(0, 0, 0, 1)

        self.tam_cubo = 1
        self.cube = self.create_wireframe_cube(0, 0, 0, self.tam_cubo)
        self.octree = Octree((-self.tam_cubo / 2, -self.tam_cubo / 2, -self.tam_cubo / 2,
                              self.tam_cubo / 2, self.tam_cubo / 2, self.tam_cubo / 2), 2)
        



        # Crear un botón para cambiar el color del cubo transparente
        #self.color_button = DirectButton(text="Cambiar Color", scale=0.1, pos=(0, 0, -0.9),
                                         #command=self.change_cube_color)

        self.add_point_button = DirectButton(text="Agregar Punto", scale=0.1, pos=(0, 0, -0.8),
                                             command=self.insertar_random)
        
    def insertar_random(self): 
        """Agrega un punto aleatorio al octree."""
        point = (random.uniform(-self.tam_cubo / 2, self.tam_cubo / 2),
                 random.uniform(-self.tam_cubo / 2, self.tam_cubo / 2),
                 random.uniform(-self.tam_cubo / 2, self.tam_cubo / 2))
        if self.octree.insert(point):
            print(f"Punto {point} agregado al octree.")
            self.draw_esfera(point)
            self.octree.visualize(self.render)
        else:
            print(f"Punto {point} fuera de los límites del octree.")
        
    def draw_esfera(self, posicion):
        """Dibuja una esfera en la posición dada."""
        sphere = self.loader.load_model("sphere3D/scene.gltf")
        sphere.set_scale(0.02)  # Escalar la esfera
        sphere.set_pos(LVecBase3(*posicion))
        sphere.reparent_to(self.render)
        sphere.set_color(LColor(1, 1, 1, 0.1))  # Color azul para la esfera  
        
    def create_wireframe_cube(self, x, y, z, size):
        """Crea un cubo con aristas visibles y caras transparentes."""
        # Crear el modelo de cubo transparente
        cube = self.loader.load_model("scene.gltf")
        cube.reparent_to(self.render)
        cube.set_scale(size)
        cube.set_pos(LVecBase3(x, y, z))
        cube.set_transparency(True)
        cube.set_color(LColor(1, 1, 1, 0.1))  # Color blanco con baja opacidad (transparente)

        # Crear líneas para las aristas del cubo
        line_segs = LineSegs()
        #line_segs.set_thickness(2)
        #line_segs.set_color(LColor(1, 1, 1, 1))  # Color de las aristas (blanco)

        # Coordenadas para las 8 esquinas del cubo
        vertices = [
            (-size / 2, -size / 2, -size / 2), (size / 2, -size / 2, -size / 2),
            (size / 2, size / 2, -size / 2), (-size / 2, size / 2, -size / 2),
            (-size / 2, -size / 2, size / 2), (size / 2, -size / 2, size / 2),
            (size / 2, size / 2, size / 2), (-size / 2, size / 2, size / 2)
        ]

        # Definir las aristas del cubo usando los índices de las esquinas
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Cara inferior
            (4, 5), (5, 6), (6, 7), (7, 4),  # Cara superior
            (0, 4), (1, 5), (2, 6), (3, 7)   # Conexiones verticales
        ]

        # Crear cada arista en el LineSegs
        for edge in edges:
            start, end = edge
            line_segs.move_to(vertices[start])
            line_segs.draw_to(vertices[end])

        # Convertir LineSegs a NodePath y adjuntarlo a render
        wireframe = line_segs.create()
        wireframe_node = self.render.attach_new_node(wireframe)
        #wireframe_node.set_pos(x, y, z)

        return cube

    def change_cube_color(self):
        """Cambia el color del cubo transparente a verde."""
        if self.c_color ==1:
            self.cube.set_color(LColor(0, 1, 0, 0.1))
            self.c_color=0# Cambia el color del cubo a verde con transparencia
        elif self.c_color ==0:
            self.cube.set_color(LColor(1, 1, 0, 0.1))  # Cambia el color del cubo a verde con transparencia
            self.c_color=1
            
# Ejecutar la aplicación
app = CubeApp()
app.run()
