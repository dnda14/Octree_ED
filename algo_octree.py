
from direct.showbase.ShowBase import ShowBase
from panda3d.core import LVecBase3, LColor, LineSegs, TextNode
from direct.gui.DirectGui import DirectButton  # Importa DirectButton para crear el botón

class Octree:
    def __init__(self, boundary, capacidad, level=0):
        """
        Inicializa el octree.
        :param boundary: un cubo que define los límites del octree (xmin, ymin, zmin, xmax, ymax, zmax)
        :param capacidad: número máximo de puntos que el cubo puede contener antes de dividirse
        """
        self.boundary = boundary  # (xmin, ymin, zmin, xmax, ymax, zmax)
        self.capacidad = capacidad
        self.puntos = []
        self.divided = False
        self.subtrees = []          

    def visualizar(self, render):
        """
        Visualiza el cubo actual y sus subcubos si están divididos.
        :param render: gestiona todos los elementos de la escena 
        """
        # Graficar el cubo actual
        self.draw_cube(self.boundary, render)
        
        # Si está dividido, graficar los subcubos
        if self.divided:
            for subtree in self.subtrees:
                subtree.visualizar(render)
                
    def draw_cube(self, boundary, render):
        """Dibuja el cubo a partir de sus límites."""
        xmin, ymin, zmin, xmax, ymax, zmax = boundary

        # Crear líneas para las aristas del cubo
        line_segs = LineSegs()
        line_segs.set_thickness(2)
        line_segs.set_color(LColor(1, 1, 0, 1))  # Color de las aristas (amarillo)

        # Coordenadas para las 8 esquinas del cubo
        vertices = [
            (xmin, ymin, zmin), (xmax, ymin, zmin),
            (xmax, ymax, zmin), (xmin, ymax, zmin),
            (xmin, ymin, zmax), (xmax, ymin, zmax),
            (xmax, ymax, zmax), (xmin, ymax, zmax)
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
        wireframe_node = render.attach_new_node(wireframe)
        wireframe_node.set_pos(0, 0, 0)  # Posición base, se ajustará más tarde

    def insert(self, point):
        """
        Inserta un punto en el octree.
        :param point: un tuple que representa el punto (x, y, z)
        :return: True si se insertó, False si no se pudo insertar
        """
        if not self.contains(point):
            return False

        if len(self.puntos) < self.capacidad:
            self.puntos.append(point)
            #self.mostrar_arbol()
            print("punyo agrgado")
            self.imprimir_nodos_compacto()
            return True
        else:
            if not self.divided:
                self.subdivide()

            for subtree in self.subtrees:
                if subtree.insert(point):
                    return True
                
        return False
    
    def contains(self, point):
        """
        Verifica si el punto está dentro de los límites del octree.
        """
        x, y, z = point
        xmin, ymin, zmin, xmax, ymax, zmax = self.boundary
        return (xmin <= x < xmax) and (ymin <= y < ymax) and (zmin <= z < zmax)

    def subdivide(self):
        """Divide el cubo en ocho subcubos."""
        xmin, ymin, zmin, xmax, ymax, zmax = self.boundary
        xmid = (xmin + xmax) / 2
        ymid = (ymin + ymax) / 2
        zmid = (zmin + zmax) / 2

        # Crear 8 subcubos
        self.subtrees.append(Octree((xmin, ymin, zmin, xmid, ymid, zmid), self.capacidad))
        self.subtrees.append(Octree((xmid, ymin, zmin, xmax, ymid, zmid), self.capacidad))
        self.subtrees.append(Octree((xmin, ymid, zmin, xmid, ymax, zmid), self.capacidad))
        self.subtrees.append(Octree((xmid, ymid, zmin, xmax, ymax, zmid), self.capacidad))
        self.subtrees.append(Octree((xmin, ymin, zmid, xmid, ymid, zmax), self.capacidad))
        self.subtrees.append(Octree((xmid, ymin, zmid, xmax, ymid, zmax), self.capacidad))
        self.subtrees.append(Octree((xmin, ymid, zmid, xmid, ymax, zmax), self.capacidad))
        self.subtrees.append(Octree((xmid, ymid, zmid, xmax, ymax, zmax), self.capacidad))
        
        self.divided = True
        for point in self.puntos:
            for subtree in self.subtrees:
                if subtree.contains(point):
                    subtree.insert(point)
                    break

        # Limpiar los puntos en el nodo actual, ya que ahora se han trasladado a los subcubos
        self.puntos = []
        
    def imprimir_nodos_compacto(self, level=0):
        """
        Imprime una descripción compacta de cada nodo en el octree y los puntos que contiene.
        Muestra el nivel de profundidad, el número de puntos y sus coordenadas.
        """
        indent = ' ' * (level * 4)  # Cuatro espacios de indentación por nivel
        xmin, ymin, zmin, xmax, ymax, zmax = self.boundary
        
        # Información breve del nodo actual
        print(f"{indent}Nivel {level}: {len(self.puntos)} puntos en ({xmin}, {ymin}, {zmin}) a ({xmax}, {ymax}, {zmax})")
        
        # Lista compacta de puntos
        if self.puntos:
            print(f"{indent}Puntos: {', '.join(map(str, self.puntos))}")
        
        # Llamada recursiva para los subnodos si está dividido
        if self.divided:
            for subtree in self.subtrees:
                subtree.imprimir_nodos_compacto(level + 1)
                
    def __str__(self):
        return f'Octree(boundary={self.boundary}, puntos={self.puntos}, divided={self.divided})'
