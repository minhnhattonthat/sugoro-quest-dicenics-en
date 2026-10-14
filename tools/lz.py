"""LZSS codec of the $00:BE77 decompressor (Okumura style): header u16 output size, then flag bytes (LSB first,
1 = literal) and 2-byte refs b1 b2: pos = b1 | (b2 & 0xF0) << 4, len = (b2 & 0x0F) + 3. Ring 4 KB, zero-filled, r = 0xFEE.
Source reads cross LoROM banks ($xx:FFFF -> next bank $8000), which in file offsets is contiguous.
    python -X utf8 tools/lz.py dec OFFSET OUT     |  python -X utf8 tools/lz.py selftest
"""
import sys
from pathlib import Path

N, F, R0 = 4096, 18, 0xFEE


def decompress(data, pos=0):
    """Returns (output bytes, compressed length incl. header)."""
    size = data[pos] | data[pos + 1] << 8
    p = pos + 2
    ring = bytearray(N)
    r = R0
    out = bytearray()
    flags = 0
    while len(out) < size:
        flags >>= 1
        if not flags & 0x100:
            flags = data[p] | 0xFF00
            p += 1
        if flags & 1:
            c = data[p]
            p += 1
            out.append(c)
            ring[r] = c
            r = (r + 1) & (N - 1)
        else:
            b1, b2 = data[p], data[p + 1]
            p += 2
            i = b1 | (b2 & 0xF0) << 4
            for k in range((b2 & 0x0F) + 3):
                c = ring[(i + k) & (N - 1)]
                out.append(c)
                ring[r] = c
                r = (r + 1) & (N - 1)
                if len(out) == size:
                    break
    return bytes(out), p - pos


def compress(src):
    """Greedy LZSS matching the decoder (ring starts zero-filled, so leading zero runs can match the pre-fill)."""
    ring = bytearray(N)
    r = R0
    out = bytearray([len(src) & 0xFF, len(src) >> 8])
    i = 0
    while i < len(src):
        flag_pos = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if i >= len(src):
                break
            best_len, best_pos = 0, 0
            maxlen = min(F, len(src) - i)
            # search the ring as the decoder would see it (positions written so far, plus zero pre-fill)
            for start in range(N):
                if start == r:
                    continue
                L = 0
                while L < maxlen:
                    q = (start + L) & (N - 1)
                    # bytes at or after r are written during this copy: emulate overlap
                    dist = (r - start) & (N - 1)
                    c = src[i + L - dist] if L >= dist else ring[q]
                    if c != src[i + L]:
                        break
                    L += 1
                if L > best_len:
                    best_len, best_pos = L, start
                    if L == maxlen:
                        break
            if best_len >= 3:
                out += bytes([best_pos & 0xFF, (best_pos >> 4) & 0xF0 | (best_len - 3)])
                n = best_len
            else:
                flags |= 1 << bit
                out.append(src[i])
                n = 1
            for k in range(n):
                ring[r] = src[i + k]
                r = (r + 1) & (N - 1)
            i += n
        out[flag_pos] = flags
    return bytes(out)


def main():
    if sys.argv[1] == "selftest":
        import random
        rnd = random.Random(1)
        for n in (0, 1, 5, 300, 2000):
            src = bytes(rnd.choice(b"\x00\x00\x00ABCD\xff") for _ in range(n))
            assert decompress(compress(src))[0] == src, n
        print("lz selftest ok")
    elif sys.argv[1] == "dec":
        rom = Path(Path(__file__).resolve().parent.parent / "rom/orig.sfc").read_bytes()
        data, used = decompress(rom, int(sys.argv[2], 16))
        Path(sys.argv[3]).write_bytes(data)
        print(f"{len(data):#x} bytes from {used:#x} compressed")


if __name__ == "__main__":
    main()
