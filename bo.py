from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import copy
import sympy
import random


def func(args):
    # [0; pi], [-pi; pi] - область определения
    f = -np.sin(args[0]) * np.sin(args[0] ** 2/np.pi)
    for i in range(1, len(args)):
        f += -np.sin(args[i]) * np.sin((i + 1) * args[i] ** 2/np.pi)
    return f

def func2(x, y):
    return (x * x + y * y)**0.5 + 3 * np.cos((x * x + y * y)**0.5) + 5

def makeData(minimum_num, maximum_num):
    # Создаем двумерную матрицу-сетку
    
    # В узлах рассчитываем значение функции
    #zgrid = -np.sin (xgrid) * np.sin (ygrid) / (xgrid * ygrid)
    zgrid = (xgrid * xgrid + ygrid * ygrid)**0.5 + 3 * np.cos((xgrid * xgrid + ygrid * ygrid)**0.5) + 5
    return xgrid, ygrid, zgrid

def generate_vector(min_length=-1, max_length=1, problem_size=3):
    size = problem_size - 1
    vec = np.random.uniform(min_length, max_length, size)
    return vec

def draw_graphics(cells_coord, minimum_num, maximum_num):
    try:
        fig = plt.figure()
        ax = Axes3D(fig)
        x = np.arange(minimum_num, maximum_num, 0.1)
        y = np.arange(minimum_num, maximum_num, 0.1)
        xgrid, ygrid = np.meshgrid(x, y)
        zgrid = func([xgrid, ygrid])
        ax.plot_surface(xgrid, ygrid, zgrid, cmap = cm.Pastel1)
        for cell in cells_coord:
            ax.scatter(cell[0], cell[1], cell[2], s=40, c='0.1')
        ax.legend()
        plt.show()
    except:
        print("Error")

class Cell(object):
    """docstring for Cell"""
    def __init__(self, d_attr, w_attr, h_rep, w_rep):
        self.coord = None
        self.vector = None
        self.d_attr = d_attr
        self.w_attr = w_attr
        self.h_rep = h_rep
        self.w_rep = w_rep
        self.fitness = 0
        self.interaction = 0
        #self.search_space = search_space
    
    def initialize_coord(self,problem_size, min_num, max_num, func):
        """
        limit = x_min, x_max, y_min....
        """
        size = problem_size - 1
        xy = np.random.uniform(min_num, max_num, size)
        z = func(xy)
        self.coord = np.hstack((xy, z))
        return self.coord

    def compute_cell_interaction(self, cells):
        for j in range(len(cells)):
            self.interaction += (-self.d_attr * np.exp(-self.w_attr * np.sum((self.coord - cells[j].coord) ** 2))) + (
                self.h_rep * np.exp(-self.w_rep * np.sum((self.coord - cells[j].coord) ** 2)))
        return self.interaction

    def tumble(self, step_size, vec, func):
        crd = []
        crd = self.coord[:-1] + step_size * vec
        crd = np.append(crd, func(crd[:-1]))
        self.coord = copy.copy(crd)


    def swim(self, step_size, func):
        vec = generate_vector()
        crd = []
        crd = self.coord[:-1] + step_size * vec
        crd = np.append(crd, func(crd[:-1]))

    def calculate_fitness(self):
        self.fitness = self.coord[-1] + self.interaction
        return self.fitness

    def __lt__(self, other):
        return self.coord[-1] < other.coord[-1]

def compute_cell_interaction(cells, problem_size, d_attr, w_attr, h_rep, w_rep):
    """ A bacteria cost is derated by its interaction with other cells. This function is calculated interaction
    """
    #for i in range(cells.shape[0] - 1)
    g = np.zeros(len(cells))
    for i in range(len(g)):
        cells_array = np.vstack((cells[:i], cells[i + 1:]))
        for j in range(cells_array.shape[0]):
            g[i] += (-d_attr * np.exp(-w_attr * np.sum((cells[i][:problem_size] - cells_array[j][:problem_size]) ** 2))) + (h_rep * np.exp(-w_rep * np.sum((cells[i][:problem_size] - cells_array[j][:problem_size]) ** 2)))
    return g

def chemotaxis(cells, chem_steps, swim_length, step_size,
                d_attr, w_attr, h_rep, w_rep, problem_size):
    best_cell = None
    for cs in range(chem_steps):
        sum_nutrients = 0
        for i in range(len(cells)):
            cells[i].compute_cell_interaction(cells)
            if best_cell == None or best_cell > cells[i].coord[-1]:
                best_cell = cells[i].coord[-1] 
                number_cell = i
            #print('best=', best_cell)
            sum_nutrients += cells[i].calculate_fitness()
            vec = generate_vector(problem_size=problem_size)
            for sl in range(swim_length):
                new_cell = Cell(d_attr, w_attr, h_rep, w_rep)
                new_cell.coord = np.array(cells[i].coord)
                new_cell.tumble(step_size, vec, func)
                cells_array = cells[:i] + cells[i + 1:]
                new_cell.compute_cell_interaction(cells_array)
                if new_cell.calculate_fitness() <= best_cell:
                    cells[i] = copy.copy(new_cell)
                    del new_cell
                    sum_nutrients += cells[i].fitness
                else:
                    break
            cells[i].interaction = sum_nutrients
        print('chemo={}, f={}, cost={}'.format(cs, best_cell, number_cell))
    return best_cell, cells, number_cell

def search_optimum(problem_size, cells_num, N_ed, N_re, N_c, N_s, 
    d_attract, w_attract, h_repellant, w_repellant, P_ed,
    step_size, min_num=-10, max_num=10):
    """ p: Dimension of the search space,
         S: Total number of bacteria in the population,
         Nc : The number of chemotactic steps,
         Ns : The swimming length.
         Nre : The number of reproduction steps,
         Ned : The number of elimination-dispersal events,
         Ped : Elimination-dispersal probability,
         C (i): The size of the step taken in the random direc
    """
    cells = []
    for i in range(cells_num):
        cells.append(Cell(d_attract, w_attract, h_repellant, w_repellant))
        cells[i].initialize_coord(problem_size, min_num, max_num, func)
    best = None
    for ed in range(N_ed):
        for re in range(N_re):
            c_best, cells, number_cell = chemotaxis(cells, N_c, N_s, step_size, d_attract, w_attract, h_repellant, w_repellant, problem_size)
            if best == None or best > c_best:
                best = c_best
            print('best fitness = {}, coord = {}'.format(best, cells[number_cell].coord))

            #sort
            #fck
            cells.sort()
            cells = cells[:round(len(cells)/2)] + cells[:round(len(cells)/2)]
        for i in range(len(cells)):
            if random.random() < P_ed:
                cells[i].initialize_coord

if __name__ == '__main__':

    #default coefficients
    number_cells = 50
    d_attr = 0.1
    w_attr = 0.2
    h_repell = 0.1 # h_repell = d_attr
    w_repell = 10
    step_size = 0.1 #C[i]
    elim_disp_steps = 1 # Ned is the number of elimination-dispersal steps
    repro_steps = 4 # Nre is the number of reproduction steps
    chem_steps = 30 # Nc is the number of chemotaxis steps
    swim_length = 4 # Ns is the number of swim steps for a given cell
    p_eliminate = 0.25 # Ped

    #The step size is commonly a small fraction of the search space, such as 0.1.
    #for i in range(cells_init.shape[0]):
    # print('cost = ', compute_cell_interaction(cells_init, 3, d_attr, w_attr, h_repell, w_repell))
    #cells_array = np.vstack((cells_init[:3], cells_init[3 + 1:]))
    #step_limit = np.array([-5, 5])
    #print(tumble(np.array([-1.0, 1.0, 0.5]), np.array([-0.9, -0.9, 1.1]), 0.9, np.array([-10.0, 10.0])))
    # ax.legend()
    # plt.show()
    search_space =  [[-10, 10], [-10, 10]]
    problem_size = 3


    my_cell = []
    for i in range(number_cells):
        my_cell.append(Cell(d_attr, w_attr, h_repell, w_repell))
        my_cell[i].initialize_coord(problem_size, -5, 5, func)
    cells = np.array(my_cell)
    search_optimum(problem_size, number_cells, elim_disp_steps, repro_steps, chem_steps, swim_length,d_attr, w_attr, h_repell, w_repell, p_eliminate, step_size)

