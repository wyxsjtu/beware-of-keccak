import params
import random
import numpy as np


# The zetas used in the NTT algorithm zeta^bitrev7(i), zeta=17
zetas = [
    1, 1729, 2580, 3289, 2642, 630, 1897, 848,
    1062, 1919, 193, 797, 2786, 3260, 569, 1746,
    296, 2447, 1339, 1476, 3046, 56, 2240, 1333,
    1426, 2094, 535, 2882, 2393, 2879, 1974, 821,
    289, 331, 3253, 1756, 1197, 2304, 2277, 2055,
    650, 1977, 2513, 632, 2865, 33, 1320, 1915,
    2319, 1435, 807, 452, 1438, 2868, 1534, 2402,
    2647, 2617, 1481, 648, 2474, 3110, 1227, 910,
    17, 2761, 583, 2649, 1637, 723, 2288, 1100,
    1409, 2662, 3281, 233, 756, 2156, 3015, 3050,
    1703, 1651, 2789, 1789, 1847, 952, 1461, 2687,
    939, 2308, 2437, 2388, 733, 2337, 268, 641,
    1584, 2298, 2037, 3220, 375, 2549, 2090, 1645,
    1063, 319, 2773, 757, 2099, 561, 2466, 2594,
    2804, 1092, 403, 1026, 1143, 2150, 2775, 886,
    1722, 1212, 1874, 1029, 2110, 2935, 885, 2154
]




#Computes ̂ the NTT representation 𝑓 of the given polynomial 𝑓 ∈ 𝑅𝑞.
#Input: array 𝑓 ∈ ℤ256𝑞 . ▷ the coefficients of the input polynomial
#Output ̂ : array 𝑓 ∈ ℤ256𝑞 . ▷ the coefficients of the NTT of the input polynomial
def NTT(f):
    f_hat = f[:]
    i=1
    len=params.MLKEM_N//2
    while (len >=2):                       # Outer loop: layers of the NTT buterflies
        start=0
        while (start < params.MLKEM_N):    # Middle loop: Groups of butterflies in each layer
            zeta=zetas[i]
            i+=1
            j=start
            while (j < start+len):         # Inner loop: butterflies in each group
                t=zeta*f_hat[j+len]     # MUL zeta^bitrev7(j+len)
                f_hat[j+len]=barrett_reduce(f_hat[j]-t)    # Lower half
                f_hat[j]=barrett_reduce(f_hat[j]+t)         # Upper half
                j+=1
            start+=2*len
        len = len//2
    return f_hat

#Computes ̂ the polynomial 𝑓 ∈ 𝑅𝑞 that corresponds to the given NTT representation 𝑓 ∈ 𝑇𝑞.
#̂ Input: array 𝑓 ∈ ℤ256𝑞 . ▷ the coefficients of input NTT representation
# Output: array 𝑓 ∈ ℤ256𝑞 . ▷ the coefficients of the inverse NTT of the input
def iNTT(f_hat):
    f=f_hat[:]
    i=params.MLKEM_N//2-1
    len=2
    while (len <= params.MLKEM_N//2):     # Outer loop: layers of the inverse NTT butterflies
        start=0
        while (start < params.MLKEM_N):    # Middle loop: Groups of butterflies in each layer
            zeta=zetas[i]
            i-=1
            j=start
            while (j < start+len):         # Inner loop: butterflies in each group
                t=f[j]
                f[j]=barrett_reduce(t+f[j+len])        # Upper half
                f[j+len]=barrett_reduce(zeta*(f[j+len]-t))  # Lower half: -z^-k= z^(N/2-k)
                j+=1
            start+=2*len
        len = len*2
    for index in range(params.MLKEM_N):
        f[index]=barrett_reduce(f[index]*params.MLKEM_INTTCONST) 
    return f

#Computes the product of two degree-one polynomials with respect to a quadratic modulus.
#Input: 𝑎0, 𝑎1, 𝑏0, 𝑏1 ∈ ℤ𝑞. ▷ the coefficients of 𝑎0 + 𝑎1𝑋 and 𝑏0 + 𝑏1𝑋
#Input: 𝛾 ∈ ℤ𝑞. ▷ the modulus is 𝑋2 − 𝛾
#Output: 𝑐0, 𝑐1 ∈ ℤ𝑞. ▷ the coefficients of the product of the two polynomials
def BaseCaseMultiply(a0,a1,b0,b1,gamma):
    c0=barrett_reduce(a1*b1)
    c0=barrett_reduce(c0*gamma+a0*b0)
    c1=barrett_reduce(a0*b1+a1*b0)
    return (c0,c1)

#Computes the product (in the ring 𝑇𝑞) of two NTT representations.
#Input: Two arrays 𝑓 ∈ ℤ256𝑞 ̂ 𝑞 . ▷ the coefficients of two NTT representations ̂ and 𝑔 ∈ ℤ256
#Output ̂ : An array ℎ ∈ ℤ256𝑞 . ▷ the coefficients of the product of the inputs
def MultiplyNTT(f_hat,g_hat):
    h_hat=[0]*params.MLKEM_N
    for i in range (params.MLKEM_N//2):
        (h_hat[2*i],h_hat[2*i+1])=BaseCaseMultiply(f_hat[2*i],f_hat[2*i+1],g_hat[2*i],g_hat[2*i+1],((-1)**i)*zetas[i//2+64])
    return h_hat

#Computes the product (in the ring 𝑅𝑞) of two polynomials.
def dummy_multiply(f,g):
    helper_f=f[::-1]
    np_g=np.array(g, dtype=int)
    matrix_f=np.zeros((params.MLKEM_N,params.MLKEM_N), dtype=int)
    for i in range(params.MLKEM_N):
        matrix_f[i]=np.roll(helper_f,i+1)
        for j in range(params.MLKEM_N-i-1):
            matrix_f[i][params.MLKEM_N-1-j]=-matrix_f[i][params.MLKEM_N-1-j]
    return (matrix_f.dot(np_g)%params.MLKEM_Q).tolist()







# The Montgomery version of the NTT algorithm

zetas_montgomery = [
    -1044,  -758,  -359, -1517,  1493,  1422,   287,   202,
    -171,   622,  1577,   182,   962, -1202, -1474,  1468,
    573, -1325,   264,   383,  -829,  1458, -1602,  -130,
    -681,  1017,   732,   608, -1542,   411,  -205, -1571,
    1223,   652,  -552,  1015, -1293,  1491,  -282, -1544,
    516,    -8,  -320,  -666, -1618, -1162,   126,  1469,
    -853,   -90,  -271,   830,   107, -1421,  -247,  -951,
    -398,   961, -1508,  -725,   448, -1065,   677, -1275,
    -1103,   430,   555,   843, -1251,   871,  1550,   105,
    422,   587,   177,  -235,  -291,  -460,  1574,  1653,
    -246,   778,  1159,  -147,  -777,  1483,  -602,  1119,
    -1590,   644,  -872,   349,   418,   329,  -156,   -75,
    817,  1097,   603,   610,  1322, -1285, -1465,   384,
    -1215,  -136,  1218, -1335,  -874,   220, -1187, -1659,
    -1185, -1530, -1278,   794, -1510,  -854,  -870,   478,
    -108,  -308,   996,   991,   958, -1460,  1522,  1628
]

# zetas_montgomery generation algorithm
def generate_zetas_montgomery():
    zetas_montgomery = []
    for z in zetas:
        zetas_montgomery.append((z*params.R_MODQ)%params.MLKEM_Q)
    print(zetas_montgomery)
    return zetas_montgomery



# montgomery reduction
# Input:      integer in {(-q+1)R,...,(q-1)R}
# Returns:     integer in {-q+1,...,q-1} congruent to a * R^-1 modulo q.
def mont_reduce(a):
    t=(a*params.QINV_MODR)&((1<<16) - 1)
    t=(a-t*params.MLKEM_Q)>>16
    return t


# barrett reduction
# Arguments:   - int16_t a: input integer to be reduced
# Returns:     integer in 0 1 ... q-1
def barrett_reduce(a):
    barrett_const=20158   #2^26 mod q
    t=(a*barrett_const)>>26
    t=a-t*params.MLKEM_Q
    if t>=params.MLKEM_Q:
        t-=params.MLKEM_Q
    elif t<0:
        t+=params.MLKEM_Q
    return t


#input: a,b in Fq  montgomery domain    
#output: a*b in Fq  montgomery domain
#(xR*yR)*R^-1
def fqmul_montgomery(a,b):
    return mont_reduce(a*b)

def NTT_montgomery(f):
    f_hat = f[:]
    i=1
    len=params.MLKEM_N//2
    while (len >=2):                       # Outer loop: layers of the NTT buterflies
        start=0
        while (start < params.MLKEM_N):    # Middle loop: Groups of butterflies in each layer
            zeta=zetas_montgomery[i]
            i+=1
            j=start
            while (j < start+len):         # Inner loop: butterflies in each group
                t=fqmul_montgomery(zeta,f_hat[j+len])     # MUL zeta^bitrev7(j+len)
                f_hat[j+len]=f_hat[j]-t     # Lower half
                f_hat[j]=f_hat[j]+t      # Upper half
                j+=1
            start+=2*len
        len = len//2
    for i in range(params.MLKEM_N):
        f_hat[i]=barrett_reduce(f_hat[i]) 
    return f_hat

def iNTT_montgomery(f_hat):
    f=f_hat[:]
    i=params.MLKEM_N//2-1
    len=2
    while (len <= params.MLKEM_N//2):     # Outer loop: layers of the inverse NTT butterflies
        start=0
        while (start < params.MLKEM_N):    # Middle loop: Groups of butterflies in each layer
            zeta=zetas_montgomery[i]
            i-=1
            j=start
            while (j < start+len):         # Inner loop: butterflies in each group
                t=f[j]
                f[j]=barrett_reduce(t+f[j+len])         # Upper half
                f[j+len]=fqmul_montgomery(zeta,f[j+len]-t)  # Lower half: -z^-k= z^(N/2-k)
                j+=1
            start+=2*len
        len = len*2
    for i in range(params.MLKEM_N):
        f[i]=fqmul_montgomery(f[i],params.MLKEM_INTTCONST_MONT) 
        if f[i]<0:
            f[i]+=params.MLKEM_Q 
    return f


def tomont(a):
    tomont_const=1353     #2^32 mod q
    return mont_reduce(a*tomont_const)

def BaseCaseMultiply_montgomery(a0,a1,b0,b1,gamma):
    c0=fqmul_montgomery(a1,b1)
    c0=fqmul_montgomery(c0,gamma)
    c0+=fqmul_montgomery(a0,b0)
    c1=fqmul_montgomery(a0,b1)
    c1+=fqmul_montgomery(a1,b0)
    return(tomont(c0),tomont(c1))



def MultiplyNTT_montgomery(f_hat,g_hat):
    h_hat=[0]*params.MLKEM_N
    for i in range (params.MLKEM_N//2):
        (h_hat[2*i],h_hat[2*i+1])=BaseCaseMultiply_montgomery(f_hat[2*i],f_hat[2*i+1],g_hat[2*i],g_hat[2*i+1],((-1)**i)*zetas_montgomery[i//2+64])
    return h_hat





if __name__ == '__main__':
    print("Testing NTT and iNTT (basic implementation)...")
    f=[123]*params.MLKEM_N
    g=[456]*params.MLKEM_N
    for i in range(params.MLKEM_N):
        f[i]=random.randint(0,params.MLKEM_Q-1)
        g[i]=random.randint(0,params.MLKEM_Q-1)
    f_hat=NTT(f)
    f_inv=iNTT(f_hat)
    if f==f_inv:
        print("Test passed")
    else:
        print("Test failed")
    
    print("Testing MultiplyNTT (compare with dummy multiplication)...")
    g_hat=NTT(g)
    f_hat=NTT(f)
    h_hat=MultiplyNTT(f_hat,g_hat)
    h=iNTT(h_hat)

    h1=dummy_multiply(f,g)
    if h==h1:
        print("Test passed")
    else:
        print("Test failed")

    # for i in range(100):
    #     a=random.randint(0,params.MLKEM_Q*65536-1)
    #     print(mont_reduce(a))

    print("Testing NTT and iNTT (Montgomery implementation)")
    f_hat1=NTT_montgomery(f)
    f1=iNTT_montgomery(f_hat1)
    if f==f1:
        print("Test passed")
    else:
        print("Test failed")

    print("Testing MultiplyNTT_montgomery (compare with dummy multiplication)...")
    g_hat1=NTT_montgomery(g)
    f_hat1=NTT_montgomery(f)
    h_hat1=MultiplyNTT_montgomery(f_hat1,g_hat1)
    # print(h_hat1)
    # print(h_hat)
    h=iNTT_montgomery(h_hat1)

    h1=dummy_multiply(f,g)
    if h==h1:
        print("Test passed")
    else:
        print("Test failed")
    # for i in range(100000):
    #     a=random.randint(0,67108864-1)
    #     if barrett_reduce(a)>=3329 or barrett_reduce(a)<0:
    #         print("aasdfasdfadfadfsasdf")

