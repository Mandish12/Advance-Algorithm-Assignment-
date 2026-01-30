from collections import defaultdict

hours = [6, 7]

demand = {
    6: {"A": 20, "B": 15, "C": 25},
    7: {"A": 22, "B": 16, "C": 28}
}

sources = {
    "Solar": {
        "capacity": 50,
        "cost": 1.0,
        "available": lambda h: 6 <= h <= 18
    },
    "Hydro": {
        "capacity": 40,
        "cost": 1.5,
        "available": lambda h: True
    },
    "Diesel": {
        "capacity": 60,
        "cost": 3.0,
        "available": lambda h: 17 <= h <= 23
    }
}

results = {}
total_cost = 0
renewable_energy = 0
total_energy = 0
diesel_usage = []

def allocate_hour(hour):
    allocations = defaultdict(lambda: defaultdict(float))
    remaining_demand = demand[hour].copy()
    source_remaining = {}

    for s in sources:
        if sources[s]["available"](hour):
            source_remaining[s] = sources[s]["capacity"]

    sorted_sources = sorted(
        source_remaining.keys(),
        key=lambda s: sources[s]["cost"]
    )

    for s in sorted_sources:
        for d in remaining_demand:
            if remaining_demand[d] <= 0:
                continue
            if source_remaining[s] <= 0:
                continue

            min_needed = 0.9 * demand[hour][d]
            max_allowed = 1.1 * demand[hour][d]

            supply = min(
                remaining_demand[d],
                source_remaining[s],
                max_allowed
            )

            if supply + allocations[d][s] < min_needed:
                supply = min(min_needed, source_remaining[s])

            allocations[d][s] += supply
            remaining_demand[d] -= supply
            source_remaining[s] -= supply

    hour_cost = 0
    hour_renewable = 0
    hour_total = 0

    for d in allocations:
        for s in allocations[d]:
            energy = allocations[d][s]
            hour_cost += energy * sources[s]["cost"]
            hour_total += energy
            if s != "Diesel":
                hour_renewable += energy
            if s == "Diesel" and energy > 0:
                diesel_usage.append((hour, d))

    return allocations, hour_cost, hour_renewable, hour_total

dp = {}

for h in hours:
    alloc, cost, ren, tot = allocate_hour(h)
    dp[h] = cost + (dp[h - 1] if h - 1 in dp else 0)
    results[h] = alloc
    total_cost += cost
    renewable_energy += ren
    total_energy += tot

print("\nENERGY DISTRIBUTION RESULT\n")

for h in results:
    print(f"Hour {h}")
    for d in demand[h]:
        supplied = sum(results[h][d].values())
        percent = (supplied / demand[h][d]) * 100
        solar = results[h][d].get('Solar', 0)
        hydro = results[h][d].get('Hydro', 0)
        diesel = results[h][d].get('Diesel', 0)
        print(
            f" District {d} | "
            f"Solar: {solar:.1f} "
            f"Hydro: {hydro:.1f} "
            f"Diesel: {diesel:.1f} | "
            f"Demand: {demand[h][d]} | "
            f"Supplied: {supplied:.1f} | "
            f"Fulfilled: {percent:.2f}%"
        )
    print()

renewable_percentage = (renewable_energy / total_energy) * 100

print("ANALYSIS REPORT\n")
print(f"Total Cost: Rs. {total_cost:.2f}")
print(f"Renewable Energy Usage: {renewable_percentage:.2f}%")

if diesel_usage:
    print("Diesel Used In:")
    for h, d in diesel_usage:
        print(f" Hour {h}, District {d}")
else:
    print("No Diesel Usage")

print("\nAlgorithm Complexity:")
print(" Time: O(H × S × D)")
print(" Space: O(H)")
