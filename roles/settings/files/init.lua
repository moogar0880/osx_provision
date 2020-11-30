local window_management = require('window_management')

local anycomplete = require('anycomplete')
hs.hotkey.bind({"cmd", "shift"}, "A", anycomplete.anycomplete)
