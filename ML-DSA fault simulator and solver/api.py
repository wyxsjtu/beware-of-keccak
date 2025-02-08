# Only these 3+1 functions are exposed to the user.
import MLDSA
import correctness_check
import time

# Input: variant (default=44), MLDSA variant, can be 44, 65 or 87
# Output: pk, sk, public key and private key, bytearrays
# length of pk: 1312 (variant=44), 1952 (variant=65), 2592 (variant=87)
# length of sk: 2560 (variant=44), 4032 (variant=65), 4896 (variant=87)
# lengths are in bytes
def MLDSA_KeyGen_api(variant=44):
    return MLDSA.MLDSA_KeyGen(variant)

# Input: sk (private key, bytearray), m (message, bytearray), ctx (context,bytearray), variant (default=44), MLDSA variant, can be 44, 65 or 87
# Output: signature, bytearray
# length of sk: 2560 (variant=44), 4032 (variant=65), 4896 (variant=87)
# length of ctx: less than 255, default is 32-byte zero array
# length of signature: 2420 (variant=44), 3309 (variant=65), 4627 (variant=87)
# lengths are in bytes
def MLDSA_Sign_api(sk,m,ctx=bytearray(32), variant=44):
    return MLDSA.MLDSA_Sign(sk,m,ctx, variant)

# Input: pk (public key, bytearray), m (message, bytearray), signature (bytearray), ctx (context,bytearray), variant (default=44), MLDSA variant, can be 44, 65 or 87
# Output: True if signature is valid, False otherwise
# length of pk: 1312 (variant=44), 1952 (variant=65), 2592 (variant=87)
# length of ctx: less than 255, default is 32-byte zero array
# length of signature: 2420 (variant=44), 3309 (variant=65), 4627 (variant=87)
# lengths are in bytes
def MLDSA_Verify_api(pk,m,signature,ctx=bytearray(32), variant=44):
    return MLDSA.MLDSA_Verify(pk,m,signature,ctx, variant)

def check_correctness_api():
    correctness_check.correctness_check()

if __name__ == '__main__':
    print("ML-DSA API")
    print("KeyGen")
    pk, sk = MLDSA_KeyGen_api(variant=87)
    print("pk length:", len(pk))
    print("sk length:", len(sk))
    print("Sign")
    m = bytearray(b"Hello World")
    signature = MLDSA_Sign_api(sk,m,variant=87)
    print("signature length:", len(signature))
    print("Verify")
    result = MLDSA_Verify_api(pk,m,signature,variant=87)
    print("Result:", result)
    print("Checking correctness using test vectors, this may take about 40 seconds...")
    start_time = time.time()
    check_correctness_api()
    end_time = time.time()
    print("Time taken:", round(end_time - start_time,2), "seconds")