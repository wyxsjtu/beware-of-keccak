# Keccak implementation in Python !!! This implementation is based on the PQClean C implementation of Keccak.


# 8 bytes -> a 64 bit int           little-endian
def load64(x):
    if len(x)!= 8:
        raise ValueError("load64: Input must be 8 bytes long")
    return int.from_bytes(x, byteorder='little')

#  64 bit int -> 8 bytes           Little-endian
def store64(x):
    return x.to_bytes(8, byteorder='little')
    
# Keccak round constants
RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
      0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
      0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
      0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
      0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
      0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]

def ROL(value,shift):
    return ((value << shift) ^ (value >> (64-shift))) & ((1 << 64) - 1)                                               

# Keccak-p permutation (Following the PQClean implementation)
def keccak_p(state):
    PERMUTATION_ROUNDS=24
# define helper variables
    Aba = state[0]
    Abe = state[1]
    Abi = state[2]
    Abo = state[3]
    Abu = state[4]
    Aga = state[5]
    Age = state[6]
    Agi = state[7]
    Ago = state[8]
    Agu = state[9]
    Aka = state[10]
    Ake = state[11]
    Aki = state[12]
    Ako = state[13]
    Aku = state[14]
    Ama = state[15]
    Ame = state[16]
    Ami = state[17]
    Amo = state[18]
    Amu = state[19]
    Asa = state[20]
    Ase = state[21]
    Asi = state[22]
    Aso = state[23]
    Asu = state[24]
    for round in range(0, PERMUTATION_ROUNDS, 2):
    # round i
        BCa = Aba ^ Aga ^ Aka ^ Ama ^ Asa
        BCe = Abe ^ Age ^ Ake ^ Ame ^ Ase
        BCi = Abi ^ Agi ^ Aki ^ Ami ^ Asi
        BCo = Abo ^ Ago ^ Ako ^ Amo ^ Aso
        BCu = Abu ^ Agu ^ Aku ^ Amu ^ Asu

        Da = BCu ^ ROL(BCe, 1)
        De = BCa ^ ROL(BCi, 1)
        Di = BCe ^ ROL(BCo, 1)
        Do = BCi ^ ROL(BCu, 1)
        Du = BCo ^ ROL(BCa, 1)

        Aba ^= Da
        BCa = Aba
        Age ^= De
        BCe = ROL(Age, 44)
        Aki ^= Di
        BCi = ROL(Aki, 43)
        Amo ^= Do
        BCo = ROL(Amo, 21)
        Asu ^= Du
        BCu = ROL(Asu, 14)
        Eba = BCa ^ ((~BCe) & BCi)
        Eba ^= RC[round]
        Ebe = BCe ^ ((~BCi) & BCo)
        Ebi = BCi ^ ((~BCo) & BCu)
        Ebo = BCo ^ ((~BCu) & BCa)
        Ebu = BCu ^ ((~BCa) & BCe)

        Abo ^= Do
        BCa = ROL(Abo, 28)
        Agu ^= Du
        BCe = ROL(Agu, 20)
        Aka ^= Da
        BCi = ROL(Aka, 3)
        Ame ^= De
        BCo = ROL(Ame, 45)
        Asi ^= Di
        BCu = ROL(Asi, 61)
        Ega = BCa ^ ((~BCe) & BCi)
        Ege = BCe ^ ((~BCi) & BCo)
        Egi = BCi ^ ((~BCo) & BCu)
        Ego = BCo ^ ((~BCu) & BCa)
        Egu = BCu ^ ((~BCa) & BCe)

        Abe ^= De
        BCa = ROL(Abe, 1)
        Agi ^= Di
        BCe = ROL(Agi, 6)
        Ako ^= Do
        BCi = ROL(Ako, 25)
        Amu ^= Du
        BCo = ROL(Amu, 8)
        Asa ^= Da
        BCu = ROL(Asa, 18)
        Eka = BCa ^ ((~BCe) & BCi)
        Eke = BCe ^ ((~BCi) & BCo)
        Eki = BCi ^ ((~BCo) & BCu)
        Eko = BCo ^ ((~BCu) & BCa)
        Eku = BCu ^ ((~BCa) & BCe)

        Abu ^= Du
        BCa = ROL(Abu, 27)
        Aga ^= Da
        BCe = ROL(Aga, 36)
        Ake ^= De
        BCi = ROL(Ake, 10)
        Ami ^= Di
        BCo = ROL(Ami, 15)
        Aso ^= Do
        BCu = ROL(Aso, 56)
        Ema = BCa ^ ((~BCe) & BCi)
        Eme = BCe ^ ((~BCi) & BCo)
        Emi = BCi ^ ((~BCo) & BCu)
        Emo = BCo ^ ((~BCu) & BCa)
        Emu = BCu ^ ((~BCa) & BCe)

        Abi ^= Di
        BCa = ROL(Abi, 62)
        Ago ^= Do
        BCe = ROL(Ago, 55)
        Aku ^= Du
        BCi = ROL(Aku, 39)
        Ama ^= Da
        BCo = ROL(Ama, 41)
        Ase ^= De
        BCu = ROL(Ase, 2)
        Esa = BCa ^ ((~BCe) & BCi)
        Ese = BCe ^ ((~BCi) & BCo)
        Esi = BCi ^ ((~BCo) & BCu)
        Eso = BCo ^ ((~BCu) & BCa)
        Esu = BCu ^ ((~BCa) & BCe)
        # round i+1
        BCa = Eba ^ Ega ^ Eka ^ Ema ^ Esa
        BCe = Ebe ^ Ege ^ Eke ^ Eme ^ Ese
        BCi = Ebi ^ Egi ^ Eki ^ Emi ^ Esi
        BCo = Ebo ^ Ego ^ Eko ^ Emo ^ Eso
        BCu = Ebu ^ Egu ^ Eku ^ Emu ^ Esu

        Da = BCu ^ ROL(BCe, 1)
        De = BCa ^ ROL(BCi, 1)
        Di = BCe ^ ROL(BCo, 1)
        Do = BCi ^ ROL(BCu, 1)
        Du = BCo ^ ROL(BCa, 1)

        Eba ^= Da
        BCa = Eba
        Ege ^= De
        BCe = ROL(Ege, 44)
        Eki ^= Di
        BCi = ROL(Eki, 43)
        Emo ^= Do
        BCo = ROL(Emo, 21)
        Esu ^= Du
        BCu = ROL(Esu, 14)
        Aba = BCa ^ ((~BCe) & BCi)
        Aba ^= RC[round + 1]
        Abe = BCe ^ ((~BCi) & BCo)
        Abi = BCi ^ ((~BCo) & BCu)
        Abo = BCo ^ ((~BCu) & BCa)
        Abu = BCu ^ ((~BCa) & BCe)

        Ebo ^= Do
        BCa = ROL(Ebo, 28)
        Egu ^= Du
        BCe = ROL(Egu, 20)
        Eka ^= Da
        BCi = ROL(Eka, 3)
        Eme ^= De
        BCo = ROL(Eme, 45)
        Esi ^= Di
        BCu = ROL(Esi, 61)
        Aga = BCa ^ ((~BCe) & BCi)
        Age = BCe ^ ((~BCi) & BCo)
        Agi = BCi ^ ((~BCo) & BCu)
        Ago = BCo ^ ((~BCu) & BCa)
        Agu = BCu ^ ((~BCa) & BCe)

        Ebe ^= De
        BCa = ROL(Ebe, 1)
        Egi ^= Di
        BCe = ROL(Egi, 6)
        Eko ^= Do
        BCi = ROL(Eko, 25)
        Emu ^= Du
        BCo = ROL(Emu, 8)
        Esa ^= Da
        BCu = ROL(Esa, 18)
        Aka = BCa ^ ((~BCe) & BCi)
        Ake = BCe ^ ((~BCi) & BCo)
        Aki = BCi ^ ((~BCo) & BCu)
        Ako = BCo ^ ((~BCu) & BCa)
        Aku = BCu ^ ((~BCa) & BCe)

        Ebu ^= Du
        BCa = ROL(Ebu, 27)
        Ega ^= Da
        BCe = ROL(Ega, 36)
        Eke ^= De
        BCi = ROL(Eke, 10)
        Emi ^= Di
        BCo = ROL(Emi, 15)
        Eso ^= Do
        BCu = ROL(Eso, 56)
        Ama = BCa ^ ((~BCe) & BCi)
        Ame = BCe ^ ((~BCi) & BCo)
        Ami = BCi ^ ((~BCo) & BCu)
        Amo = BCo ^ ((~BCu) & BCa)
        Amu = BCu ^ ((~BCa) & BCe)

        Ebi ^= Di
        BCa = ROL(Ebi, 62)
        Ego ^= Do
        BCe = ROL(Ego, 55)
        Eku ^= Du
        BCi = ROL(Eku, 39)
        Ema ^= Da
        BCo = ROL(Ema, 41)
        Ese ^= De
        BCu = ROL(Ese, 2)
        Asa = BCa ^ ((~BCe) & BCi)
        Ase = BCe ^ ((~BCi) & BCo)
        Asi = BCi ^ ((~BCo) & BCu)
        Aso = BCo ^ ((~BCu) & BCa)
        Asu = BCu ^ ((~BCa) & BCe)
    state[0], state[1], state[2], state[3], state[4] = Aba, Abe, Abi, Abo, Abu
    state[5], state[6], state[7], state[8], state[9] = Aga, Age, Agi, Ago, Agu
    state[10], state[11], state[12], state[13], state[14] = Aka, Ake, Aki, Ako, Aku
    state[15], state[16], state[17], state[18], state[19] = Ama, Ame, Ami, Amo, Amu
    state[20], state[21], state[22], state[23], state[24] = Asa, Ase, Asi, Aso, Asu



def keccak_absorb(state,rate,message,mlen,p):    #p is the domain separation tag
    remaining_input = message
    for i in range(25):
        state[i] = 0
    while mlen >= rate:
        for i in range(rate//8):
            state[i] ^= load64(remaining_input[8*i:8*(i+1)])
        keccak_p(state)
        remaining_input = remaining_input[rate:]
        mlen -= rate
    t=[]
    for i in range(rate):
        t.append(0)
    for i in range(mlen):
        t[i] = remaining_input[i]
    t[mlen] = p
    t[rate-1] |= 0x80
    for i in range(rate//8):
        state[i] ^= load64(t[8*i:8*(i+1)])

def faulty_keccak_absorb(state,rate,message,mlen,p,a2):    #p is the domain separation tag
    remaining_input = message
    for i in range(25):
        state[i] = 0
    while mlen >= rate:
        for i in range(rate//8):
            state[i] ^= load64(remaining_input[8*i:8*(i+1)])
        keccak_p(state)
        remaining_input = remaining_input[rate:]
        mlen -= rate
    t=[]
    for i in range(rate):
        t.append(0)
    if a2!=1:
        for i in range(mlen):
            t[i] = remaining_input[i]
    t[mlen] = p
    t[rate-1] |= 0x80
    if a2!=2:
        for i in range(rate//8):
            state[i] ^= load64(t[8*i:8*(i+1)])

def faulty_keccak_absorb_2(state,rate,message,mlen,p,a2):    #p is the domain separation tag
    remaining_input = message


def keccak_squeezeblocks(output,nblocks,state,rate):
    curblock=0
    while nblocks > 0:
        keccak_p(state)
        for i in range(rate//8):
            output[curblock*rate+8*i:curblock*rate+8*(i+1)] = store64(state[i])
            #print (output)
        curblock += 1
        nblocks -= 1


def faulty_keccak_squeezeblocks(output,nblocks,state,rate,a2):
    curblock=0
    while nblocks > 0:
        if a2!=3:
            keccak_p(state)
        for i in range(rate//8):
            output[curblock*rate+8*i:curblock*rate+8*(i+1)] = store64(state[i])
            #print (output)
        curblock += 1
        nblocks -= 1

#SHA3-256
def sha3_256(output,input):
    inlen=len(input)
    SHA3_256_RATE=136
    s = [0] * 25 
    t = bytearray(SHA3_256_RATE) 
    keccak_absorb(s, SHA3_256_RATE, input, inlen, 0x06)
    keccak_squeezeblocks(t, 1, s, SHA3_256_RATE)
    for i in range(32):
        output[i] = t[i]

# SHA3-512
def sha3_512(output,input):
    inlen=len(input)
    SHA3_512_RATE=72
    s = [0] * 25 
    t = bytearray(SHA3_512_RATE) 
    keccak_absorb(s, SHA3_512_RATE, input, inlen, 0x06)
    keccak_squeezeblocks(t, 1, s, SHA3_512_RATE)
    for i in range(64):
        output[i] = t[i]

def faulty_sha3_512(output,input,a2):
    inlen=len(input)
    SHA3_512_RATE=72
    s = [0] * 25 
    t = bytearray(SHA3_512_RATE) 
    if a2==1 or a2==2:
        faulty_keccak_absorb(s, SHA3_512_RATE, input, inlen, 0x06,a2)
    else:
        keccak_absorb(s, SHA3_512_RATE, input, inlen, 0x06)
    if a2==3:
        faulty_keccak_squeezeblocks(t, 1, s, SHA3_512_RATE,a2)
    else:
        keccak_squeezeblocks(t, 1, s, SHA3_512_RATE)
    for i in range(64):
        output[i] = t[i]

# SHAKE256 
# outlen is No. bits. It should be multiples of 8
def shake256(output,outlen,input):
    inlen=len(input)
    SHAKE256_RATE=136
    s = [0] * 25
    t=bytearray(SHAKE256_RATE) 
    nblocks=outlen//(SHAKE256_RATE*8)
    keccak_absorb(s, SHAKE256_RATE, input, inlen, 0x1F)
    keccak_squeezeblocks(output, nblocks, s, SHAKE256_RATE)
    outlen %= SHAKE256_RATE*8
    if outlen > 0:
        keccak_squeezeblocks(t, 1, s, SHAKE256_RATE)
        for i in range(outlen//8):
            output[i+SHAKE256_RATE*nblocks] = t[i]

def faulty_shake256(output,outlen,input,a2):
    inlen=len(input)
    SHAKE256_RATE=136
    s = [0] * 25
    t=bytearray(SHAKE256_RATE) 
    nblocks=outlen//(SHAKE256_RATE*8)
    if a2==1 or a2==2:
        faulty_keccak_absorb(s, SHAKE256_RATE, input, inlen, 0x1F,a2)
    else:
        keccak_absorb(s, SHAKE256_RATE, input, inlen, 0x1F)
        keccak_squeezeblocks(output, nblocks, s, SHAKE256_RATE)
    outlen %= SHAKE256_RATE*8
    if outlen > 0:
        if a2==3:
            faulty_keccak_squeezeblocks(t, 1, s, SHAKE256_RATE,a2)
        else:
            keccak_squeezeblocks(t, 1, s, SHAKE256_RATE)
        for i in range(outlen//8):
            output[i+SHAKE256_RATE*nblocks] = t[i]

def faulty_shake256_2(output,outlen,input,a2):
    inlen=len(input)
    SHAKE256_RATE=136
    s = [0] * 25
    t=bytearray(SHAKE256_RATE) 
    nblocks=outlen//(SHAKE256_RATE*8)
    if a2==1 or a2==2:
        faulty_keccak_absorb_2(s, SHAKE256_RATE, input, inlen, 0x1F,a2)
    else:
        keccak_absorb(s, SHAKE256_RATE, input, inlen, 0x1F)
        keccak_squeezeblocks(output, nblocks, s, SHAKE256_RATE)
    outlen %= SHAKE256_RATE*8
    if outlen > 0:
        if a2==3:
            faulty_keccak_squeezeblocks(t, 1, s, SHAKE256_RATE,a2)
        else:
            keccak_squeezeblocks(t, 1, s, SHAKE256_RATE)
        for i in range(outlen//8):
            output[i+SHAKE256_RATE*nblocks] = t[i]
        
def shake128(output,outlen,input):
    inlen=len(input)
    SHAKE128_RATE=168
    s = [0] * 25
    t=bytearray(SHAKE128_RATE) 
    nblocks=outlen//(SHAKE128_RATE*8)
    keccak_absorb(s, SHAKE128_RATE, input, inlen, 0x1F)
    keccak_squeezeblocks(output, nblocks, s, SHAKE128_RATE)
    outlen %= SHAKE128_RATE*8
    if outlen > 0:
        keccak_squeezeblocks(t, 1, s, SHAKE128_RATE)
        for i in range(outlen//8):
            output[i+SHAKE128_RATE*nblocks] = t[i]


# Incremental implementation of Keccak
# ctx is a 26-bytes state array, ctx[25] is the number of non-absorbed bytes
def keccak_inc_init():
    ctx=[0]*26
    return ctx

def keccak_inc_absorb(ctx, rate, input, inlen):
    remaining_input = input
    while (inlen+ctx[25]>=rate):
        for i in range(rate-ctx[25]):
            ctx[(ctx[25]+i)>>3] ^= remaining_input[i] << (8*((ctx[25]+i) & 7))
        inlen -= rate-ctx[25]
        remaining_input = remaining_input[rate-ctx[25]:]
        ctx[25] = 0
        keccak_p(ctx)
    for i in range(inlen):
        ctx[(ctx[25]+i)>>3] ^= remaining_input[i] << (8*((ctx[25]+i) & 7))
    ctx[25] += inlen

def faulty_keccak_inc_absorb(ctx, rate, input, inlen):
    remaining_input = input
    while (inlen+ctx[25]>=rate):
        for i in range(rate-ctx[25]):
            ctx[(ctx[25]+i)>>3] ^= remaining_input[i] << (8*((ctx[25]+i) & 7))
        inlen -= rate-ctx[25]
        remaining_input = remaining_input[rate-ctx[25]:]
        ctx[25] = 0
        keccak_p(ctx)
    ctx[25] += inlen


# padding
def keccak_inc_finalize(ctx, rate, p):
    ctx[ctx[25]>>3] ^= p << (8*(ctx[25] & 7))
    ctx[(rate-1)>>3] ^= 0x80 << (8*((rate-1) & 7))
    ctx[25] = 0

def keccak_inc_squeeze(output,outlen,ctx,rate):
    curindex=0
    i=-1
    for i in range(min(outlen,ctx[25])):
        output[i]=(ctx[(rate-ctx[25]+i)>>3] >> (8*((rate-ctx[25]+i) & 7))) & 0xff
    curindex+=i+1
    outlen-=i+1
    ctx[25] -= i+1
    while (outlen>0):
        keccak_p(ctx)
        for i in range(min(outlen,rate)):
            output[curindex+i]=(ctx[i>>3] >> (8*(i & 7))) & 0xff
        curindex+=i+1
        outlen-=i+1
        ctx[25] = rate-i-1

def keccak_inc_release(ctx):
    ctx=None

def shake128_inc_init():
    return keccak_inc_init()

def shake128_inc_absorb(ctx, input):
    keccak_inc_absorb(ctx, 168, input, len(input))

def shake128_inc_finalize(ctx):
    keccak_inc_finalize(ctx, 168, 0x1F)

def shake128_inc_squeeze(output, outlen, ctx):
    keccak_inc_squeeze(output, outlen, ctx, 168)

def shake128_inc_release(ctx):
    keccak_inc_release(ctx)

def shake256_inc_init():
    return keccak_inc_init()

def shake256_inc_absorb(ctx, input):
    keccak_inc_absorb(ctx, 136, input, len(input))

def faulty_shake256_inc_absorb(ctx, input):
    faulty_keccak_inc_absorb(ctx, 136, input, len(input))

def shake256_inc_finalize(ctx):
    keccak_inc_finalize(ctx, 136, 0x1F)

def shake256_inc_squeeze(output, outlen, ctx):
    keccak_inc_squeeze(output, outlen, ctx, 136)

def shake256_inc_release(ctx):
    keccak_inc_release(ctx)


#PRF function using Keccak
def PRF(eta,s,b):
    output=bytearray(512*eta)
    shake256(output,512*eta,s+b)
    return output

def faulty_PRF(eta,s,b,a2):
    output=bytearray(512*eta)
    faulty_shake256(output,512*eta,s+b,a2)
    return output


if __name__ == '__main__':
    print ("Testing Keccak Functions...")
    message = bytearray(b"666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666")
    message1=bytearray(b"555555555555555555555555555555555555555555555")
    message2=bytearray(b"12345678901234567890123456789012345678901234")

    allright=True

    #test shake256 incremental API
    print("Testing incremental shake256 API...")
    output1 = bytearray(3)
    output2 = bytearray(100)
    output3 = bytearray(47)
    ctx= shake256_inc_init()
    shake256_inc_absorb(ctx, message)
    shake256_inc_absorb(ctx, message1)
    shake256_inc_absorb(ctx, message2)
    shake256_inc_finalize(ctx)
    shake256_inc_squeeze(output1, 3, ctx)
    shake256_inc_squeeze(output2, 100, ctx)
    shake256_inc_squeeze(output3, 47, ctx)
    shake256_inc_release(ctx)
    if (output1.hex()=='16fcf8' 
    and output2.hex()=='24272762c5e096bc97b9b6603011f63592688754ded842cd65ebc77d5db2923813d610a16049bf8727e30209010661811b6188df2064229387073f772cf1a9f57f39bc20ebdfbe084408fd8fff71df7873ca567aba6ab088f07bc4d6ff302d6a0816fac2'
    and output3.hex()=='487089b471704098f9e2e8136afbba3c3ff8d29e4120b0d08d2688ce2f67ec1211fe7addc47e1bdd547499e4682244') :
        print("Incremental shake256 API test passed")
    else:
        print("Incremental shake256 API test failed")
        allright=False

    #test shake128 incremental API
    print("Testing incremental shake128 API...")
    output1 = bytearray(47)
    output2 = bytearray(3)
    output3 = bytearray(100)
    ctx=shake128_inc_init()
    shake128_inc_absorb(ctx, message)
    shake128_inc_absorb(ctx, message1)
    shake128_inc_absorb(ctx, message2)
    shake128_inc_finalize(ctx)
    shake128_inc_squeeze(output1, 47, ctx)
    shake128_inc_squeeze(output2, 3, ctx)
    shake128_inc_squeeze(output3, 100, ctx)
    shake128_inc_release(ctx)
    if (output1.hex()=='1e4b63a719b007c597404f33e1718f59d7cebc06b95772f51f280a238b8b8584a7808b7f922205527884ae5a264ebd'
    and output2.hex()=='46cc36'
    and output3.hex()=='f6890fdfac3720018bc54e7948c2664bd02c25c02a82f1aa509790a27c2f82f78e51226191e69c13fc93bdea23ff608429006dc3bf46de0be0d483fc53052e479db54832cefef4d733f253d19ab68e2ffea98d788b9e93d2fb4384454ad67fb20b0d1651') :
        print("Incremental shake128 API test passed")
    else:
        print("Incremental shake128 API test failed")
        allright=False

    #test sha3_256
    print("Testing sha3_256 API...")
    output1 = bytearray(32)
    sha3_256(output1, [233])
    output2 = bytearray(32)
    sha3_256(output2, bytearray.fromhex('b1caa396771a09a1db9bc20543e988e359d47c2a616417bbca1b62cb02796a888fc6eeff5c0b5c3d5062fcb4256f6ae1782f492c1cf03610b4a1fb7b814c057878e1190b9835425c7a4a0e182ad1f91535ed2a35033a5d8c670e21c575ff43c194a58a82d4a1a44881dd61f9f8161fc6b998860cbe4975780be93b6f87980bad0a99aa2cb7556b478ca35d1f3746c33e2bb7c47af426641cc7bbb3425e2144820345e1d0ea5b7da2c3236a52906acdc3b4d34e474dd714c0c40bf006a3a1d889a632983814bbc4a14fe5f159aa89249e7c738b3b73666bac2a615a83fd21ae0a1ce7352ade7b278b587158fd2fabb217aa1fe31d0bda53272045598015a8ae4d8cec226fefa58daa05500906c4d85e7567'))
    if (output1.hex()=='f0d04dd1e6cfc29a4460d521796852f25d9ef8d28b44ee91ff5b759d72c1e6d6' and output2.hex()=='cb5648a1d61c6c5bdacd96f81c9591debc3950dcf658145b8d996570ba881a05' ) :
        print("sha3_256 test passed")
    else:
        print("sha3_256 test failed")
        allright=False
    
    #test sha3_512
    print("Testing sha3_512 API...")
    output1 = bytearray(64)
    sha3_512(output1, bytearray.fromhex('fc7b8cda'))
    output2 = bytearray(64) 
    sha3_512(output2, bytearray.fromhex('85ff5f072442756665a41f36cb2c99d3152f3458bfc3fcb5cc759901c33f7311f8b41a490c7ee4b2b70ad84dc582caa75ffcc8ae8cf1b5c3f8f03410f393c81cbcb3399c00d8398d9ef3477fad50d434c0c6a469683178f4fb22ea0f94d498f45b6284aa0738bb1ea1c735758a7efda1bff591325c6b8c6f5f7282a6afe92cc05d2bc5182986b38e48ef6ad764f38e17e5f157b16f873a5dab4ac67c4bbacca94875c2916eaa69041bd1ae4c4499cebdb822be8da96dcae668117c3a702fbfd7a6a744bbdf8c25a9a3d6c97c315707bcc2f18e6f120584311d2e6d8726304f71fe2b133e83152fa46766821033157f3b8bc48efeb338af67520b610c76a5c29fd968f7c3632bce1eefeaa2b052bb8063990487e393ec95af900f20716776618bbec6b8f285b74c3fc4c8f2039732505b761a42c5ba0a7c325da2715d028b745a35ad1d72f3a2ef2e6d6a37b20960374caa6c844d317bad18442c1d784ecc4337c685f0ecb5d2001472363c64b02e7f5ebb641823ff257088ca15ed6b53221548fab6f707d131c6185c96c8c295846eb83369c5ee2cf20daa79c6a6de197334b558a8fb6c51a68b63b2f1a274bf4b4e839ae25256c1c9cba7d8a51378a9a9e6a769c4c3c23c18951cfcaf9321366965e676398805c591f3a76f1bfbe20aaa7446b37019b29b712e6cc337637103c8fc0a51d52fa04034cdd1c79125c4446026b9c015c3e475989c7b8df3da0e2d4e5a17b21e0fd23b99a14e676d5ac460b14329181c8affd2752770e54abf9dbce5c934227cef40bca8b746d718628d658715bd41eb36acbbf0197450a4dcc9b9748f8928579895ce4956e0a0fb05c55bc9e29ec5ec8f9236f1b8ae5869f7372be3f53f4c17d3777664c844497d0b154a5ff3f32c865c5a4e604e478402d9921a1a437e1624668fbee1539b5a053b243b3090e5fc2067ab082521665cd54a808f00c16d0fe71984ada8400d5cfd5e9b3526009cbf24762e6e287934694b12a9907fb735bec6b6fe4ba2d7c1d6cc3c2141288d3ffcf9528a8752a0d932cdf8b7287e6cfdab2a03a7a1b55fe050da9d5f661f7df63c07c3685b89dd7c40c1c54f5ce629ee5f7cca24b6ca2291528f49fcacf119eb06b69170f3b677451990411b369d36306122d12093ca66fd655307a11b87a943e26e834956c2b75d47a334c3bd8cdbea3986e1413e9b744b108ea1f6bcc975295897629c8c93e5ec526166eff99b6045700ec12fc12794a4dca8dda2969fc4c3f199f6109e134919c0319f46f3b30c688d243b9324540d305009844eb1f2e03934dc074e93282a0d1b7da670b2ba287b182f1515'))
    if (output1.hex()=='58a5422d6b15eb1f223ebe4f4a5281bc6824d1599d979f4c6fe45695ca89014260b859a2d46ebf75f51ff204927932c79270dd7aef975657bb48fe09d8ea008e'
        and output2.hex()=='6d87f523d51ebfc11fffb33357ed7ff3e4051f58a52d45fba208429ee5b53995e5129d35e3b8d3448a3f56d32dbfdc762a1458569c839a4a1c57b4d69251f565'):
        print("sha3_512 test passed")
    else:
        print("sha3_512 test failed")
        allright=False

    #test shake128
    print("Testing shake128 API...")
    output1 = bytearray(111)
    shake128(output1,888,message)
    if output1.hex()=='f614bd18af5c48f6c4064925c2a9263b5b8012076a25220b8ddf945dd80fe29fc79b716f9e250f9c0b1eb25274da9c9d33040492ef1ce77c7e0805ced04f46a3a93368c0cd1461f53fbad15201dad5623430f3063c78d0e3a6599ee5aa439ff97c10a4332fb308ede6509e848f8184':
        print("shake128 test passed")
    else:
        print("shake128 test failed")
        allright=False

    #test shake128
    print("Testing shake256 API...")
    output1 = bytearray(150)
    shake256(output1,1200,message)
    if output1.hex()=='7c4c495eed3ea3f2f4a4c42f071339e2edc446a9659fa6c4c379481a4beabe07ae1c35d7948e44889ae49f0ee11fd86f4ca0a240f6b11a365914174f189ed85a4ba7391a9d2097a0f5521270d1f3f132dec8e47a1894e30b2923d64cb7487b7923718875ad724ad654f4197dac3b7bb16483352524ebaca63d4d8591d22e72e539ced0e405585aef85e58cabdf2052e94b19d106dd8c':
        print("shake256 test passed")
    else:
        print("shake256 test failed")
        allright=False

    print("////////////////////////////////////////////////////////////////////////////////////////////////")
    if allright:
        print("All tests passed!!!")
    else:
        print("Some tests failed")