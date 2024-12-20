import random as rn
import numpy as np
from numpy.random import choice as np_choice
import queue

class ACO(object):

    def __init__(self, distances, points, n_ants, n_best, n_iterations, decay, alpha, beta):
        """
        Args:
            distances (2D numpy.array): Square matrix of distances. Diagonal is assumed to be np.inf.
            points (list of lists): List that contains the lists with information about the points [x, y, name]. Used only to normalize the display after the iteration as NumPy DataTypes change the values.
            n_ants (int): Number of ants running per iteration
            n_best (int): Number of best ants who deposit pheromone
            n_iteration (int): Number of iterations
            decay (float): Rate it which pheromone decays. The pheromone value is multiplied by decay, so 0.95 will lead to decay, 0.5 to much faster decay.
            alpha (int or float): exponenet on pheromone, higher alpha gives pheromone more weight. Default=1
            beta (int or float): exponent on distance, higher beta give distance more weight. Default=1

        Example:
            ant_colony = AntColony(german_distances, 100, 20, 2000, 0.95, alpha=1, beta=2)
        """
        self.distances  = distances
        self.points = points
        self.pheromone = np.ones(self.distances.shape) / len(distances)
        self.all_inds = range(len(distances))
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta

    def run(self, guiQueue: queue.Queue):
        shortest_path = None
        all_time_shortest_path = ("placeholder", np.inf)
        for i in range(self.n_iterations):
            all_paths = self.gen_all_paths()
            self.spread_pheronome(all_paths, self.n_best, shortest_path=shortest_path)
            shortest_path = min(all_paths, key=lambda x: x[1])

            # Convert indices to meaningful output for shortest_path
            path_indices = shortest_path[0]
            total_distance = shortest_path[1]

            # Create readable path output
            path_data = {"points": [], "distances": []}
            for (a, b) in path_indices:
                if self.points[a] not in path_data["points"]:
                    path_data["points"].append(self.points[a])  # Full point info for plotting
                path_data["points"].append(self.points[b])
                path_data["distances"].append(float(self.distances[a, b]))

            print(f"Iteration {i + 1}: Shortest Path so far:")
            print(f"Points: {path_data['points']}")
            print(f"Distances: {path_data['distances']}")
            print(f"Total distance: {total_distance:.2f}\n")

            # Update all-time shortest path
            if total_distance < all_time_shortest_path[1]:
                guiQueue.put(path_data['points'])
                all_time_shortest_path = shortest_path

            self.pheromone = self.pheromone * self.decay

        # Final shortest path
        return all_time_shortest_path

    def spread_pheronome(self, all_paths, n_best, shortest_path):
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        for path, dist in sorted_paths[:n_best]:
            for move in path:
                self.pheromone[move] += 1.0 / self.distances[move]

    def gen_path_dist(self, path):
        total_dist = 0
        for ele in path:
            total_dist += self.distances[ele]
        return total_dist

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            path = self.gen_path(0)
            all_paths.append((path, self.gen_path_dist(path)))
        return all_paths

    def gen_path(self, start):
        path = []
        visited = set()
        visited.add(start)
        prev = start
        for i in range(len(self.distances) - 1):
            move = self.pick_move(self.pheromone[prev], self.distances[prev], visited)
            path.append((prev, move))
            prev = move
            visited.add(move)
        path.append((prev, start)) # going back to where we started
        return path

    def pick_move(self, pheromone, dist, visited):
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0

        row = pheromone ** self.alpha * (( 1.0 / dist) ** self.beta)

        norm_row = row / row.sum()
        move = np_choice(self.all_inds, 1, p=norm_row)[0]
        return move