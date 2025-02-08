import converse
import params
import numpy as np

# Encodes a secret key for ML-DSA into a byte string.
# Input: 𝜌 ∈ 𝔹32, 𝐾 ∈ 𝔹32, 𝑡𝑟 ∈ 𝔹64, 𝐬1 ∈ 𝑅ℓ with coefficients in [−𝜂, 𝜂], 𝐬2 ∈ 𝑅𝑘 with
# coefficients in [−𝜂, 𝜂], 𝐭0 ∈ 𝑅𝑘 with coefficients in [−2𝑑−1 + 1, 2𝑑−1].
# Output: Private key 𝑠𝑘 ∈ 𝔹32+32+64+32⋅((𝑘+ℓ)⋅bitlen (2𝜂)+𝑑𝑘).
def skEncode(eta,k,l,rho,K,tr,s1,s2,t0):
    d=params.MLDSA_D
    sk=bytearray([])
    sk+=rho+K+tr
    for i in range(l):
        sk+=converse.BitPack(s1[i],eta,eta)
    for i in range(k):
        sk+=converse.BitPack(s2[i],eta,eta)
    for i in range(k):
        sk+=converse.BitPack(t0[i],(1<<d-1)-1,1<<d-1)
    return sk

# Algorithm 25 skDecode(𝑠𝑘)
# Reverses the procedure skEncode.
# Input: Private key 𝑠𝑘 ∈ 𝔹32+32+64+32⋅((ℓ+𝑘)⋅bitlen (2𝜂)+𝑑𝑘).
# Output: 𝜌 ∈ 𝔹32, 𝐾 ∈ 𝔹32, 𝑡𝑟 ∈ 𝔹64,
# 𝐬1 ∈ 𝑅ℓ, 𝐬2 ∈ 𝑅𝑘, 𝐭0 ∈ 𝑅𝑘 with coefficients in [−2𝑑−1 + 1, 2𝑑−1].
def skDecode(eta,k,l,sk):
    s1=[[0 for i in range(params.MLDSA_N)] for j in range(l)]
    s2=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
    t0=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
    rho=sk[:32]
    K=sk[32:64]
    tr=sk[64:128]
    s1_len=32*(2*eta).bit_length()
    s2_len=32*(2*eta).bit_length()
    t0_len=32*params.MLDSA_D
    base=128
    for i in range(l):
        s1[i]=converse.BitUnpack(sk[base+s1_len*i:base+s1_len*(i+1)],eta,eta)
    base+=l*s1_len
    for i in range(k):
        s2[i]=converse.BitUnpack(sk[base+s2_len*i:base+s2_len*(i+1)],eta,eta)
    base+=k*s2_len
    for i in range(k):
        t0[i]=converse.BitUnpack(sk[base+t0_len*i:base+t0_len*(i+1)],(1<<params.MLDSA_D-1)-1,1<<params.MLDSA_D-1)
    return rho,K,tr,s1,s2,t0


# Encodes a public key for ML-DSA into a byte string.
# Input:𝜌 ∈ 𝔹32, 𝐭1 ∈ 𝑅𝑘 with coefficients in [0, 2bitlen (𝑞−1)−𝑑 − 1].
# Output: Public key 𝑝𝑘 ∈ 𝔹32+32𝑘(bitlen (𝑞−1)−𝑑).
def pkEncode(eta,k,rho,t1):
    pk=bytearray([])
    pk+=rho
    tmp=(params.MLDSA_Q-1).bit_length()-params.MLDSA_D
    for i in range(k):
        pk+=converse.SimpleBitPack(t1[i],(1<<tmp)-1)
    return pk

# Reverses the procedure pkEncode.
# Input: Public key 𝑝𝑘 ∈ 𝔹32+32𝑘(bitlen (𝑞−1)−𝑑).
# Output: 𝜌 ∈ 𝔹32, 𝐭1 ∈ 𝑅𝑘 with coefficients in [0, 2bitlen (𝑞−1)−𝑑 − 1].
def pkDecode(eta,k,pk):
    rho=pk[:32]
    t1=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
    pk_len=32*((params.MLDSA_Q-1).bit_length()-params.MLDSA_D)
    for i in range(k):
        t1[i]=converse.SimpleBitUnpack(pk[32+pk_len*i:32+pk_len*(i+1)],(1<<(pk_len>>5))-1)
    return rho,t1


# Encodes a signature into a byte string.
# Input: ̃ 2 𝑐 ∈ 𝔹 . 𝜆/4, 𝐳 ∈ 𝑅ℓ with coefficients in [−𝛾1 + 1, 𝛾1], 𝐡 ∈ 𝑅𝑘
# Output: Signature 𝜎 ∈ 𝔹𝜆/4+ℓ⋅32⋅(1+bitlen (𝛾1−1))+𝜔+𝑘.
def sigEncode(omega,k,l,gamma1,c_tilde,z,h):
    sigma=c_tilde[:]
    for i in range(l):
        sigma+=converse.BitPack(z[i],gamma1-1,gamma1)
    #print(sigma.hex())
    sigma+=converse.HintBitPack(omega,k,h)
    return sigma


# Reverses the procedure sigEncode.
# Input: Signature 𝜎 ∈ 𝔹𝜆/4+ℓ⋅32⋅(1+bitlen (𝛾1−1))+𝜔+𝑘.
# Output: ̃ 2 𝑐 ∈ 𝔹 , or ⊥. 𝜆/4, 𝐳 ∈ 𝑅ℓ with coefficients in [−𝛾1 + 1, 𝛾1], 𝐡 ∈ 𝑅2𝑘 or ⊥.
def sigDecode(lambda_c,omega,k,l,gamma1,sigma):
    c_tilde=sigma[:lambda_c//4]
    z_len=32*(gamma1-1).bit_length()+32
    z=[[0 for i in range(params.MLDSA_N)] for j in range(l)]
    base=lambda_c//4
    for i in range(l):
        z[i]=converse.BitUnpack(sigma[base+z_len*i:base+z_len*(i+1)],gamma1-1,gamma1)
    base+=l*z_len
    h=converse.HintBitUnpack(omega,k,sigma[base:])
    return c_tilde,z,h



# Encodes a polynomial vector 𝐰1 into a byte string.
# Input: 𝐰1 ∈ 𝑅𝑘 whose polynomial coordinates have coefficients in [0,(𝑞 − 1)/(2𝛾2) − 1].
# Output: A byte string representation 𝐰1 ∈ 𝔹32𝑘⋅bitlen ((𝑞−1)/(2𝛾2)−1) 
def w1Encode(gamma2,k,w1):
    w1_tilde=bytearray([])
    for i in range(k):
        w1_tilde+=converse.SimpleBitPack(w1[i],(params.MLDSA_Q-1)//(2*gamma2)-1)
    return w1_tilde


if __name__=="__main__":
    print("Testing skEncode and skDecode...")
    eta=4
    k=6
    l=5
    rho = bytearray(np.random.randint(0, 256, size=32, dtype=np.uint8))
    K = bytearray(np.random.randint(0, 256, size=32, dtype=np.uint8))
    tr = bytearray(np.random.randint(0, 256, size=64, dtype=np.uint8))
    s1 = np.random.randint(-eta, eta + 1, size=(l, 256)).tolist()
    s2 = np.random.randint(-eta, eta + 1, size=(k, 256)).tolist()
    t0 = np.random.randint(-(1<<params.MLDSA_D-1)+1, (1<<params.MLDSA_D-1), size=(k, 256)).tolist()
    sk = skEncode(eta,k,l,rho,K,tr,s1,s2,t0)
    rho_d,K_d,tr_d,s1_d,s2_d,t0_d = skDecode(eta,k,l,sk)
    if rho_d==rho and K_d==K and tr_d==tr and s1_d==s1 and s2_d==s2 and t0_d==t0 and len(sk)==4032:
        print("Test passed.")
    else:
        print("Test failed.")
    print("Testing pkEncode and pkDecode...")
    t1 = np.random.randint(0, 1<<((params.MLDSA_Q-1).bit_length()-params.MLDSA_D), size=(k, 256)).tolist()
    pk = pkEncode(eta,k,rho,t1)
    rho_d,t1_d = pkDecode(eta,k,pk)
    if rho_d==rho and t1_d==t1 and len(pk)==1952:
        print("Test passed.")
    else:
        print("Test failed.")

    print("Testing sigEncode and sigDecode...")
    omega=55
    gamma1=1<<19
    lambda_c=192
    c_tilde = bytearray(np.random.randint(0, 256, size=lambda_c//4, dtype=np.uint8))
    z=np.random.randint(0, 256, size=(l,256)).tolist()
    h_helper = np.random.randint(0, k*256, size=(omega)).tolist()
    h=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
    for index in h_helper:
        h[index//256][index%256]=1
    sig=sigEncode(omega,k,l,gamma1,c_tilde,z,h)
    c_tilde_d,z_d,h_d=sigDecode(lambda_c,omega,k,l,gamma1,sig)
    if c_tilde_d==c_tilde and z_d==z and h_d==h and len(sig)==3309:
        print("Test passed.")
    else:
        print("Test failed.")

    print("Testing w1Encode...")
    gamma2=(params.MLDSA_Q-1)//32
    w1 = np.random.randint(0, (params.MLDSA_Q-1)//(2*gamma2)-1, size=(k, 256)).tolist()
    w1_tilde = w1Encode(gamma2,k,w1)
    if len(w1_tilde)==768:
        print("Test passed.")
    else:    
        print("Test failed.")