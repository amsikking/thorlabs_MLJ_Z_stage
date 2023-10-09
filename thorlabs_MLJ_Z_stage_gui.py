# Imports from the python standard library:
import tkinter as tk

# Our code, one .py file per module, copy files to your local directory:
import tkinter_compound_widgets as tkcw # github.com/amsikking/tkinter
import thorlabs_MLJ_Z_stage # github.com/amsikking/thorlabs_MLJ_Z_stage

class GuiZStage:
    def __init__(self,
                 which_ports,           # tuple of 2 ports i.e. ('COM1', 'COM2')
                 name='GuiZStage',
                 limits_mm=(0, 20),     # range (adjust as needed)
                 limits_mmps=(0.2, 1),  # velocity (adjust as needed)
                 limit_mmpss=2,         # acceleration (adjust as needed)
                 verbose=True,
                 very_verbose=False):
        if verbose:
            print('%s: initializing'%name)
        # init hardware:
        edge_limits_mm = (limits_mm[0] + 0.1, limits_mm[1] - 0.1)
        z_stage = thorlabs_MLJ_Z_stage.ZStage(
            which_ports=('COM7','COM9'),
            limits_mm=limits_mm,
            acceleration_mmpss=limit_mmpss,
            verbose=very_verbose)
        # init gui:
        root = tk.Tk()
        root.title('Z Stage GUI')
        frame = tk.LabelFrame(root, text='Z Stage', bd=6)
        frame.grid(row=0, rowspan=1, padx=20, pady=20)
        h, w, p = 3, 25, 10
        # get position command:
        def _get_position():
            self.z_mm = z_stage.stage1.get_position_mm()
            return None
        # stop command:
        def _stop():
            z_stage.stop(mode='abrupt')
            _get_position()
            if verbose:
                print('%s: stopped'%name)
            return None
        # up:
        def _move_up():
            _get_position()
            z_stage.move_mm(limits_mm[1], relative=False, block=False)
            if verbose:
                print('%s: moving up'%name)
            return None
        button_up = tk.Button(frame, text="MOVE UP", height=h, width=w)
        button_up.grid(row=0, padx=p, pady=p)
        button_up.bind("<ButtonPress>", lambda event: _move_up())
        button_up.bind("<ButtonRelease>", lambda event: _stop())
        # move fast:
        def _move_fast():
            if move_fast.get():
                z_stage.set_velocity_mmps(limits_mmps[1])
                if verbose:
                    print('%s: Move fast!'%name)
            else:
                z_stage.set_velocity_mmps(limits_mmps[0])
                if verbose:
                    print('%s: Move fast disabled!'%name)
            return None
        move_fast = tk.BooleanVar()
        move_fast_checkbox = tk.Checkbutton(
            frame,
            text='Move fast!',
            variable=move_fast,
            command=_move_fast)
        move_fast_checkbox.grid(row=1, padx=p, pady=p)
        # down:
        def _move_down():
            _get_position()
            z_stage.move_mm(limits_mm[0], relative=False, block=False)
            if verbose:
                print('%s: moving down'%name)
            return None        
        button_down = tk.Button(frame, text="MOVE DOWN", height=h, width=w)
        button_down.grid(row=2, padx=p, pady=p)
        button_down.bind("<ButtonPress>", lambda event: _move_down())
        button_down.bind("<ButtonRelease>", lambda event: _stop())
        # position:
        def _run_update_position():
            if edge_limits_mm[0] <= self.z_mm <= edge_limits_mm[1]:
                _get_position()
            position_textbox.textbox.delete('1.0', '10.0')
            position_textbox.textbox.insert('1.0', 'Z=%0.3f'%self.z_mm)
            wait_ms = 33
            root.after(wait_ms, _run_update_position)
            return None
        position_textbox = tkcw.Textbox(
            frame, label='position (mm)', height=1, width=20)
        position_textbox.grid(row=3, padx=p, pady=p)
        # equalize:
        def _equalize():
            z_stage.equalize()
            if verbose:
                print('%s: equalizing stages'%name)
            return None
        button_equalize = tk.Button(
            frame, text="EQUALIZE", command=_equalize, height=h, width=w)
        button_equalize.grid(row=4, padx=p, pady=p)
        # quit:
        def _quit():
            if verbose:
                print('%s: closing'%name)
            z_stage.close()
            root.quit()
            if verbose:
                print('%s: -> done.'%name)
            return None
        button_quit = tk.Button(
            root, text="QUIT", command=_quit, height=h, width=w)
        button_quit.grid(row=4, padx=p, pady=p)
        # sync gui and hardware:
        _move_fast()
        _get_position()
        _run_update_position()
        if verbose:
            print('%s: -> done.'%name)
            print('%s: current Z_mm   = %s'%(name, z_stage.stage1.position_mm))
        # run gui:
        root.mainloop()
        root.destroy()

if __name__ == '__main__':
    z_stage = GuiZStage(
        which_ports=('COM7','COM9'), verbose=True, very_verbose=False)

