# spark-helix -- spark inside helix

spark (https://spark.forgewright.ai) is your own AI on your own machine;
this plugin puts it under one key in helix. Helix ships no plugin runtime
yet, so the plugin is a keys block: A-s opens a little spark menu, and
where words are needed helix's own command line is left open, pre-filled
-- type them, press Enter.

    A-s r words        rewrite the whole file
    A-s s words        rewrite the selection (--part rides along)
    A-s a words        ask about the selection: the answer lands after
                       it in the buffer -- read it, then u removes it
    A-s f              fix spelling and punctuation, one keystroke

Nothing runs until you press Enter: a proposal you asked for, never a
surprise. A macro cannot hook the cursor, so there is no completion here
-- micro's, neovim's and vim's plugins have it.

## Install

You need spark 1.7 or newer on this machine (`spark edit -h` answers), and
helix 23.03 or newer (`hx --version`; Arch names the binary `helix`).
Then:

```sh
git clone https://github.com/forgewright-ai/spark-helix ~/.config/helix/spark
```

and paste the two `[keys...]` blocks from `spark.toml` into your
`config.toml` (`:config-open`, paste, `:config-reload`). Helix has no
include, so one line became one small block; the comment block above the
keys is the help. An update is `git -C ~/.config/helix/spark pull`, then
re-paste what changed. A-s is the suggestion -- name the table any key
you like.

On Ubuntu, helix is not in the archives: the maintained PPA
(`sudo add-apt-repository ppa:maveonair/helix-editor`) or
`sudo snap install helix --classic` gets it.

## What leaves this machine

The piped text -- at most 12 kB for a rewrite, 16 kB for a question --
and only to the brain spark is configured for. Helix's pipe carries no
file name, so not even that travels. Every run is one call to `spark
edit` with the text on stdin; the plugin never speaks HTTP and never
sees a token.

## Contributing

`git config core.hooksPath .githooks` once; the hook keeps the tree free
of private names, ASCII, and the payload parseable TOML. `python3
tests/helix_pty.py` drives a real helix in a pty against a stub spark,
with the repo's `spark.toml` as the very config it runs (skips without
helix). Another editor joins spark the same way this one does: one client
of `spark edit`, in its own repo.

MIT. Credits in `CREDITS.md`. Built with Claude.
