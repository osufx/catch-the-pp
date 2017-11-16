def Cpn(p, n):
    if p < 0 or p > n:
        return 0
    p = min(p, n - p)
    out = 1
    for i in range(1, p + 1):
        out = out * (n - p + i) / i
    
    return out