
import heapq


def shortest_path(graph, start, destination, blocked_links=None):
    """Find the lowest-cost available route."""

    blocked_links = blocked_links or set()
    distances = {node: float("inf") for node in graph}
    previous = {}

    distances[start] = 0
    queue = [(0, start)]

    while queue:
        cost, node = heapq.heappop(queue)

        if cost > distances[node]:
            continue

        if node == destination:
            break

        for neighbour, link_cost in graph[node].items():
            link = frozenset((node, neighbour))

            if link in blocked_links:
                continue

            new_cost = cost + link_cost

            if new_cost < distances[neighbour]:
                distances[neighbour] = new_cost
                previous[neighbour] = node
                heapq.heappush(queue, (new_cost, neighbour))

    if distances[destination] == float("inf"):
        return None, float("inf")

    path = []
    node = destination

    while node != start:
        path.append(node)
        node = previous[node]

    path.append(start)
    path.reverse()

    return path, distances[destination]


def simulate_disruption():
    graph = {
        "Earth": {"Relay-A": 2, "Relay-B": 3},
        "Relay-A": {"Earth": 2, "Target": 2, "Relay-C": 3},
        "Relay-B": {"Earth": 3, "Relay-C": 1},
        "Relay-C": {"Relay-A": 3, "Relay-B": 1, "Target": 2},
        "Target": {"Relay-A": 2, "Relay-C": 2},
    }

    print("EXOPLANET HUNTER: ADAPTIVE ROUTING")
    print("=" * 40)

    path, cost = shortest_path(graph, "Earth", "Target")
    print("Initial route:", " -> ".join(path))
    print("Initial route cost:", cost)

    blocked = {frozenset(("Earth", "Relay-A"))}

    print("\nALERT: Communication link disrupted!")
    print("Blocked link: Earth <-> Relay-A")
    print("Recalculating route...")

    new_path, new_cost = shortest_path(
        graph, "Earth", "Target", blocked
    )

    if new_path:
        print("Alternative route:", " -> ".join(new_path))
        print("Alternative route cost:", new_cost)
        print("STATUS: Communication route restored in simulation.")
    else:
        print("STATUS: No available route. Communication unavailable.")

    # TEST 2: Block every communication link leaving Earth.
    print("\nTEST 2: All routes blocked")

    all_blocked = {
        frozenset(("Earth", "Relay-A")),
        frozenset(("Earth", "Relay-B")),
    }

    path, cost = shortest_path(
        graph, "Earth", "Target", all_blocked
    )

    if path is None:
        print("PASS: No route found, as expected.")
    else:
        print("FAIL: Unexpected route:", " -> ".join(path))


if __name__ == "__main__":
    simulate_disruption()
