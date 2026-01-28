class Solution:
    def getMinDistSum(self, points):
        import math

        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)

        for _ in range(100):
            num_x = num_y = den = 0.0
            for px, py in points:
                dist = math.hypot(x - px, y - py)
                if dist == 0:
                    continue
                w = 1 / dist
                num_x += px * w
                num_y += py * w
                den += w

            if den == 0:
                break
            x, y = num_x / den, num_y / den

        return sum(math.hypot(x - px, y - py) for px, py in points)


# ✅ Test code MUST be outside the class
points = [[0, 1], [1, 0], [1, 2], [2, 1]]
print(Solution().getMinDistSum(points))
