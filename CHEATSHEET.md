# helix with spark -- the cheatsheet

helix edits; spark writes with you. Section 1 is survival helix,
section 2 is the key menu that puts your own AI inside it.

The key spellings here are the editor's: `A-s` is Alt-s -- Option-s
on a Mac (spark's Terminal profile makes Option the Meta key), or Esc
and then s, quickly. Keys are case-sensitive.

## 1. helix, the basics

Modes (helix selects first, then acts)

    i              insert text at the cursor
    Esc            back to normal mode (where keys are commands)
    v              extend a selection as you move
    x              select the whole line (again for the next)

Files

    :w Enter       save         :q Enter    quit
    :wq Enter      save + quit  :q! Enter   quit, drop changes

Editing (normal mode)

    u              undo         U        redo
    y              copy the selection
    d              cut the selection
    p              paste after it

Moving and finding

    gg / ge        top / end of the file
    42G            go to line 42
    /words Enter   search -- then n next match, N previous
    :tutor         helix's own lessons

## 2. the text, with spark

One key opens a little spark menu: `A-s`, then one letter. Where
words are needed, helix's own command line opens pre-filled -- type
them, press Enter. Nothing runs until that Enter. Helix has no
plugin runtime yet, so there is no completion and no pane here; an
answer lands in the buffer after the selection, and `u` removes it
once read.

    A-s r words    rewrite the whole file as the words ask
    A-s s words    rewrite the selection (--part rides along)
    A-s a words    ask about the selection: the answer lands after
                   it -- read it, then u removes it
    A-s f          fix spelling and punctuation, one keystroke

By example

    A-s s shorter                   the selection, tighter
    A-s s translate to Portuguese   the selection, in Portuguese
    A-s a is the title too long     a question; u removes the answer
    A-s f                           the one-keystroke cleanup
    a summary?     A-s a summarize this -- the ASK key: the answer
                   lands after the selection, u removes it. On r/s
                   the words REPLACE the text (u undoes).

The comment block above the keys in `spark.toml` is the help; the
key is a suggestion -- name the table any key you like.
