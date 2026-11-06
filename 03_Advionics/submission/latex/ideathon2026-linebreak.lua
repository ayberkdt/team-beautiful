-- ideathon2026-linebreak.lua
-- First-fit ("greedy") line breaking, the way Microsoft Word breaks lines.
--
-- TeX normally chooses line breaks for the whole paragraph at once
-- (Knuth-Plass).  Word fills each line with as many words as fit at their
-- natural width and then stretches the spaces.  To get the same line breaks
-- as the Word template, this filter
--   1. walks the paragraph once and finds, line by line, the last legal
--      break that still fits at natural width (no shrinking, like Word);
--   2. forces those breaks (penalty -10000) and blocks every other break
--      (penalty 10000);
--   3. hands the list to TeX's normal line breaker, which then only builds
--      and justifies the lines.
-- Hyphenation by patterns is never used (Word's template has no automatic
-- hyphenation).  Breaks after an explicit hyphen "-" are allowed (Word does
-- the same).
--
-- Switch: \ideathongreedytrue / \ideathongreedyfalse (count register
-- \ideathon@greedy, 1 = on).

local ia = {}

local GLYPH   = node.id("glyph")
local GLUE    = node.id("glue")
local KERN    = node.id("kern")
local PENALTY = node.id("penalty")
local DISC    = node.id("disc")
local HLIST   = node.id("hlist")
local VLIST   = node.id("vlist")
local RULE    = node.id("rule")
local MATH    = node.id("math")

local dimensions = node.dimensions

local function width_of(n)
  -- natural width of a single node
  local id = n.id
  if id == GLUE then return n.width end
  if id == KERN then return n.kern end
  if id == PENALTY then return 0 end
  local w = dimensions(n, n.next)
  return w or 0
end

local function list_width(l)
  if not l then return 0 end
  return dimensions(l) or 0
end

local function discardable(n)
  local id = n.id
  return id == GLUE or id == KERN or id == PENALTY or id == MATH
end

-- available width of line number k (1-based) at natural size
local function make_avail()
  local hsize = tex.hsize
  local ls = tex.getglue("leftskip") or 0
  local rs = tex.getglue("rightskip") or 0
  local ps = tex.parshape
  local hi = tex.hangindent
  local ha = tex.hangafter
  local pslist = nil
  if type(ps) == "table" and #ps > 0 then pslist = ps end
  return function(k)
    local w = hsize
    if pslist then
      local e = pslist[math.min(k, #pslist)]
      w = e[2]
    elseif hi ~= 0 then
      local hanging
      if ha >= 0 then hanging = (k > ha) else hanging = (k <= -ha) end
      if hanging then w = hsize - math.abs(hi) end
    end
    return w - ls - rs
  end
end

local function force_break(head, n)
  if n.id == PENALTY then
    n.penalty = -10000
    return head
  end
  local p = node.new(PENALTY)
  p.penalty = -10000
  if n.id == DISC then
    head = node.insert_after(head, n, p)
  else
    head = node.insert_before(head, n, p)
  end
  return head
end

local function block_break(head, n)
  if n.id == PENALTY then
    if n.penalty > -10000 then n.penalty = 10000 end
    return head
  end
  if n.id == GLUE then
    local p = node.new(PENALTY)
    p.penalty = 10000
    head = node.insert_before(head, n, p)
  elseif n.id == DISC then
    -- disc nodes carry their own penalty (set from \exhyphenpenalty)
    n.penalty = 10000
  end
  return head
end

function ia.linebreak(head, is_display)
  if tex.count["ideathon@greedy"] ~= 1 then
    local h, info = tex.linebreak(head)
    if info then tex.prevdepth = info.prevdepth; tex.prevgraf = info.prevgraf end
    return h
  end
  ia.parno = (ia.parno or 0) + 1
  local avail = make_avail()
  if ia.debug then
    ia.debugfile = ia.debugfile or io.open(tex.jobname .. "-linebreak-debug.txt", "w")
    local sp = 65536 * 72.27 / 72
    ia.debugfile:write(string.format("PAR %d avail1=%.3f avail2=%.3f hsize=%.3f%s",
      ia.parno, avail(1) / sp, avail(2) / sp, tex.hsize / sp, string.char(10)))
    for nn in node.traverse(head) do
      local d = ""
      if nn.id == GLYPH then d = utf8.char(nn.char) end
      ia.debugfile:write(string.format("  %s %s w=%.3f %s%s", node.type(nn.id),
        tostring(nn.subtype), width_of(nn) / sp, d, string.char(10)))
    end
  end
  local exhyph = tex.exhyphenpenalty
  -- Word compresses spaces only in justified paragraphs; a paragraph is
  -- justified when neither the left skip nor the right skip can stretch
  local _, lst = tex.getglue("leftskip")
  local _, rst = tex.getglue("rightskip")
  local justified = ((lst or 0) == 0) and ((rst or 0) == 0)

  -- collect legal breakpoints with the natural width of the line material
  -- in front of them (bw) and the width at which the next line would start
  -- (aw) if we break there
  local bps = {}
  local w = 0
  local sh = 0     -- running sum of glue shrink (the spaces Word may compress)
  local prev = nil
  local inmath = false   -- glue and kerns inside a formula are no breakpoints
  local n = head
  while n do
    local id = n.id
    if id == MATH then
      inmath = (n.subtype == 0)
    end
    if id == GLUE then
      if prev and not discardable(prev) and not inmath then
        bps[#bps+1] = { node = n, bw = w, aw = w + n.width, bs = sh,
                        as = sh + n.shrink, kind = "glue" }
      end
    elseif id == PENALTY then
      if n.penalty < 10000 then
        bps[#bps+1] = { node = n, bw = w, aw = w, bs = sh, as = sh, kind = "pen",
                        forced = (n.penalty <= -10000) }
      end
    elseif id == DISC then
      -- subtype 2 = automatic (after an explicit "-"), 1 = \-, 0 = \discretionary
      -- 3 = regular (patterns): never (Word does not hyphenate)
      local st = n.subtype
      if (st == 1 or st == 2) and exhyph < 10000 then
        local wr = list_width(n.replace)
        bps[#bps+1] = { node = n, bw = w + list_width(n.pre),
                        aw = w + wr - list_width(n.post), bs = sh, as = sh,
                        kind = "disc" }
      end
    end
    w = w + width_of(n)
    if id == GLUE and n.shrink_order == 0 then sh = sh + n.shrink end
    prev = n
    n = n.next
  end
  -- the end of the paragraph acts as the final breakpoint; trailing glue
  -- (parfillskip etc.) is not part of the text width
  local tailw = w
  do
    local t = node.tail(head)
    while t and (t.id == GLUE or t.id == PENALTY) do
      tailw = tailw - width_of(t)
      t = t.prev
    end
  end
  local tails = sh
  do
    local t = node.tail(head)
    while t and (t.id == GLUE or t.id == PENALTY) do
      if t.id == GLUE and t.shrink_order == 0 then tails = tails - t.shrink end
      t = t.prev
    end
  end
  bps[#bps+1] = { node = nil, bw = tailw, aw = tailw, bs = tails, as = tails,
                  kind = "end", forced = true }

  -- first fit
  local chosen = {}
  local line = 1
  local start = 0
  local starts = 0
  local cand = nil
  local eps = 1   -- 1 sp tolerance
  local i = 1
  while i <= #bps do
    local b = bps[i]
    -- Word keeps a word on the line if
    --   (a) the line fits at natural width, or
    --   (b) it fits after the spaces are compressed by the allowed amount
    --       (glue shrink) AND the overflow is at most ia.half of the word
    --       (with its space in front).
    -- Rule fitted to 900 keep/wrap decisions measured in Word output
    -- (450 justified Montserrat 11 pt lines); it explains all of them.
    local over = (b.bw - start) - avail(line)
    local fits
    if over <= eps then
      fits = true
    else
      fits = justified and (over - (b.bs - starts) <= eps)
      if fits and cand then
        fits = over <= ia.half * (b.bw - cand.bw) + eps
      end
      if ia.debug and cand then
        local sp = 65536 * 72.27 / 72   -- sp per bp
        ia.debugfile = ia.debugfile or io.open(tex.jobname .. "-linebreak-debug.txt", "w")
        ia.debugfile:write(string.format(
          "IDEATHON-LB par %d line %d over=%.3fbp shrinkavail=%.3fbp word=%.3fbp ratio=%.4f half=%.3f fits=%s",
          ia.parno or 0, line, over / sp, (b.bs - starts) / sp, (b.bw - cand.bw) / sp,
          over / ((b.bs - starts) / ia.shrink), over / (b.bw - cand.bw), tostring(fits)) .. string.char(10))
      end
    end
    if fits then
      if b.forced then
        if b.node then chosen[b.node] = "forced" end
        line = line + 1
        start = b.aw; starts = b.as
        cand = nil
      else
        cand = b
      end
      i = i + 1
    else
      if cand then
        chosen[cand.node] = true
        line = line + 1
        start = cand.aw; starts = cand.as
        cand = nil
        -- re-test the same breakpoint on the new line (do not advance i)
      else
        -- a single word wider than the line: let it stick out, break here
        if b.node then chosen[b.node] = true end
        line = line + 1
        start = b.aw; starts = b.as
        i = i + 1
      end
    end
  end

  -- apply
  for _, b in ipairs(bps) do
    if b.node then
      if chosen[b.node] then
        head = force_break(head, b.node)
      else
        head = block_break(head, b.node)
      end
    end
  end
  local h, info = tex.linebreak(head, {
    pretolerance = -1, tolerance = 10000, emergencystretch = 0,
    hyphenpenalty = 10000, exhyphenpenalty = 10000, looseness = 0,
    linepenalty = 0, adjdemerits = 0, doublehyphendemerits = 0,
    finalhyphendemerits = 0,
  })
  -- the engine does not update \prevdepth / \prevgraf after a
  -- linebreak_filter; do it here (needed for the spacing model in the class)
  if info then tex.prevdepth = info.prevdepth; tex.prevgraf = info.prevgraf end
  return h
end

luatexbase.add_to_callback("linebreak_filter", ia.linebreak, "ideathon2026.greedy")

-- Interword space of every font loaded after this file: natural width as in
-- the font, shrink = ia.shrink x width (Word compresses spaces in justified
-- lines by up to about 25.6 %, measured on 450 Word lines), generous
-- stretch.  All spaces of a line get the same stretch/shrink, so TeX
-- spreads the difference evenly, as Word does.
ia.shrink = 0.2505
ia.half = 0.365
ia.debug = token.get_macro("ideathondebuglines") ~= nil
local user_half = token.get_macro("ideathonhalf")
if user_half and tonumber(user_half) then ia.half = tonumber(user_half) end
local user_shrink = token.get_macro("ideathonshrink")
if user_shrink and tonumber(user_shrink) then ia.shrink = tonumber(user_shrink) end
luatexbase.add_to_callback("luaotfload.patch_font", function(tfmdata)
  local p = tfmdata.parameters
  if p and p.space and p.space > 0 then
    p.space_stretch = p.space
    p.space_shrink = math.floor(p.space * ia.shrink + 0.5)
  end
end, "ideathon2026.wordspace")

-- Folder of ideathon2026.cls, relative to the current folder if possible
-- (used for fonts/ and images/).  The PDF backend cannot embed a file whose
-- absolute path contains a space, so an absolute path is avoided.
function ia.classroot()
  local p = kpse.find_file("ideathon2026.cls", "tex") or "./ideathon2026.cls"
  p = p:gsub(string.char(92), "/")
  local d = p:match("^(.*)/") or "."
  if not d:match("^%a:") and d:sub(1, 1) ~= "/" then
    return d .. "/"
  end
  local cwd = (lfs.currentdir() or ""):gsub(string.char(92), "/")
  local function split(x)
    local t = {}
    for part in x:gmatch("[^/]+") do
      if part == ".." and #t > 0 and t[#t] ~= ".." then t[#t] = nil
      elseif part ~= "." then t[#t + 1] = part end
    end
    return t
  end
  local a, b = split(d), split(cwd)
  if #a == 0 or #b == 0 or a[1]:lower() ~= b[1]:lower() then return d .. "/" end
  local i = 1
  while i <= #a and i <= #b and a[i]:lower() == b[i]:lower() do i = i + 1 end
  local rel = {}
  for _ = i, #b do rel[#rel + 1] = ".." end
  for k = i, #a do rel[#rel + 1] = a[k] end
  if #rel == 0 then return "./" end
  return table.concat(rel, "/") .. "/"
end

return ia
