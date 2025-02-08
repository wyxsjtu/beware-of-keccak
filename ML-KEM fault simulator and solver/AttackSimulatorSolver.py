import KPKE_MLKEM
import keccak
import params
import converse_compress
import polyvec
import NTT

print("ML-KEM fault simulator and solver, using ML-KEM-512 as an example.")
print("Simulating ML-KEM Attack 1...")
print("Case 1: Keccak Attack 1")
pk,sk=KPKE_MLKEM.faulty_MLKEM_keygen(512,1,1)
print("The secret s (encoded as a hex string) is fixed to:")
print(sk[:768].hex())
pk,sk=KPKE_MLKEM.faulty_MLKEM_keygen(512,1,2)
print("Case 2: Keccak Attack 2")
print("The secret s (encoded as a hex string) is fixed to:")
print(sk[:768].hex())
print("Case 3: Keccak Attack 3")
pk,sk=KPKE_MLKEM.faulty_MLKEM_keygen(512,1,3)
print("The secret s (encoded as a hex string) is fixed to:")
print(sk[:768].hex())


print("\n\nSimulating ML-KEM Attack 2...")
print("Case 1: Keccak Attack 1")
pk,sk=KPKE_MLKEM.faulty_MLKEM_keygen(512,2,1)
print("The secret s (encoded as a hex string) is fixed to:")
print(sk[:768].hex())
print("Case 2: Keccak Attack 2")
pk,sk=KPKE_MLKEM.faulty_MLKEM_keygen(512,2,2)
print("The secret s (encoded as a hex string) is fixed to:")
print(sk[:768].hex())


pk,sk=KPKE_MLKEM.MLKEM_keygen(512)
print("\n\nSimulating ML-KEM Attack 3...")
print("Case 1: Keccak Attack 1")
k,c=KPKE_MLKEM.faulty_MLKEM_encaps(pk, 512,3,1)
print("The shared key k is fixed to:")
print(k.hex())
print("Case 2: Keccak Attack 2")
k,c=KPKE_MLKEM.faulty_MLKEM_encaps(pk, 512,3,2)
print("The shared key k is fixed to:")
print(k.hex())

print("Case 3: Keccak Attack 3")
k,c=KPKE_MLKEM.faulty_MLKEM_encaps(pk, 512,3,3)
print("The shared key k equals m")
print("the seed r equals the hash of encapsulation key:")
Hek=bytearray(32)
keccak.sha3_256(Hek,pk)
K=params.MLKEM512_K
eta1=params.MLKEM512_eta1
eta2=params.MLKEM512_eta2
du=params.MLKEM512_du
dv=params.MLKEM512_dv
r=Hek
t_hat=[0]*K
for i in range(K):
    t_hat[i]=converse_compress.byte_decode(12,pk[384*i:384*(i+1)])     #run ByteDecode12 𝑘 times to decode 𝐭 ∈ (ℤ256q)^{K}


N=0
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

c2=c[32*K*du:32*K*du+32*dv]
v_prime=converse_compress.byte_decode(dv,c2)
for i in range(params.MLKEM_N):
    v_prime[i]=converse_compress.decompress(dv,v_prime[i])
#𝐯 ← NTT−1(t^T∘𝐲)+𝐞2+mu
tty=NTT.iNTT_montgomery(polyvec.MultiplyNTT_montgomery_vec(t_hat,y_hat))
mu=polyvec.polysub(v_prime,tty)
mu=polyvec.polysub(mu,e2)
omega_compressed=[0]*params.MLKEM_N
for i in range(params.MLKEM_N):
    omega_compressed[i]=converse_compress.compress(1,mu[i])
m=converse_compress.byte_encode(1,omega_compressed)
print("The message m is recovered as:")
print(m.hex())
print("The shared key k is recovered as:")
print(k.hex())


pk,sk=KPKE_MLKEM.MLKEM_keygen(512)
print("\n\nSimulating ML-KEM Attack 4...")
print("Case 1: Keccak Attack 1")
k,c=KPKE_MLKEM.faulty_MLKEM_encaps(pk, 512,4,1)
y=[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3327, 2, 0, 3, 3326, 3327, 0, 0, 3327, 0, 0, 0, 2, 1, 1, 1, 0, 3, 3326, 3328, 0, 1, 3328, 0, 1, 0, 0, 3327, 
2, 1, 3328, 0, 3328, 3328, 1, 0, 0, 1, 1, 0, 0, 1, 3327, 2, 0, 0, 3328, 3328, 2, 3328, 3328, 1, 0, 1, 3328, 0, 2, 1, 0, 2, 0, 0, 0, 2, 3328, 1, 3327, 0, 0, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3327, 2, 0, 3, 3326, 3327, 0, 0, 3327, 0, 0, 0, 2, 1, 1, 1, 0, 3, 3326, 3328, 0, 1, 3328, 0, 1, 0, 0, 3327, 2, 1, 3328, 0, 3328, 3328, 1, 0, 0, 1, 1, 0, 0, 1, 3327, 2, 0, 0, 3328, 3328, 2, 3328, 3328, 1, 0, 1, 3328, 0, 2, 1, 0, 2, 0, 0, 0, 2, 3328, 1, 3327, 0, 0, 1, 1, 1, 1, 1]]
print("y is fixed to:")
print(y)
y_hat=polyvec.NTT_montgomery_vec(y)
c2=c[32*K*du:32*K*du+32*dv]
v_prime=converse_compress.byte_decode(dv,c2)
for i in range(params.MLKEM_N):
    v_prime[i]=converse_compress.decompress(dv,v_prime[i])
t_hat=[0]*K
for i in range(K):
    t_hat[i]=converse_compress.byte_decode(12,pk[384*i:384*(i+1)])     #run ByteDecode12 𝑘 times to decode 𝐭 ∈ (ℤ256q)^{K}
tty=NTT.iNTT_montgomery(polyvec.MultiplyNTT_montgomery_vec(t_hat,y_hat))
mu=polyvec.polysub(v_prime,tty)
omega_compressed=[0]*params.MLKEM_N
for i in range(params.MLKEM_N):
    omega_compressed[i]=converse_compress.compress(1,mu[i])
m=converse_compress.byte_encode(1,omega_compressed)
print("The message m is recovered as:")
print(m.hex())
Hek=bytearray(32)
keccak.sha3_256(Hek,pk)
buf=bytearray(64)
keccak.sha3_512(buf,m+Hek)
K1=buf[:32]
if K1==k:
    print("Attack successful! The shared key k is recovered as:")
    print(k.hex())



print("Case 2: Keccak Attack 2")
k,c1=KPKE_MLKEM.faulty_MLKEM_encaps(pk, 512,4,2)
y=[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3328, 0, 1, 0, 2, 0, 0, 2, 1, 0, 3327, 0, 0, 1, 3327, 0, 0, 2, 0, 1, 1, 3327, 3328, 3328, 3328, 1, 3328, 0, 3327, 1, 1, 1, 1, 0, 0, 0, 3328, 2, 0, 3, 1, 0, 1, 2, 1, 3328, 0, 0, 1, 3328, 1, 3327, 3328, 3328, 0, 1, 3327, 3326, 1, 0, 3328, 3327, 1, 0, 1, 3327, 0, 2, 0, 0, 3327, 1, 3328, 2, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3328, 0, 1, 0, 2, 0, 0, 2, 1, 0, 3327, 0, 0, 1, 3327, 0, 0, 2, 0, 1, 1, 3327, 3328, 3328, 3328, 1, 3328, 0, 3327, 1, 1, 1, 1, 0, 0, 0, 3328, 2, 0, 3, 1, 0, 1, 2, 1, 3328, 0, 0, 1, 3328, 1, 3327, 3328, 3328, 0, 1, 3327, 3326, 1, 0, 3328, 3327, 1, 0, 1, 3327, 0, 2, 0, 0, 3327, 1, 3328, 2, 0]]
print("y is fixed to:")
print(y)
y_hat=polyvec.NTT_montgomery_vec(y)
c2=c1[32*K*du:32*K*du+32*dv]
v_prime=converse_compress.byte_decode(dv,c2)
for i in range(params.MLKEM_N):
    v_prime[i]=converse_compress.decompress(dv,v_prime[i])
t_hat=[0]*K
for i in range(K):
    t_hat[i]=converse_compress.byte_decode(12,pk[384*i:384*(i+1)])     #run ByteDecode12 𝑘 times to decode 𝐭 ∈ (ℤ256q)^{K}
tty=NTT.iNTT_montgomery(polyvec.MultiplyNTT_montgomery_vec(t_hat,y_hat))
mu=polyvec.polysub(v_prime,tty)
omega_compressed=[0]*params.MLKEM_N
for i in range(params.MLKEM_N):
    omega_compressed[i]=converse_compress.compress(1,mu[i])
m=converse_compress.byte_encode(1,omega_compressed)
print("The message m is recovered as:")
print(m.hex())
Hek=bytearray(32)
keccak.sha3_256(Hek,pk)
buf=bytearray(64)
keccak.sha3_512(buf,m+Hek)
K1=buf[:32]
if K1==k:
    print("Attack successful! The shared key k is recovered as:")
    print(k.hex())



pk,sk=KPKE_MLKEM.MLKEM_keygen(512)
k,c=KPKE_MLKEM.MLKEM_encaps(pk, 512)
print("\n\nSimulating ML-KEM Attack 5...")
print("Case 1: Keccak Attack 1")
k=KPKE_MLKEM.faulty_MLKEM_decaps(sk, c, 512,5,1)
if (k.hex()=="243d92f5a1328a4cc9f4cb6da60ee6f7b362472f7ad4fc117e3646c85061574c"):
    print("Attack successful!")
print("The shared secret key is fixed to:")
print("243d92f5a1328a4cc9f4cb6da60ee6f7b362472f7ad4fc117e3646c85061574c")

print("Case 2: Keccak Attack 2")
k=KPKE_MLKEM.faulty_MLKEM_decaps(sk, c, 512,5,2)
if (k.hex()=="e7dde140798f25f18a47c033f9ccd584eea95aa61e2698d54d49806f304715bd"):
    print("Attack successful!")
print("The shared secret key is fixed to:")
print("e7dde140798f25f18a47c033f9ccd584eea95aa61e2698d54d49806f304715bd")

pk,sk=KPKE_MLKEM.MLKEM_keygen(512)
k,c=KPKE_MLKEM.MLKEM_encaps(pk, 512)
print("\n\nSimulating ML-KEM Attack 6...")
print("Case 1: Keccak Attack 2")
k=KPKE_MLKEM.faulty_MLKEM_decaps2(sk, c, 512,6,2)
print("Recovered ctx:")
ctx=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32]
print(ctx)
K_bar=bytearray(32)
keccak.shake256_inc_absorb(ctx,c)
keccak.shake256_inc_finalize(ctx)
keccak.shake256_inc_squeeze(K_bar,32,ctx)
if K_bar==k:
    print("Attack success!")
print("The shared secret key is:")
print(K_bar.hex())