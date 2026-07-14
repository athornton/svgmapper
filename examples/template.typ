#set page(
  "us-letter",
  margin: 1cm
)
#show title: set align(center)
#set document(
  title: [Dungeon, Level N: XXXXX],
)
#set text(
  font: "Helvetica Neue",
  weight: "light",
  size: 8pt,
)
#set par(
  leading: 0.3em
)
#set heading(numbering: "1.")
#title()
#grid(
  columns: (69%, 2%, 28%),
  grid.cell(
    image("./svg/template.svg", width: 100%),
  ),
  grid.cell([]),
  grid.cell(
    [
    *Wandering Monsters*
    + monsters...

    *Legend*
    + symbols...

    *Notes*
    + notes...
    ]
  )
)
*Room Key*
+ *Room Name*: Description.
