-- copy a battery save file into SRAM on frame 1 (savestates carry their own SRAM)
L.on_frame(L.safe(function(n)
  if n == 1 then
    local f = io.open(SRM, "rb"); local d = f:read("*a"); f:close()
    for i = 1, #d do emu.write(i - 1, d:byte(i), emu.memType.snesSaveRam) end
    L.log("srm loaded " .. #d)
  end
end))
