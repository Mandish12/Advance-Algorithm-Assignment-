
# 🚀 Advanced Algorithms Coursework

**Module:** ST5003CEM – Advanced Algorithms
**Student:** Mandish Sen
**Institution:** Softwarica College of IT & E-Commerce (Coventry University)
**Language:** Python
**Focus:** Algorithm Design · Optimization · Correctness · Real-World Modeling

---

## 🧠 Design Philosophy

This coursework follows a structured algorithmic discipline:

> **Problem Modeling → Algorithm Selection → Proof of Correctness → Complexity Analysis → Trade-off Discussion**

Each solution is:

* Algorithmically efficient
* Scalable
* Defensible in examination
* Mapped to real-world systems

---

# 📌 QUESTION 1(a)

## Optimizing Sensor Placement (Geometric Optimization)

### Problem

Find a hub position minimizing total Euclidean distance to all sensors.

### Algorithm

**Geometric Median Optimization** minimizes the sum of distances, unlike the centroid which minimizes squared distances.

### Diagram

```mermaid
graph TD
    S1((Sensor))
    S2((Sensor))
    S3((Sensor))
    S4((Sensor))
    H[Optimal Hub]

    S1 --> H
    S2 --> H
    S3 --> H
    S4 --> H
```

### Correctness

* Objective is convex → global minimum guaranteed

### Complexity

* Time: Iterative convergence
* Space: O(1)

---

# 📌 QUESTION 1(b)

## Traveling Salesperson Problem (Simulated Annealing)

### Reasoning

TSP is NP-Hard → exact solutions do not scale. Simulated Annealing allows:

* Controlled randomness
* Escaping local minima
* Near-optimal solutions

### State Transition

```mermaid
flowchart LR
    A[Current Tour]
    B[Neighbor Tour]
    C{Accept?}
    D[Update State]
    E[Reject]

    A --> B --> C
    C -->|Yes| D
    C -->|No| E
```

### Complexity

* Time: O(iterations × N)
* Space: O(N)

---

# 📌 QUESTION 2

## Strategic Tile Shatter (Dynamic Programming)

### Insight

Equivalent to **Burst Balloons** problem. Choose the **last tile to shatter** for optimal substructure.

### DP Table Growth

```mermaid
flowchart TB
    dp00 --> dp01 --> dp02 --> dp03
    dp11 --> dp12 --> dp13
    dp22 --> dp23
    dp33
```

### Complexity

* Time: O(n³)
* Space: O(n²)

---

# 📌 QUESTION 3

## Minimum Service Centers in a Tree

### Problem Type

Tree coverage optimization using DFS.

### Node States

* Needs coverage
* Covered
* Has service center

### Tree Example

```mermaid
graph TD
    A((City))
    B((City))
    C((City))
    D((City))
    E((City))

    A --> B
    A --> C
    B --> D
    B --> E
```

### Complexity

* Time: O(n)
* Space: O(height)

---

# 📌 QUESTION 4

## Smart Energy Grid Load Optimization (Nepal)

### Real-World Model

Energy sources:

* Solar (cheap, limited hours)
* Hydro (moderate, always available)
* Diesel (expensive, fallback)

### Algorithm

* Dynamic Programming across hours
* Greedy allocation within each hour

### Allocation Flow

```mermaid
flowchart TD
    H[Hourly Demand]
    S[Solar]
    Hy[Hydro]
    D[Diesel]

    H --> S --> Hy --> D
```

### Objectives

* Minimize cost
* Maximize renewables
* Reduce diesel usage
* Allow ±10% flexibility

### Complexity

* Time: O(H × S × D)
* Space: O(H)

---

# 📌 QUESTION 5(a)

## Interactive Emergency Network Simulator (GUI)

### System Components

* Graph-based city network
* Tree-based command hierarchy
* Real-time algorithm visualization

### System Architecture

```mermaid
graph TD
    GUI[GUI Interface]
    Graph[Graph Algorithms]
    Tree[Command Tree]
    MST[MST / Paths]
    Fail[Failure Simulation]

    GUI --> Graph
    GUI --> Tree
    Graph --> MST
    Graph --> Fail
```

### Algorithms Used

* Kruskal / Prim (MST)
* BFS / DFS / A*
* Tree Rebalancing
* Rerouting after failures

---

# 📌 QUESTION 5(b)

## Multithreaded Sorting Application

### Thread Architecture

```mermaid
flowchart LR
    A[Unsorted Array]
    T1[Sort Thread 1]
    T2[Sort Thread 2]
    M[Merge Thread]
    S[Sorted Output]

    A --> T1
    A --> T2
    T1 --> M
    T2 --> M
    M --> S
```

### Key Concepts

* Shared memory
* Thread synchronization
* Race-free design

### Complexity

* Sorting: O(n log n)
* Merge: O(n)

---

# 📌 QUESTION 6

## Robot Navigation & Search Algorithms

### State Space Model

```mermaid
graph LR
    Start --> A --> B --> Goal
    A --> C --> Goal
```

### DFS vs BFS

| Algorithm | Strength      | Weakness    |
| --------- | ------------- | ----------- |
| DFS       | Low memory    | Not optimal |
| BFS       | Shortest path | High memory |

### A* Search

**Heuristic:** Straight-line (Euclidean) distance to goal

```mermaid
flowchart TD
    S[Start]
    O[Open List]
    C[Closed List]
    G[Goal]

    S --> O
    O --> C
    C --> O
    O --> G
```

**Advantage:** Optimal + efficient when heuristic is admissible

---

## 🎓 Takeaway

Each problem is solved by identifying its computational structure and applying the most appropriate algorithmic paradigm, supported by correctness arguments and complexity analysis.

---

## ✅ Repository Highlights

* Advanced algorithmic thinking
* Strong modeling skills
* Real-world system optimization
* Clear, examination-ready explanations
* Professional presentation



Do you want me to   `
