/* or1k-nop.h -- Defines codes OR1K simulator NOP Hack 

   Copyright (C) 1999 Damjan Lampret, lampret@opencores.org
   Copyright (C) 2008 Embecosm Limited
  
   Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>
   Contributor Peter Gavin <pgavin@gmail.com>
  
   This program is free software; you can redistribute it and/or modify it
   under the terms of the GNU General Public License as published by the Free
   Software Foundation; either version 3 of the License, or (at your option)
   any later version.
  
   This program is distributed in the hope that it will be useful, but WITHOUT
   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
   more details.
  
   You should have received a copy of the GNU General Public License along
   with this program.  If not, see <http://www.gnu.org/licenses/>. */

#ifndef OR1K_NOP__H
#define OR1K_NOP__H

/*
 * l.nop constants used only in simulations
 */
#define OR1K_NOP_NOP         0x0000  /* Normal nop instruction */
#define OR1K_NOP_EXIT        0x0001  /* End of simulation */
#define OR1K_NOP_REPORT      0x0002  /* Simple report */
#define OR1K_NOP_PUTC        0x0004  /* putc instruction */
#define OR1K_NOP_CNT_RESET   0x0005  /* Reset statistics counters */
#define OR1K_NOP_GET_TICKS   0x0006  /* Get # ticks running */
#define OR1K_NOP_GET_PS      0x0007  /* Get picosecs/cycle */
#define OR1K_NOP_TRACE_ON    0x0008  /* Turn on tracing */
#define OR1K_NOP_TRACE_OFF   0x0009  /* Turn off tracing */
#define OR1K_NOP_RANDOM      0x000a  /* Return 4 random bytes */
#define OR1K_NOP_OR1KSIM     0x000b  /* Return non-zero if this is Or1ksim */
#define OR1K_NOP_EXIT_SILENT 0x000c  /* End of simulation, quiet version */

#endif  /* OR1K_NOP__H */
