import params
import keccak
import converse_compress
import NTT
import polyvec

import random


#Uses randomness to generate an encryption key and a corresponding decryption key.
#Input: randomness 𝑑 ∈ 𝔹32.
#Output: encryption key ek_PKE ∈ 𝔹384𝑘+32
#        decryption key dk_PKE ∈ 𝔹384𝑘
def KPKE_keygen(d,variant=512):
    #select parameters based on variant
    if variant==512:
        K=params.MLKEM512_K
        eta1=params.MLKEM512_eta1
    elif variant==768:
        K=params.MLKEM768_K
        eta1=params.MLKEM768_eta1
    elif variant==1024:
        K=params.MLKEM1024_K
        eta1=params.MLKEM1024_eta1
    else:
        print("Invalid variant selected. Please select 512, 768 or 1024.")
        return None,None

    #expand 32+1 bytes to two pseudorandom 32-byte seeds
    seeds=bytearray(64)
    seeds[:32]=d
    seeds[32]=K
    keccak.sha3_512(seeds,seeds[:33])
    rho=seeds[:32]
    sigma=seeds[32:]

    N=0
    
    #generate matrix 𝐀∈ (ℤ256q)^{K×K}
    A_hat=[[[] for j in range(K)] for i in range(K)]
    for i in range(K):
        for j in range(K):
            A_hat[i][j]=converse_compress.SampleNTT(rho+ bytearray([j])+bytearray([i]))   #𝑗 and 𝑖 are bytes 33 and 34 of the input

    #generate vector s∈ (ℤ256q)^{K}
    s=[[] for i in range(K)]
    for i in range(K):
        s[i]=converse_compress.SamplePolyCBD(eta1,keccak.PRF(eta1,sigma,bytearray([N])))
        N+=1
    
    #generate vector e∈ (ℤ256q)^{K}
    e=[[] for i in range(K)]
    for i in range(K):
        e[i]=converse_compress.SamplePolyCBD(eta1,keccak.PRF(eta1,sigma,bytearray([N])))
        N+=1
    
    #run NTT 𝑘 times (once for each coordinate of 𝐬 and e)
    s_hat=polyvec.NTT_montgomery_vec(s)
    e_hat=polyvec.NTT_montgomery_vec(e)

    #noisy linear system in NTT domain   !! Compute t_hat=A_hat*s_hat+e_hat
    t_hat=[0]*K
    for i in range(K):
        t_hat[i]=polyvec.MultiplyNTT_montgomery_vec(A_hat[i],s_hat)
    t_hat=polyvec.polyadd_vec(t_hat,e_hat)
    
    #encryption key : run ByteEncode12 𝑘 times, then append 𝐀-seed, encode t_hat and rho
    ek_PKE=bytearray([])
    for i in range(K):
        ek_PKE+=converse_compress.byte_encode(12,t_hat[i])
    ek_PKE+=rho
    
    #decryption key : run ByteEncode12 𝑘 times, encode s_hat
    dk_PKE=bytearray([])
    for i in range(K):
        dk_PKE+=converse_compress.byte_encode(12,s_hat[i])

    return ek_PKE,dk_PKE

def faulty_KPKE_keygen(d,variant,a1,a2):
    #select parameters based on variant
    if variant==512:
        K=params.MLKEM512_K
        eta1=params.MLKEM512_eta1
    elif variant==768:
        K=params.MLKEM768_K
        eta1=params.MLKEM768_eta1
    elif variant==1024:
        K=params.MLKEM1024_K
        eta1=params.MLKEM1024_eta1
    else:
        print("Invalid variant selected. Please select 512, 768 or 1024.")
        return None,None

    #expand 32+1 bytes to two pseudorandom 32-byte seeds
    seeds=bytearray(64)
    seeds[:32]=d
    seeds[32]=K
    if a1==1:
        keccak.faulty_sha3_512(seeds,seeds[:33],a2)
    else:
        keccak.sha3_512(seeds,seeds[:33])
    rho=seeds[:32]
    sigma=seeds[32:]

    N=0
    
    #generate matrix 𝐀∈ (ℤ256q)^{K×K}
    A_hat=[[[] for j in range(K)] for i in range(K)]
    for i in range(K):
        for j in range(K):
            A_hat[i][j]=converse_compress.SampleNTT(rho+ bytearray([j])+bytearray([i]))   #𝑗 and 𝑖 are bytes 33 and 34 of the input

    #generate vector s∈ (ℤ256q)^{K}
    s=[[] for i in range(K)]
    if a1==2:
        for i in range(K):
            s[i]=converse_compress.SamplePolyCBD(eta1,keccak.faulty_PRF(eta1,sigma,bytearray([N]),a2))
            N+=1
    else:
        for i in range(K):
            s[i]=converse_compress.SamplePolyCBD(eta1,keccak.PRF(eta1,sigma,bytearray([N])))
            N+=1
    #generate vector e∈ (ℤ256q)^{K}
    e=[[] for i in range(K)]
    for i in range(K):
        e[i]=converse_compress.SamplePolyCBD(eta1,keccak.PRF(eta1,sigma,bytearray([N])))
        N+=1
    
    #run NTT 𝑘 times (once for each coordinate of 𝐬 and e)
    s_hat=polyvec.NTT_montgomery_vec(s)
    e_hat=polyvec.NTT_montgomery_vec(e)

    #noisy linear system in NTT domain   !! Compute t_hat=A_hat*s_hat+e_hat
    t_hat=[0]*K
    for i in range(K):
        t_hat[i]=polyvec.MultiplyNTT_montgomery_vec(A_hat[i],s_hat)
    t_hat=polyvec.polyadd_vec(t_hat,e_hat)
    
    #encryption key : run ByteEncode12 𝑘 times, then append 𝐀-seed, encode t_hat and rho
    ek_PKE=bytearray([])
    for i in range(K):
        ek_PKE+=converse_compress.byte_encode(12,t_hat[i])
    ek_PKE+=rho
    
    #decryption key : run ByteEncode12 𝑘 times, encode s_hat
    dk_PKE=bytearray([])
    for i in range(K):
        dk_PKE+=converse_compress.byte_encode(12,s_hat[i])

    return ek_PKE,dk_PKE

# Uses the encryption key to encrypt a plaintext message using the randomness 𝑟.
# ∈ 𝔹384𝑘+32 Input: encryption key ekPKE .
# Input: message 𝑚 ∈ 𝔹32.
# Input: randomness 𝑟 ∈ 𝔹32.
# Output: ciphertext 𝑐 ∈ 𝔹32(𝑑𝑢𝑘+𝑑𝑣)

def KPKE_encrypt(ek_PKE,m,r,variant=512):
    
    if variant==512:
        K=params.MLKEM512_K
        eta1=params.MLKEM512_eta1
        eta2=params.MLKEM512_eta2
        du=params.MLKEM512_du
        dv=params.MLKEM512_dv
    elif variant==768:
        K=params.MLKEM768_K
        eta1=params.MLKEM768_eta1
        eta2=params.MLKEM768_eta2
        du=params.MLKEM768_du
        dv=params.MLKEM768_dv
    elif variant==1024:
        K=params.MLKEM1024_K
        eta1=params.MLKEM1024_eta1
        eta2=params.MLKEM1024_eta2
        du=params.MLKEM1024_du
        dv=params.MLKEM1024_dv
    else:
        print("Invalid variant selected. Please select 512, 768 or 1024.")
        return None,None

    N=0

    # recover t_hat and rho from ek_PKE
    t_hat=[0]*K
    for i in range(K):
        t_hat[i]=converse_compress.byte_decode(12,ek_PKE[384*i:384*(i+1)])     #run ByteDecode12 𝑘 times to decode 𝐭 ∈ (ℤ256q)^{K}
    rho=ek_PKE[384*K:384*K+32]                                                  #extract 32-byte seed from ekPKE

    # recover matrix 𝐀∈ (ℤ256q)^{K×K}
    A_hat=[[[] for j in range(K)] for i in range(K)]
    for i in range(K):
        for j in range(K):
            A_hat[i][j]=converse_compress.SampleNTT(rho+ bytearray([j])+bytearray([i]))   #𝑗 and 𝑖 are bytes 33 and 34 of the input
    
    #generate 𝐲 ∈ (ℤ256_q)^{K}
    y=[[] for i in range(K)]
    for i in range(K):
        y[i]=converse_compress.SamplePolyCBD(eta1,keccak.PRF(eta1,r,bytearray([N])))
        N+=1
    
    #generate e1 ∈ (ℤ256_q)^{K}
    e1=[[] for i in range(K)]
    for i in range(K):
        e1[i]=converse_compress.SamplePolyCBD(eta2,keccak.PRF(eta2,r,bytearray([N])))
        N+=1
    
    #generate e2 ∈ (ℤ256_q)
    e2=converse_compress.SamplePolyCBD(eta2,keccak.PRF(eta2,r,bytearray([N])))

    #run NTT 𝑘 times (once for each coordinate of y)
    y_hat=polyvec.NTT_montgomery_vec(y)
    
    #𝐮 ← NTT−1(A^T∘𝐲)+𝐞1
    #first compute A^T
    A_hat_T=[[[] for j in range(K)] for i in range(K)]
    for i in range(K):
        for j in range(K):
            A_hat_T[i][j]=A_hat[j][i]
    #then compute A^T∘𝐲
    u=[0]*K
    for i in range(K):
        u[i]=polyvec.MultiplyNTT_montgomery_vec(A_hat_T[i],y_hat)
    u=polyvec.iNTT_montgomery_vec(u)
    u=polyvec.polyadd_vec(u,e1)
    
    #𝜇 ← Decompress1(ByteDecode1(𝑚))
    mu=[0]*params.MLKEM_N
    omega=converse_compress.byte_decode(1,m)
    for i in range(params.MLKEM_N):
        mu[i]=converse_compress.decompress(1,omega[i])
    #𝐯 ← NTT−1(t^T∘𝐲)+𝐞2+mu
    v=polyvec.MultiplyNTT_montgomery_vec(t_hat,y_hat)
    v=NTT.iNTT_montgomery(v)
    v=polyvec.polyadd(v,e2)
    v=polyvec.polyadd(v,mu)

    #compress and encode to get ciphertext
    c1=bytearray(32*du*K)
    compressed_u=u[:]
    for i in range(K):
        for j in range(params.MLKEM_N):
            compressed_u[i][j]=converse_compress.compress(du,u[i][j])
    for i in range(K):
        c1[i*(32*du):(i+1)*(32*du)]=converse_compress.byte_encode(du,compressed_u[i])
    
    c2=bytearray(32*dv)
    compressed_v=v[:]
    for i in range(params.MLKEM_N):
        compressed_v[i]=converse_compress.compress(dv,v[i])
    c2=converse_compress.byte_encode(dv,compressed_v)
    c=c1+c2

    return c
    




def faulty_KPKE_encrypt(ek_PKE,m,r,variant,a2):
    
    if variant==512:
        K=params.MLKEM512_K
        eta1=params.MLKEM512_eta1
        eta2=params.MLKEM512_eta2
        du=params.MLKEM512_du
        dv=params.MLKEM512_dv
    elif variant==768:
        K=params.MLKEM768_K
        eta1=params.MLKEM768_eta1
        eta2=params.MLKEM768_eta2
        du=params.MLKEM768_du
        dv=params.MLKEM768_dv
    elif variant==1024:
        K=params.MLKEM1024_K
        eta1=params.MLKEM1024_eta1
        eta2=params.MLKEM1024_eta2
        du=params.MLKEM1024_du
        dv=params.MLKEM1024_dv
    else:
        print("Invalid variant selected. Please select 512, 768 or 1024.")
        return None,None

    N=0

    # recover t_hat and rho from ek_PKE
    t_hat=[0]*K
    for i in range(K):
        t_hat[i]=converse_compress.byte_decode(12,ek_PKE[384*i:384*(i+1)])     #run ByteDecode12 𝑘 times to decode 𝐭 ∈ (ℤ256q)^{K}
    rho=ek_PKE[384*K:384*K+32]                                                  #extract 32-byte seed from ekPKE

    # recover matrix 𝐀∈ (ℤ256q)^{K×K}
    A_hat=[[[] for j in range(K)] for i in range(K)]
    for i in range(K):
        for j in range(K):
            A_hat[i][j]=converse_compress.SampleNTT(rho+ bytearray([j])+bytearray([i]))   #𝑗 and 𝑖 are bytes 33 and 34 of the input
    
    #generate 𝐲 ∈ (ℤ256_q)^{K}
    y=[[] for i in range(K)]
    for i in range(K):
        y[i]=converse_compress.SamplePolyCBD(eta1,keccak.faulty_PRF(eta1,r,bytearray([N]),a2))
        N+=1
    
    #generate e1 ∈ (ℤ256_q)^{K}
    e1=[[] for i in range(K)]
    for i in range(K):
        e1[i]=converse_compress.SamplePolyCBD(eta2,keccak.PRF(eta2,r,bytearray([N])))
        N+=1
    
    #generate e2 ∈ (ℤ256_q)
    e2=converse_compress.SamplePolyCBD(eta2,keccak.PRF(eta2,r,bytearray([N])))

    #run NTT 𝑘 times (once for each coordinate of y)
    y_hat=polyvec.NTT_montgomery_vec(y)
    
    #𝐮 ← NTT−1(A^T∘𝐲)+𝐞1
    #first compute A^T
    A_hat_T=[[[] for j in range(K)] for i in range(K)]
    for i in range(K):
        for j in range(K):
            A_hat_T[i][j]=A_hat[j][i]
    #then compute A^T∘𝐲
    u=[0]*K
    for i in range(K):
        u[i]=polyvec.MultiplyNTT_montgomery_vec(A_hat_T[i],y_hat)
    u=polyvec.iNTT_montgomery_vec(u)
    u=polyvec.polyadd_vec(u,e1)
    
    #𝜇 ← Decompress1(ByteDecode1(𝑚))
    mu=[0]*params.MLKEM_N
    omega=converse_compress.byte_decode(1,m)
    for i in range(params.MLKEM_N):
        mu[i]=converse_compress.decompress(1,omega[i])

    
    #𝐯 ← NTT−1(t^T∘𝐲)+𝐞2+mu
    v=polyvec.MultiplyNTT_montgomery_vec(t_hat,y_hat)
    v=NTT.iNTT_montgomery(v)
    v=polyvec.polyadd(v,e2)
    v=polyvec.polyadd(v,mu)

    #compress and encode to get ciphertext
    c1=bytearray(32*du*K)
    compressed_u=u[:]
    for i in range(K):
        for j in range(params.MLKEM_N):
            compressed_u[i][j]=converse_compress.compress(du,u[i][j])
    for i in range(K):
        c1[i*(32*du):(i+1)*(32*du)]=converse_compress.byte_encode(du,compressed_u[i])
    
    c2=bytearray(32*dv)
    compressed_v=v[:]
    for i in range(params.MLKEM_N):
        compressed_v[i]=converse_compress.compress(dv,v[i])
    c2=converse_compress.byte_encode(dv,compressed_v)
    c=c1+c2

    return c


#Uses the decryption key to decrypt a ciphertext.
# Input: decryption key dkPKE ∈ 𝔹384𝑘 .
# Input: ciphertext 𝑐 ∈ 𝔹32(𝑑𝑢𝑘+𝑑𝑣)
# Output: message 𝑚 ∈ 𝔹32.

def KPKE_decrypt(dk_PKE,c,variant=512):
    #select parameters based on variant
    if variant==512:
        K=params.MLKEM512_K
        du=params.MLKEM512_du
        dv=params.MLKEM512_dv
    elif variant==768:
        K=params.MLKEM768_K
        du=params.MLKEM768_du
        dv=params.MLKEM768_dv
    elif variant==1024:
        K=params.MLKEM1024_K
        du=params.MLKEM1024_du
        dv=params.MLKEM1024_dv
    else:
        print("Invalid variant selected. Please select 512, 768 or 1024.")
        return None,None

    # extract c1 and c2 from ciphertext
    c1=c[0:32*K*du]
    c2=c[32*K*du:32*K*du+32*dv]

    #decode and decompress c1 and c2 to get u_prime and v_prime
    u_prime=[0]*K
    for i in range(K):
        u_prime[i]=converse_compress.byte_decode(du,c1[i*(32*du):(i+1)*(32*du)])
    for i in range(K):
        for j in range(params.MLKEM_N):
            u_prime[i][j]=converse_compress.decompress(du,u_prime[i][j])
    
    v_prime=converse_compress.byte_decode(dv,c2)
    for i in range(params.MLKEM_N):
        v_prime[i]=converse_compress.decompress(dv,v_prime[i])
    
    s_hat=[0]*K
    for i in range(K):
        s_hat[i]=converse_compress.byte_decode(12,dk_PKE[384*i:384*(i+1)])
    
    #𝑤 ← v'-NTT^-1(s_hat^T ∘ NTT(u_prime))
    omega=polyvec.MultiplyNTT_montgomery_vec(s_hat,polyvec.NTT_montgomery_vec(u_prime))   # a poly
    omega=NTT.iNTT_montgomery(omega)
    omega=polyvec.polysub(v_prime,omega)

    #compress and encode omega to get message
    omega_compressed=[0]*params.MLKEM_N
    for i in range(params.MLKEM_N):
        omega_compressed[i]=converse_compress.compress(1,omega[i])
    m=converse_compress.byte_encode(1,omega_compressed)

    return m



#ML_KEM_INTERNAL
# Uses randomness to generate an encapsulation key and a corresponding decapsulation key.
# Input: randomness 𝑑 ∈ 𝔹32.
# Input: randomness 𝑧 ∈ 𝔹32.
# Output: encapsulation key ek ∈ 𝔹384𝑘+32.
# Output: decapsulation key dk ∈ 𝔹768𝑘+96
def MLKEM_keygen_internal(d,z,variant=512):
    ek_PKE,dk_PKE=KPKE_keygen(d,variant=variant)
    ek=ek_PKE
    dk=dk_PKE+ek
    Hek=bytearray(32)
    keccak.sha3_256(Hek,ek)
    dk+=Hek+z
    return ek,dk

def faulty_MLKEM_keygen_internal(d,z,variant,a1,a2):
    ek_PKE,dk_PKE=faulty_KPKE_keygen(d,variant,a1,a2)
    ek=ek_PKE
    dk=dk_PKE+ek
    Hek=bytearray(32)
    keccak.sha3_256(Hek,ek)
    dk+=Hek+z
    return ek,dk

# Uses the encapsulation key and randomness to generate a key and an associated ciphertext.
# Input: encapsulation key ek ∈ 𝔹384𝑘+32.
# Input: randomness 𝑚 ∈ 𝔹32.
# Output: shared secret key 𝐾 ∈ 𝔹32.
# Output: ciphertext 𝑐 ∈ 𝔹32(𝑑𝑢𝑘+𝑑𝑣)
def MLKEM_encaps_internal(ek,m,variant=512):
    Hek=bytearray(32)
    keccak.sha3_256(Hek,ek)
    buf=bytearray(64)
    keccak.sha3_512(buf,m+Hek)
    K=buf[:32]
    r=buf[32:]
    c=KPKE_encrypt(ek,m,r,variant=variant)
    return K,c

def faulty_MLKEM_encaps_internal(ek,m,variant,a1,a2):
    Hek=bytearray(32)
    keccak.sha3_256(Hek,ek)
    buf=bytearray(64)
    if a1==3:
        keccak.faulty_sha3_512(buf,m+Hek,a2)
    else:
        keccak.sha3_512(buf,m+Hek)
    K=buf[:32]
    r=buf[32:]
    if a1==4:
        c=faulty_KPKE_encrypt(ek,m,r,variant,a2)
    else:
        c=KPKE_encrypt(ek,m,r,variant=variant)
    return K,c

# Uses the decapsulation key to produce a shared secret key from a ciphertext.
# Input: decapsulation key dk ∈ 𝔹768𝑘+96.
# Input: ciphertext 𝑐 ∈ 𝔹32(𝑑𝑢𝑘+𝑑𝑣)
# Output: shared secret key 𝐾 ∈ 𝔹32.
def MLKEM_decaps_internal(dk,c,variant=512):
    if variant==512:
        K=params.MLKEM512_K
    elif variant==768:
        K=params.MLKEM768_K
    elif variant==1024:
        K=params.MLKEM1024_K
    else:
        print("Invalid variant selected. Please select 512, 768 or 1024.")
        return None
    
    #Decode dk
    dk_PKE=dk[:K*384]
    ek_PKE=dk[K*384:K*768+32]
    Hek=dk[K*768+32:K*768+64]
    z=dk[K*768+64:]

    #decrypt ciphertext
    m_prime=KPKE_decrypt(dk_PKE,c,variant=variant)

    buf=bytearray(64)
    keccak.sha3_512(buf,m_prime+Hek)
    K_prime=buf[:32]
    r_prime=buf[32:]

    K_bar=bytearray(32)
    keccak.shake256(K_bar,256,z+c)
    
    #re-encrypt and check
    c_prime=KPKE_encrypt(ek_PKE,m_prime,r_prime,variant=variant)
    if c_prime!=c:
        return K_bar
    return K_prime


def faulty_MLKEM_decaps_internal(dk,c,variant,a1,a2):
    if variant==512:
        K=params.MLKEM512_K
    elif variant==768:
        K=params.MLKEM768_K
    elif variant==1024:
        K=params.MLKEM1024_K
    else:
        print("Invalid variant selected. Please select 512, 768 or 1024.")
        return None
    
    #Decode dk
    dk_PKE=dk[:K*384]
    ek_PKE=dk[K*384:K*768+32]
    Hek=dk[K*768+32:K*768+64]
    z=dk[K*768+64:]

    #decrypt ciphertext
    m_prime=KPKE_decrypt(dk_PKE,c,variant=variant)

    buf=bytearray(64)
    if a1==5:
        keccak.faulty_sha3_512(buf,m_prime+Hek,a2)
    else:
        keccak.sha3_512(buf,m_prime+Hek)
    K_prime=buf[:32]
    r_prime=buf[32:]

    K_bar=bytearray(32)
    keccak.shake256(K_bar,256,z+c)
    
    #re-encrypt and check
    c_prime=KPKE_encrypt(ek_PKE,m_prime,r_prime,variant=variant)
    return K_prime

def faulty_MLKEM_decaps_internal2(dk,c,variant,a1,a2):
    if variant==512:
        K=params.MLKEM512_K
    elif variant==768:
        K=params.MLKEM768_K
    elif variant==1024:
        K=params.MLKEM1024_K
    else:
        print("Invalid variant selected. Please select 512, 768 or 1024.")
        return None
    
    #Decode dk
    dk_PKE=dk[:K*384]
    ek_PKE=dk[K*384:K*768+32]
    Hek=dk[K*768+32:K*768+64]
    z=dk[K*768+64:]

    #decrypt ciphertext
    m_prime=KPKE_decrypt(dk_PKE,c,variant=variant)

    buf=bytearray(64)
    keccak.sha3_512(buf,m_prime+Hek)
    K_prime=buf[:32]
    r_prime=buf[32:]

    K_bar=bytearray(32)
    ctx=keccak.shake256_inc_init()
    keccak.faulty_shake256_inc_absorb(ctx,z)
    keccak.shake256_inc_absorb(ctx,c)
    keccak.shake256_inc_finalize(ctx)
    keccak.shake256_inc_squeeze(K_bar,32,ctx)
    
    #re-encrypt and check
    c_prime=KPKE_encrypt(ek_PKE,m_prime,r_prime,variant=variant)
    return K_bar


# REAL MLKEM functions

# Generates an encapsulation key and a corresponding decapsulation key.
# Output: encapsulation key ek ∈ 𝔹384𝑘+32.
# Output: decapsulation key dk ∈ 𝔹768𝑘+96
def MLKEM_keygen(variant=512):
    d = bytearray(random.getrandbits(8) for _ in range(32))
    z = bytearray(random.getrandbits(8) for _ in range(32))
    if d==None or z==None:
        print("Error generating randomness.")
        return None,None
    ek,dk=MLKEM_keygen_internal(d,z,variant=variant)
    return ek,dk

def faulty_MLKEM_keygen(variant,a1,a2):
    d = bytearray(random.getrandbits(8) for _ in range(32))
    z = bytearray(random.getrandbits(8) for _ in range(32))
    if d==None or z==None:
        print("Error generating randomness.")
        return None,None
    ek,dk=faulty_MLKEM_keygen_internal(d,z,variant,a1,a2)
    return ek,dk

# Uses the encapsulation key to generate a shared secret key and an associated ciphertext.
# Checked input: encapsulation key ek ∈ 𝔹384𝑘+32.
# Output: shared secret key 𝐾 ∈ 𝔹32.
# Output: ciphertext 𝑐 ∈ 𝔹32(𝑑𝑢𝑘+𝑑𝑣)
def MLKEM_encaps(ek,variant=512):
    m = bytearray(random.getrandbits(8) for _ in range(32))
    if m==None:
        print("Error generating randomness.")
        return None,None
    K,c=MLKEM_encaps_internal(ek,m,variant=variant)
    return K,c

def faulty_MLKEM_encaps(ek,variant,a1,a2):
    m = bytearray(random.getrandbits(8) for _ in range(32))
    if m==None:
        print("Error generating randomness.")
        return None,None
    K,c=faulty_MLKEM_encaps_internal(ek,m,variant,a1,a2)
    return K,c

# Uses the decapsulation key to produce a shared secret key from a ciphertext.
# Checked input: decapsulation key dk ∈ 𝔹768𝑘+96.
# Checked input: ciphertext 𝑐 ∈ 𝔹32(𝑑𝑢𝑘+𝑑𝑣).
# Output: shared secret key 𝐾 ∈ 𝔹32.
def MLKEM_decaps(dk,c,variant=512):
    K_prime=MLKEM_decaps_internal(dk,c,variant=variant)
    return K_prime

def faulty_MLKEM_decaps(dk,c,variant,a1,a2):
    K_prime=faulty_MLKEM_decaps_internal(dk,c,variant,a1,a2)
    return K_prime

def faulty_MLKEM_decaps2(dk,c,variant,a1,a2):
    K_prime=faulty_MLKEM_decaps_internal2(dk,c,variant,a1,a2)
    return K_prime






#########################################################################################################
#simple tests
if __name__=="__main__":
    # seed="109a248fe8052f84271ff57bac156b1ba6a509cdcdbcc96ccdb1ccb85ca49315"
    # d=bytearray.fromhex(seed)

    print("Testing KPKE keygen and encryption/decryption...")
    d=bytearray(32)
    for i in range(32):
        d[i]=random.getrandbits(8)
    ek_PKE,dk_PKE=KPKE_keygen(d,variant=512)


    m=bytearray(32)
    for i in range(32):
        m[i]=random.getrandbits(8)
    r=bytearray(32)
    for i in range(32):
        r[i]=random.getrandbits(8)
    c=KPKE_encrypt(ek_PKE,m,r,variant=512)

    m1=KPKE_decrypt(dk_PKE,c,variant=512)
    if m1==m:
        print("successful.")
    else:
        print("failed.")
    # print(m1.hex())



    print("Testing MLKEM_keygen and MLKEM_encaps and MLKEM_decaps (internal)...")
    ek,dk=MLKEM_keygen_internal(d,d,variant=512)
    # print(ek.hex())
    # print(dk.hex())
    # mseed="fcc3ddd244e3c338758ff2097ae171c850f5405ba43ba6b3ec54d3722d0fc165"
    # m=bytearray.fromhex(mseed)
    # ekseed="56d118aa5b6ecdd0ba14961f68b60cf89cb521f9366c92aa50fabfe82a8f8353887cc34e3f8bb16ee48cf62bad343670f913338c213edd04193ab811bae8200a2a7f8e988ef4862587f95962d668af753f89b41e1bc314ecac2039086323db3ba015141b26a24edc1a2b03165c3186cf4798acd6b457bacd5e5bc21af977ea4c05576777cb198752a239fe7abc6eb15271f0680d7860f9619f3a684985e3b131f78e36f09922428cf4e7365116b08c83a5f1db9c44e04afbf64af20378033c62e8e554e8783b3cc923c5e96d8e849a775597b3c1b399cb98c44bc2b6b9cb35589d078ab5639964c7fa8cfb87224524c5b4a357abd35d572a48b0a090a430a9a05aa965a6c5c29821b3921eab93b71a5a125979b434ecc1c556bb6568befe68202d434977599df911cde0018330c62aa8e66118e287853bc594481834b366b236595a9022b588968cdc5b12cb422737a9396130e5a66a2dfb2eebb2bdc87419a06b39577916c7b31f7c94541ac53f89d5a86b90113e118daeb6a9140a75c41c16a640cf973a5a59823f95d09b36d7bc705606ac43cfee9644626b872e40a6e807b6e1145588b36256d4cab1f9529c5c1eb99abf422245161c89b359b96a33c8cab9b358b58e42212fbdb6acdf54c65c1725759c3878573c59133bae3572ac1b1c313bb07d423350690f1ceca991135a27ac529eca069470bdc0595a317b8147309936265cdc3821c4156fcbf53e1c129d84eb5a20f95bddbb1e09a35d88d49a94e80703584574c6809317ca18f1bdeb23cec48c12e73765e371be21b5c832734f7992c04e2216aed04f2b9647876449100b458d5a1c02f4272ca24584c688c9b57e2c66c63a1a021a74a8f448542a2bc9fa76462076340b973bf28015cb832665f77d585bc0150aa0ea2a1b562a3558377dddd0c3ef952accb41d3f25cac0dc0c0ca38721d4b701696894919b7d54177cd9cb26f056d4c8733cb54b0475b4795a7391aa453281c7e096493ecabaf331a7e785799468b5cd4a6dff325595b4c93f749dd5e933d3039a5c507719267e737b5811326aec0267445a74829086dccbafddf670ac2fc7d2543e6d4add0121dd82857b80afc88a672eff9f32b53ff434d7"
    # ek=bytearray.fromhex(ekseed)
    k,c=MLKEM_encaps_internal(ek,m,variant=512)
    # print(k.hex())
    # print(c.hex())
    # dkseed="d0bcce7ba24c8f607e482a7f33e134df5a13fe8075f8272e03483c40b65b7d912509bc27b8c52602cba1c96458619aa8df70601d68686a919bb672a405e7017cd6a43db78c10c477ebc17daf68b284b487b2aa76bcfa090d9965de853518dc4a93927017b4b2ccf45cd51226d0f74d63a350578375481b692840a16b2471a64069ae6ac527fb86a57b81ff5067c612aca70a0ed14c3f286b9b8a36041937caff8c5c62dbac272959adb833ef63523e089b5e1327641b1af3d4944454ce1ebc19b4d151ec406b1ea8aa8f6523c0b53ff7a20081f35f222a95ab667141babc8446bc8f728eb9dc98e0852eea1ab4c695a006c338b584b48f104e0bc21dc8905e4582c05dd5226d3cac422cbea0450da8c28bf4e81a872b67d1385d27d54d37293522bb243be14f3869108ed9aaa64384f01b14f2e59ba2e9ae6ddb848885cc623787357022754a4f7b8a6b8d48afbf8a72167c49cb32a3f750ba316cb8c88514b4d56dae87cd510a25994856d68a292ec650360b813e33559d0b9f123326fa574e5c15428d902230018280f73bbdb0cbdac436f2d4bad50286e766991df63bd4b57b432443d075052caab180b0cf42c35897343a1a69ab93910c41766693eb37692bccf1508fef06b5a9d297bf749fc8194de5264daca5920c909a542c419c868e1429a34b7ca47e941f43aa7a6b99c8498a7c5af9c994a367c14182cd64b338f106c33754cda4990ef466ce262766dc191e2b9bffc7258fb878d48b86644223dfa471885c9212811f44d0b6a8602d93b2c1ade1157c5558452193b51202950451157b2612393abeb25b45f70e18a0b612355b004001836b5183ac3904eb8bbc3850926897e5d27d43f1ac466487000d6a6ec79facc35b1dbbb8d02409f92c4dd5c6334c9b878bf01666b3c5a01cce0b18a2ca4910354b6042446a6ed6ce3aa5a844d7cb11aba66c495eafc67fbeda3687350d3096bcfb37965f587467a6b62c7146f1f28769da9244a22003cb17353460788944cc6aa06d6b5f58d0398c3778b326ba12474961fa9ef12cb8bd9963d3ca79a28116886a6bf2b601cee155562997ff8b0218d34b0a7cb52902bcbee2c2f41878a73509e999090622a404079cd4b29dda058064d2457817758fe468fc76b95b994bee5768d34c3ed60124364ac98e583f405680cbe0c37e016eb5f091093825734c36c2296724e8ca04632caca3a2da293a23606159947d57d97601f43ab278988f509748272d86c2b4d2419af403a5bfa356c788525775b5709ca52727a432f4205966350ff5b14ad0906d2477212166286578c97968e7cc97b15b5186214b54297a3fa522b2f5a0a54c90723c091382585e1725a3b4c98159852be39848d6432e4401e91b3bd136b8eeb15998e31aa5f667d9329586926f540b10dc583b2c6a2571657b91e217504ca4e9938c4d5343eb7b7905939787c6380aa2c67d667e485c8427a8b23daca033cc6e01f5a250865422f43b32f6290a88848d6359ac498f28892293b2a52bc17bbed833561b96b15778fb741b7e4ba889472d1ac58a9537a065e38e6337cfc3115b243953be2467ef3b507de13dad619b657b92ed8b8d46b58746fc6428315478ab1bb8b6b3a37424b74428e6d7819c81aadaf1920770c49b266f7880931128592ac564effc7f896ac1104cae391c9e491730248b25872c58171227fd221b21ac72d96b64327539b1d4351f239027956e8d404b6002b1d36b7b7b430b5c43179578bd4b775c2ab53f9e878f36e2ba6c539c67694f60126423b88581b8bb8e804342850f802a27eb2941547a43fe2292c2cc1e9bc503d4322be036239c112841d140a1d7cd202b3e64806f5fa2964094bf842705765540ea1032b0fc5c57e30b27c17292d1b0f615cb8adc8fb0132dfc6a49c37857880370f4e2b84ff448c30c10ace52ca2ec88c304c00a831a7027239548a67096713e1b0de7898d4df6877e7491449015d7e64b00d5cecbacba0291bd38a43c6dd63a20074556e2b3fb1b285c6185f551b7e906ab8f41102f927cae12981eeba3a2c76e2649a8315c071407bb31c7503ffc5629e9a46d874a60cbc51ed2c71db803f83446bf5709f735c55155766b6461561a4a39813c1cc056f5b8c96ea334aa30562f341752831e7f314f6630829ee2229e8aa9706921f94f6cb2bdcafc0c088a4463cbef9505481bba2d0dafda0eeab07aa575f82eb869a4231c3096595bf5ee87ef2c8540865e836799029d25a437ce73c2c2973458560e2ed2123d247ba7f81fae824e5f93596b5759991f79299826"
    # dk=bytearray.fromhex(dkseed)
    # cseed="4750315128b640a8bf381290871193d1c4a9b77dacb8afecacbe89cf6d92eee08147e96f491687df2eb7c4562b7ff72001ec7fa0864c3512fe0698ce32ac5412d75a80a647ed6a4c15253766ebd8db72e778c45c58caa45b76cd473127525edf7efe5f443c5670f3b4353cdf080e3d589d4cde7dfa7b5604b24c0d7b844bfbee3c7923c33c334bf460ab522d99735c5648a8000d173ba94e22fb212180a2c9f007670e1e7d3d51f4968e648289e634fd36e93aaa2ad1183d30b321cd1f983fe435226c5c9ed11cfe6a8e16469509de853cf80440289febb0b3327c46ee4693cf267f566a7f98864998256488613575674f3927376f31c87ae83eba2627dfc5f14e1d65bfbd26c8e242aaf91aca3db4188856b816dbea36c669082100f4ace32e00683dfe55142aaaf74133d075661f01edacd902a1910949b8d9db4f0a09b443dd7f9089851816d0a8c2b79e6c22154ad79881b5225e2bf7cbfcb101a27cded887494b89a596b2c47eb70d73b5ea5a39322d9f368465b4f45300b7ea5ed8e4c1735d784a8d639bb24fea5b5f3beed83b038671c302ad7c7a82b5000f00079c93b6d6962e43157b6f3a89831630e778101f2a2537ba2fabc0e856d2356a1d79cb5b3e71380efeaf84245ecf7bbf6cf361745a5c7e6817dbe94bad5cfa053e487ce4fba401a015cf340a4aa3be032b0264689e6d9882815dbad83b6f2af97f37376386e65f0dd0b84b824374fee6918c03ec1e419602e47187f3d920437fc4f7570fb0407f6b369844f6961ee97e46226a3bcd695535e4ed5dedfa1d958148609bd9fa6b2e5d81f1ff2bc94c8933a87abf81089bef966e5d7d2a1cd406aa5b4b643247399403c981a274a836dfa60a724c56bedcb98ec7d2ce2c02acddde5ecd53c2809466a6dee9f97f8a1100c305b6fb8128005fc45994fac6ae398b2b43790065e12f262d06bb6c1a01284f36b03bbfe15a044bd363c6574df23cde32adf4be9d68216b17861d1035e6dc9a3a92978220c94d5b71886ffb04e1eb60b44fa33263024ece7afb6467c25a948d95de962e81073e64164820398043d2642d8e9d04"
    # c=bytearray.fromhex(cseed)
    kprime=MLKEM_decaps_internal(dk,c,variant=512)
    # print(kprime.hex())
    if k==kprime:
        print("successful.")
    else:
        print("failed.")
    # print(kprime.hex())



    print("Testing MLKEM_keygen and MLKEM_encaps and MLKEM_decaps (external)...")
    ek,dk=MLKEM_keygen()
    k,c=MLKEM_encaps(ek)
    kprime=MLKEM_decaps(dk,c)
    if k==kprime:
        print("successful.")
    else:
        print("failed.")
    #print(kprime.hex())

    