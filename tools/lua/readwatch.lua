-- Log each distinct PC that reads CPU range LO..HI (and its $80 mirror), with registers.
--   emu.py ... --script tools/lua/readwatch.lua --var LO=0x09DD00 --var HI=0x09DE00
local seen = {}
local function hook(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if seen[pc] then return end
  seen[pc] = true
  L.log(string.format("f%d pc=%06X read %06X (off %06X)=%02X A=%04X X=%04X Y=%04X DB=%02X D=%04X", L.frame, pc, addr,
    L.rom_off(addr), value, s["cpu.a"], s["cpu.x"], s["cpu.y"], s["cpu.dbr"], s["cpu.d"]))
end
L.on_read(LO, HI, L.safe(hook))
if LO < 0x800000 then L.on_read(LO | 0x800000, HI | 0x800000, L.safe(hook)) end
