from tqdm import tqdm
import testvectors
import MLDSA

def correctness_check():
    keygenflag=False
    signflag=False
    verifyflag=False
    print("Correctness Check")
    print("Checking ML-DSA Key Generation...")
    mldsa44keygenflag=True
    for i in tqdm(range(len(testvectors.MLDSA44_keygen_testvectors))):
        cur=testvectors.MLDSA44_keygen_testvectors[i]
        seed=bytearray.fromhex(cur[0])
        pk,sk=MLDSA.MLDSA_KeyGen_Internal(seed,variant=44)
        if pk.hex()!=cur[1].lower() or sk.hex()!=cur[2].lower():
            mldsa44keygenflag=False
            print("ML-DSA-44 Key Generation Test Vector",i+1,"Failed")
            break
    if mldsa44keygenflag:
        print("ML-DSA-44 Key Generation Test Vectors Passed")
    mldsa65keygenflag=True
    for i in tqdm(range(len(testvectors.MLDSA65_keygen_testvectors))):
        cur=testvectors.MLDSA65_keygen_testvectors[i]
        seed=bytearray.fromhex(cur[0])
        pk,sk=MLDSA.MLDSA_KeyGen_Internal(seed,variant=65)
        if pk.hex()!=cur[1].lower() or sk.hex()!=cur[2].lower():
            mldsa65keygenflag=False
            print("ML-DSA-65 Key Generation Test Vector",i+1,"Failed")
            break
    if mldsa65keygenflag:
        print("ML-DSA-65 Key Generation Test Vectors Passed")
    mldsa87keygenflag=True
    for i in tqdm(range(len(testvectors.MLDSA87_keygen_testvectors))):
        cur=testvectors.MLDSA87_keygen_testvectors[i]
        seed=bytearray.fromhex(cur[0])
        pk,sk=MLDSA.MLDSA_KeyGen_Internal(seed,variant=87)
        if pk.hex()!=cur[1].lower() or sk.hex()!=cur[2].lower():
            mldsa87keygenflag=False
            print("ML-DSA-87 Key Generation Test Vector",i+1,"Failed")
            break
    if mldsa87keygenflag:
        print("ML-DSA-87 Key Generation Test Vectors Passed")
    if mldsa44keygenflag and mldsa65keygenflag and mldsa87keygenflag:
        keygenflag=True
        print("ML-DSA Key Generation Test Vectors Passed")
    
    print("Checking ML-DSA Signing...")
    mldsa44signflag=True
    for i in tqdm(range(len(testvectors.MLDSA44_sign_testvectors))):
        cur=testvectors.MLDSA44_sign_testvectors[i]
        sk=bytearray.fromhex(cur[0])
        msg=bytearray.fromhex(cur[1])
        sig=MLDSA.MLDSA_Sign_Internal(sk,msg,bytearray(32),variant=44)
        if sig.hex()!=cur[2].lower():
            mldsa44signflag=False
            print("ML-DSA-44 Signing Test Vector",i+1,"Failed")
            break
    if mldsa44signflag:
        print("ML-DSA-44 Signing Test Vectors Passed")
    mldsa65signflag=True
    for i in tqdm(range(len(testvectors.MLDSA65_sign_testvectors))):
        cur=testvectors.MLDSA65_sign_testvectors[i]
        sk=bytearray.fromhex(cur[0])
        msg=bytearray.fromhex(cur[1])
        sig=MLDSA.MLDSA_Sign_Internal(sk,msg,bytearray(32),variant=65)
        if sig.hex()!=cur[2].lower():
            mldsa65signflag=False
            print("ML-DSA-65 Signing Test Vector",i+1,"Failed")
            break
    if mldsa65signflag:
        print("ML-DSA-65 Signing Test Vectors Passed")
    mldsa87signflag=True
    for i in tqdm(range(len(testvectors.MLDSA87_sign_testvectors))):
        cur=testvectors.MLDSA87_sign_testvectors[i]
        sk=bytearray.fromhex(cur[0])
        msg=bytearray.fromhex(cur[1])
        sig=MLDSA.MLDSA_Sign_Internal(sk,msg,bytearray(32),variant=87)
        if sig.hex()!=cur[2].lower():
            mldsa87signflag=False
            print("ML-DSA-87 Signing Test Vector",i+1,"Failed")
            break
    if mldsa87signflag:
        print("ML-DSA-87 Signing Test Vectors Passed")
    if mldsa44signflag and mldsa65signflag and mldsa87signflag:
        signflag=True
        print("ML-DSA Signing Test Vectors Passed")

    print("Checking ML-DSA Verification...")
    mldsa44verifyflag=True
    for i in tqdm(range(len(testvectors.MLDSA44_verify_testvectors))):
        cur=testvectors.MLDSA44_verify_testvectors[i]
        pk=bytearray.fromhex(cur[1])
        msg=bytearray.fromhex(cur[2])
        sig=bytearray.fromhex(cur[3])
        if MLDSA.MLDSA_Verify_Internal(pk,msg,sig,variant=44) != cur[0]:
            mldsa44verifyflag=False
            print("ML-DSA-44 Verification Test Vector",i+1,"Failed")
            break
    if mldsa44verifyflag:
        print("ML-DSA-44 Verification Test Vectors Passed")
    mldsa65verifyflag=True
    for i in tqdm(range(len(testvectors.MLDSA65_verify_testvectors))):
        cur=testvectors.MLDSA65_verify_testvectors[i]
        pk=bytearray.fromhex(cur[1])
        msg=bytearray.fromhex(cur[2])
        sig=bytearray.fromhex(cur[3])
        if MLDSA.MLDSA_Verify_Internal(pk,msg,sig,variant=65) != cur[0]:
            mldsa65verifyflag=False
            print("ML-DSA-65 Verification Test Vector",i+1,"Failed")
            break
    if mldsa65verifyflag:
        print("ML-DSA-65 Verification Test Vectors Passed")
    mldsa87verifyflag=True
    for i in tqdm(range(len(testvectors.MLDSA87_verify_testvectors))):
        cur=testvectors.MLDSA87_verify_testvectors[i]
        pk=bytearray.fromhex(cur[1])
        msg=bytearray.fromhex(cur[2])
        sig=bytearray.fromhex(cur[3])
        if MLDSA.MLDSA_Verify_Internal(pk,msg,sig,variant=87) != cur[0]:
            mldsa87verifyflag=False
            print("ML-DSA-87 Verification Test Vector",i+1,"Failed")
            break
    if mldsa87verifyflag:
        print("ML-DSA-87 Verification Test Vectors Passed")
    if mldsa44verifyflag and mldsa65verifyflag and mldsa87verifyflag:
        verifyflag=True
        print("ML-DSA Verification Test Vectors Passed")

    if keygenflag and signflag and verifyflag:
        print("All Correctness Tests Passed !!!!!!")



if __name__=="__main__":
    correctness_check()