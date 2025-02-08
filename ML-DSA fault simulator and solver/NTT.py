import params
import random
import numpy as np

# The zetas used in the NTT algorithm zeta^bitrev8(i), zeta=1753
zetas=[0, 4808194, 3765607, 3761513, 5178923, 5496691, 5234739, 5178987,
7778734, 3542485, 2682288, 2129892, 3764867, 7375178, 557458, 7159240,
5010068, 4317364, 2663378, 6705802, 4855975, 7946292, 676590, 7044481,
5152541, 1714295, 2453983, 1460718, 7737789, 4795319, 2815639, 2283733,
3602218, 3182878, 2740543, 4793971, 5269599, 2101410, 3704823, 1159875,
394148, 928749, 1095468, 4874037, 2071829, 4361428, 3241972, 2156050,
3415069, 1759347, 7562881, 4805951, 3756790, 6444618, 6663429, 4430364,
5483103, 3192354, 556856, 3870317, 2917338, 1853806, 3345963, 1858416,
3073009, 1277625, 5744944, 3852015, 4183372, 5157610, 5258977, 8106357,
2508980, 2028118, 1937570, 4564692, 2811291, 5396636, 7270901, 4158088,
1528066, 482649, 1148858, 5418153, 7814814, 169688, 2462444, 5046034,
4213992, 4892034, 1987814, 5183169, 1736313, 235407, 5130263, 3258457,
5801164, 1787943, 5989328, 6125690, 3482206, 4197502, 7080401, 6018354,
7062739, 2461387, 3035980, 621164, 3901472, 7153756, 2925816, 3374250,
1356448, 5604662, 2683270, 5601629, 4912752, 2312838, 7727142, 7921254,
348812, 8052569, 1011223, 6026202, 4561790, 6458164, 6143691, 1744507,
1753, 6444997, 5720892, 6924527, 2660408, 6600190, 8321269, 2772600,
1182243, 87208, 636927, 4415111, 4423672, 6084020, 5095502, 4663471,
8352605, 822541, 1009365, 5926272, 6400920, 1596822, 4423473, 4620952,
6695264, 4969849, 2678278, 4611469, 4829411, 635956, 8129971, 5925040,
4234153, 6607829, 2192938, 6653329, 2387513, 4768667, 8111961, 5199961,
3747250, 2296099, 1239911, 4541938, 3195676, 2642980, 1254190, 8368000,
2998219, 141835, 8291116, 2513018, 7025525, 613238, 7070156, 6161950,
7921677, 6458423, 4040196, 4908348, 2039144, 6500539, 7561656, 6201452,
6757063, 2105286, 6006015, 6346610, 586241, 7200804, 527981, 5637006,
6903432, 1994046, 2491325, 6987258, 507927, 7192532, 7655613, 6545891,
5346675, 8041997, 2647994, 3009748, 5767564, 4148469, 749577, 4357667,
3980599, 2569011, 6764887, 1723229, 1665318, 2028038, 1163598, 5011144,
3994671, 8368538, 7009900, 3020393, 3363542, 214880, 545376, 7609976,
3105558, 7277073, 508145, 7826699, 860144, 3430436, 140244, 6866265,
6195333, 3123762, 2358373, 6187330, 5365997, 6663603, 2926054, 7987710,
8077412, 3531229, 4405932, 4606686, 1900052, 7598542, 1054478, 7648983]

# Computes the NTT.
# Input: Polynomial 𝑤(𝑋) = ∑255 𝑗=0 𝑤𝑗𝑋𝑗 ∈ 𝑅𝑞.
# Output: 𝑤̂ ̂ = (𝑤[0], … , 𝑤[255]) ̂ ∈ 𝑇𝑞.
def NTT(w):
    w_hat=w[:]
    m=0
    len=params.MLDSA_N//2
    while len>=1:
        start=0
        while start<params.MLDSA_N:
            m+=1
            z=zetas[m]
            for j in range(start,start+len):
                t=(z*w_hat[j+len])%params.MLDSA_Q
                w_hat[j+len]=(w_hat[j]-t)%params.MLDSA_Q
                w_hat[j]=(w_hat[j]+t)%params.MLDSA_Q
            start+=len*2
        len//=2
    return w_hat


# Computes the inverse of the NTT.
# Input: 𝑤̂ ̂ = (𝑤[0], … , 𝑤[255]) ̂ ∈ 𝑇𝑞.
# Output: Polynomial 𝑤(𝑋) = ∑255𝑗=0 𝑤𝑗𝑋𝑗 ∈ 𝑅𝑞.
def iNTT(w_hat):
    w=w_hat[:]
    m=params.MLDSA_N
    len=1
    while len<params.MLDSA_N:
        start=0
        while start<params.MLDSA_N:
            m-=1
            z=-zetas[m]
            for j in range(start,start+len):
                t=w[j]
                w[j]=(w[j+len]+t)%params.MLDSA_Q
                w[j+len]=(t-w[j+len])%params.MLDSA_Q
                w[j+len]=(w[j+len]*z)%params.MLDSA_Q
            start+=len*2
        len*=2
    f=8347681
    for i in range(params.MLDSA_N):
        w[i]=(w[i]*f)%params.MLDSA_Q
    return w


# The Montgomery version of the NTT algorithm
zetas_montgomery=[0,    25847, -2608894, -518909,   237124, -777960, -876248,   466468,
    1826347,  2353451, -359251, -2091905,  3119733, -2884855,  3111497,  2680103,
    2725464,  1024112, -1079900,  3585928, -549488, -1119584,  2619752, -2108549,
    -2118186, -3859737, -1399561, -3277672,  1757237, -19422,  4010497,   280005,
    2706023,    95776,  3077325,  3530437, -1661693, -3592148, -2537516,  3915439,
    -3861115, -3043716,  3574422, -2867647,  3539968, -300467,  2348700, -539299,
    -1699267, -1643818,  3505694, -3821735,  3507263, -2140649, -1600420,  3699596,
    811944,   531354,   954230,  3881043,  3900724, -2556880,  2071892, -2797779,
    -3930395, -1528703, -3677745, -3041255, -1452451,  3475950,  2176455, -1585221,
    -1257611,  1939314, -4083598, -1000202, -3190144, -3157330, -3632928,   126922,
    3412210, -983419,  2147896,  2715295, -2967645, -3693493, -411027, -2477047,
    -671102, -1228525, -22981, -1308169, -381987,  1349076,  1852771, -1430430,
    -3343383,   264944,   508951,  3097992,    44288, -1100098,   904516,  3958618,
    -3724342, -8578,  1653064, -3249728,  2389356, -210977,   759969, -1316856,
    189548, -3553272,  3159746, -1851402, -2409325, -177440,  1315589,  1341330,
    1285669, -1584928, -812732, -1439742, -3019102, -3881060, -3628969,  3839961,
    2091667,  3407706,  2316500,  3817976, -3342478,  2244091, -2446433, -3562462,
    266997,  2434439, -1235728,  3513181, -3520352, -3759364, -1197226, -3193378,
    900702,  1859098,   909542,   819034,   495491, -1613174, -43260, -522500,
    -655327, -3122442,  2031748,  3207046, -3556995, -525098, -768622, -3595838,
    342297,   286988, -2437823,  4108315,  3437287, -3342277,  1735879,   203044,
    2842341,  2691481, -2590150,  1265009,  4055324,  1247620,  2486353,  1595974,
    -3767016,  1250494,  2635921, -3548272, -2994039,  1869119,  1903435, -1050970,
    -1333058,  1237275, -3318210, -1430225, -451100,  1312455,  3306115, -1962642,
    -1279661,  1917081, -2546312, -1374803,  1500165,   777191,  2235880,  3406031,
    -542412, -2831860, -1671176, -1846953, -2584293, -3724270,   594136, -3776993,
    -2013608,  2432395,  2454455, -164721,  1957272,  3369112,   185531, -1207385,
    -3183426,   162844,  1616392,  3014001,   810149,  1652634, -3694233, -1799107,
    -3038916,  3523897,  3866901,   269760,  2213111, -975884,  1717735,   472078,
    -426683,  1723600, -1803090,  1910376, -1667432, -1104333, -260646, -3833893,
    -2939036, -2235985, -420899, -2286327,   183443, -976891,  1612842, -3545687,
    -554416,  3919660, -48306, -1362209,  3937738,  1400424, -846154,  1976782]


# zetas_montgomery generation algorithm
def generate_zetas_montgomery():
    zetas_montgomery = []
    for z in zetas:
        zetas_montgomery.append((z*params.R_MODQ)%params.MLDSA_Q)
    print(zetas_montgomery)
    return zetas_montgomery

# montgomery reduction
# Input:      integer in {(-q+1)R,...,(q-1)R}
# Returns:     integer in {-q+1,...,q-1} congruent to a * R^-1 modulo q.
def mont_reduce(a):
    t=(a*params.QINV_MODR)&((1<<32) - 1)
    t=(a-t*params.MLDSA_Q)>>32
    return t

#input: a,b in Fq  montgomery domain    
#output: a*b in Fq  montgomery domain
#(xR*yR)*R^-1
def fqmul_montgomery(a,b):
    return mont_reduce(a*b)


#reduce
def reduce(a):
    t = (a + (1 << 22)) >> 23
    t = a - t * params.MLDSA_Q
    if  t<0:
        t+=params.MLDSA_Q
    return t

def NTT_montgomery(w):
    w_hat=w[:]
    m=0
    len=params.MLDSA_N//2
    while len>=1:
        start=0
        while start<params.MLDSA_N:
            m+=1
            z=zetas_montgomery[m]
            for j in range(start,start+len):
                t=fqmul_montgomery(w_hat[j+len],z)
                w_hat[j+len]=w_hat[j]-t
                w_hat[j]=w_hat[j]+t
            start+=len*2
        len//=2
    for i in range(params.MLDSA_N):
        w_hat[i]=reduce(w_hat[i])
    return w_hat
    
def iNTT_montgomery(w_hat):
    w=w_hat[:]
    m=params.MLDSA_N
    len=1
    while len<params.MLDSA_N:
        start=0
        while start<params.MLDSA_N:
            m-=1
            z=-zetas_montgomery[m]
            for j in range(start,start+len):
                t=w[j]
                w[j]=(w[j+len]+t)
                w[j+len]=(t-w[j+len])
                w[j+len]=fqmul_montgomery(w[j+len],z)
            start+=len*2
        len*=2
    for i in range(params.MLDSA_N):
        w[i]=fqmul_montgomery(w[i],16382) 
        if w[i]<0:
            w[i]+=params.MLDSA_Q 
    return w


def NTT_vec(v):
    l1=len(v)
    v_hat=[0]*l1
    for i in range(l1):
        v_hat[i]=NTT_montgomery(v[i])
    return v_hat

def iNTT_vec(v_hat):
    l1=len(v_hat)
    v=[0]*l1
    for i in range(l1):
        v[i]=iNTT_montgomery(v_hat[i])
    return v


def tomont(a):
    tomont_const=2365951
    return mont_reduce(a*tomont_const)


# Computes the sum ̂ 𝑏 of two elements 𝑎, 𝑏 ∈ 𝑇𝑞 𝑎 + . ̂ ̂ ̂
# ̂ Input: 𝑎,̂𝑏 ∈ 𝑇𝑞.
# Output: 𝑐 ̂∈ 𝑇𝑞.
def AddNTT(f_hat,g_hat):
    c_hat=[0]*params.MLDSA_N
    for i in range(params.MLDSA_N):
        c_hat[i]=reduce(f_hat[i]+g_hat[i])
    return c_hat

def SubNTT(f_hat,g_hat):
    c_hat=[0]*params.MLDSA_N
    for i in range(params.MLDSA_N):
        c_hat[i]=reduce(f_hat[i]-g_hat[i])
    return c_hat

# Computes ̂ ̂ the product 𝑎 ∘̂ 𝑏 of two elements 𝑎,̂𝑏 ∈ 𝑇𝑞.
# ̂ Input: 𝑎,̂𝑏 ∈ 𝑇𝑞.
# Output: 𝑐 ̂∈ 𝑇𝑞.
def MultiplyNTT(f_hat,g_hat):
    c_hat=[0]*params.MLDSA_N
    for i in range(params.MLDSA_N):
        c_hat[i]=tomont(fqmul_montgomery(f_hat[i],g_hat[i]))
    return c_hat


# Computes the sum 𝐯̂ ̂ + 𝐰 of two vectors 𝐯,̂ ̂ 𝐰 over 𝑇𝑞.
# Input: ℓ ∈ ℕ, ̂ 𝑞 , ̂ 𝑞 𝐯 ∈ 𝑇 . ℓ 𝐰 ∈ 𝑇 ℓ
# Output: ̂ 𝑞 𝐮 ∈ 𝑇 . ℓ
def AddVectorNTT(l,v_hat,w_hat):
    u_hat=[0]*l
    for i in range(l):
        u_hat[i]=AddNTT(v_hat[i],w_hat[i])
    return u_hat

def SubVectorNTT(l,v_hat,w_hat):
    u_hat=[0]*l
    for i in range(l):
        u_hat[i]=SubNTT(v_hat[i],w_hat[i])
    return u_hat

# Computes the product 𝑐 ∘̂ 𝐯̂of a scalar 𝑐 ̂and a vector 𝐯̂over 𝑇𝑞.
# Input: ̂ ̂ 𝑞 𝑐 ∈ 𝑇 . 𝑞, ℓ ∈ ℕ, 𝐯 ∈ 𝑇 ℓ
# Output: ̂ 𝑞 𝐰 ∈ 𝑇 .
def ScalarVectorNTT(l,c_hat,v_hat):
    w_hat=[0]*l
    for i in range(l):
        w_hat[i]=MultiplyNTT(v_hat[i],c_hat)
    return w_hat


# Computes the product 𝐌 ∘̂ 𝐯̂of a matrix 𝐌̂ and a vector 𝐯̂over 𝑇𝑞.
# Input: 𝑘, ℓ ∈ ℕ, 𝐌 ∈ 𝑇𝑞
# 𝑘×ℓ ̂ 𝑞 . ̂ , 𝐯 ∈ 𝑇 ℓ
# Output: ̂ 𝑞 𝐰 ∈ 𝑇 .
def MatrixVectorNTT(k,l,M_hat,v_hat):
    w_hat=[ [0 for i in range(params.MLDSA_N)] for j in range(k)]
    for i in range(k):
        for j in range(l):
            w_hat[i]=AddNTT(w_hat[i],MultiplyNTT(M_hat[i][j],v_hat[j]))
    return w_hat


def dummy_multiply(f,g):
    helper_f=f[::-1]
    np_g=np.array(g, dtype=int)
    matrix_f=np.zeros((params.MLDSA_N,params.MLDSA_N), dtype=int)
    for i in range(params.MLDSA_N):
        matrix_f[i]=np.roll(helper_f,i+1)
        for j in range(params.MLDSA_N-i-1):
            matrix_f[i][params.MLDSA_N-1-j]=-matrix_f[i][params.MLDSA_N-1-j]
    return (matrix_f.dot(np_g)%params.MLDSA_Q).tolist()


if __name__ == '__main__':
    print("Testing NTT and iNTT (basic implementation)...")
    f=[123]*params.MLDSA_N
    g=[456]*params.MLDSA_N
    for i in range(params.MLDSA_N):
        f[i]=random.randint(0,params.MLDSA_Q-1)
        g[i]=random.randint(0,params.MLDSA_Q-1)
    f_hat=NTT(f)
    f_inv=iNTT(f_hat)
    if f==f_inv:
        print("Test passed")
    else:
        print("Test failed")
    
    print("Testing NTT and iNTT (Montgomery implementation)...")
    f_hat_montgomery=NTT_montgomery(f)
    f_inv_montgomery=iNTT_montgomery(f_hat_montgomery)
    if f==f_inv_montgomery and f_hat_montgomery==f_hat:
        print("Test passed")
    else:
        print("Test failed")

    print("Testing MultiplyNTT_montgomery (compare with dummy multiplication)...")
    g_hat1=NTT_montgomery(g)
    f_hat1=NTT_montgomery(f)
    h_hat1=MultiplyNTT(f_hat1,g_hat1)
    h=iNTT_montgomery(h_hat1)

    h1=dummy_multiply(f,g)
    if h==h1:
        print("Test passed")
    else:
        print("Test failed")
    

