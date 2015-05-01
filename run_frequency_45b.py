from run_frequency import env,stimulus,phases
import experiment

env['groups'] = ['Day1','F_50ms','fs30Pd_50ms','fs_50ms','FD_50ms','fs24Pd_50ms']
env['num_trials'] = 45
env['default_blocks'] = 1
experiment.start(env,stimulus,phases)
