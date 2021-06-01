import networkx as nx
from mpl_toolkits.mplot3d import Axes3D, proj3d
import matplotlib.pyplot as plt
import numpy as np
import hexagonal_lattice as hl
from matplotlib.patches import FancyArrowPatch


class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)


def generate_initial_plot_positions(lattice):
    pos = {i: (lattice[i].return_coordinates()[0],
               lattice[i].return_coordinates()[1],
               lattice[i].return_coordinates()[2])
           for i in range(0, len(lattice))}
    return pos


def generate_manipulated_plot_positions(dim, lattice, stretch_factor=1, displace_value=1, factor=False, d=1, k=2):
    pos = {}
    if factor:
        list_mobile_coords = hl.run(dim, stretch_factor=stretch_factor, plot=False, d=d, k=k).x
    else:
        list_mobile_coords = hl.run_absolute_displacement(dim, displace_value, plot=False, d=d, k=k).x

    for i in range(0, len(lattice)):
        if lattice[i].return_mobility():
            pos[i] = (list_mobile_coords[0], list_mobile_coords[1], list_mobile_coords[2])

            list_mobile_coords = list_mobile_coords[3:]
        elif not lattice[i].return_mobility():
            vector = lattice[i].return_coordinates()
            pos[i] = (vector[0], vector[1], vector[2])
    return pos


def draw_initial_graph(A, angle, pos, lattice, nodes=False, vectors=False):
    rows, cols = np.where(A == 1)
    edges = zip(rows.tolist(), cols.tolist())
    G = nx.Graph()
    G.add_edges_from(edges)

    with plt.style.context('classic'):
        fig = plt.figure(figsize=(20, 20))
        ax = Axes3D(fig)

        if nodes:
            for key, value in pos.items():
                xi = value[0]
                yi = value[1]
                zi = value[2]
                name = lattice[key].return_name()
                if name[2] == 1:
                    ax.scatter(xi, yi, zi, c='cornflowerblue', edgecolors='k')
                    ax.text(xi+.05, yi+.05, zi, f'({name[0]}{name[1]})')
                else:
                    ax.scatter(xi, yi, zi, c='red', edgecolors='k')
                    ax.text(xi+.05, yi+.05, zi, f'({name[0]}{name[1]})')
                if vectors:
                    ax.plot((0, 1), (0, 0), (0, 0), lw=5, c='cyan')
                    ax.text(.4, -.25, 0, 'd', size=20, c='cyan')
                    ax.text(-.4, -.25, 0, '\u03B4', size=20, c='pink')
                    ax.text(-.85, .7, 0, 'a2', c='gold', size=20)
                    ax.text(.75, .7, 0, 'a1', c='gold', size=20)
                    delta = Arrow3D([0, 0], [0, -1/3**.5],
                                [0, 0], mutation_scale=20,
                                lw=3, arrowstyle="-|>", color="pink")
                    a1 = Arrow3D([0, .5], [0, .5 * 3 ** .5],
                                    [0, 0], mutation_scale=20,
                                    lw=3, arrowstyle="-|>", color="gold")
                    a2 = Arrow3D([0, -.5], [0, .5 * 3 ** .5],
                                    [0, 0], mutation_scale=20,
                                    lw=3, arrowstyle="-|>", color="gold")
                    ax.add_artist(delta)
                    ax.add_artist(a1)
                    ax.add_artist(a2)
        #ax.set_zlim3d(0, d*dim/2)
        #ax.set_xlim3d(-4.5, 4.5)
        #ax.set_ylim3d(-4.5, 4.5)

        for i, j in enumerate(G.edges()):
            x = np.array((pos[j[0]][0], pos[j[1]][0]))
            y = np.array((pos[j[0]][1], pos[j[1]][1]))
            z = np.array((pos[j[0]][2], pos[j[1]][2]))

            # Plot the connecting lines
            ax.plot(x, y, z, c='black', alpha=0.5)

    # Set the initial view
    # 90
    ax.view_init(13, angle)
    # Hide the axes
    #ax.set_axis_off()
    ax.set_xlabel('x', fontsize=15)
    ax.set_ylabel('y', fontsize=15)
    ax.set_zlabel('z', fontsize=15)

    plt.show()


def plot_graph(dim, stretch_factor=1, displace_value=1, factor=False, d=1, k=2, nodes=False):
    ls = hl.create_lattice(dim, d)
    l = ls[0]
    l = hl.manipulate_lattice_absolute_value(l, ls[1], displace_value=displace_value)
    matrices = hl.adjacency_matrix(l)
    A = np.add(matrices[0], matrices[1])

    draw_initial_graph(A, 22, generate_manipulated_plot_positions(dim, l,
                                                                  stretch_factor=stretch_factor,
                                                                  displace_value=displace_value, factor=factor,
                                                                  d=d, k=k), l, nodes=nodes)


plot_graph(27, displace_value=1)

lattice = hl.create_lattice(6)[0]
matrices = hl.adjacency_matrix(lattice)
A = np.add(matrices[0], matrices[1])

#draw_initial_graph(A, -90, generate_initial_plot_positions(lattice), lattice, True, True)
