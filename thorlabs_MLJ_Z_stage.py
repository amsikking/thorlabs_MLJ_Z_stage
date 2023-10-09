import thorlabs_MLJ050 # github.com/amsikking/thorlabs_MLJ050
import thorlabs_MLJ150 # github.com/amsikking/thorlabs_MLJ150

class ZStage:
    def __init__(self,
                 which_ports,           # tuple of 2 ports i.e. ('COM1', 'COM2')
                 name='Z_stage',    
                 limits_mm=(0, 50),     # reduce if necessary e.g. (0, 10)
                 velocity_mmps=1,       # adjust as needed
                 acceleration_mmpss=2,  # adjust as needed
                 verbose=True,
                 very_verbose=False):
        self.name = name
        self.verbose = verbose
        self.very_verbose = very_verbose
        if self.verbose:
            print("%s: opening..."%self.name)
        self.stage1 = thorlabs_MLJ050.Controller(
            which_port=which_ports[0],
            limits_mm=limits_mm,
            velocity_mmps=velocity_mmps,
            acceleration_mmpss=acceleration_mmpss,            
            home=False,
            verbose=very_verbose)
        self.stage2 = thorlabs_MLJ150.Controller(
            which_port=which_ports[1],
            limits_mm=limits_mm,
            velocity_mmps=velocity_mmps,
            acceleration_mmpss=acceleration_mmpss, 
            home=False,
            verbose=very_verbose)
        if not self.stage1._homed or not self.stage2._homed: # then home both
            self.stage1._home(block=False)
            self.stage2._home(block=False)
            self.stage1._finish_home()
            self.stage2._finish_home()
        self.equalize()
        if self.verbose:
            print("%s: done opening."%self.name)

    def set_velocity_mmps(self, velocity_mmps):
        if self.verbose:
            print('%s: setting velocity_mmps = %0.3f'%(
                self.name, velocity_mmps))
        self.stage1.set_velocity_mmps(velocity_mmps)
        self.stage2.set_velocity_mmps(velocity_mmps)
        if self.verbose:
            print('%s: -> finished setting velocity.'%self.name)
        return None

    def move_mm(self, move_mm, relative, block=True):
        if self.verbose:
            print('%s: move_mm = %0.2f (relative=%s)'%(
                self.name, move_mm, relative))
        self.stage1.move_mm(move_mm, relative=relative, block=False)
        self.stage2.move_mm(move_mm, relative=relative, block=False)
        if block:
            self.stage1._finish_move()
            self.stage2._finish_move()
        if self.verbose:
            print('%s: -> finished move.'%self.name)
        return None

    def stop(self, mode='abrupt'):
        if self.verbose:
            print('%s: stopping (mode=%s)'%(self.name, mode))
        self.stage1.stop(mode)
        self.stage2.stop(mode)
        if self.verbose:
            print('%s: -> stopped.'%self.name)
        return None

    def equalize(self):
        if self.verbose:
            print('%s: equalizing'%(self.name))
        if self.stage1.position_mm < self.stage2.position_mm:
            self.stage1.move_mm( # stages move faster in +ve direction
                self.stage2.position_mm, relative=False, block=True)
        if self.stage1.position_mm > self.stage2.position_mm:
            self.stage2.move_mm( # stages move faster in +ve direction
                self.stage1.position_mm, relative=False, block=True)
        if self.verbose:
            print('%s: -> done.'%self.name)
        return None

    def close(self):
        if self.verbose: print("%s: closing..."%self.name)
        self.equalize()
        self.stage1.close()
        self.stage2.close()
        if self.verbose: print("%s: closed."%self.name)
        return None

if __name__ == '__main__':
    z_stage = ZStage(which_ports=('COM7','COM9'),
                     limits_mm=(0, 50),
                     verbose=True,
                     very_verbose=False)

    print('\n# Some random absolute moves:')
    import random
    for moves in range(3): # tested to 100 moves with 0-50mm range
        print('\n Random test #%i'%moves)
        random_move_mm = random.uniform(0, 5)
        z_stage.move_mm(random_move_mm, relative=False)

    print('\n# Move and stop:')
    z_stage.move_mm(1, relative=False, block=False)
    z_stage.stop()
    z_stage.move_mm(1, relative=False, block=False)
    z_stage.stop(mode='profiled')

    z_stage.move_mm(0, relative=False)
    z_stage.close()
