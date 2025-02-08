import MLDSA
import random
import encode
import params
import sample
import NTT
import keccak
import compress
import converse

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

def modInv(x, n):
    gcd, inv, _ = extended_gcd(x, n)
    if gcd != 1:
        return None 
    else:
        return inv % n 

print("ML-DSA fault simulator and solver, using ML-DSA-44 as an example.")
print("Simulating ML-DSA Attack 1...")
print("Case 1: Keccak Attack 1")
pk,sk=MLDSA.faulty_MLDSA_KeyGen(44,1,1)
print("The secret s1 (encoded as a hex string) is fixed to:")
print(sk[128:512].hex())

print("Case 2: Keccak Attack 2")
pk,sk=MLDSA.faulty_MLDSA_KeyGen(44,1,2)
print("The secret s1 (encoded as a hex string) is fixed to:")
print(sk[128:512].hex())

print("Case 3: Keccak Attack 3")
pk,sk=MLDSA.faulty_MLDSA_KeyGen(44,1,3)
print("The secret s1 (encoded as a hex string) is fixed to:")
print(sk[128:512].hex())


print("\n\nSimulating ML-DSA Attack 2...")
print("Only Keccak Attack 2 is applicapable in this case.")
pk,sk=MLDSA.faulty_MLDSA_KeyGen(44,2,2)
print("The secret s1 (encoded as a hex string) is fixed to:")
print(sk[128:512].hex())




print("\n\nSimulating ML-DSA Attack 3...")


for i in range(2):
    pk,sk=MLDSA.MLDSA_KeyGen(44)
    m = bytearray(b"Hello World")
    ctx=bytearray(32)
    if i==0:
        print("Case 1: Keccak Attack 1")
        sig=MLDSA.faulty_MLDSA_Sign(sk,m,ctx, 44,3,1)
        rho_2prime=bytearray.fromhex('22864b96d3487c56e1aa7e4574e548d2f9c1122df1aa96c841877403d2f3cbbac1e833db97a50c148f37e443687029cb6d73549284ea2eb0a223c507ef0497ca')
        print("rho'' is fixed to: 22864b96d3487c56e1aa7e4574e548d2f9c1122df1aa96c841877403d2f3cbbac1e833db97a50c148f37e443687029cb6d73549284ea2eb0a223c507ef0497ca")
    if i==1:
        print("Case 2: Keccak Attack 2")
        sig=MLDSA.faulty_MLDSA_Sign(sk,m,ctx, 44,3,2)
        rho_2prime=bytearray.fromhex('e7dde140798f25f18a47c033f9ccd584eea95aa61e2698d54d49806f304715bd57d05362054e288bd46f8e7f2da497ffc44746a4a0e5fe90762e19d60cda5b8c')
        print("rho'' is fixed to: e7dde140798f25f18a47c033f9ccd584eea95aa61e2698d54d49806f304715bd57d05362054e288bd46f8e7f2da497ffc44746a4a0e5fe90762e19d60cda5b8c")

    k=params.MLDSA44_k
    l=params.MLDSA44_l
    eta=params.MLDSA44_eta
    gamma1=params.MLDSA44_gamma1
    gamma2=params.MLDSA44_gamma2
    lambda_c=params.MLDSA44_lambda
    tao=params.MLDSA44_tao
    beta=params.MLDSA44_beta
    omega=params.MLDSA44_omega

    c_tilde,z,h=encode.sigDecode(lambda_c,omega,k,l,gamma1,sig)
    c=sample.SampleInBall(tao,c_tilde)
    c_hat=NTT.NTT_montgomery(c)
    c_hat_inv=[]
    for n in c_hat:
        c_hat_inv.append(modInv(n,8380417))
    # c_inv=NTT.iNTT_montgomery(c_hat_inv)
    rho,t1=encode.pkDecode(eta,k,pk)
    A_hat=sample.ExpandA(k,l,rho)                                               # A_hat k*l*256 
    tr=bytearray(64)                                                             # tr 64 bytes
    keccak.shake256(tr,64*8,pk)
    # 𝜇 ← H(BytesToBits(𝑡𝑟)||𝑀′, 64)
    M_prime=converse.IntegerToBytes(0,1)+converse.IntegerToBytes(len(ctx),1)+ctx+m
    mu=bytearray(64)                                                             # mu 64 bytes    
    ctx=keccak.shake256_inc_init()
    keccak.shake256_inc_absorb(ctx,tr)
    keccak.shake256_inc_absorb(ctx,M_prime)
    keccak.shake256_inc_finalize(ctx)
    keccak.shake256_inc_squeeze(mu,64,ctx)
    kappa=0
    while kappa<10000:
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
        c_tilde1=bytearray(lenc_tilde)
        keccak.shake256(c_tilde1,lenc_tilde*8,mu+encode.w1Encode(gamma2,k,w1))
        if c_tilde1==c_tilde:
            zminusy=NTT.SubVectorNTT(4,z,y)
            zminusy_hat=NTT.NTT_vec(zminusy)

            s1_hat=NTT.ScalarVectorNTT(4,c_hat_inv,zminusy_hat)
            s1=NTT.iNTT_vec(s1_hat)
            for i in range(l):
                for j in range(params.MLDSA_N):
                    if s1[i][j]>2:
                        s1[i][j]-=8380417

            s1_encode=bytearray([])
            for i in range(l):
                s1_encode+=converse.BitPack(s1[i],eta,eta)
            if s1_encode==sk[128:512]:
                print("attack success! kappa is: ")
                print(kappa)
                print("secret s1 (encoded as a hex string) is:")
                print(s1_encode.hex())
            break
        kappa+=4


print("\n\nSimulating ML-DSA Attack 4...")
print("Only Keccak Attack 2 is applicapable in this case.")
pk,sk=MLDSA.MLDSA_KeyGen(44)
m = bytearray(b"Hello World")
ctx=bytearray(32)
sig=MLDSA.MLDSA_Sign(sk,m,ctx, 44)

c=[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0, 1, 0, -1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 
0, 0, 0, -1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, -1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0]
print("c is set to:")
print(c)

malicious_m=bytearray(b"This is a malicious message!")

rho,t1=encode.pkDecode(eta,k,pk)                                              # rho 32 bytes, t1 k*256
#decode signature
c_tilde,z,h=encode.sigDecode(lambda_c,omega,k,l,gamma1,sig)
#recover A_hat and tr
A_hat=sample.ExpandA(k,l,rho)                                               # A_hat k*l*256 
tr=bytearray(64)                                                             # tr 64 bytes
keccak.shake256(tr,64*8,pk)
M_prime=converse.IntegerToBytes(0,1)+converse.IntegerToBytes(len(ctx),1)+ctx+malicious_m
# recover mu
mu=bytearray(64)                                                             # mu 64 bytes    
ctx=keccak.shake256_inc_init()
keccak.shake256_inc_absorb(ctx,tr)
keccak.shake256_inc_absorb(ctx,M_prime)
keccak.shake256_inc_finalize(ctx)
keccak.shake256_inc_squeeze(mu,64,ctx)
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

print("c_tilde_prime computed:")
print(c_tilde_prime.hex())

malicious_sig=encode.sigEncode(omega,k,l,gamma1,c_tilde_prime,z,h)

ctx=bytearray(32)
print("signing malicious message: \"This is a malicious message!\"")
ver=MLDSA.faulty_MLDSA_Verify(pk,malicious_m,malicious_sig,ctx, 44,4,2)
if ver:
    print("attack success!")

print("\n\nSimulating ML-DSA Attack 5...")
print("Only Keccak Attack 2 is applicapable in this case.")
c_tilde_prime=bytearray.fromhex("e7dde140798f25f18a47c033f9ccd584eea95aa61e2698d54d49806f304715bd")
print("c_tilde_prime is set to:")
print(c_tilde_prime.hex())
pk,sk=MLDSA.MLDSA_KeyGen(44)
m = bytearray(b"Hello World")
ctx=bytearray(32)
sig=MLDSA.MLDSA_Sign(sk,m,ctx, 44)
malicious_sig=encode.sigEncode(omega,k,l,gamma1,c_tilde_prime,z,h)
print("signing malicious message: \"This is a malicious message!\"")
ver=MLDSA.faulty_MLDSA_Verify(pk,malicious_m,malicious_sig,ctx, 44,5,2)
if ver:
    print("attack success!")