# -------------------------------
# 1️⃣ Definition of TreeNode
# -------------------------------
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# -------------------------------
# 2️⃣ Helper to build tree from list (like LeetCode)
# -------------------------------
from collections import deque

def build_tree(nodes):
    """
    Build a binary tree from a list.
    None represents missing nodes.
    """
    if not nodes or nodes[0] is None:
        return None

    root = TreeNode(nodes[0])
    queue = deque([root])
    index = 1

    while queue and index < len(nodes):
        node = queue.popleft()

        # left child
        if index < len(nodes) and nodes[index] is not None:
            node.left = TreeNode(nodes[index])
            queue.append(node.left)
        index += 1

        # right child
        if index < len(nodes) and nodes[index] is not None:
            node.right = TreeNode(nodes[index])
            queue.append(node.right)
        index += 1

    return root

# -------------------------------
# 3️⃣ Solution using 3-state DP
# -------------------------------
class Solution:
    def minCameraCover(self, root: TreeNode) -> int:
        def dfs(node):
            """
            Returns a tuple (s0, s1, s2):
            s0 = min cameras if children covered but node not
            s1 = min cameras if node covered, no camera at node
            s2 = min cameras if node covered, camera at node
            """
            if not node:
                return (0, 0, float('inf'))

            l = dfs(node.left)
            r = dfs(node.right)

            # Node not covered, children covered
            s0 = l[1] + r[1]

            # Node covered, no camera here
            s1 = min(l[2] + min(r[1], r[2]),
                     r[2] + min(l[1], l[2]))

            # Camera at this node
            s2 = 1 + min(l) + min(r)

            return (s0, s1, s2)

        res = dfs(root)
        return min(res[1], res[2])

# -------------------------------
# 4️⃣ Example Test Case
# -------------------------------
if __name__ == "__main__":
    # Input: [0,0,None,0,None,0,None,None,0]
    nodes = [0,0,None,0,None,0,None,None,0]
    root = build_tree(nodes)

    sol = Solution()
    print("Minimum number of service centers:", sol.minCameraCover(root))
    # Expected Output: 2
