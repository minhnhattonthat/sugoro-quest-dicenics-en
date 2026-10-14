-- Each frame, log the bytes at WRAM ADDR..ADDR+LEN-1 when they change.  --var ADDR=0x7E0019 --var LEN=2
local last
L.on_frame(function(n)
  local t = {}
  for i = 0, (LEN or 1) - 1 do t[#t + 1] = string.format("%02X", emu.read(ADDR + i, emu.memType.snesMemory)) end
  local s = table.concat(t, " ")
  if s ~= last then L.log(string.format("f%d %s", n, s)); last = s end
end)
