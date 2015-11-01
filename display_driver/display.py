from myhdl import *

# Can't just change these and expect it to work :/
width = 64
height = 32
bitsPerColor = 8

# Input pins:
#  clk is 32MHz clock
# Output pins:
#  dclk is clock output to display
#  A, B, C, D select which pair of rows to write to
#  R1, B1, G1 are the RBG values for the top row selected
#  R2, B2, G2 are the RBG values for the bottom row selected
#  latch is the SPI latch (TODO: Document exactly what it does)
#  OE is output enable
## Input:
##  next_img is 2d array of 4-tuples of 8 bit Signal(intbv), that is what the
##  matrix should display once the current image is done being switched in
# Input:
#  next_img is a (width*height*4*bitsPerColor)-long intbv
#   It is a column-major matrix. Each number is LSB first. It goes RGB0, where
#   the last bitsPerColor bits are all 0's
#   So it might look like [ (row 0, column 0's red LSB), (row 0, column 0's
#    red's second bit), ..., (row 0, column 0's green LSB), 0,0,0,0,0,0,0,0,
#    ..., (row 0, column
#   1's red LSB), ..., (row 1 column 0's red LSB), ....]
# next_img actually goes 
def display(clk, rst, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE, img, imgoffset):
    bpc = bitsPerColor # Alias for shorter lines

    @always_comb
    def do_dclk():
        dclk.next = not clk

    # This goes up to 2^(bpc)-1
    # There are 2^(bpc) different shades, and one is "always off" and one is
    # "always on" so we need one fewer part in our counter
    pwm_ctr = Signal(intbv(0, min=0, max=2**bpc-1))

    which_row = Signal(intbv(val=0, min=0, max=height/2))
    which_col = Signal(intbv(val=0, min=0, max=width))
    next_row = Signal(intbv(val=0, min=0, max=height/2))
    next_col = Signal(intbv(val=0, min=0, max=width))
    next_colors = Signal(intbv(val=0)[3*bpc*2:])

    @always(clk.posedge, rst.negedge)
    def disp():
        # Output is always enabled
        OE.next = False

        if not rst:
            # Actually do the reset (it's active low)
            next_row.next = 1
            next_col.next = 1
            which_row.next = 0
            which_col.next = 0
            pwm_ctr.next = 0
            #next_colors.next = img[imgoffset + (0+1)*width + 0]
        else:

            R1.next = next_colors[1*bpc : 0*bpc] > pwm_ctr
            G1.next = next_colors[2*bpc : 1*bpc] > pwm_ctr
            B1.next = next_colors[3*bpc : 2*bpc] > pwm_ctr
            R2.next = next_colors[4*bpc : 3*bpc] > pwm_ctr
            G2.next = next_colors[5*bpc : 4*bpc] > pwm_ctr
            B2.next = next_colors[6*bpc : 5*bpc] > pwm_ctr

            #next_colors.next = img[imgoffset + (next_row+1)*width + next_col]
            next_colors.next = img[imgoffset + next_row*width + next_col]

            latch.next = which_col == width-1
            which_col.next = next_col
            which_row.next = next_row

            if next_col >= width-1:
                next_col.next = 0

                A.next = which_row[0]
                B.next = which_row[1]
                C.next = which_row[2]
                D.next = which_row[3]

                if next_row >= height/2-1:
                    next_row.next = 0
                    if pwm_ctr >= pwm_ctr.max - 1:
                        pwm_ctr.next = 0
                    else:
                        pwm_ctr.next = pwm_ctr + 1
                else:
                    next_row.next = next_row + 1
            else:
                next_col.next = next_col + 1

    return disp, do_dclk

def read_spi(mosi, sclk, spi_rst, rxdata, minor_size, major_size):
    minor_idx = Signal(intbv(val=0, min=0, max=minor_size))
    major_idx = Signal(intbv(val=0, min=0, max=major_size))

    buf = Signal(intbv(0)[minor_size-1:])
    @always(sclk.posedge, spi_rst.negedge)
    def RX():
        if not spi_rst:
            # Actually reset because they're active low
            minor_idx.next = 0
            major_idx.next = 0
        else:
            if minor_idx >= minor_size-1:
                rxdata[major_idx].next = concat(mosi, buf)
                major_idx.next = major_idx+1
                minor_idx.next = 0
            else:
                buf[minor_idx].next = mosi
                minor_idx.next = minor_idx+1
    return RX

def clk_driver(clk):
    halfPeriod = delay(1)

    @always(halfPeriod)
    def driveClk():
        clk.next = not clk

    return driveClk

def clockDivider(clk, slowclk, divRate = 0x400000):

    count = intbv(val=0, min=0, max=divRate)

    @always(clk.posedge)
    def divide():
        if count < count.max-1:
            count.next = count + 1
        else:
            slowclk.next = not slowclk
            count.next = 0

    return divide

def main(inclk, rst, mosi, sclk, spi_rst,
        dclka, Aa, Ba, Ca, Da, R1a, B1a, G1a, R2a, B2a, G2a, latcha, OEa,
        dclkb, Ab, Bb, Cb, Db, R1b, B1b, G1b, R2b, B2b, G2b, latchb, OEb):
    clk = Signal(bool(0))
    #divider = clockDivider(inclk, clk, 0x400000);
    
    img = [Signal(intbv(0)[2*bitsPerColor*3:]) for i in range(2*width*height/2)]

    cd = clockDivider(inclk, clk, 1)

    rs = read_spi(mosi, sclk, spi_rst, img, 2*bitsPerColor*3, 2*width*height/2)
    da = display(clk, rst, dclka, Aa, Ba, Ca, Da, R1a, B1a, G1a, R2a, B2a, G2a, latcha, OEa, img, 0)
    db = display(clk, rst, dclkb, Ab, Bb, Cb, Db, R1b, B1b, G1b, R2b, B2b, G2b, latchb, OEb, img, width*height/2)
    return rs, da, db, cd

clk = Signal(bool(0))
dclka = Signal(bool(0))
Aa  = Signal(bool(0))
Ba  = Signal(bool(0))
Ca  = Signal(bool(0))
Da  = Signal(bool(0))
R1a = Signal(bool(0))
B1a = Signal(bool(0))
G1a = Signal(bool(0))
R2a = Signal(bool(0))
B2a = Signal(bool(0))
G2a = Signal(bool(0))
latcha = Signal(bool(0))
OEa = Signal(bool(0))
dclkb = Signal(bool(0))
Ab  = Signal(bool(0))
Bb  = Signal(bool(0))
Cb  = Signal(bool(0))
Db  = Signal(bool(0))
R1b = Signal(bool(0))
B1b = Signal(bool(0))
G1b = Signal(bool(0))
R2b = Signal(bool(0))
B2b = Signal(bool(0))
G2b = Signal(bool(0))
latchb = Signal(bool(0))
OEb = Signal(bool(0))
mosi = Signal(bool(0))
sclk = Signal(bool(0))
spi_rst = ResetSignal(0, active=0, async=True)

rst = ResetSignal(0, active=0, async=True)

clk_driver_inst = clk_driver(clk)

main_inst = toVerilog(main, clk, rst, mosi, sclk, spi_rst,
        dclka, Aa, Ba, Ca, Da, R1a, B1a, G1a, R2a, B2a, G2a, latcha, OEa,
        dclkb, Ab, Bb, Cb, Db, R1b, B1b, G1b, R2b, B2b, G2b, latchb, OEb)

#sim = Simulation(main_inst, clk_driver_inst)
#sim.run(10000)

#main_inst = toVerilog(mymain, clk, led)
#main_inst = mymain(clk, led)
#clk_driver_inst = clk_driver(clk)
#sim = Simulation(main_inst, clk_driver_inst)
#sim.run(1000)
