-- warp: at frame AT set main mode $0112=MODE, substate $0114=SUB
L.on_frame(L.safe(function(n)
  if n == (AT or 30) then
    emu.write16(0x7E0112, MODE, emu.memType.snesMemory)
    emu.write16(0x7E0114, SUB or 0, emu.memType.snesMemory)
    L.log("warp mode " .. MODE)
  end
end))
