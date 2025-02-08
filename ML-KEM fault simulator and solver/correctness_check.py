from tqdm import tqdm
import testvectors
import KPKE_MLKEM
def correctness_check():
    keygenflag=False
    encapsflag=False
    decapsflag=False
    print("Correctness check")
    print("Checking ML-KEM 512 key generation...")
    mlkem512keygenflag=True
    for i in tqdm(range(len(testvectors.MLKEM512_keygen_testvectors))):
        cur=testvectors.MLKEM512_keygen_testvectors[i]
        d=bytearray.fromhex(cur[1])
        z=bytearray.fromhex(cur[0])
        ek,dk=KPKE_MLKEM.MLKEM_keygen_internal(d,z,variant=512)
        if ek.hex()!=cur[2].lower() or dk.hex()!=cur[3].lower():
            mlkem512keygenflag=False
            print("ML-KEM 512 key generation test vector",i+1,"failed")
            break
    if mlkem512keygenflag:
        print("ML-KEM 512 key generation test vectors passed")

    print("Checking ML-KEM 768 key generation...")
    mlkem768keygenflag=True
    for i in tqdm(range(len(testvectors.MLKEM768_keygen_testvectors))):
        cur=testvectors.MLKEM768_keygen_testvectors[i]
        d=bytearray.fromhex(cur[1])
        z=bytearray.fromhex(cur[0])
        ek,dk=KPKE_MLKEM.MLKEM_keygen_internal(d,z,variant=768)
        if ek.hex()!=cur[2].lower() or dk.hex()!=cur[3].lower():
            mlkem768keygenflag=False
            print("ML-KEM 768 key generation test vector",i+1,"failed")
            break
    if mlkem768keygenflag:
        print("ML-KEM 768 key generation test vectors passed")

    print("Checking ML-KEM 1024 key generation...")
    mlkem1024keygenflag=True
    for i in tqdm(range(len(testvectors.MLKEM1024_keygen_testvectors))):
        cur=testvectors.MLKEM1024_keygen_testvectors[i]
        d=bytearray.fromhex(cur[1])
        z=bytearray.fromhex(cur[0])
        ek,dk=KPKE_MLKEM.MLKEM_keygen_internal(d,z,variant=1024)
        if ek.hex()!=cur[2].lower() or dk.hex()!=cur[3].lower():
            mlkem1024keygenflag=False
            print("ML-KEM 1024 key generation test vector",i+1,"failed")
            break
    if mlkem1024keygenflag:
        print("ML-KEM 1024 key generation test vectors passed")
    if mlkem512keygenflag and mlkem768keygenflag and mlkem1024keygenflag:
        print("All ML-KEM key generation test vectors passed")
        keygenflag=True


    print("Checking ML-KEM 512 encapsulation...")
    mlkem512encapsflag=True
    for i in tqdm(range(len(testvectors.MLKEM512_encaps_testvectors))):
        cur=testvectors.MLKEM512_encaps_testvectors[i]
        m=bytearray.fromhex(cur[0])
        ek=bytearray.fromhex(cur[1])
        k,c=KPKE_MLKEM.MLKEM_encaps_internal(ek,m,variant=512)
        if k.hex()!=cur[3].lower() or c.hex()!=cur[2].lower():
            mlkem512encapsflag=False
            print("ML-KEM 512 encapsulation test vector",i+1,"failed")
            break
    if mlkem512encapsflag:
        print("ML-KEM 512 encapsulation test vectors passed")
    
    print("Checking ML-KEM 768 encapsulation...")
    mlkem768encapsflag=True
    for i in tqdm(range(len(testvectors.MLKEM768_encaps_testvectors))):
        cur=testvectors.MLKEM768_encaps_testvectors[i]
        m=bytearray.fromhex(cur[0])
        ek=bytearray.fromhex(cur[1])
        k,c=KPKE_MLKEM.MLKEM_encaps_internal(ek,m,variant=768)
        if k.hex()!=cur[3].lower() or c.hex()!=cur[2].lower():
            mlkem768encapsflag=False
            print("ML-KEM 768 encapsulation test vector",i+1,"failed")
            break
    if mlkem768encapsflag:
        print("ML-KEM 768 encapsulation test vectors passed")

    print("Checking ML-KEM 1024 encapsulation...")
    mlkem1024encapsflag=True
    for i in tqdm(range(len(testvectors.MLKEM1024_encaps_testvectors))):
        cur=testvectors.MLKEM1024_encaps_testvectors[i]
        m=bytearray.fromhex(cur[0])
        ek=bytearray.fromhex(cur[1])
        k,c=KPKE_MLKEM.MLKEM_encaps_internal(ek,m,variant=1024)
        if k.hex()!=cur[3].lower() or c.hex()!=cur[2].lower():
            mlkem1024encapsflag=False
            print("ML-KEM 1024 encapsulation test vector",i+1,"failed")
            break
    if mlkem1024encapsflag:
        print("ML-KEM 1024 encapsulation test vectors passed")

    if mlkem512encapsflag and mlkem768encapsflag and mlkem1024encapsflag:
        print("All ML-KEM encapsulation test vectors passed")
        encapsflag=True

    print("Checking ML-KEM 512 decapsulation...")
    mlkem512decapsflag=True
    for i in tqdm(range(len(testvectors.MLKEM512_decaps_testvectors))):
        cur=testvectors.MLKEM512_decaps_testvectors[i]
        dk=bytearray.fromhex(cur[0])
        c=bytearray.fromhex(cur[1])
        k=KPKE_MLKEM.MLKEM_decaps_internal(dk,c,variant=512)
        if k.hex()!=cur[2].lower():
            mlkem512decapsflag=False
            print("ML-KEM 512 decapsulation test vector",i+1,"failed")
            break
    if mlkem512decapsflag:
        print("ML-KEM 512 decapsulation test vectors passed")

    print("Checking ML-KEM 768 decapsulation...")
    mlkem768decapsflag=True
    for i in tqdm(range(len(testvectors.MLKEM768_decaps_testvectors))):
        cur=testvectors.MLKEM768_decaps_testvectors[i]
        dk=bytearray.fromhex(cur[0])
        c=bytearray.fromhex(cur[1])
        k=KPKE_MLKEM.MLKEM_decaps_internal(dk,c,variant=768)
        if k.hex()!=cur[2].lower():
            mlkem768decapsflag=False
            print("ML-KEM 768 decapsulation test vector",i+1,"failed")
            break
    if mlkem768decapsflag:
        print("ML-KEM 768 decapsulation test vectors passed")

    print("Checking ML-KEM 1024 decapsulation...")
    mlkem1024decapsflag=True
    for i in tqdm(range(len(testvectors.MLKEM1024_decaps_testvectors))):
        cur=testvectors.MLKEM1024_decaps_testvectors[i]
        dk=bytearray.fromhex(cur[0])
        c=bytearray.fromhex(cur[1])
        k=KPKE_MLKEM.MLKEM_decaps_internal(dk,c,variant=1024)
        if k.hex()!=cur[2].lower():
            mlkem1024decapsflag=False
            print("ML-KEM 1024 decapsulation test vector",i+1,"failed")
            break
    if mlkem1024decapsflag:
        print("ML-KEM 1024 decapsulation test vectors passed")

    if mlkem512decapsflag and mlkem768decapsflag and mlkem1024decapsflag:
        print("All ML-KEM decapsulation test vectors passed")
        decapsflag=True

    flag=keygenflag and encapsflag and decapsflag
    if flag:
        print("All ML-KEM test vectors passed")
    return flag

if __name__ == '__main__':
    correctness_check()

