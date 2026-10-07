# -*- coding: utf-8 -*-
"""Read an animated WebP's frame durations straight from its ANMF chunks (Pillow cannot read them
for some files). Usage: python webp_frames.py file.webp"""
import struct, sys
def durations(path):
    b = open(path, "rb").read()
    assert b[:4] == b"RIFF" and b[8:12] == b"WEBP"
    i, out, loop = 12, [], None
    while i + 8 <= len(b):
        cid, size = b[i:i+4], struct.unpack("<I", b[i+4:i+8])[0]
        p = b[i+8:i+8+size]
        if cid == b"ANIM": loop = struct.unpack("<H", p[4:6])[0]
        if cid == b"ANMF": out.append(p[12] | (p[13] << 8) | (p[14] << 16))
        i += 8 + size + (size & 1)
    return out, loop
if __name__ == "__main__":
    d, loop = durations(sys.argv[1]); print(len(d), "frames", sum(d), "ms, loop", loop, d[:16])
