from run_frequency import env,stimulus,phases
import experiment

env['num_trials'] = 60
experiment.start(env,stimulus,phases)
