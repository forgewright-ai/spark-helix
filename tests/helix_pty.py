#!/usr/bin/env python3
# helix_pty.py -- the spark keys inside a real helix, in a pty, against a
# stub `spark` (on PATH: the snippet says `spark` plainly, and that is
# what must be proven) that logs what it was asked and answers a fixed
# word. Proves the whole loop the snippet promises: A-s r leaves
# `:pipe spark edit ` open on helix's own command line, the words reach
# spark with the selection on stdin and no path, the answer replaces the
# selection (or lands after it for an ask), Escape runs nothing. The test
# performs the README's paste: the repo's spark.toml IS the config.toml it
# runs helix with, so snippet and test cannot drift. Skips (exit 0)
# without helix (the binary is `hx` from brew and the PPA, `helix` on
# Arch).
#
#   python3 tests/helix_pty.py

import fcntl
import os
import re
import pty
import select
import shutil
import struct
import sys
import tempfile
import termios
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = REPO                                   # the repo root is the plugin
CSI = re.compile(r"\x1b(?:\[[0-9;?]*[ -/]*[@-~]|\([A-Za-z0-9]|\][^\x07\x1b]*(?:\x07|\x1b\\)|[@-Z\\-_])")

STUB = r'''#!/bin/sh
# the stub spark: log argv and stdin, answer one word
printf '%s\n' "$*" >> "$STUB_LOG"
cat > "$STUB_LOG.stdin"
case " $* " in
    *" ? "*)      printf 'STUB-ASK'; exit 0 ;;
    *" fail "*)   printf 'spark: no brain today -- spark serve\n' >&2; exit 1 ;;
esac
printf 'STUB-EDIT'
'''


class Editor:
    def __init__(self, argv, env, cwd, rows=30, cols=100):
        self.buf = b""
        self.pos = 0
        pid, fd = pty.fork()
        if pid == 0:
            os.chdir(cwd)
            os.execvpe(argv[0], argv, env)
        self.pid, self.fd = pid, fd
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))

    def read(self, timeout):
        end = time.time() + timeout
        while time.time() < end:
            r, _, _ = select.select([self.fd], [], [], 0.1)
            if r:
                try:
                    data = os.read(self.fd, 4096)
                except OSError:
                    return
                if not data:
                    return
                self.buf += data

    def plain(self):
        """what was drawn since mark(), with the escape sequences removed"""
        return CSI.sub("", self.buf[self.pos:].decode("utf-8", "replace"))

    def expect(self, text, timeout=10):
        end = time.time() + timeout
        while time.time() < end:
            if text in self.plain():
                return True
            self.read(0.2)
        return False

    def send(self, s):
        os.write(self.fd, s.encode())
        time.sleep(0.25)

    def mark(self):
        self.pos = len(self.buf)

    def close(self):
        try:
            os.close(self.fd)
        except OSError:
            pass
        try:
            os.waitpid(self.pid, 0)
        except OSError:
            pass


def main():
    hx = shutil.which("hx") or shutil.which("helix")
    if not hx:
        print("helix_pty: helix is not installed here -- skipped (brew install helix / pacman -S helix / the PPA)")
        return 0
    fail = 0

    def ok(cond, what, extra=""):
        nonlocal fail
        print("  %s %s%s" % ("ok  " if cond else "FAIL", what, ("   " + extra) if extra and not cond else ""))
        if not cond:
            fail += 1

    with tempfile.TemporaryDirectory(prefix="spark-helix-") as tmp:
        work, bindir, cfg = [os.path.join(tmp, d) for d in ("work", "bin", "cfg")]
        os.makedirs(work)
        os.makedirs(bindir)
        os.makedirs(os.path.join(cfg, "helix"))
        # the README's paste, performed: the repo's spark.toml IS the
        # config.toml helix runs with (the payload file is the fixture)
        shutil.copy(os.path.join(REPO, "spark.toml"),
                    os.path.join(cfg, "helix", "config.toml"))
        stub = os.path.join(bindir, "spark")
        with open(stub, "w") as f:
            f.write(STUB)
        os.chmod(stub, 0o755)
        log = os.path.join(tmp, "stub.log")
        note = os.path.join(work, "note.txt")
        with open(note, "w") as f:
            f.write("hello world\n")
        env = {"HOME": tmp, "XDG_CONFIG_HOME": cfg, "XDG_CACHE_HOME": os.path.join(tmp, "cache"),
               "TERM": "xterm-256color",
               "PATH": bindir + ":" + os.environ.get("PATH", "/usr/bin:/bin"),
               "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "STUB_LOG": log}
        argv = [hx, "note.txt"]

        def logged():
            try:
                with open(log) as f:
                    return f.read()
            except OSError:
                return ""

        def fresh(text="hello world\n"):
            if os.path.exists(log):
                os.unlink(log)
            with open(note, "w") as f:
                f.write(text)
            m = Editor(argv, env, work)
            # a cold helix (first run on a fresh runner) can take a while
            # to take the tty: keys sent before that echo back unseen
            ok(m.expect(text.splitlines()[0], 30), "helix draws the file", m.plain()[-300:])
            time.sleep(0.3)
            m.mark()
            return m

        # A. A-s r: the command line opens pre-filled with :pipe spark edit
        m = fresh()
        m.send("\x1bs")
        m.send("r")
        ok(m.expect("pipe spark edit"), "A-s r leaves :pipe spark edit open", m.plain()[-300:])
        m.send("shorter\r")
        ok(m.expect("STUB-EDIT"), "the words run the pipe: the answer replaces the file", m.plain()[-300:])
        m.send(":wq\r")
        m.read(1.0)
        m.close()
        with open(note) as f:
            saved = f.read()
        ok(saved in ("STUB-EDIT", "STUB-EDIT\n"), "the saved file is the answer, nothing doubled", repr(saved))
        got = logged()
        ok(got.strip() == "edit shorter", "spark edit got exactly the words -- no name, no path", got)
        ok(work not in got, "the file's path never reaches spark", got)
        with open(log + ".stdin") as f:
            stdin = f.read()
        ok(stdin == "hello world\n", "the whole file travelled on stdin", repr(stdin))

        # B. A-s s over a selection: --part rides along, the selection
        # alone travels and is replaced
        m = fresh()
        m.send("e")                 # select `hello`
        m.send("\x1bs")
        m.send("s")
        ok(m.expect("pipe spark edit --part"), "A-s s leaves :pipe spark edit --part open", m.plain()[-300:])
        m.send("shorter\r")
        ok(m.expect("STUB-EDIT"), "the selection is replaced", m.plain()[-300:])
        m.send(":wq\r")
        m.read(1.0)
        m.close()
        with open(note) as f:
            saved = f.read()
        ok(saved == "STUB-EDIT world\n", "only the selection became the answer", repr(saved))
        ok("edit --part shorter" in logged(), "a selection travels with --part", logged())
        with open(log + ".stdin") as f:
            ok(f.read() == "hello", "the selection alone travelled on stdin")

        # C. A-s a: an ask lands after the selection; u removes it
        m = fresh()
        m.send("%")                 # the whole file is the selection
        m.send("\x1bs")
        m.send("a")
        ok(m.expect("append-output spark edit ?"), "A-s a leaves :append-output spark edit ? open", m.plain()[-300:])
        m.send("why\r")
        ok(m.expect("STUB-ASK"), "the answer lands in the buffer, after the text", m.plain()[-300:])
        ok("edit ? why" in logged(), "the question reached spark edit as ? words", logged())
        m.send("u")                 # the answer goes; the text stays
        time.sleep(0.4)
        m.send(":wq\r")
        m.read(1.0)
        m.close()
        with open(note) as f:
            ok(f.read() == "hello world\n", "u removed the answer: the file is your text again")

        # D. A-s f: fix spelling and punctuation, one keystroke
        m = fresh()
        m.send("\x1bs")
        m.send("f")
        ok(m.expect("STUB-EDIT"), "A-s f runs in one keystroke", m.plain()[-300:])
        ok("edit fix spelling and punctuation" in logged(), "the one-shot words reached spark", logged())
        m.send(":q!\r")
        m.read(1.0)
        m.close()
        with open(note) as f:
            ok(f.read() == "hello world\n", "unsaved, the file on disk is untouched")

        # E. Escape at the pre-filled prompt cancels: nothing runs
        m = fresh()
        m.send("\x1bs")
        m.send("r")
        m.expect("pipe spark edit")
        m.send("\x1b")              # Escape: the command line closes
        time.sleep(0.4)
        ok(not os.path.exists(log), "a cancelled prompt runs nothing")
        m.send(":q!\r")
        m.read(1.0)
        m.close()

        # F. a failing spark leaves the text alone (helix keeps the
        # selection when the pipe dies)
        m = fresh()
        m.send("\x1bs")
        m.send("r")
        m.expect("pipe spark edit")
        m.send("fail\r")
        time.sleep(0.8)
        m.send(":q!\r")
        m.read(1.0)
        m.close()
        with open(note) as f:
            ok(f.read() == "hello world\n", "a failed pipe leaves the file untouched")

    print("helix_pty: %s" % ("all ok" if not fail else "%d FAILED" % fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
