-- Log nonzero joypad auto-read values ($4218/$4219) to check scripted input reaches the game.
L.on_read(0x4218, 0x4219, L.safe(function(addr, value)
  if value ~= 0 then L.log(string.format("f%d %04X=%02X", L.frame, addr & 0xFFFF, value)) end
end))
