# Sony IMX477

From [How fast the shutter speed the HQ camera can achieve?](https://forums.raspberrypi.com/viewtopic.php?t=323983)

```quote
Exposure is generally set as a number of lines, and the time taken to read a line is dictated by the pixel rate.
The minimum for IMX477 is 20 lines. The pixel rate is 840MPix/s.
The line length varies dependent on mode - 0x5dc0 (24000) for the full 12MPix mode, and 0x31c4 (12740) for the other 2 modes. line_length / pixel_rate gives you the line duration - 28.57usec for 12MPix mode, and 15.16usecs for the other 2 modes. The minimum exposure time should therefore be 28.57*20 = 571usecs, or 15.16*20 = 303usec based on mode.
```

```quote
However, I am still confused by the "line length" you mentioned. What is it exactly? My current understanding is that the exposure time is measured by the unit of time that it takes to scan a line of pixels at the pixel rate (720M or 840M whatever). But how it can reach 24000 for a single line? It's not a physical line in the pixel array?
```

```quote
The magic of a FIFO.

The pixel array is likely to be running at the listed 840MPix/s and writing into a FIFO.
The CSI2 link configuration is insufficient to consume at that rate. The pixel array therefore has to be paced by making the line take far more clock cycles (at 840MPix/s) so as not to overflow the FIFO. The magic number for the number of clock cycles is that line length parameter.

The minimum of 20 lines should have come out of the datasheet.
```