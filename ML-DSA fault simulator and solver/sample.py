import keccak
import converse
import params

# Samples a polynomial 𝑐 ∈ 𝑅 with coefficients from {−1, 0, 1} and Hamming weight 𝜏 ≤ 64.
# Input: A seed 𝜌 ∈ 𝔹𝜆/4
# Output: A polynomial 𝑐 in 𝑅.
def SampleInBall(tao,rho):
    c=[0]*params.MLDSA_N
    ctx=keccak.shake256_inc_init()
    keccak.shake256_inc_absorb(ctx, rho)
    keccak.shake256_inc_finalize(ctx)
    s=bytearray(8)
    keccak.shake256_inc_squeeze(s,8,ctx)
    h=converse.BytesToBits(s)
    j_arr=bytearray(1)
    for i in range(256-tao,256):
        keccak.shake256_inc_squeeze(j_arr,1,ctx)
        j=int(j_arr[0])
        while j>i:
            keccak.shake256_inc_squeeze(j_arr,1,ctx)
            j=int(j_arr[0])
        c[i]=c[j]
        if h[i+tao-256]==1:
            c[j]=-1
        else:
            c[j]=1
    return c

def faulty_SampleInBall(tao,rho,a2):
    c=[0]*params.MLDSA_N
    ctx=keccak.shake256_inc_init()
    keccak.faulty_shake256_inc_absorb(ctx, rho)
    keccak.shake256_inc_finalize(ctx)
    s=bytearray(8)
    keccak.shake256_inc_squeeze(s,8,ctx)
    h=converse.BytesToBits(s)
    j_arr=bytearray(1)
    for i in range(256-tao,256):
        keccak.shake256_inc_squeeze(j_arr,1,ctx)
        j=int(j_arr[0])
        while j>i:
            keccak.shake256_inc_squeeze(j_arr,1,ctx)
            j=int(j_arr[0])
        c[i]=c[j]
        if h[i+tao-256]==1:
            c[j]=-1
        else:
            c[j]=1
    return c


# Samples a polynomial ∈ 𝑇𝑞.
# Input: A seed 𝜌 ∈ 𝔹34.
# Output: An element 𝑎̂∈ 𝑇𝑞.
def RejNTTPoly(rho):
    j=0
    a_hat=[0]*params.MLDSA_N
    ctx=keccak.shake128_inc_init()
    keccak.shake128_inc_absorb(ctx, rho)
    keccak.shake128_inc_finalize(ctx)
    s=bytearray(3)
    while j<params.MLDSA_N:
        keccak.shake128_inc_squeeze(s,3,ctx)
        a_hat[j]=converse.CoeffFromThreeBytes(s[0],s[1],s[2])
        if a_hat[j]!=None:
            j+=1
    return a_hat


# Samples an element 𝑎 ∈ 𝑅 with coefficients in [−𝜂, 𝜂] computed via rejection sampling from 𝜌.
# Input: A seed 𝜌 ∈ 𝔹66.
# Output: A polynomial 𝑎 ∈ 𝑅.
def RejBoundedPoly(eta,rho):
    j=0
    a=[0]*params.MLDSA_N
    ctx=keccak.shake256_inc_init()
    keccak.shake256_inc_absorb(ctx, rho)
    keccak.shake256_inc_finalize(ctx)
    z=bytearray(1)
    while j<params.MLDSA_N:
        keccak.shake256_inc_squeeze(z,1,ctx)
        z0=converse.CoeffFromHalfByte(eta,z[0]&0x0f)
        z1=converse.CoeffFromHalfByte(eta,z[0]>>4)
        if z0!=None:
            a[j]=z0
            j+=1
        if z1!=None and j<params.MLDSA_N:
            a[j]=z1
            j+=1
    return a

def faulty_RejBoundedPoly(eta,rho,a2):
    j=0
    a=[0]*params.MLDSA_N
    ctx=keccak.shake256_inc_init()
    if a2==2:
        keccak.faulty_shake256_inc_absorb(ctx, rho)
    else:
        keccak.shake256_inc_absorb(ctx, rho)
    keccak.shake256_inc_finalize(ctx)
    z=bytearray(1)
    while j<params.MLDSA_N:
        keccak.shake256_inc_squeeze(z,1,ctx)
        z0=converse.CoeffFromHalfByte(eta,z[0]&0x0f)
        z1=converse.CoeffFromHalfByte(eta,z[0]>>4)
        if z0!=None:
            a[j]=z0
            j+=1
        if z1!=None and j<params.MLDSA_N:
            a[j]=z1
            j+=1
    return a

# Samples a 𝑘 × ℓ matrix 𝐀̂of elements of 𝑇𝑞.
# Input: A seed 𝜌 ∈ 𝔹32.
# Output ̂ : Matrix 𝐀 ∈ (𝑇𝑞)𝑘×ℓ.
def ExpandA(k,l,rho):
    A_hat=[[0 for i in range(l)] for j in range(k)]
    for r in range(k):
        for s in range(l):
            A_hat[r][s]=RejNTTPoly(rho+converse.IntegerToBytes(s,1)+converse.IntegerToBytes(r,1))
    return A_hat
            

# Samples vectors 𝐬1 ∈ 𝑅ℓ and 𝐬2 ∈ 𝑅𝑘, each with polynomial coordinates whose coefficients are
# in the interval [−𝜂, 𝜂].
# Input: A seed 𝜌 ∈ 𝔹64.
# Output: Vectors 𝐬1, 𝐬2 of polynomials in R
def ExpandS(eta,k,l,rho):
    s1=[0]*l
    s2=[0]*k
    for r in range(l):
        s1[r]=RejBoundedPoly(eta,rho+converse.IntegerToBytes(r,2))
    for r in range(k):
        s2[r]=RejBoundedPoly(eta,rho+converse.IntegerToBytes(r+l,2))
    return s1,s2


def faulty_ExpandS(eta,k,l,rho,a2):
    s1=[0]*l
    s2=[0]*k
    for r in range(l):
        s1[r]=faulty_RejBoundedPoly(eta,rho+converse.IntegerToBytes(r,2),a2)
    for r in range(k):
        s2[r]=RejBoundedPoly(eta,rho+converse.IntegerToBytes(r+l,2))
    return s1,s2

# Samples a vector 𝐲 ∈ 𝑅ℓ such that each polynomial 𝐲[𝑟] has coefficients between −𝛾1 + 1 and 𝛾1.
# Input: A seed 𝜌 ∈ 𝔹64 and a nonnegative integer 𝜇.
# Output: Vector 𝐲 ∈ 𝑅ℓ.
def ExpandMask(l,gamma1,rho,mu):
    c=1+(gamma1-1).bit_length()
    v=bytearray(c*32)
    y=[0]*l
    for r in range(l):
        rho_prime=rho+converse.IntegerToBytes(mu+r,2)
        keccak.shake256(v,c*256,rho_prime)
        y[r]=converse.BitUnpack(v,gamma1-1,gamma1)
    return y






    
if __name__ == '__main__':
    print("Testing SampleInBall()...")
    lambda_c=192
    tao=37
    rho=bytearray(lambda_c//4)
    c=SampleInBall(tao,rho)
    hw=0
    for i in range(params.MLDSA_N):
        if c[i]!=0:
            hw+=1
    if hw==tao:
        print("Test passed.")
    else:
        print("Test failed.")

    print("Testing RejNTTPoly()...")
    rho=bytearray(34)
    a_hat=RejNTTPoly(rho)
    for i in range(params.MLDSA_N):
        if a_hat[i]>=params.MLDSA_Q:
            print("Test failed.")
            break
    print("Test passed.")

    print("Testing RejBoundedPoly()...")
    eta=4
    rho=bytearray(66)
    a=RejBoundedPoly(eta,rho)
    for i in range(params.MLDSA_N):
        if a[i]<-eta or a[i]>eta:
            print("Test failed.")
            break
    print("Test passed.")

    print("Testing ExpandA()...")
    k=6
    l=5
    rho=bytearray(32)
    A_hat=ExpandA(k,l,rho)
    flag=True
    for i in range(k):
        for j in range(l):
            for n in range(params.MLDSA_N):
                if A_hat[i][j][n]>=params.MLDSA_Q:
                    flag=False
                    break
            if not flag:
                break
        if not flag:
            break
    if flag:
        print("Test passed.")
    else:
        print("Test failed.")

    print("Testing ExpandS()...")
    rho=bytearray(64)
    s1,s2=ExpandS(4,6,5,rho)
    flag1=True
    flag2=True
    for i in range(5):
        for n in range(params.MLDSA_N):
            if s1[i][n]<-4 or s1[i][n]>4:
                flag1=False
                break
        if not flag1:
            break
    for i in range(6):
        for n in range(params.MLDSA_N):
            if s2[i][n]<-4 or s2[i][n]>4:
                flag2=False
                break
        if not flag2:
            break
    if flag1 and flag2:
        print("Test passed.")
    else:
        print("Test failed.")

    print("Testing ExpandMask()...")
    gamma1=1<<19
    rho=bytearray(64)
    mu=123
    y=ExpandMask(l,gamma1,rho,mu)
    flag=True
    for i in range(l):
        for n in range(params.MLDSA_N):
            if y[i][n]<-gamma1+1 or y[i][n]>gamma1:
                flag=False
                break
        if not flag:
            break
    if flag:
        print("Test passed.")
    else:
        print("Test failed.")
    

