/*
 * Copyright 2016-2024 NXP
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

/**
 * @file    LPC55S69_Project1.c
 * @brief   Application entry point.
 */
#include <stdio.h>
#include "board.h"
#include "peripherals.h"
#include "pin_mux.h"
#include "clock_config.h"
#include "LPC55S69_cm33_core0.h"
#include "fsl_debug_console.h"
/* TODO: insert other include files here. */

/* TODO: insert other definitions and declarations here. */

/*
 * @brief   Application entry point.
 */
volatile uint32_t g_systickCounter;
void SysTick_Handler(void)
{
    if (g_systickCounter != 0U)
    {
        g_systickCounter--;
    }
}

void SysTick_DelayTicks(uint32_t n)
{
    g_systickCounter = n;
    while (g_systickCounter != 0U)
    {
    }
}


int main(void) {
    /* attach 12 MHz clock to FLEXCOMM0 (debug console) */
    CLOCK_AttachClk(BOARD_DEBUG_UART_CLK_ATTACH);
    /* enable clock for GPIO*/
    CLOCK_EnableClock(kCLOCK_Gpio0);
    CLOCK_EnableClock(kCLOCK_Gpio1);
    BOARD_InitBootClocks();
    /* Init board hardware. */
    BOARD_InitBootPins();
    BOARD_InitBootClocks();
    BOARD_InitBootPeripherals();
#ifndef BOARD_INIT_DEBUG_CONSOLE_PERIPHERAL
    /* Init FSL debug console. */
    BOARD_InitDebugConsole();
#endif

    if (SysTick_Config(SystemCoreClock / 1000U))
        {
            while (1)
            {
            }
        }
    gpio_pin_config_t gpio1_9_config = {
            .pinDirection = kGPIO_DigitalOutput,
            .outputLogic = 0U
        };
        /* Initialize GPIO functionality on pin PIO1_4 (pin 1)  */
    GPIO_PinInit(GPIO, 1, 9, &gpio1_9_config);
    gpio_pin_config_t gpio1_10_config = {
            .pinDirection = kGPIO_DigitalOutput,
            .outputLogic = 0U
        };
        /* Initialize GPIO functionality on pin PIO1_4 (pin 1)  */
    GPIO_PinInit(GPIO, 1, 10, &gpio1_10_config);



    GPIO_PinWrite(GPIO, 1, 9, 0);
    GPIO_PinWrite(GPIO, 1, 10, 0);
    PRINTF("Hello World\r\n");





    uint8_t output[64];
    uint8_t t[64];





    /* Force the counter to be placed into memory. */

    /* Enter an infinite loop, just incrementing a counter. */
    while(1) {
        uint8_t cmd;
        SCANF("%c", &cmd);
        //PRINTF("%u",cmd);
        for (size_t i0 = 0; i0 < 64; i0++) {
                output[i0] = i0;
          }

        for (size_t i1 = 0; i1 < 64; i1++) {
                t[i1] = i1+64;
          }
        //SysTick_DelayTicks(100U);
        GPIO_PinWrite(GPIO, 1, 9, 1);
        GPIO_PinWrite(GPIO, 1, 10, 1);
        for (size_t i=0; i < 64; i++) {
                output[i]=t[i];
          }
        GPIO_PinWrite(GPIO, 1, 10, 0);
        GPIO_PinWrite(GPIO, 1, 9, 0);
        //SysTick_DelayTicks(100U);
        for (size_t j=0; j < 64; j++) {
                PRINTF("%u ", output[j]);
          }


        /* 'Dummy' NOP to allow source level single stepping of
            tight while() loop */
        //__asm volatile ("nop");
    }
    return 0 ;
}
