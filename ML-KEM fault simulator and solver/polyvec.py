import NTT
import params

# NTT transform of a vector using NTT_montgomery
def NTT_montgomery_vec(vec):
    n=len(vec)
    vec_hat=[0 for i in range(n)]
    for i in range(n):
        vec_hat[i]=NTT.NTT_montgomery(vec[i])
    return vec_hat

# iNTT transform of a vector using NTT_montgomery
def iNTT_montgomery_vec(vec_hat):
    n=len(vec_hat)
    vec=[0 for i in range(n)]
    for i in range(n):
        vec[i]=NTT.iNTT_montgomery(vec_hat[i])
    return vec

def polyadd(poly1,poly2):
    poly_sum=[0 for i in range(params.MLKEM_N)]
    for i in range(params.MLKEM_N):
        poly_sum[i]=NTT.barrett_reduce(poly1[i]+poly2[i])
    return poly_sum

def polyadd_vec(vec1,vec2):
    n=len(vec1)
    vec_sum=[0 for i in range(n)]
    for i in range(n):
        vec_sum[i]=polyadd(vec1[i],vec2[i])
    return vec_sum

def polysub(poly1,poly2):
    poly_sum=[0 for i in range(params.MLKEM_N)]
    for i in range(params.MLKEM_N):
        poly_sum[i]=NTT.barrett_reduce(poly1[i]-poly2[i])
    return poly_sum

def polysub_vec(vec1,vec2):
    n=len(vec1)
    vec_sum=[0 for i in range(n)]
    for i in range(n):
        vec_sum[i]=polysub(vec1[i],vec2[i])
    return vec_sum

def MultiplyNTT_montgomery_vec(vec1,vec2):
    n=len(vec1)
    vec_prod=[0 for i in range(params.MLKEM_N)]
    for i in range(n):
        vec_prod=polyadd(vec_prod,NTT.MultiplyNTT_montgomery(vec1[i],vec2[i]))
    return vec_prod





if __name__=="__main__":
    poly1=[2222]*256
    poly2=[3333]*256
    poly_sum=polyadd(poly1,poly2)
    print(poly_sum)

    polyvec1=[[i for i in range(256)] for i in range(3)]
    polyvec2=[[3300 for i in range(256)] for i in range(3)]
    polyvec_sum=polyadd_vec(polyvec1,polyvec2)
    print(polyvec_sum)