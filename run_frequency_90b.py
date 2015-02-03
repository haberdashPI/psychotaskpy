from run_frequency import env,stimulus,phases
import experiment

env['num_trials'] = 90
env['default_blocks'] = 1
experiment.start(env,stimulus,phases)
