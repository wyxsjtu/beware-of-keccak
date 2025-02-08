
# Only these 3+1 functions are exposed to the user.
import KPKE_MLKEM
import correctness_check

#Input: variant (default=512), MLKEM variant, can be 512 or 768 or 1024
#Output: ek dk, public key and private key, bytearrays
#length of ek: 800 (variant=512), 1184 (variant=768), 1568 (variant=1024)
#length of dk: 1632 (variant=512), 2400 (variant=768), 3168 (variant=1024)
#lengths are in bytes
def MLKEM_keygen_api(variant=512):
    return KPKE_MLKEM.MLKEM_keygen(variant)


#Input: ek (public key), bytearray; variant (default=512), MLKEM variant, can be 512 or 768 or 1024
#length of ek: 800 (variant=512), 1184 (variant=768), 1568 (variant=1024)
#Output: k, shared key, bytearray; c, ciphertext, bytearray
#length of k: 32
#length of c: 768 (variant=512), 1088 (variant=768), 1568 (variant=1024)
#lengths are in bytes
def MLKEM_encaps_api(ek, variant=512):
    return KPKE_MLKEM.MLKEM_encaps(ek, variant)


#Input: dk (private key), bytearray; c (ciphertext), bytearray; variant (default=512), MLKEM variant, can be 512 or 768 or 1024
#length of dk: 1632 (variant=512), 2400 (variant=768), 3168 (variant=1024)
#length of c: 768 (variant=512), 1088 (variant=768), 1568 (variant=1024)
#Output: k, shared key, bytearray
#length of k: 32
def MLKEM_decaps_api(dk, c, variant=512):
    return KPKE_MLKEM.MLKEM_decaps(dk, c, variant)

# CHECK CORRECTNESS OF OUR IMPLEMENTATION USING OFFICIAL TEST VECTORS FROM NIST
def correctness_check_api():
    return correctness_check.correctness_check()



#Examples:
if __name__ == '__main__':
    # Generate key pair (Keygen)
    ek, dk= MLKEM_keygen_api(variant=1024)
    print("length of ek:",len(ek))
    print("length of dk:",len(dk))
    # Generate shared key and ciphertext (Encaps)
    k, c = MLKEM_encaps_api(ek, variant=1024)
    print("length of k:",len(k))
    print("length of c:",len(c))
    # Decrypt shared key (Decaps)
    k_dec = MLKEM_decaps_api(dk, c, variant=1024)
    print("length of k_dec:",len(k_dec))
    # Check correctness of our implementation using official test vectors from NIST
    res=correctness_check_api()

    if k == k_dec and res:
        print("Example successful")
    else:
        print("Example failed")