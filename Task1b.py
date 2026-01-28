import random
import math

# -------------------------------
# 1️⃣ Generate TSP Cities
# -------------------------------
def generate_cities(n, limit=1000):
    """
    Generate n cities with random 2D coordinates.
    """
    return [(random.uniform(0, limit), random.uniform(0, limit)) for _ in range(n)]

# -------------------------------
# 2️⃣ Euclidean Distance
# -------------------------------
def distance(a, b):
    """
    Euclidean distance between points a and b.
    """
    return math.hypot(a[0] - b[0], a[1] - b[1])

# -------------------------------
# 3️⃣ Total Tour Distance
# -------------------------------
def tour_length(tour, cities):
    """
    Calculate total distance of a tour (including return to start).
    """
    total = 0
    for i in range(len(tour)):
        total += distance(cities[tour[i]], cities[tour[(i + 1) % len(tour)]])
    return total

# -------------------------------
# 4️⃣ Neighborhood Operators
# -------------------------------
def swap(tour):
    """
    Swap two random cities in the tour.
    """
    a, b = random.sample(range(len(tour)), 2)
    tour[a], tour[b] = tour[b], tour[a]

def two_opt(tour):
    """
    Reverse a segment of the tour.
    """
    a, b = sorted(random.sample(range(len(tour)), 2))
    tour[a:b] = reversed(tour[a:b])

# -------------------------------
# 5️⃣ Simulated Annealing
# -------------------------------
def simulated_annealing(
    cities,
    initial_temp=1000,
    max_iter=50000,
    cooling="exponential",
    alpha=0.995,
    beta=0.01,
    min_temp=1e-3
):
    """
    Approximate TSP solution using Simulated Annealing.
    """
    n = len(cities)
    current = list(range(n))
    random.shuffle(current)

    best = current[:]
    current_cost = tour_length(current, cities)
    best_cost = current_cost

    T = initial_temp

    for k in range(max_iter):
        if T < min_temp:
            break

        neighbor = current[:]

        # Choose neighborhood
        if random.random() < 0.5:
            swap(neighbor)
        else:
            two_opt(neighbor)

        neighbor_cost = tour_length(neighbor, cities)
        delta = neighbor_cost - current_cost

        # Acceptance probability
        if delta < 0 or random.random() < math.exp(-delta / T):
            current = neighbor
            current_cost = neighbor_cost

            if current_cost < best_cost:
                best = current[:]
                best_cost = current_cost

        # Cooling schedule
        if cooling == "exponential":
            T *= alpha
        else:  # linear
            T -= beta

    return best_cost

# -------------------------------
# 6️⃣ Run Experiment
# -------------------------------
if __name__ == "__main__":
    # Number of cities
    N = 30
    cities = generate_cities(N)

    # Exponential cooling
    cost_exp = simulated_annealing(
        cities,
        cooling="exponential",
        alpha=0.995
    )

    # Linear cooling
    cost_lin = simulated_annealing(
        cities,
        cooling="linear",
        beta=0.01
    )

    print("Exponential Cooling Cost:", round(cost_exp, 2))
    print("Linear Cooling Cost:", round(cost_lin, 2))
