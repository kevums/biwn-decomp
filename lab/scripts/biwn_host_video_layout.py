"""Headless equivalent of frontend host-buffer geometry refresh, at 1x."""
import ctypes as c


def install(runtime):
    core = runtime.core
    pitch = c.c_uint32.in_dll(core, 'screenPitch')
    width = c.c_uint32.in_dll(core, 'tomWidth')
    height = c.c_uint32.in_dll(core, 'tomHeight')
    frontend_width = c.c_int.in_dll(core, 'videoWidth')
    frontend_height = c.c_int.in_dll(core, 'videoHeight')
    core.JaguarSetScreenPitch.argtypes = [c.c_uint32]
    records = []

    def refresh():
        if not width.value or not height.value:
            return
        assert width.value <= 1024 and height.value <= 512
        if (pitch.value, frontend_width.value, frontend_height.value) == (width.value, width.value, height.value):
            return
        records.append(dict(before=[pitch.value, frontend_width.value, frontend_height.value],
                            after=[width.value, width.value, height.value]))
        # Host pitch and frontend bookkeeping only. No guest MMIO/RAM writes,
        # processor instructions, event scheduling or geometry fixture seed.
        core.JaguarSetScreenPitch(width.value)
        frontend_width.value, frontend_height.value = width.value, height.value

    runtime.refresh_host_video_layout = refresh
    runtime.host_video_layout_changes = records
