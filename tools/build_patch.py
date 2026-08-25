#!/usr/bin/env python3
"""
build_patch.py – rebuild the "No Offline Warning" patches from ORIGINAL legacy
.AST files exported from MMC Editor (Legacy Explorer -> Export).

    python build_patch.py <original.AST> <patched.AST>

The script auto-detects which asset it was given by searching the decompressed
"Apt Data" bytecode for one of the known byte patterns below, applies the
single-byte change, recompresses with zlib level 9 (matches EA's compressor)
and writes a new archive with the ORIGINAL header/TOC/layout untouched.
It refuses to write anything if the patch site isn't found unambiguously or the
recompressed entry no longer fits the original slot.

Patches
  v1.0  common/ui/node_cfm/hub/corenode.ast
        art_control.button.DynastyPlayButton press handler: the second operand
        of the offline check (`!IsPopupShowing(EXIT_POPUP) == true`) is turned
        into `== false`, so the "Proceed Without Rewards" popup is skipped and
        the normal start-game path runs.                       0x73 -> 0x74
  v1.1  common/ui/node_com/scriptpod.ast
        madden.online.module.Login._ShowLoginFailedPopup: the gate
        `if (mShowLoginFailedPopup == true)` becomes
        `if (true < mShowLoginFailedPopup)` which is never true, so the
        "ACCOUNT ERROR" login-failure popup (the one MMC fills with
        "Mods require being offline...") is never opened. The failure callback
        that runs before the gate is untouched, so login flows still complete.
                                                                0x49 -> 0x48
"""
import struct, sys, zlib

PATCHES = [
    dict(
        name="v1.0 offline-warning gate (node_cfm/hub/corenode.ast)",
        pattern=bytes.fromhex("49124cb8000000100000001773b901af225ab901af86a2eb524912b8"),
        index=12, old=0x73, new=0x74, known_offset=145501,
    ),
    dict(
        name="v1.1 login-failed popup gate (node_com/scriptpod.ast)",
        # ... 5a b9 01 b2 e6 | 73 b9 01 af 48 [49] b8 00 00 7a 00 00 00 b9 01 af 20 ...
        pattern=bytes.fromhex("5ab901b2e673b901af4849b800007a000000b901af20"),
        index=10, old=0x49, new=0x48, known_offset=1051956,
    ),
]


def toc_entries(d):
    assert d[:8] == b"BGFA1.05", "not a BGFA1.05 archive"
    toc_off = struct.unpack_from("<i", d, 16)[0]
    toc_len = struct.unpack_from("<i", d, 24)[0]
    lens = [d[33 + i] for i in range(5)]          # unknown, id, start, size, extra
    shift, add, desc = d[38], d[40] * 4, d[44]
    entry_len = sum(lens) + desc + 1
    i, out = toc_off + add, []
    while i + entry_len <= toc_off + toc_len + add:
        e = d[i + 1:i + entry_len]
        p = lens[0]
        eid = e[p:p + lens[1]]; p += lens[1]
        start = int.from_bytes(e[p:p + lens[2]], "little") << shift; p += lens[2]
        size = int.from_bytes(e[p:p + lens[3]], "little")
        out.append((eid.hex(), start, size))
        i += entry_len
    return out


def find_site(data):
    """Return (patch, offset) for the single patch whose pattern matches."""
    found = []
    for pt in PATCHES:
        hits = []
        k = data.find(pt["pattern"])
        while k != -1:
            hits.append(k + pt["index"])
            k = data.find(pt["pattern"], k + 1)
        if len(hits) == 1:
            found.append((pt, hits[0], "pattern"))
        elif len(hits) > 1:
            sys.exit(f"{pt['name']}: pattern is ambiguous (hits={hits})")
    if len(found) == 1:
        return found[0]
    if len(found) > 1:
        sys.exit("more than one patch pattern matched this file; refusing")
    # fallback: known offsets (only if the byte there is the expected original)
    for pt in PATCHES:
        ko = pt["known_offset"]
        if len(data) > ko and data[ko] == pt["old"]:
            return pt, ko, "known offset"
        if len(data) > ko and data[ko] == pt["new"] and \
                data.find(pt["pattern"][:pt["index"]]) == ko - pt["index"]:
            sys.exit(f"{pt['name']}: this file is already patched")
    sys.exit("could not locate any patch site in this file (is this an original export of a supported asset?)")


def main(src, dst):
    d = open(src, "rb").read()
    apt = None
    for eid, start, size in toc_entries(d):
        raw = d[start:start + size]
        try:
            dec = zlib.decompress(raw)
        except zlib.error:
            continue
        if dec.startswith(b"Apt Data"):
            apt = (eid, start, size, dec)
    if apt is None:
        sys.exit("no 'Apt Data' entry found")
    eid, start, size, data = apt
    print(f"Apt Data entry {eid}: archive offset {start}, compressed {size}, decompressed {len(data)}")

    pt, off, how = find_site(data)
    print(f"{pt['name']}: site found by {how} at offset {off}")
    if data[off] == pt["new"]:
        sys.exit("already patched")
    assert data[off] == pt["old"], f"unexpected byte 0x{data[off]:02x} at {off}"
    patched = bytearray(data); patched[off] = pt["new"]

    comp = zlib.compressobj(9, zlib.DEFLATED, 15, 8, zlib.Z_DEFAULT_STRATEGY)
    s = comp.compress(bytes(patched)) + comp.flush()
    print(f"zlib-9 recompressed size {len(s)} (slot {size})")
    if len(s) > size:
        # EA's own stream was zlib-9 and fits by construction, but one changed byte can
        # push our stream over by a few bytes. zopfli produces a smaller but still
        # standard zlib stream, so the loader can't tell the difference.
        try:
            import zopfli.zlib
        except ImportError:
            sys.exit(f"recompressed entry ({len(s)}) larger than original slot ({size}); "
                     f"install zopfli (pip install zopfli) so the entry can be shrunk to fit")
        s = zopfli.zlib.compress(bytes(patched), numiterations=15)
        print(f"zopfli recompressed size {len(s)}")
        if len(s) > size:
            sys.exit(f"zopfli output ({len(s)}) still larger than slot ({size}); layout would need rewriting")
    s = s + b"\0" * (size - len(s))          # zero-pad if smaller (inflate stops at end-of-stream)
    new = d[:start] + s + d[start + size:]
    assert len(new) == len(d)

    # verify round trip
    chk = zlib.decompress(new[start:start + size])
    diffs = [i for i in range(len(data)) if data[i] != chk[i]]
    assert diffs == [off], diffs
    open(dst, "wb").write(new)
    print(f"wrote {dst}: exactly one byte changed (offset {off}: 0x{pt['old']:02x} -> 0x{pt['new']:02x}); header/TOC unchanged")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
