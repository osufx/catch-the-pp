def Cpn(p, n):
    if p < 0 or p > n:
        return 0
    p = min(p, n - p)
    out = 1
    for i in range(1, p + 1):
        out = out * (n - p + i) / i
    
    return out

def Array_calc(o, a0, a1):
    m = min(len(a0), len(a1))
    r = []

    for i in range(m):
        r.append(a0[i] + o * a1[i])
    
    return r