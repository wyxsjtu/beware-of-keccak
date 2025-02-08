import params
import converse
import keccak
import sample
import NTT
import compress
import encode

import random


def infinity_norm(l,v):
    maxv=0
    for i in range(l):
        for j in range(params.MLDSA_N):
            if v[i][j]>params.MLDSA_Q//2:
                v[i][j]-=params.MLDSA_Q
            maxv=max(maxv,abs(v[i][j]))
    return maxv 


# Generates a public-private key pair from a seed.
# Input: Seed 𝜉 ∈ 𝔹32
# Output: Public key 𝑝𝑘 ∈ 𝔹32+32𝑘(bitlen (𝑞−1)−𝑑) and private key 𝑠𝑘 ∈ 𝔹32+32+64+32⋅((ℓ+𝑘)⋅bitlen (2𝜂)+𝑑𝑘)
def MLDSA_KeyGen_Internal(xi,variant=44):
    #select parameters based on variant
    if variant==44:
        k=params.MLDSA44_k
        l=params.MLDSA44_l
        eta=params.MLDSA44_eta
    elif variant==65:
        k=params.MLDSA65_k
        l=params.MLDSA65_l
        eta=params.MLDSA65_eta
    elif variant==87:
        k=params.MLDSA87_k
        l=params.MLDSA87_l
        eta=params.MLDSA87_eta
    else:
        print("Invalid variant selected. Please select 44, 65, or 87.")
        return None,None
    
    #expand seed
    seeds=bytearray(128)
    seeds[0:32]=xi
    seeds[32:33]=converse.IntegerToBytes(k,1)
    seeds[33:34]=converse.IntegerToBytes(l,1)
    keccak.shake256(seeds,128*8,seeds[:34])
    rho=seeds[:32]
    rho_prime=seeds[32:96]
    K=seeds[96:128]

    # 𝐀 is generated and stored in NTT representation as A_hat
    A_hat=sample.ExpandA(k,l,rho)
    
    # Sample s1 and s2
    s1,s2=sample.ExpandS(eta,k,l,rho_prime)
    
    # MLWE instance in NTT domain
    s1_hat=NTT.NTT_vec(s1)
    t_hat=NTT.MatrixVectorNTT(k,l,A_hat,s1_hat)
    t=NTT.iNTT_vec(t_hat)
    t=NTT.AddVectorNTT(k,t,s2)
    
    # PowerTwoRound is applied componentwise
    t1=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
    t0=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
    for i in range(k):
        for j in range(params.MLDSA_N):
            t1[i][j],t0[i][j]=compress.Power2Round(t[i][j])
    
    # encode pk and sk
    pk=encode.pkEncode(eta,k,rho,t1)
    tr=bytearray(64)
    keccak.shake256(tr,64*8,pk)
    sk=encode.skEncode(eta,k,l,rho,K,tr,s1,s2,t0)
    
    return pk,sk


def faulty_MLDSA_KeyGen_Internal(xi,variant,a1,a2):
    #select parameters based on variant
    if variant==44:
        k=params.MLDSA44_k
        l=params.MLDSA44_l
        eta=params.MLDSA44_eta
    elif variant==65:
        k=params.MLDSA65_k
        l=params.MLDSA65_l
        eta=params.MLDSA65_eta
    elif variant==87:
        k=params.MLDSA87_k
        l=params.MLDSA87_l
        eta=params.MLDSA87_eta
    else:
        print("Invalid variant selected. Please select 44, 65, or 87.")
        return None,None
    
    #expand seed
    seeds=bytearray(128)
    seeds[0:32]=xi
    seeds[32:33]=converse.IntegerToBytes(k,1)
    seeds[33:34]=converse.IntegerToBytes(l,1)
    if a1==1:
        keccak.faulty_shake256(seeds,128*8,seeds[:34],a2)
    else:
        keccak.shake256(seeds,128*8,seeds[:34])
    rho=seeds[:32]
    rho_prime=seeds[32:96]
    K=seeds[96:128]

    # 𝐀 is generated and stored in NTT representation as A_hat
    A_hat=sample.ExpandA(k,l,rho)
    
    # Sample s1 and s2
    if a1==2:
        s1,s2=sample.faulty_ExpandS(eta,k,l,rho_prime,a2)
    else:
        s1,s2=sample.ExpandS(eta,k,l,rho_prime)
    
    # print(s1)
    # MLWE instance in NTT domain
    s1_hat=NTT.NTT_vec(s1)
    t_hat=NTT.MatrixVectorNTT(k,l,A_hat,s1_hat)
    t=NTT.iNTT_vec(t_hat)
    t=NTT.AddVectorNTT(k,t,s2)
    
    # PowerTwoRound is applied componentwise
    t1=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
    t0=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
    for i in range(k):
        for j in range(params.MLDSA_N):
            t1[i][j],t0[i][j]=compress.Power2Round(t[i][j])
    
    # encode pk and sk
    pk=encode.pkEncode(eta,k,rho,t1)
    tr=bytearray(64)
    keccak.shake256(tr,64*8,pk)
    sk=encode.skEncode(eta,k,l,rho,K,tr,s1,s2,t0)
    
    return pk,sk



# Deterministic algorithm to generate a signature for a formatted message 𝑀′.
# Input: Private key 𝑠𝑘 ∈ 𝔹32+32+64+32⋅((ℓ+𝑘)⋅bitlen (2𝜂)+𝑑𝑘), formatted message 𝑀′ ∈ {0, 1}∗, and
# per message randomness or dummy variable 𝑟𝑛𝑑 ∈ 𝔹32.
# Output: Signature 𝜎 ∈ 𝔹𝜆/4+ℓ⋅32⋅(1+bitlen (𝛾1−1))+𝜔+𝑘.
def MLDSA_Sign_Internal(sk,M_prime,rnd,variant=44):
    #select parameters based on variant
    if variant==44:
        k=params.MLDSA44_k
        l=params.MLDSA44_l
        eta=params.MLDSA44_eta
        gamma1=params.MLDSA44_gamma1
        gamma2=params.MLDSA44_gamma2
        lambda_c=params.MLDSA44_lambda
        tao=params.MLDSA44_tao
        beta=params.MLDSA44_beta
        omega=params.MLDSA44_omega
    elif variant==65:
        k=params.MLDSA65_k
        l=params.MLDSA65_l
        eta=params.MLDSA65_eta
        gamma1=params.MLDSA65_gamma1
        gamma2=params.MLDSA65_gamma2
        lambda_c=params.MLDSA65_lambda
        tao=params.MLDSA65_tao
        beta=params.MLDSA65_beta
        omega=params.MLDSA65_omega
    elif variant==87:
        k=params.MLDSA87_k
        l=params.MLDSA87_l
        eta=params.MLDSA87_eta
        gamma1=params.MLDSA87_gamma1
        gamma2=params.MLDSA87_gamma2
        lambda_c=params.MLDSA87_lambda
        tao=params.MLDSA87_tao
        beta=params.MLDSA87_beta
        omega=params.MLDSA87_omega
    else:
        print("Invalid variant selected. Please select 44, 65, or 87.")
        return None,None
    
    #decode sk
    rho,K,tr,s1,s2,t0=encode.skDecode(eta,k,l,sk)

    # to NTT domain
    s1_hat=NTT.NTT_vec(s1)                                                      # s1_hat l*256
    s2_hat=NTT.NTT_vec(s2)                                                      # s2_hat k*256
    t0_hat=NTT.NTT_vec(t0)                                                      # t0_hat k*256  

    # recover A_hat
    A_hat=sample.ExpandA(k,l,rho)                                               # A_hat k*l*256 

    # 𝜇 ← H(BytesToBits(𝑡𝑟)||𝑀′, 64)
    mu=bytearray(64)                                                             # mu 64 bytes    
    ctx=keccak.shake256_inc_init()
    keccak.shake256_inc_absorb(ctx,tr)
    keccak.shake256_inc_absorb(ctx,M_prime)
    keccak.shake256_inc_finalize(ctx)
    keccak.shake256_inc_squeeze(mu,64,ctx)

    rho_2prime=bytearray(64)                                                   # rho_2prime 64 bytes
    keccak.shake256(rho_2prime,64*8,K+rnd+mu)
    kappa=0
    z,h=None,None
    while z is None and h is None:
        y=sample.ExpandMask(l,gamma1,rho_2prime,kappa)                              # y l*256
        #𝐰 ← NTT−1(𝐀 ∘̂ NTT(𝐲))   𝐰1 ← HighBits(𝐰)    signer’s commitment
        y_hat=NTT.NTT_vec(y)                                                     # y_hat l*256
        w_hat=NTT.MatrixVectorNTT(k,l,A_hat,y_hat)                                  # w_hat k*256
        w=NTT.iNTT_vec(w_hat)                                                    # w k*256
        w1=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
        for i in range(k):
            for j in range(params.MLDSA_N):
                w1[i][j]=compress.HighBits(gamma2,w[i][j])                        # w1 k*256
        
        #sample c
        lenc_tilde=lambda_c//4
        c_tilde=bytearray(lenc_tilde)
        keccak.shake256(c_tilde,lenc_tilde*8,mu+encode.w1Encode(gamma2,k,w1))
        c=sample.SampleInBall(tao,c_tilde)                                         # c poly 256
        c_hat=NTT.NTT_montgomery(c)                                             # c_hat poly 256
        
        #compute z
        z=NTT.ScalarVectorNTT(l,c_hat,s1_hat)                                     # z l*256
        z=NTT.iNTT_vec(z)
        z=NTT.AddVectorNTT(l,y,z)                                               # z l*256
        
        #conditional checks
        cs2=NTT.ScalarVectorNTT(k,c_hat,s2_hat)
        cs2=NTT.iNTT_vec(cs2)                                                    # cs2 k*256
        r0_poly=NTT.SubVectorNTT(k,w,cs2)                                         # r0_poly k*256
        r0=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
        for i in range(k):
            for j in range(params.MLDSA_N):
                r0[i][j]=compress.LowBits(gamma2,r0_poly[i][j])
        max_z=infinity_norm(l,z)
        max_r0=infinity_norm(k,r0)
        if max_z>=gamma1-beta or max_r0>=gamma2-beta:
            z,h=None,None
        else:
            ct0=NTT.ScalarVectorNTT(k,c_hat,t0_hat)                                   # ct0 k*256
            ct0=NTT.iNTT_vec(ct0)
            zeros=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
            minus_ct0=NTT.SubVectorNTT(k,zeros,ct0)                                  # minus_ct0 k*256
            w_approx=NTT.AddVectorNTT(k,r0_poly,ct0)
            h=compress.MakeHints_vec(k,gamma2,minus_ct0,w_approx)                       # h k*256
            max_ct0=infinity_norm(k,ct0)
            hw_h=0
            for i in range(k):
                for j in range(params.MLDSA_N):
                    hw_h+=h[i][j]
            if max_ct0>=gamma2 or hw_h>omega:
                z,h=None,None
        kappa+=l
    sig=encode.sigEncode(omega,k,l,gamma1,c_tilde,z,h)
    return sig

def faulty_MLDSA_Sign_Internal(sk,M_prime,rnd,variant,a1,a2):
    #select parameters based on variant
    if variant==44:
        k=params.MLDSA44_k
        l=params.MLDSA44_l
        eta=params.MLDSA44_eta
        gamma1=params.MLDSA44_gamma1
        gamma2=params.MLDSA44_gamma2
        lambda_c=params.MLDSA44_lambda
        tao=params.MLDSA44_tao
        beta=params.MLDSA44_beta
        omega=params.MLDSA44_omega
    elif variant==65:
        k=params.MLDSA65_k
        l=params.MLDSA65_l
        eta=params.MLDSA65_eta
        gamma1=params.MLDSA65_gamma1
        gamma2=params.MLDSA65_gamma2
        lambda_c=params.MLDSA65_lambda
        tao=params.MLDSA65_tao
        beta=params.MLDSA65_beta
        omega=params.MLDSA65_omega
    elif variant==87:
        k=params.MLDSA87_k
        l=params.MLDSA87_l
        eta=params.MLDSA87_eta
        gamma1=params.MLDSA87_gamma1
        gamma2=params.MLDSA87_gamma2
        lambda_c=params.MLDSA87_lambda
        tao=params.MLDSA87_tao
        beta=params.MLDSA87_beta
        omega=params.MLDSA87_omega
    else:
        print("Invalid variant selected. Please select 44, 65, or 87.")
        return None,None
    
    #decode sk
    rho,K,tr,s1,s2,t0=encode.skDecode(eta,k,l,sk)

    # to NTT domain
    s1_hat=NTT.NTT_vec(s1)                                                      # s1_hat l*256
    s2_hat=NTT.NTT_vec(s2)                                                      # s2_hat k*256
    t0_hat=NTT.NTT_vec(t0)                                                      # t0_hat k*256  

    # recover A_hat
    A_hat=sample.ExpandA(k,l,rho)                                               # A_hat k*l*256 

    # 𝜇 ← H(BytesToBits(𝑡𝑟)||𝑀′, 64)
    mu=bytearray(64)                                                             # mu 64 bytes    
    ctx=keccak.shake256_inc_init()
    keccak.shake256_inc_absorb(ctx,tr)
    keccak.shake256_inc_absorb(ctx,M_prime)
    keccak.shake256_inc_finalize(ctx)
    keccak.shake256_inc_squeeze(mu,64,ctx)

    rho_2prime=bytearray(64)  
    if a1==3:                                                 # rho_2prime 64 bytes
        keccak.faulty_shake256(rho_2prime,64*8,K+rnd+mu,a2)
    else:
        keccak.shake256(rho_2prime,64*8,K+rnd+mu)
    #print(rho_2prime.hex())
    kappa=0
    z,h=None,None
    while z is None and h is None:
        y=sample.ExpandMask(l,gamma1,rho_2prime,kappa)                              # y l*256
        #𝐰 ← NTT−1(𝐀 ∘̂ NTT(𝐲))   𝐰1 ← HighBits(𝐰)    signer’s commitment
        y_hat=NTT.NTT_vec(y)                                                     # y_hat l*256
        w_hat=NTT.MatrixVectorNTT(k,l,A_hat,y_hat)                                  # w_hat k*256
        w=NTT.iNTT_vec(w_hat)                                                    # w k*256
        w1=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
        for i in range(k):
            for j in range(params.MLDSA_N):
                w1[i][j]=compress.HighBits(gamma2,w[i][j])                        # w1 k*256
        
        #sample c
        lenc_tilde=lambda_c//4
        c_tilde=bytearray(lenc_tilde)
        keccak.shake256(c_tilde,lenc_tilde*8,mu+encode.w1Encode(gamma2,k,w1))
        c=sample.SampleInBall(tao,c_tilde)                                         # c poly 256
        c_hat=NTT.NTT_montgomery(c)                                             # c_hat poly 256
        
        #compute z
        z=NTT.ScalarVectorNTT(l,c_hat,s1_hat)                                     # z l*256
        z=NTT.iNTT_vec(z)
        z=NTT.AddVectorNTT(l,y,z)                                               # z l*256
        
        #conditional checks
        cs2=NTT.ScalarVectorNTT(k,c_hat,s2_hat)
        cs2=NTT.iNTT_vec(cs2)                                                    # cs2 k*256
        r0_poly=NTT.SubVectorNTT(k,w,cs2)                                         # r0_poly k*256
        r0=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
        for i in range(k):
            for j in range(params.MLDSA_N):
                r0[i][j]=compress.LowBits(gamma2,r0_poly[i][j])
        max_z=infinity_norm(l,z)
        max_r0=infinity_norm(k,r0)
        if max_z>=gamma1-beta or max_r0>=gamma2-beta:
            z,h=None,None
        else:
            ct0=NTT.ScalarVectorNTT(k,c_hat,t0_hat)                                   # ct0 k*256
            ct0=NTT.iNTT_vec(ct0)
            zeros=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
            minus_ct0=NTT.SubVectorNTT(k,zeros,ct0)                                  # minus_ct0 k*256
            w_approx=NTT.AddVectorNTT(k,r0_poly,ct0)
            h=compress.MakeHints_vec(k,gamma2,minus_ct0,w_approx)                       # h k*256
            max_ct0=infinity_norm(k,ct0)
            hw_h=0
            for i in range(k):
                for j in range(params.MLDSA_N):
                    hw_h+=h[i][j]
            if max_ct0>=gamma2 or hw_h>omega:
                z,h=None,None
        kappa+=l
    sig=encode.sigEncode(omega,k,l,gamma1,c_tilde,z,h)
    return sig



# Internal function to verify a signature 𝜎 for a formatted message 𝑀′.
# Input: Public key 𝑝𝑘 ∈ 𝔹32+32𝑘(bitlen (𝑞−1)−𝑑) and message 𝑀′ ∈ {0, 1}∗.
# Input: Signature 𝜎 ∈ 𝔹𝜆/4+ℓ⋅32⋅(1+bitlen (𝛾1−1))+𝜔+𝑘.
# Output: Boolean
def MLDSA_Verify_Internal(pk,M_prime,sig,variant=44):
    #select parameters based on variant
    if variant==44:
        k=params.MLDSA44_k
        l=params.MLDSA44_l
        eta=params.MLDSA44_eta
        gamma1=params.MLDSA44_gamma1
        gamma2=params.MLDSA44_gamma2
        lambda_c=params.MLDSA44_lambda
        tao=params.MLDSA44_tao
        beta=params.MLDSA44_beta
        omega=params.MLDSA44_omega
    elif variant==65:
        k=params.MLDSA65_k
        l=params.MLDSA65_l
        eta=params.MLDSA65_eta
        gamma1=params.MLDSA65_gamma1
        gamma2=params.MLDSA65_gamma2
        lambda_c=params.MLDSA65_lambda
        tao=params.MLDSA65_tao
        beta=params.MLDSA65_beta
        omega=params.MLDSA65_omega
    elif variant==87:
        k=params.MLDSA87_k
        l=params.MLDSA87_l
        eta=params.MLDSA87_eta
        gamma1=params.MLDSA87_gamma1
        gamma2=params.MLDSA87_gamma2
        lambda_c=params.MLDSA87_lambda
        tao=params.MLDSA87_tao
        beta=params.MLDSA87_beta
        omega=params.MLDSA87_omega
    else:
        print("Invalid variant selected. Please select 44, 65, or 87.")
        return None,None
    
    #decode pk
    rho,t1=encode.pkDecode(eta,k,pk)                                              # rho 32 bytes, t1 k*256

    #decode signature
    c_tilde,z,h=encode.sigDecode(lambda_c,omega,k,l,gamma1,sig)

    if h is None:
        return False
    
    #recover A_hat and tr
    A_hat=sample.ExpandA(k,l,rho)                                               # A_hat k*l*256 
    tr=bytearray(64)                                                             # tr 64 bytes
    keccak.shake256(tr,64*8,pk)

    # recover mu
    mu=bytearray(64)                                                             # mu 64 bytes    
    ctx=keccak.shake256_inc_init()
    keccak.shake256_inc_absorb(ctx,tr)
    keccak.shake256_inc_absorb(ctx,M_prime)
    keccak.shake256_inc_finalize(ctx)
    keccak.shake256_inc_squeeze(mu,64,ctx)

    #recover c
    c=sample.SampleInBall(tao,c_tilde)

    # 𝐰′approx ← NTT−1(𝐀 ∘̂ NTT(𝐳) − NTT(𝑐) ∘ NTT(𝐭1 ⋅ 2𝑑)) 
    z_hat=NTT.NTT_vec(z)                                                         # z_hat l*256
    w_approx_prime=NTT.MatrixVectorNTT(k,l,A_hat,z_hat)                            # w_approx_prime k*256
    ct1_mul2d=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
    for i in range(k):
        for j in range(params.MLDSA_N):
            ct1_mul2d[i][j]=t1[i][j]<<params.MLDSA_D                                       # t1*2^d
    ct1_mul2d=NTT.NTT_vec(ct1_mul2d)                                            # NTT(t1*2^d) k*256
    ct1_mul2d=NTT.ScalarVectorNTT(k,NTT.NTT_montgomery(c),ct1_mul2d)                # NTT(c)*NTT(t1*2^d) k*256))
    w_approx_prime=NTT.SubVectorNTT(k,w_approx_prime,ct1_mul2d)                     # w_approx_prime k*256
    w_approx_prime=NTT.iNTT_vec(w_approx_prime)                                         # w_approx k*256
    w1_prime=compress.UseHints_vec(k,gamma2,h,w_approx_prime)                              # w1 k*256)
    lenc_tilde=lambda_c//4
    c_tilde_prime=bytearray(lenc_tilde)
    keccak.shake256(c_tilde_prime,lenc_tilde*8,mu+encode.w1Encode(gamma2,k,w1_prime))
    z_max=infinity_norm(l,z)
    return z_max<gamma1-beta and c_tilde==c_tilde_prime


def faulty_MLDSA_Verify_Internal(pk,M_prime,sig,variant,a1,a2):
    #select parameters based on variant
    if variant==44:
        k=params.MLDSA44_k
        l=params.MLDSA44_l
        eta=params.MLDSA44_eta
        gamma1=params.MLDSA44_gamma1
        gamma2=params.MLDSA44_gamma2
        lambda_c=params.MLDSA44_lambda
        tao=params.MLDSA44_tao
        beta=params.MLDSA44_beta
        omega=params.MLDSA44_omega
    elif variant==65:
        k=params.MLDSA65_k
        l=params.MLDSA65_l
        eta=params.MLDSA65_eta
        gamma1=params.MLDSA65_gamma1
        gamma2=params.MLDSA65_gamma2
        lambda_c=params.MLDSA65_lambda
        tao=params.MLDSA65_tao
        beta=params.MLDSA65_beta
        omega=params.MLDSA65_omega
    elif variant==87:
        k=params.MLDSA87_k
        l=params.MLDSA87_l
        eta=params.MLDSA87_eta
        gamma1=params.MLDSA87_gamma1
        gamma2=params.MLDSA87_gamma2
        lambda_c=params.MLDSA87_lambda
        tao=params.MLDSA87_tao
        beta=params.MLDSA87_beta
        omega=params.MLDSA87_omega
    else:
        print("Invalid variant selected. Please select 44, 65, or 87.")
        return None,None
    
    #decode pk
    rho,t1=encode.pkDecode(eta,k,pk)                                              # rho 32 bytes, t1 k*256

    #decode signature
    c_tilde,z,h=encode.sigDecode(lambda_c,omega,k,l,gamma1,sig)

    if h is None:
        return False
    
    #recover A_hat and tr
    A_hat=sample.ExpandA(k,l,rho)                                               # A_hat k*l*256 
    tr=bytearray(64)                                                             # tr 64 bytes
    keccak.shake256(tr,64*8,pk)

    # recover mu
    mu=bytearray(64)                                                             # mu 64 bytes    
    ctx=keccak.shake256_inc_init()
    keccak.shake256_inc_absorb(ctx,tr)
    keccak.shake256_inc_absorb(ctx,M_prime)
    keccak.shake256_inc_finalize(ctx)
    keccak.shake256_inc_squeeze(mu,64,ctx)

    #recover c
    if a1==4:
        c=sample.faulty_SampleInBall(tao,c_tilde,a2)
    else:
        c=sample.SampleInBall(tao,c_tilde)
    
    # 𝐰′approx ← NTT−1(𝐀 ∘̂ NTT(𝐳) − NTT(𝑐) ∘ NTT(𝐭1 ⋅ 2𝑑)) 
    z_hat=NTT.NTT_vec(z)                                                         # z_hat l*256
    w_approx_prime=NTT.MatrixVectorNTT(k,l,A_hat,z_hat)                            # w_approx_prime k*256
    ct1_mul2d=[[0 for i in range(params.MLDSA_N)] for j in range(k)]
    for i in range(k):
        for j in range(params.MLDSA_N):
            ct1_mul2d[i][j]=t1[i][j]<<params.MLDSA_D                                       # t1*2^d
    ct1_mul2d=NTT.NTT_vec(ct1_mul2d)                                            # NTT(t1*2^d) k*256
    ct1_mul2d=NTT.ScalarVectorNTT(k,NTT.NTT_montgomery(c),ct1_mul2d)                # NTT(c)*NTT(t1*2^d) k*256))
    w_approx_prime=NTT.SubVectorNTT(k,w_approx_prime,ct1_mul2d)                     # w_approx_prime k*256
    w_approx_prime=NTT.iNTT_vec(w_approx_prime)                                         # w_approx k*256
    w1_prime=compress.UseHints_vec(k,gamma2,h,w_approx_prime)                              # w1 k*256)
    lenc_tilde=lambda_c//4
    c_tilde_prime=bytearray(lenc_tilde)
    if a1==5:
        keccak.faulty_shake256_2(c_tilde_prime,lenc_tilde*8,mu+encode.w1Encode(gamma2,k,w1_prime),2)
    else:
        keccak.shake256(c_tilde_prime,lenc_tilde*8,mu+encode.w1Encode(gamma2,k,w1_prime))
    
    z_max=infinity_norm(l,z)
    return z_max<gamma1-beta and c_tilde==c_tilde_prime




def MLDSA_KeyGen(variant=44):
    xi= bytearray(random.getrandbits(8) for _ in range(32))
    if xi==None:
        print("Error generating random bytes for xi.")
        return None,None
    return MLDSA_KeyGen_Internal(xi,variant)

def faulty_MLDSA_KeyGen(variant,a1,a2):
    xi= bytearray(random.getrandbits(8) for _ in range(32))
    if xi==None:
        print("Error generating random bytes for xi.")
        return None,None
    return faulty_MLDSA_KeyGen_Internal(xi,variant,a1,a2)

def MLDSA_Sign(sk,M,ctx,variant=44):
    if len(ctx)>255:
        print("Error: context too long.")
        return None
    rnd=bytearray(random.getrandbits(8) for _ in range(32))
    if rnd==None:
        print("Error generating random bytes for rnd.")
        return None
    M_prime=converse.IntegerToBytes(0,1)+converse.IntegerToBytes(len(ctx),1)+ctx+M
    return MLDSA_Sign_Internal(sk,M_prime,rnd,variant)

def faulty_MLDSA_Sign(sk,M,ctx,variant,a1,a2):
    if len(ctx)>255:
        print("Error: context too long.")
        return None
    rnd=bytearray(random.getrandbits(8) for _ in range(32))
    if rnd==None:
        print("Error generating random bytes for rnd.")
        return None
    M_prime=converse.IntegerToBytes(0,1)+converse.IntegerToBytes(len(ctx),1)+ctx+M
    return faulty_MLDSA_Sign_Internal(sk,M_prime,rnd,variant,a1,a2)

def MLDSA_Verify(pk,M,sig,ctx,variant=44):
    if len(ctx)>255:
        print("Error: context too long.")
        return None
    M_prime=converse.IntegerToBytes(0,1)+converse.IntegerToBytes(len(ctx),1)+ctx+M
    return MLDSA_Verify_Internal(pk,M_prime,sig,variant)

def faulty_MLDSA_Verify(pk,M,sig,ctx,variant,a1,a2):
    if len(ctx)>255:
        print("Error: context too long.")
        return None
    M_prime=converse.IntegerToBytes(0,1)+converse.IntegerToBytes(len(ctx),1)+ctx+M
    return faulty_MLDSA_Verify_Internal(pk,M_prime,sig,variant,a1,a2)


if __name__ == '__main__':
    print("Testing key generation...")
    xi=bytearray.fromhex("125f633352d76d9f62fe5f14112cb19ea7af1173cd0fa424b638b6d578a17280")
    pubkey,privkey=MLDSA_KeyGen_Internal(xi,variant=65)
    M=bytearray.fromhex("d9438ce55f7a59ae8a2bd8c5febf23d029375447e4b38a4b9fd05426802ebb2af417046702ddd1ca0304555a4d13964606e055174f8c5658a0b222e009ec44c31bb55ba7953588369dd4abb44c83f229489b37e9ce7b40f0bce995e474463768b01aa81a3b803bb0a016659d6c27474c713be0e782b704f79db048cad9dc18799b390545492da339dbda0418a1224a2e3b197299285a384bf52baf55cad6134fbcd18ab718281d40fbe7317cc14a3a9c5c5c140ae2fa5aa01cfc6b9d10f5a6ffa4e1b07e288bff06c3bfdb648b53ebe9b0893a2d0659a74095")
    rnd=bytearray(32)
    #privkey=bytearray.fromhex("7f27cdbe54b26cceccd263345b1cd4b7f07fadd6bf19ecdee22a3c4b364ff2a282b5e53a5139cff7aa3dc6dc38a700f96f3899a0605b211d77b1c408615d894522bd676935ea91313bf1fc47e8d86c0a87f77d2724050558f03815da7693919561fc9b9c69e23f6d65b89645308434d0c331d6f7d5f0219642e9949cc59d2070788742708847434777407426808242545864467127122073378113608326476535355863813240113813514813420807707175742078720443882444484575476650167020706474350671361684508062452202532365520841018330778423171164271154042642630680015648317230475600320503727764275688881060004714852522566857780310277165136321742545428875561614133567645743680872862488848613225166882272501467110215413871270626801302832088808623584044762585155044256575344056767507821520605117206478872183502017667285866214252843234264718136651138046228302558066127717406326801464462012357067383131155178837607084686531547223187461625843020410885771464638844528517775028525815730255705008383080652112148724126364116365048131652125010651348503317325402405447556071002268435454661538470157506432380646501827786432856548105211063684052027675266303510314543265584012180517863167143886574486327880358043451201122710448135581775385808734115243185831600772016368510111185183806737153808540788120260426087057670726044558417778313046541187036702631430610663258318650260253747362120340081046534186176051714547801885288341530522574645415384060422531403332511807860603080872172336783883000600311883506461674578383344430822736124855302345683183874471710646284843766214532878456825726747747062466424147665245473856325811134615311446213727150832321507815610040886100684248372765237487538674147276641438048702010554864752764685856647313475071040236355880126145125302128710470411588152118353332302244461865586462527524887801663116024005666442642648341446186846257180475822228467517845307714310833254650024720052353587028166268462142888100588874455044800828141160143713335365253847613375667830357582266814231141260567041841134713411307514852215512275645068174757347867074438552685262145471212706621584504674856703006111326253743172488170308172472061684121813758403663520772636027361043445518407124437087256568200774755207211451183725084417182787487028035641606305124721088242767505348673268162184682408031707255460338206060571048515002205813131188360167706723661606226125815376766276833854567643643034712657358751441543880131768505466802382428810113440708730748163677168300644104380237860152341420427577183085518717737074227338050200314532038551567585114861551122285456001343407507587141252318753814038460147878282475687715148065035865863842617536113514065744172175737178307548381665844841186318730628873742588181850328318844353632133052428780588327864760747350412275123022367820852510748780824123083738427501701063086114005873368840671568777050624725385661034425812132078764448377420345223073515872886103022565884004648476500646766875267801006850781451852785681752623855707252348270588622824133014857000788312571418782171644854270866180265418015326010264875605627463248507574226481636385235141331344085711106444625347618035165313753350326824638503088513115528352678702513176527038812a39fdb32de66bf7159cbb1f69a9d91fd8052cf0f9cd3d7a016bf612b849d5a452c482c56280aa4fed95365f8b99c8a3a710fcb3d5cd193a05d54d2dff28606917b216cdca331ed0207dd33d425de7182fc85d02157cfc38fe19242821e7e215cd468d3c513b64dfa64bbece4089b3484e7960b36f881d799d782cd4270ece0caf3647b552f9b8affddcacadef5fb662c549be1f0e94d5ad591363e8da687b0df768c9b1cfe1ca907432c9e4071cb6b48363b3b7d332ddcbc54fff860457644fd71ce8f551fbccdeac4687214abe1f52857d896c66843991c4cd5af598a2d8e8284915e14014addfd380a1fe4f09ebebd30a64374a292d326c0888003f24ce0286d5d82d9ed6433615dcd9ccbb0e0960837bc930c7828613a6daeda0e37fbec45cd9b7e615603e50dfbbcf3e8c46eab4b67aa078033ebd2392c99fae0bbb9f29b78d978468af9d8b4a24243532435948d778dbf8c3d1922cab8f5713aaaff5b6fbe673ffae594bbdc9dda45f2e97ccfdd43f8254d496abd71038b229c71c35084db79e7870bd08b7b83c6c7de082d30def30cf4adc1e345cf86b93c5607b9ec23b81767f72bf96a93f0e4aae4d085727b876d9adf5857a2a4806e0a33356fc33fc8be159d98e786526089019083040e8cfa434587e668e52ab05d4577d33fd5b53ac9d538ffbdc3e9154384ec57ffb24d5bcbb9e9c116194f34ce35d7c4d152769978a7a44436ec8c2f486231b2c41850b2c4014f61953a2d95f376569b1e732a620fef5b5538a43c39b8eb58923ea1142b6d0887239f81e5a85e2e954d821aa8a9990ee6e5543948bb1dc4e7718ce6d5cbbd00483faeeb0da15884b823e0df0022010f8477149f6d89a4e479c8a69b37d100d2034b67e1188b67cbe3ac228f0fa83b825d085e10d9637baa1fb3e8b871dd3e5470998e299898b6e0e14d012df0729d467c25a84bf818543a736bd8b87baa371c9134991407e2d7ef8fcffbe11e58c93b489fa80d2eaf77eb926fb3d07cb725ea805300b9c3d3d8bdb0f8e4c7fac21a3a5e5d7e6a3a10cfba807d2f0537a1b86a40269c7fe6587b2b36533cdb5ce4ac78a84262d9d31f7e97f821ab9f50f6b04b0ee9b0c1b3e7c49a7d415f8572aab0d6c9474a04cd80e401ffc12614068debb796627eecf4c0362d6fc9e7759f32e442707ebba0b14759125553e84a6bc91f983e798ef0a30774b19751197be526b835a7288caeecdea30b5228776ea05af66eff9e5178e7a4516102a23aaec684fc5b697ae9fe250b0594bcd646680c798ca4c392701de3380828695efc921ecb3f418ac2dce2522174e60cf744994a293ab9c017b781cff792ecee9a1130577e52956691b1b1cc770cdd72aa824ffbfad8713d22049ea13539c0f9922347e7455c4aa99366510db86fef3d2417e1d72d6727bbe0b95df1f15bd33f3724ca2d4505059f627fe8a997b3446aee530385fe9c23851f0d0f4cd48bb728136081fed690ef009826e70f487597d8c702a1646f0d70413d18ddf7c49e586bdd4b123e9516002b6bd110542e85a1d15a28c2142037caae0374c35d30f1a87570082a6e308da4062867016fe66bee4267443b08f66f576ead4413641654a181ec24ac0640a770af3d8d90e688c2f94b2f1358c11e233d95929676fa261a7e56758b2a6c3513b8ce4c29748dc394b898d8d9d760ea8ab346040407199518e39e7f83c097e29d964259ac778175568185912aca6794b986a7f0d103abc31d1a2ae7a5813e28b832df9988a5b023870bc92d31f6abf28f55ca517b2c6ef3f006211fec443653907ba15f8852f06e7042d22d32e2ca83d8540150a092cc646213d691e2fd36d8fcb1fc1ebc1ec4aa200dc0244e9b0acccdd4a402e6b8f24d49aeab9896f421934b69a391d0b91e128d11b59a11046540c5ebbe1656585451d0a729fd6de8b33a65185a5923f3b2a3449d47689f31aa320759c699c69555b7736c591dc770eaf8060d155178b474f20645b198a32cc3a0d87cdad651d41f0b95c18159323eab98137b2d79073e1ebba7a72ba10aa7549e766e35b9e822945bebef99cf238d5d50f1d5f9750daea2b59f5e27cf9a1802148d79e1e0c412e8dc22d97a2d6ee240fe3fd19ca7f107c52cd3c83e0aa46da394921422c7fdc1cbdfe586a8a2160e2e5eb38864a21a77f049153fcff583fbeae421797243020736b817704d045be18f1210a2861b23e198a695facc5dd42530c0f1c2ccdef36677effa75d52472c99487a5248cd93949677814fd505e266abdba96d73e1047d6937be53ef3eaee7e6bb8f47e6c6b6eda46e5324f50ada5c5dd2b65c442475e59bab1b5f29ea850c3f0ee1784eba3cbb0bdbc3a0789b4ea612bd402fff97fd1876c8862c21d33b5c6131d4be2e239f90cacffdc205dd1f05664c1acf53cd1643b5bc89842b3b77e478a68656f11079bf79ce5696864c2eb53ec3b06bc2261ecc2d1f9b25482bba6c55cb0696b5a74514d330cff1eb9e60352339c4d4cec912a8c650c3bc660e1d61104cd7ba360f54ab40c3a08fb72a88318dff6092f1dc0be520f4f64e939ddd333f35e1f0857570da4ec3159ad3e309808161aae9021ef4edf30a258054c9f7b0c70091154b5a27540a26ff5815d4d5e5734ba1b1e8be0c31a59f24534ac37fb3ac212e0fee665a87ad0bb72302adae6b16f4c68662e8d3cfe50daf1dda3352c05edc027d6c155eb84e4aa25a0a8164960bde1668e44e364312e84d01402fb4442ac90060543082a0fc08c47feee7cba10ccca3de9fde039295bcefff856c64fa5e624393b2154deb9602035f1f76c3197dc9ba4371a92ad94873b2789e388de84b9990ada08812b325a8eb0b2555d24b5d92381125bbfffaa4b0096626097c891a134309e8d83e391836ab6b63ec52b28c15ccf61aef47727e90812ee0874d058d5d11d62472384bad639911336297aa4b717c3dfa579224a6ff0436b7082834df654ee2c76199f0294c8ab62f404ceac2a2dfb5c16652e3d69303cf3301c9429144904697eb38f2121e21a21bfcd768f9ea239bac29d46eaece52670dd3ffcb5c83109ca35cc8ca3ee29aad967b28c0654f29bb182ee34390ffa2b6b83583a9107db683784aa536f7670f25aa944e9d060213799d2d68839cae894307c2aa0905de37ea414396487d04141c4e0f7fe500df581a3136d0c36aa36ee019cfa191b73d7a49d7a36f9a49fe95776cdaf99006b038d02a6276d8eeb0a8ccf710f20dbcabce6617956ea67a46ee211b7ed7ca8ad5e35a20901db67ec0ef4a91a0d537ca3c2614cb4b588d395fa3166845a1bda6e16a19ae5cc8190b57e765f6dd3ac2125b238b75cd520c8067ac61756aac0ff44a46ff70fc2a4069aaf131698269c8e545fb5807d41222341fa16a7980a837a0b16b8849905c0302e64f87a059275818b72fbc02bcfca04ebc7b684c351979c09af3b8057b71c44e8da24c7f795665e9e852eef7567881e98f9a5c54776dda37dca88e172c497f813ce4987d4141443a")
    sig=MLDSA_Sign_Internal(privkey,M,rnd,variant=65)
    res=MLDSA_Verify_Internal(pubkey,M,sig,65)
    if res:
        print("success")

    ctx=bytearray([232,1,2,3,4])
    M=bytearray([12,13,14,15])
    pk,sk=MLDSA_KeyGen()
    sig=MLDSA_Sign(sk,M,ctx)
    validity=MLDSA_Verify(pk,M,sig,ctx)
    if validity:
        print("success")


