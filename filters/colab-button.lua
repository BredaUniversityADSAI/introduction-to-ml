-- Adds an "Open in Colab" button to every page rendered from a Jupyter notebook.
-- The Colab URL is built from the notebook's path in the repository, so new
-- notebooks get a working button automatically.

local COLAB_BASE = "https://colab.research.google.com/github/BredaUniversityADSAI/introduction-to-ml/blob/main/"

local function repo_relative_path()
  local input = quarto.doc.input_file
  local root = quarto.project.directory
  if not input or not root or not input:match("%.ipynb$") then
    return nil
  end
  local prefix = root:gsub("/$", "") .. "/"
  if input:sub(1, #prefix) ~= prefix then
    return nil
  end
  return input:sub(#prefix + 1)
end

local function button_html(url)
  return [[
<p class="colab-launch">
  <a href="]] .. url .. [[" target="_blank" rel="noopener">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab">
  </a>
</p>
]]
end

function Pandoc(doc)
  if not quarto.doc.is_format("html") then
    return doc
  end
  local path = repo_relative_path()
  if not path then
    return doc
  end
  local button = pandoc.RawBlock("html", button_html(COLAB_BASE .. path))

  -- Place the button directly below the page title. Notebooks whose title is
  -- a leading "# Heading" keep that heading in the body, so go after it.
  local first = doc.blocks[1]
  if first and first.t == "Header" and first.level == 1 then
    doc.blocks:insert(2, button)
  else
    doc.blocks:insert(1, button)
  end
  return doc
end
