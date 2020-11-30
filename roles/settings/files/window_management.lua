print('loding window_management')
--[[
    Bind the current window to the left half of the screen
--]]
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "Left", function()
  local win = hs.window.focusedWindow()
  local frame = win:frame()
  local screen = win:screen()
  local max = screen:frame()

  frame.x = max.x
  frame.y = max.y
  frame.w = max.w / 2
  frame.h = max.h
  win:setFrame(frame)
end)

--[[
    Bind the current window to the right half of the screen
--]] 
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "Right", function()
  local win = hs.window.focusedWindow()
  local frame = win:frame()
  local screen = win:screen()
  local max = screen:frame()

  frame.x = max.x + (max.w / 2)
  frame.y = max.y
  frame.w = max.w / 2
  frame.h = max.h
  win:setFrame(frame)
end)

--[[
    Bind the current window to the top half of the screen
--]]
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "Up", function()
  local win = hs.window.focusedWindow()
  local frame = win:frame()
  local screen = win:screen()
  local max = screen:frame()

  frame.x = max.x
  frame.y = max.y / 2
  frame.w = max.w
  frame.h = max.h / 2
  win:setFrame(frame)
end)

--[[
    Bind the current window to the bottom half of the screen
--]]
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "Down", function()
  local win = hs.window.focusedWindow()
  local frame = win:frame()
  local screen = win:screen()
  local max = screen:frame()

  frame.x = max.x
  frame.y = max.y + (max.h / 2)
  frame.w = max.w
  frame.h = max.h / 2
  win:setFrame(frame)
end)

--[[
    Expand the current window to fit the entire screen
--]]
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "M", function()
  local win = hs.window.focusedWindow()
  local frame = win:frame()
  local screen = win:screen()
  local max = screen:frame()

  frame.x = max.x
  frame.y = max.y
  frame.w = max.w
  frame.h = max.h
  win:setFrame(frame)
end)

--[[
    Expand the current window by several pixels in each direction
--]]
hs.hotkey.bind({"cmd", "alt", "ctrl"}, "=", function()
  local win = hs.window.focusedWindow()
  local frame = win:frame()
  local screen = win:screen()
  local max = screen:frame()

  if frame.x >= 10 and frame.x > 0 then
    -- increase the width by 10 pixels
    frame.x = frame.x - 10
  elseif frame.x < 10 and frame.x > 0 then
    -- increase to fit at edge of window
    frame.x = 0
  end

  if frame.w < max.w-10 and framw.w < max.w then
    -- increase the width by 10 pixels
    frame.w = frame.w + 10
  elseif frame.w > max.w-10 and frame.w < max.w then
    -- increase to fit at the edge of the window
    frame.w = max.w
  end
  win:setFrame(frame)
end)
