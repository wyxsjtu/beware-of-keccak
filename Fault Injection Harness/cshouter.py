from chipshouter import ChipSHOUTER
import subprocess
import time


def init_cs(CS_COM):
    return ChipSHOUTER(CS_COM)
def set_params(cs):
    # ChipSHOUTER trigger settings
    cs.hwtrig_term = 0
    cs.hwtrig_mode = 0
    cs.voltage = 500
    cs.pulse.width = 80 # [80 , 1000]
    cs.mute=True
    
def chk_n_arm(cs):
    if not cs.armed:
        cs.clr_armed=1

# if __name__ == "__main__":
#     main()