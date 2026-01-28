class Solution:
    def maxPoints(self, tile_multipliers):
        n = len(tile_multipliers)

        # Add boundary tiles with multiplier 1
        tiles = [1] + tile_multipliers + [1]

        # DP table
        dp = [[0 for _ in range(n + 2)] for _ in range(n + 2)]

        # Length of the interval
        for length in range(1, n + 1):
            for i in range(1, n - length + 2):
                j = i + length - 1
                for k in range(i, j + 1):
                    dp[i][j] = max(
                        dp[i][j],
                        dp[i][k - 1] +
                        dp[k + 1][j] +
                        tiles[i - 1] * tiles[k] * tiles[j + 1]
                    )

        return dp[1][n]


# 🔽 THIS PART IS IMPORTANT (to run the code)
if __name__ == "__main__":
    tiles = [3, 1, 5, 8]
    sol = Solution()
    print(sol.maxPoints(tiles))  # Expected output: 167
