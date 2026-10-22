-- Dump PPU (VRAM, CGRAM, OAM, registers) and a shot at frame AT.
--   emu.py ... --script tools/lua/ppudump.lua --var AT=300 --var 'OUTP="H:/abs/path/prefix"'
L.on_frame(L.safe(function(n) if n == AT then L.dump_ppu(OUTP) ; L.shot("at") end end))
