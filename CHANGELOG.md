# Changelog

## 1.0.0

- spark in helix, the second prompt-shaped plugin: helix ships no plugin
  runtime yet, so a keys block puts a spark menu under A-s -- r/s leave
  `:pipe spark edit ` open on helix's own command line (s adds --part
  for the selection), a asks with `:append-output` so the answer lands
  after the text and u removes it, f fixes spelling in one keystroke.
  A macro cannot hook the cursor, so there is no completion.
- The install is a clone and one paste into config.toml (helix has no
  include); the snippet's comment block is the help.
- The pty test (`tests/helix_pty.py`) drives a real helix with the
  repo's spark.toml as its very config, against a stub spark; CI runs
  it on Ubuntu (the PPA), Arch (`helix`) and macOS (`hx`).
