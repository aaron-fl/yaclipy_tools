import sys, time

if __name__ == '__main__':
    t = float(sys.argv[1])

    i = 0

    out = sys.stdout
    while True:
        c = sys.stdin.read(1)
        if not c: break
        try:
            c = int(c)
        except: pass
        if isinstance(c, int): sys.exit(c)
        if c == '!':
            out = sys.stderr
            continue
        if c == '$':
            out = sys.stdout
            continue
        if c == '~':
            out.close()
            continue
        out.write(f' {c!r} {ord(c)} {i}')
        if c == '.': out.write('\n')
        out.flush()
        i += 1
        time.sleep(t)

