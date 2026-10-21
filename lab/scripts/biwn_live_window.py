"""Optional local preview window; it never changes guest RAM or CPU state."""
import time

KEYS = {'Up':4, 'Down':5, 'Left':6, 'Right':7,
        'z':8, 'x':0, 'c':1, 'space':3, 'Return':2,
        '0':9, '1':10, '2':11, '3':12, '4':13, '5':14, '6':15}
KEYBOARD_KEYS={'7':55,'8':56,'9':57,'minus':45,'equal':61,'asterisk':45,'numbersign':61}


def framebuffer_ppm(raw, width, height, pitch):
    """Convert the same little-endian XRGB8888 pixels as the saved PNGs."""
    assert width > 0 and height > 0 and pitch >= width*4
    assert len(raw) == pitch*height
    rgb = bytearray(width*height*3)
    for y in range(height):
        line = raw[y*pitch:y*pitch+width*4]
        start = y*width*3
        rgb[start:start+width*3:3] = line[2::4]
        rgb[start+1:start+width*3:3] = line[1::4]
        rgb[start+2:start+width*3:3] = line[0::4]
    return f'P6\n{width} {height}\n255\n'.encode()+rgb


class LiveWindow:
    def __init__(self):
        import tkinter as tk
        self.tk = tk
        self.root = tk.Tk()
        self.root.title('BIWN — Experimental Source Preview')
        self.pressed = set()
        self.keys_down = set()
        self.keyboard_pressed = set()
        self.keyboard_keys_down = {}
        self.input_events = 0
        self.closed = False
        self.paused = False
        self.audio_output = None
        self.audio_message = 'Audio initializing'
        self.pause_after_first_frame = True
        self.started = time.monotonic()
        self.status = tk.StringVar(value='Loading the recorded game checkpoint…')
        tk.Label(self.root, text='BIWN experimental reconstruction', font=('Helvetica',16,'bold')).pack(pady=(10,3))
        self.screen = tk.Label(self.root, background='black', width=80, height=24)
        self.screen.pack(padx=10, pady=6)
        tk.Label(self.root, text='Arrows: move / turn   Hold C + Up: run   Z: A   X: B   C: C\n'
                 'Digits 0–9: keypad; minus: *; equals: #\n'
                 '1 then tap X+C: Deck   2 then tap X+C: equip Beretta   Z: attack / read\n'
                 'In Deck: 4 opens mail   C goes back   0 exits   C exits the elevator menu').pack(padx=10)
        tk.Label(self.root, text='P: start / pause preview   M: mute   Space: Option   Enter: game pause   Esc: close').pack()
        controls = tk.Frame(self.root)
        controls.pack(pady=4)
        self.play_button = tk.Button(controls, text='Start / pause', command=self.toggle_pause)
        self.play_button.pack(side='left', padx=4)
        self.mute_button = tk.Button(controls, text='Mute', command=self.toggle_mute)
        self.mute_button.pack(side='left', padx=4)
        tk.Label(self.root, textvariable=self.status).pack(padx=10, pady=6)
        tk.Label(self.root, text='Starts from a recorded game checkpoint. Some areas may stop.\n'
                 'Experimental preview — sound may stutter when emulation runs slowly.',
                 foreground='#666666').pack(padx=10, pady=(0,10))
        self.root.bind('<KeyPress>', self.key_down)
        self.root.bind('<KeyRelease>', self.key_up)
        self.root.bind('<FocusOut>', self.focus_out)
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.update()
        self.root.focus_force()

    def key_down(self, event):
        self.input_events += 1
        key = event.keysym
        if key.startswith('KP_')and key[3:].isdigit():key=key[3:]
        repeated=key.lower() in self.keys_down
        self.keys_down.add(key.lower())
        if key == 'Escape':self.close()
        elif key.lower() == 'p' and not repeated:
            self.toggle_pause()
        elif key.lower() == 'm' and not repeated and self.audio_output:
            self.toggle_mute()
        elif key in KEYBOARD_KEYS:
            self.keyboard_keys_down[event.keycode]=KEYBOARD_KEYS[key]
            self.keyboard_pressed=set(self.keyboard_keys_down.values())
        elif key in KEYS:self.pressed.add(KEYS[key])
        elif key.lower() in KEYS:self.pressed.add(KEYS[key.lower()])

    def toggle_pause(self):
        self.paused = not self.paused
        self.pressed.clear()
        self.keyboard_pressed.clear()
        self.keyboard_keys_down.clear()
        if self.audio_output:self.audio_output.set_state(suspended=self.paused)

    def toggle_mute(self):
        if self.audio_output:
            self.audio_output.set_state(muted=not self.audio_output.muted)

    def focus_out(self, event):
        self.pressed.clear()
        self.keys_down.clear()
        self.keyboard_pressed.clear()
        self.keyboard_keys_down.clear()

    def key_up(self, event):
        self.input_events += 1
        key = event.keysym
        if key.startswith('KP_')and key[3:].isdigit():key=key[3:]
        self.keys_down.discard(key.lower())
        self.keyboard_keys_down.pop(event.keycode,None)
        self.keyboard_pressed=set(self.keyboard_keys_down.values())
        if key in KEYS:self.pressed.discard(KEYS[key])
        elif key.lower() in KEYS:self.pressed.discard(KEYS[key.lower()])

    def close(self):
        self.closed = True
        self.pressed.clear()
        self.keyboard_pressed.clear()
        self.keyboard_keys_down.clear()
        try:self.root.destroy()
        except self.tk.TclError:pass

    def poll(self, video, frame):
        if self.closed:return False
        if frame and self.pause_after_first_frame:
            self.paused = True
            self.pause_after_first_frame = False
        if video.get('raw'):
            ppm = framebuffer_ppm(video['raw'], video['width'], video['height'], video['pitch'])
            self.image = self.tk.PhotoImage(data=ppm, format='PPM').zoom(2)
            self.screen.configure(image=self.image, width=0, height=0)
        elapsed = max(time.monotonic()-self.started, 0.001)
        self.play_button.configure(text='Resume' if self.paused else 'Pause')
        self.mute_button.configure(text='Unmute' if self.audio_output and self.audio_output.muted else 'Mute',
                                   state='normal' if self.audio_output else 'disabled')
        self.status.set(('Preview paused' if self.paused else 'Running')+
                        f' • frame {frame:,} • average {frame/elapsed:.1f} emulated frames/sec • '+
                        ('Muted' if self.audio_output and self.audio_output.muted else self.audio_message))
        try:
            self.root.update_idletasks()
            self.root.update()
        except self.tk.TclError:
            self.closed = True
        return not self.closed
