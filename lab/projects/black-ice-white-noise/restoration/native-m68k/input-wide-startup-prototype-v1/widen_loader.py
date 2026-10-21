def widen_biwn_loader(original: bytes, copy_bytes: int) -> bytes:
    if type(original) is not bytes:
        raise ValueError("original must be bytes")
    if type(copy_bytes) is not int:
        raise ValueError("copy_bytes must be int")
    if len(original) != 40:
        raise ValueError("original must be 40 bytes")
    if copy_bytes < 4 or copy_bytes > 262144 or copy_bytes % 4 != 0:
        raise ValueError("copy_bytes out of range or not divisible by 4")
    template = bytes.fromhex("46fc27002e7c0020000048e7fffe41fa001843f90015edc0303c000032d851c8fffc4ef90015edd4")
    for i in range(40):
        if i in (26, 27):
            continue
        if original[i] != template[i]:
            raise ValueError("template mismatch")
    count = copy_bytes // 4 - 1
    out = bytearray(original)
    out[26] = (count >> 8) & 0xFF
    out[27] = count & 0xFF
    out[28] = 0x22
    out[29] = 0xD8
    return bytes(out)
