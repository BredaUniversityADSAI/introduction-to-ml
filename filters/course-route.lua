-- The course route: Self-study and DataLab interleave, but the sidebar (and so
-- the Next link at the bottom of each page) lists all of Self-study first.
-- The route is defined once, in filters/course-route.yml. This filter
--   - replaces each `::: {.course-route}` div with the numbered list of steps
--     (`from="N"` starts the list at step N);
--   - adds a "Next: step N+1" callout at the end of the last page of each step.

local ROUTE_FILE = "filters/course-route.yml"
local ROUTE_PAGE = "start-here.qmd#the-course-route"

local function project_path()
  local input = quarto.doc.input_file
  local root = quarto.project.directory
  if not input or not root then
    return nil
  end
  local prefix = root:gsub("/$", "") .. "/"
  if input:sub(1, #prefix) ~= prefix then
    return nil
  end
  return input:sub(#prefix + 1)
end

local function read_steps()
  local root = quarto.project.directory:gsub("/$", "")
  local f = io.open(root .. "/" .. ROUTE_FILE, "r")
  if not f then
    error("course-route.lua: cannot read " .. ROUTE_FILE)
  end
  local text = f:read("a")
  f:close()
  local meta = pandoc.read("---\n" .. text .. "\n---\n", "markdown").meta
  local steps = {}
  for i, s in ipairs(meta.steps) do
    steps[i] = {
      title = s.title,
      href = pandoc.utils.stringify(s.href),
      ends = s.ends and pandoc.utils.stringify(s.ends) or nil,
      text = s.text,
      finish = s.finish,
    }
  end
  return steps
end

-- Links in the route file are relative to the project root: make them
-- relative to this page (one "../" per folder level). Quarto then turns
-- .qmd/.ipynb links into .html links as usual.
local function relativize(inlines, up)
  return pandoc.Inlines(inlines):walk({
    Link = function(link)
      if not link.target:match("^%a[%w+.-]*:") and not link.target:match("^#") then
        link.target = up .. link.target
      end
      return link
    end,
  })
end

local function step_link(step, up)
  return pandoc.Link(relativize(step.title, up), up .. step.href)
end

local function route_list(steps, from, up)
  local items = {}
  for i = from, #steps do
    local step = steps[i]
    local para = pandoc.Inlines({ step_link(step, up), pandoc.Str("."), pandoc.Space() })
    para:extend(relativize(step.text, up))
    table.insert(items, { pandoc.Para(para) })
  end
  return pandoc.OrderedList(items, pandoc.ListAttributes(from, "Decimal", "Period"))
end

local function next_callout(steps, i, up)
  local step, nxt = steps[i], steps[i + 1]
  local body = pandoc.Blocks({})
  if step.finish then
    body:insert(pandoc.Para(relativize(step.finish, up)))
  end
  local para = pandoc.Inlines({
    pandoc.Str("This is the end of step " .. i .. ". Continue with"), pandoc.Space(),
    step_link(nxt, up), pandoc.Str("."), pandoc.Space(),
  })
  para:extend(relativize(nxt.text, up))
  body:insert(pandoc.Para(para))
  body:insert(pandoc.Para({
    pandoc.Str("The Next link at the bottom of this page follows the menu instead. All steps are in"),
    pandoc.Space(), pandoc.Link(pandoc.Inlines({ pandoc.Str("the course route") }), up .. ROUTE_PAGE),
    pandoc.Str("."),
  }))
  return quarto.Callout({
    type = "note",
    title = "Next: step " .. (i + 1) .. " of " .. #steps,
    content = body,
  })
end

function Pandoc(doc)
  if not quarto.doc.is_format("html") then
    return doc
  end
  local path = project_path()
  if not path then
    return doc
  end
  local _, depth = path:gsub("/", "")
  local up = string.rep("../", depth)
  local steps = read_steps()

  doc.blocks = doc.blocks:walk({
    Div = function(div)
      if div.classes:includes("course-route") then
        return route_list(steps, tonumber(div.attributes.from) or 1, up)
      end
    end,
  })

  for i = 1, #steps - 1 do
    if steps[i].ends == path then
      doc.blocks[#doc.blocks + 1] = next_callout(steps, i, up)
    end
  end
  return doc
end
