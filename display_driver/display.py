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
def display(clk, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE, next_img):
    bpc = bitsPerColor # Alias for shorter lines

    @always_comb
    def do_dclk():
        dclk.next = not clk

    do_latch = Signal(bool(0))

    # This goes up to 2^(bpc)-1
    # There are 2^(bpc) different shades, and one is "always off" and one is
    # "always on" so we need one fewer part in our counter
    pwm_ctr = Signal(intbv(0, min=0, max=2**bpc-1))
    cur_img = Signal(intbv(0)[bpc*4*width*height:])

    which_row = Signal(intbv(val=0, min=0, max=height/2))
    which_col = Signal(intbv(val=0, min=0, max=width))

    @always(clk.posedge)
    def disp():
        r1idx = which_row             *width*4*bpc + which_col*4*bpc
        r2idx = (which_row + height/2)*width*4*bpc + which_col*4*bpc

        #print '{:6}: {:>3}, ({:>2}, {:>2}) => ({:d} {:d} {:d}), ({:d} {:d} {:d}) L: {:d} OE: {:d} ci[r1idx] = {:6x}'.format(
        #        now(),
        #        pwm_ctr,
        #        which_row, which_col,
        #        bool(R1), bool(G1), bool(B1), 
        #        bool(R2), bool(G2), bool(B2),
        #        bool(latch), bool(OE),
        #        int(cur_img[r1idx+24:r1idx]))

        R1.next = cur_img[r1idx + bpc : r1idx ] > pwm_ctr
        G1.next = cur_img[r1idx + 2*bpc : r1idx + bpc] > pwm_ctr
        B1.next = cur_img[r1idx + 3*bpc : r1idx + 2*bpc] > pwm_ctr
        R2.next = cur_img[r2idx + bpc : r2idx ] > pwm_ctr
        G2.next = cur_img[r2idx + 2*bpc : r2idx + bpc] > pwm_ctr
        B2.next = cur_img[r2idx + 3*bpc : r2idx + 2*bpc] > pwm_ctr

        A.next = which_row[3]
        B.next = which_row[2]
        C.next = which_row[1]
        D.next = which_row[0]

        do_latch.next = False

        if which_col == width-1:
            do_latch.next = True
            if which_row == height/2-1:
                cur_img.next = next_img
                which_row.next = 0

                if pwm_ctr == pwm_ctr.max - 1:
                    pwm_ctr.next = 0
                else:
                    pwm_ctr.next = pwm_ctr + 1
            else:
                which_row.next = which_row + 1
            which_col.next = 0
        else:
            which_col.next = which_col + 1


    @always(clk.negedge)
    def close_latch():
        latch.next = do_latch

    return disp, close_latch, do_dclk

def read_spi(mosi, sclk, rxdata, num_bits):
    @always(sclk.posedge)
    def RX():
        rxdata[num_bits:1].next = rxdata[num_bits-1:1]
        rxdata[0].next = mosi
    return RX

def clk_driver(clk, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE):
    halfPeriod = delay(1)

    @always(halfPeriod)
    def driveClk():
        clk.next = not clk
        print '{:6}: ({:d} {:d} {:d}), ({:d} {:d} {:d}) L: {:d} OE: {:d}'.format(
                now(),
                bool(R1), bool(G1), bool(B1), 
                bool(R2), bool(G2), bool(B2),
                bool(latch), bool(OE))


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

def main(inclk, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE, mosi, sclk):
    clk = Signal(bool(0))
    divider = clockDivider(inclk, clk, 0x400000);
    
    img = Signal(intbv()[bitsPerColor*4*width*height:])
    rs = read_spi(mosi, sclk, img, bitsPerColor*4*width*height)
    d = display(clk, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE, img)
    return rs, divider, d


#imgList = eval(open('../../exampleimage3').read())
#
#imgBld = intbv(0)[bitsPerColor*3*width*height:]
#for i in range(len(imgBld)):
#    imgBld[i] = imgList[i]
#next_img = Signal(imgBld)

clk = Signal(bool(0))
dclk = Signal(bool(0))
A = Signal(bool(0))
B = Signal(bool(0))
C = Signal(bool(0))
D = Signal(bool(0))
R1 = Signal(bool(0))
B1 = Signal(bool(0))
G1 = Signal(bool(0))
R2 = Signal(bool(0))
B2 = Signal(bool(0))
G2 = Signal(bool(0))
latch = Signal(bool(0))
OE = Signal(bool(0))
mosi = Signal(bool(0))
sclk = Signal(bool(0))

clk_driver_inst = clk_driver(clk, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE)

#display_inst = display(clk, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE, next_img)
#display_inst = toVerilog(display, clk, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE, next_img)
#display_inst = toVerilog(display, clk, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE)
main_inst = toVerilog(main, clk, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE, mosi, sclk)
#main_inst = main(clk, dclk, A, B, C, D, R1, B1, G1, R2, B2, G2, latch, OE, mosi, sclk)

#sim = Simulation(main_inst, clk_driver_inst)
#sim.run(10000)

#main_inst = toVerilog(mymain, clk, led)
#main_inst = mymain(clk, led)
#clk_driver_inst = clk_driver(clk)
#sim = Simulation(main_inst, clk_driver_inst)
#sim.run(1000)
