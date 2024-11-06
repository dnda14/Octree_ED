import random
import threading
from tkinter import Tk, Frame, Button, Canvas
from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode, NodePath


class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = TreeNode(value)
        else:
            self._insert_rec(self.root, value)

    def _insert_rec(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
            else:
                self._insert_rec(node.left, value)
        else:
            if node.right is None:
                node.right = TreeNode(value)
            else:
                self._insert_rec(node.right, value)


def draw_tree(canvas, node, x, y, dx, scale_factor, buttons):
    if node is not None:
        
        button = Button(canvas, text=str(node.value), command=lambda: panda_app.change_cube_color(node.value))
        button.place(x=x- 20, y=y * scale_factor , width=40 * scale_factor, height=40 * scale_factor)
        buttons.append(button)  

        if node.left:
            canvas.create_line(x+ 0.0005 * scale_factor, (y +40)* scale_factor, 
                               (x - dx) , (y + 80) * scale_factor)
            draw_tree(canvas, node.left, x - dx, y + 80, dx // 2, scale_factor, buttons)
        if node.right:
            canvas.create_line(x+ 0.0005 * scale_factor , y * scale_factor + 40 * scale_factor, 
                               
                               (x + dx) , (y + 80) * scale_factor)
            draw_tree(canvas, node.right, x + dx, y + 80, dx // 2, scale_factor, buttons)


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.cubes = []  

    def create_cube(self, number):
        """Crea un cubo en Panda3D con el número en cada cara."""
        cube = self.loader.loadModel("models/box")
        cube.setScale(1, 1, 1)
        cube.setPos(len(self.cubes), 0, 0)  
        cube.reparentTo(self.render)

        
        self.add_text_to_cube(cube, number)

        self.cubes.append(cube)  

    def add_text_to_cube(self, cube, number):
        """Añadir texto a cada cara del cubo."""
        for i in range(6):
            text_node = TextNode(f"TextNode-{i}")
            text_node.setText(str(number))
            text_node.setTextColor(1, 1, 1, 1)  

            text_node_path = NodePath(text_node)
            text_node_path.setScale(0.1)  

            
            if i == 0:
                text_node_path.setPos(0, 1, 0)
            elif i == 1:
                text_node_path.setPos(0, -1, 0)
            elif i == 2:
                text_node_path.setPos(-1, 0, 0)
            elif i == 3:
                text_node_path.setPos(1, 0, 0)
            elif i == 4:
                text_node_path.setPos(0, 0, 1)
            elif i == 5:
                text_node_path.setPos(0, 0, -1)

            text_node_path.lookAt(cube)
            text_node_path.reparentTo(cube)

    def change_cube_color(self, number):
        """Cambia el color del cubo correspondiente alternando entre dos colores."""
        index = number - 1
        if 0 <= index < len(self.cubes):
            cube = self.cubes[index]
            current_color = cube.getColor()
            new_color = (random.random(), random.random(), random.random(), 1) if current_color[0] == 1 else (1, 1, 1, 1)
            cube.setColor(new_color)


def create_tkinter_window(panda_app):
    bst = BinarySearchTree()
    scale_factor = 1.0  
    buttons = []  

    def generate_random_number():
        number = random.randint(1, 100)
        bst.insert(number)  
        update_tree_display()  
        panda_app.create_cube(number)  

    def update_tree_display():
        
        canvas.delete("all")
        for button in buttons:
            button.destroy()  
        buttons.clear()  

        
        draw_tree(canvas, bst.root, 800, 40, 300, scale_factor, buttons)

    def zoom(event):
        nonlocal scale_factor
        if event.delta > 0:  
            scale_factor *= 1.1
        else:  
            scale_factor /= 1.1
        update_tree_display()  

    root = Tk()
    root.geometry("1600x400")
    root.title("Binary Search Tree with Zoom")

    frame = Frame(root)
    frame.pack(fill='both', expand=True)

    canvas = Canvas(frame, bg="white")
    canvas.pack(fill='both', expand=True)

    canvas.bind("<MouseWheel>", zoom)  

    button = Button(frame, text="Generate Random Number", command=generate_random_number)
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    panda_app = MyApp()
    threading.Thread(target=create_tkinter_window, args=(panda_app,), daemon=True).start()
    panda_app.run()
