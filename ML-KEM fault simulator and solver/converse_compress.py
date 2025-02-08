import params
import keccak

def bits_to_bytes(b):
    B = [0] * (len(b) // 8)
    for i in range(len(b)):
        B[i // 8] += (b[i] << (i % 8))
    return bytearray(B)

def bytes_to_bits(B):
    C=B[:]
    l=len(B)
    b=[0]*(l*8)
    for i in range(l):
        for j in range(8):
            b[8*i+j]=C[i]%2
            C[i]=C[i]//2
    return b

#integers modulo q to integers modulo 2^d
def compress(d,x):
    if x<0:
        x+=params.MLKEM_Q
    tmp=(2**d)*x
    n, r = divmod(tmp, params.MLKEM_Q)
    if r>params.MLKEM_Q//2:
        n+=1
    return n&((1<<d)-1)

#integers modulo 2^d to integers modulo q
def decompress(d,x):
    tmp=x*params.MLKEM_Q
    n, r = divmod(tmp, (2**d))
    if r>=2**(d-1):
        n+=1
    return n

# Encodes an array of 𝑑-bit integers into a byte array for 1 ≤ 𝑑 ≤ 12.
#Input: integer array 𝐹 ∈ ℤ^256, where 𝑚 = 2^𝑑 if 𝑑 < 12, and 𝑚 = 𝑞 if 𝑑 = 12.
#Output: byte array 𝐵 ∈ 𝔹^32𝑑.
def byte_encode(d,F):
    b=[0]*(params.MLKEM_N*d)
    for i in range(params.MLKEM_N):
        a=F[i]
        for j in range(d):
            b[i*d+j]=a%2
            a=(a-b[i*d+j])//2
    B=bits_to_bytes(b)
    return B

#Decodes a byte array into an array of 𝑑-bit integers for 1 ≤ 𝑑 ≤ 12.
#Input: byte array 𝐵 ∈ 𝔹^32𝑑.
#Output: integer array 𝐹 ∈ ℤ^256_m, where 𝑚 = 2^𝑑 𝑚 if 𝑑 < 12 and 𝑚 = 𝑞 if 𝑑 = 12.
def byte_decode(d,B):
    b=bytes_to_bits(B)
    F=[0]*params.MLKEM_N
    for i in range(params.MLKEM_N):
        for j in range(d):
            F[i]+=(b[i*d+j]*(2**(j)))%params.MLKEM_Q
    return F

#Takes a 32-byte seed and two indices as input and outputs a pseudorandom element of 𝑇𝑞.
#Input: byte array 𝐵 ∈ 𝔹34. ▷ a 32-byte seed along with two indices
#Output: array ̂ 𝑞 𝑎 ∈ ℤ . 256 ▷ the coefficients of the NTT of a polynomial
# 3 bytes -> 2* 12bits, if > q, regenerate
def SampleNTT(B):
    a=[0]* params.MLKEM_N
    ctx=keccak.shake128_inc_init()
    keccak.shake128_inc_absorb(ctx, B)
    keccak.shake128_inc_finalize(ctx)
    j=0
    while j<params.MLKEM_N:
        c=[0]*3
        keccak.shake128_inc_squeeze(c,3,ctx)
        d1=c[0]+(c[1]%16)*params.MLKEM_N
        d2=c[1]//16+16*c[2]
        if d1<params.MLKEM_Q:
            a[j]=d1
            j+=1
        if d2<params.MLKEM_Q and j<params.MLKEM_N:
            a[j]=d2
            j+=1
    return a

#Takes a seed as input and outputs a pseudorandom sample from the distribution D𝜂(𝑅𝑞).
#Input: byte array 𝐵 ∈ 𝔹64𝜂.
#Output: array 𝑓 ∈ ℤ256𝑞 . ▷ the coefficients of the sampled polynomial
def SamplePolyCBD(eta,B):
    f=[0]*params.MLKEM_N
    b=bytes_to_bits(B)
    for i in range(params.MLKEM_N):
        x=0
        y=0
        for j in range(eta):
            x+=b[2*i*eta+j]
            y+=b[2*i*eta+eta+j]
        f[i]=(x-y)%params.MLKEM_Q
    return f




if __name__ == '__main__':
    print("Testing Conversion functions and Compression functions...")
    print("Converting bits to bytes...")
    bit_string =  [1,0,1,1,0,1,1,1,0,0,0,1,0,0,1,0]
    byte_result = bits_to_bytes(bit_string)
    if byte_result.hex() == 'ed48':
        print("Conversion successful!")
    else:
        print("Conversion failed!")
    print("Converting bytes to bits...")
    byte_string = bytearray.fromhex('ed48')
    bit_result = bytes_to_bits(byte_string)
    if bit_result == bit_string:
        print("Conversion successful!")
    else:
        print("Conversion failed!")

    print("Testing Compression function...")
    if compress(4,1000) == 5:
        print("Compression successful!")
    else:
        print("Compression failed!")

    print("Testing Decompression function...")
    if abs(decompress(4,5) - 1000) < 0.5*(params.MLKEM_Q/2**4):
        print("Decompression successful!")
    else:
        print("Decompression failed!")

    print("Testing Byte Encoding function...")
    F=[13]*256
    B=byte_encode(4,F)
    if B.hex() == 'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd':
        print("Byte Encoding successful!")
    else:
        print("Byte Encoding failed!")
    print("Testing Byte Decoding function...")
    F_result=byte_decode(4,B)
    if F_result == F:
        print("Byte Decoding successful!")
    else:
        print("Byte Decoding failed!")
