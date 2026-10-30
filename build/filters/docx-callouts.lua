-- Maps callout divs (::: definition, ::: warning, ...) to Word paragraph styles
-- named "Callout <Class>" so the reference document can colour them.
local callouts = {
  definition = "Callout Definition", concept = "Callout Concept", example = "Callout Example",
  formula = "Callout Formula", tip = "Callout Tip", recommendation = "Callout Recommendation",
  mistake = "Callout Mistake", warning = "Callout Warning", industry = "Callout Industry",
  note = "Callout Note", summary = "Callout Summary",
}
local labels = {
  definition = "DEFINITION", concept = "KEY CONCEPT", example = "WORKED EXAMPLE", formula = "FORMULA",
  tip = "INTERVIEW TIP", recommendation = "RECOMMENDATION", mistake = "COMMON MISTAKE",
  warning = "WARNING / TRADE-OFF", industry = "INDUSTRY EXAMPLE", note = "NOTE", summary = "SUMMARY",
}

function Div(el)
  for _, cls in ipairs(el.classes) do
    local style = callouts[cls]
    if style then
      local label = pandoc.Para({ pandoc.Strong({ pandoc.Str(labels[cls]) }) })
      table.insert(el.content, 1, label)
      el.attributes["custom-style"] = style
      return el
    end
  end
end

-- Raw HTML <details>/<summary> wrappers carry no meaning in Word; drop them.
function RawBlock(el)
  if el.format == "html" and (el.text:match("^%s*</?details") or el.text:match("^%s*<summary")) then
    local s = el.text:match("<summary>(.-)</summary>")
    if s then return pandoc.Para({ pandoc.Strong({ pandoc.Str(s) }) }) end
    return {}
  end
end
