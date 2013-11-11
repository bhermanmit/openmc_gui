#!/bin/sh env gnuplot

set terminal png enhanced
set output "tmpdir/minicore_outputs/nfiss.png"
set palette defined (0 '#ffffff', 0.000001 '#000090',                      1 '#000fff',                      2 '#0090ff',                      3 '#0fffee',                      4 '#90ff70',                      5 '#ffee00',                      6 '#ff7000',                      7 '#ee0000',                      8 '#7f0000')
set view map
set size ratio -1
set lmargin at screen 0.10
set rmargin at screen 0.90
set bmargin at screen 0.15
set tmargin at screen 0.90
unset xtics
unset ytics
unset key
splot 'tmpdir/minicore_outputs/nfiss.dat' matrix with image
