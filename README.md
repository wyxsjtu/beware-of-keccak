

# Beware of KECCAK: A Practical Fault Injection Attack Scheme Apply to All Phases of ML-KEM and ML-DSA.

This is the code repository for the paper Beware of KECCAK: A Practical Fault Injection Attack Scheme Apply to All Phases of ML-KEM and ML-DSA

This repository contains our experimental code and auxiliary attack programs, divided into five folders:

1. **Fault Injection Harness**: This folder contains the code we use to drive the experimental environment, implementing highly automated fault experiment data collection. It drives devices such as DUT, ChipSHOUTER, and ChipWhisperer in the experimental environment.
2. **Target Code** **Example**: This folder contains the example of the experimental code on the Cortex-M33 dual core NXP LPC55S69JBD100. It implements a loop code with a GPIO trigger that can be controlled via UART by a PC. 
4. **ML-KEM/ML-DSA fault simulator and solver**: Based on an ML-KEM implementation that passed the NIST test vectors, and simulated the fault attacks proposed in the article. More importantly, they provide solving tools for recovering secret information through faulty outputs, achieving key recovery, signature forgery, and verification bypass. The AttackSimulatorSolver file can be run directly.
6. **pico_code**: This part of the code is our side-channel acquisition program, which calls the interface of the Pico 3000 series.

