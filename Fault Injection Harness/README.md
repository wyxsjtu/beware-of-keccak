**This code drives the experimental environment.**
Our experimental environment includes a host PC, a NewAE ChipSHOUTER, a NewAE ChipWhisperer, and a DUT (Device Under Test).

![](\5101.png)

In this folder, the ***main.py*** file is the entry point, where you can set the number of fault injections, the UART port, the time delay range, and other fault injection experiment parameters. This program will automatically perform the experiments based on the parameters and output the results.

***cwlite.py*** controls the ChipWhisperer, and you can modify its parameters in this file.

***cshouter.py*** controls the ChipSHOUTER, where you can set the pulse intensity and other information.

***uart_ctrl.py*** is responsible for the UART communication with the target device, sending and receiving information through the serial port.

***utils.py*** contains other auxiliary functions.

