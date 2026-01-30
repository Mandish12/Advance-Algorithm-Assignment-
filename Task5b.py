import threading
import sys

A = [7, 12, 19, 3, 18, 4, 2, 6, 15, 8]
B = [0] * len(A)

def sort_subarray(start, end):
    A[start:end] = sorted(A[start:end])

def merge(start, mid, end):
    i, j, k = start, mid, start
    while i < mid and j < end:
        if A[i] <= A[j]:
            B[k] = A[i]
            i += 1
        else:
            B[k] = A[j]
            j += 1
        k += 1
    while i < mid:
        B[k] = A[i]
        i += 1
        k += 1
    while j < end:
        B[k] = A[j]
        j += 1
        k += 1

def main():
    n = len(A)
    mid = n // 2
    t1 = threading.Thread(target=sort_subarray, args=(0, mid))
    t2 = threading.Thread(target=sort_subarray, args=(mid, n))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    t3 = threading.Thread(target=merge, args=(0, mid, n))
    t3.start()
    t3.join()
    print(B)
    sys.stdout.flush()

if __name__ == "__main__":
    main()
