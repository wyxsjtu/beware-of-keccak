import chipwhisperer as cw
import time
def init_scope():
    scope=cw.scope()
    scope.default_setup()
    return scope
def init_scope_settings(scope):
    scope.io.glitch_lp = True
    scope.io.glitch_hp = False

    scope.clock.clkgen_src = 'system' 
    scope.clock.clkgen_freq = 200e6          # Main ChipWhisperer clock
    # scope.clock.adc_mul = 0
    scope.trigger.triggers = 'tio4'          # Trigger on a rising edge of TIO4 (connected to DIO6)
    scope.adc.basic_mode = 'rising_edge'     # Rising edge for trigger

    scope.glitch.clk_src = "clkgen" # set glitch input clock
    #scope.clock.pll.update_fpga_vco(600e6)
    scope.glitch.output = 'enable_only'
    scope.glitch.trigger_src = 'ext_single' # external single trigger
    scope.glitch.ext_offset = 300            # Glitch offset from the external trigger (in cycles of the main CW clock)
    scope.glitch.repeat = 100 # You might want to try different values for this parameter
    scope.io.nrst = 'high'

def test_manual_glitch(scope):
    scope.arm()
    scope.glitch.manual_trigger()

def reset_target(scope):
    scope.io.nrst = 'low'
    time.sleep(0.02)
    scope.io.nrst = 'high'
    time.sleep(0.02)

def get_ready():
    scope = init_scope()
    #init_scope_settings(scope)
    test_manual_glitch(scope=scope)
    #init_scope_settings(scope=scope)
    #test_manual_glitch(scope=scope)

if __name__ == "__main__":
    get_ready()