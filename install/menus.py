"""Build a Settings wrapper around the user's own Lua bytecode; no original script is stored here."""
import hashlib


def build(original):
    if not original.startswith(b'\x1bLua'):
        raise ValueError('Settings input is not Lua bytecode')
    # Fixed-width decimal escapes preserve zero bytes and all Latin-1 values.
    blob = ''.join('\\%03d' % b for b in original)
    return WRAPPER.replace('@ORIGINAL@', blob).encode('ascii')


WRAPPER = r'''-- Port options layered over the original menu supplied by the user.
local config = MTG12
local chunk = assert(loadstring("@ORIGINAL@", "@original_settings"))
local base_env = getfenv(1)
local original_module = module
local menu
local langs = {"en", "es", "fr", "de", "it", "ja", "pt"}
local language_names = {"English", "Espa\241ol", "Fran\231ais", "Deutsch", "Italiano", "Nihongo", "Portugu\234s"}
local styles = {"xbox", "ps", "switch"}
local style_names = {"Xbox", "PlayStation", "Nintendo Switch"}
local function index(list, value)
  for i, v in ipairs(list) do if v == value then return i end end
  return 1
end
local function begin_module(name, ...)
  original_module(name, ...)
  menu = getfenv(1)
  setfenv(2, menu)
  local original_content = menu.content
  menu.content = function(spec)
    local items = assert(spec.items, "Settings content has no items")
    local positions = {[206]=-395, [301]=-395, [101]=-215, [202]=-215,
      [204]=-140, [205]=-65, [106]=255, [212]=255}
    local rows = {}
    for _, item in ipairs(items) do
      if item.id and positions[item.id] and type(item.y) == "number" then
        rows[item.y] = positions[item.id]
      end
    end
    for _, item in ipairs(items) do
      if item.id and positions[item.id] then item.y = positions[item.id]
      elseif rows[item.y] then item.y = rows[item.y] end
      if item.id == 106 then item.x = -185 end
      if item.id == 212 then item.x = 185 end
    end
    local function add(item) table.insert(items, item) end
    local function dropdown_row(label, id, y, text, values)
      add(menu.options_frm({y=y}))
      add(menu.options_lbl({id=label, y=y, text=text}))
      add(menu.dropdown({id=id, group=1001, x=300, y=y, w=300, h=100,
        options=values, fixed_order=true}))
    end
    dropdown_row(111, 221, 10, config.txt_idioma, language_names)
    dropdown_row(112, 222, 85, config.txt_botones, style_names)
    add(menu.options_frm({y=160}))
    add(menu.options_lbl({id=113, y=160, text=config.txt_dlc}))
    add(menu.options_lbl({id=114, x=300, y=160, text=config.dlc}))
    return original_content(spec)
  end
end
setfenv(chunk, setmetatable({module=begin_module}, {__index=base_env}))
chunk(...)
assert(menu, "Original Settings did not create a module")
local original_reset = assert(menu.reset, "Original Settings has no reset")
menu.reset = function(self, ...)
  original_reset(self, ...)
  self:send_item_message(221, menu.message.set_values, {value=index(langs, config.idioma)})
  self:send_item_message(222, menu.message.set_values, {value=index(styles, config.estilo)})
end
local function option(id, list, key)
  menu.on_event[id] = function(self, item, ev)
    if ev == menu.event.value_change then
      local value = list[item.selected_option]
      if value and value ~= config[key] then
        config[key] = value
        menu.game:playMovie("mtg12:" .. key .. "=" .. value)
      end
    end
  end
end
option(221, langs, "idioma")
option(222, styles, "estilo")
'''
