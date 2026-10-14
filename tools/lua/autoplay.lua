-- Autoplay for coverage: every STEP frames (default 20) press the next button of a cycle for 6 frames.
--   emu.py ROM --state-in S --frames N --script tools/lua/autoplay.lua [--var STEP=20]
local cycle = { "a", "start", "a", "right", "a", "b", "a", "down", "a", "start", "a", "left", "a", "b", "a", "up" }
local step, i = STEP or 20, 0
emu.addEventCallback(function()
  if L.route_done() and L.frame % step < 6 then
    emu.setInput({ [cycle[(L.frame // step) % #cycle + 1]] = true }, 0)
  end
end, emu.eventType.inputPolled)
