from datetime import date,timedelta
import expyriment as ex

from util import nth_file
from phase import phase

import datetime
import pandas as pd
import numpy as np
import time
import glob


@phase
def passive_static(env,is_start,write_line):
    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

    run(env,write_line)


@phase
def passive_today(env,is_start,write_line):
    sid = ('%04d' % env['exp'].subject)

    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

    # find the approrpiate data file from today
    tfile = nth_file(env['block'],env['data_file_dir'] + '/' + sid + '_' +
                     time.strftime("%Y_%m_%d_") + 'AFC' +
                     "_%02d.dat",wrap_around=True)

    print "Running passively from file: " + tfile
    run_track(env,pd.read_csv(tfile),write_line)

@phase
def passive_shuffled_today(env,is_start,write_line):
    sid = ('%04d' % env['exp'].subject)

    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

    # find the approrpiate data file from today
    tfile = nth_file(env['block'],env['data_file_dir'] + '/' + sid + '_' +
                     time.strftime("%Y_%m_%d_") + 'AFC' +
                     "_%02d.dat",wrap_around=True)

    print "Running passively from file: " + tfile
    run_track(env,pd.read_csv(tfile),write_line,shuffle=True)

@phase
def passive_shift_today(env,is_start,write_line):
    sid = ('%04d' % env['exp'].subject)

    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

    # find the approrpiate data file from today
    tfile = nth_file(env['block'],env['data_file_dir'] + '/' + sid + '_' +
                     time.strftime("%Y_%m_%d_") + 'AFC' +
                     "_%02d.dat",wrap_around=True)

    print "Running passively from file: " + tfile
    run_track(env,pd.read_csv(tfile),write_line,
              transform=env['passive_shift_transform_fn'])


@phase
def passive_zeroed_today(env,is_start,write_line):
    sid = ('%04d' % env['exp'].subject)

    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

    # find the approrpiate data file from today
    tfile = nth_file(env['block'],env['data_file_dir'] + '/' + sid + '_' +
                     time.strftime("%Y_%m_%d_") + 'AFC' +
                     "_%02d.dat",wrap_around=True)

    # set all deltas to 0
    track = pd.read_csv(tfile)
    track.delta = 0
    print "Running passively from file: " + tfile
    run_track(env,track,write_line)

@phase
def passive_yesterday(env,is_start,write_line):
    sid = ('%04d' % env['exp'].subject)
    yesterday = date.today() - timedelta(1)
    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

    # find the approrpiate data file from yesterday
    tfile = nth_file(env['block'],env['data_file_dir'] + '/' + sid + '_' +
                     yesterday.strftime("%Y_%m_%d_") + 'AFC' +
                     "_%02d.dat",wrap_around=True)

    print "Running passively from file: " + tfile
    run_track(env,pd.read_csv(tfile),write_line)


@phase
def passive_zeroed_yesterday(env,is_start,write_line):
    sid = ('%04d' % env['exp'].subject)
    yesterday = date.today() - timedelta(1)
    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

    # find the approrpiate data file from yesterday
    tfile = nth_file(env['block'],env['data_file_dir'] + '/' + sid + '_' +
                     yesterday.strftime("%Y_%m_%d_") + 'AFC' +
                     "_%02d.dat",wrap_around=True)

    track = pd.read_csv(tfile)  
    track.delta = 0
    print "Running passively from file: " + tfile
    run_track(env,track,write_line)

@phase
def passive_random(env,is_start,write_line):
    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

    choice = np.random.choice(env['passive_files'],size=1)[0]
    run_track(env,pd.read_csv(env['data_file_dir'] + '/' + choice),write_line)

@phase
def passive_first(env,is_start,write_line):
    sid = ('%04d' % env['exp'].subject)

    if is_start:
        ex.stimuli.TextLine('Press any key when you are ready.').present()
        env['exp'].keyboard.wait()

        print env['data_file_dir'] + '/' + sid + '_*AFC*.dat'
        tfiles = glob.glob(env['data_file_dir'] + '/' + sid + '_*AFC*.dat')
        print tfiles

    tfiles = glob.glob(env['data_file_dir'] + '/' + sid + '_*AFC*.dat')
    file = tfiles[env['block'] % len(tfiles)]
    print "Running passively from track in file: " + file
    run_track(env,pd.read_csv(file),write_line)


def run(env,write_line):
    env['exp'].screen.clear()
    env['exp'].screen.update()

    stim_1 = stim_2 = env['sound'](0)

    env['exp'].clock.wait(1000,env['exp'].keyboard.check)

    for trial in range(env['num_trials']):
        # provide an oportunity to exit/pause the program
        env['exp'].keyboard.check()
        env['exp'].screen.clear()
        env['exp'].screen.update()

        stim_1.play()
        env['exp'].clock.wait(env['SOA_ms'])
        stim_2.play()

        delay = env['response_delay_ms'] + env['passive_delay_ms']
        env['exp'].clock.wait(delay)

        write_line({'timestamp': datetime.datetime.now()},['timestamp'])

        env['exp'].clock.wait(env['feedback_delay_ms'])


def run_track(env,track,write_line,shuffle=False,transform=lambda x: x):
    if track.shape[0] < env['num_trials']:
        raise RuntimeException("Track does not have sufficeint trials")
    else:
        track = track.iloc[:env['num_trials'],:]
    if shuffle:
        order = np.random.choice(track.shape[0],size=track.shape[0],
                                 replace=False)
    else:
        order = np.arange(track.shape[0])
    env['exp'].screen.clear()
    env['exp'].screen.update()

    env['exp'].clock.wait(1000)

    delays_ms = pd.to_datetime(track.timestamp).diff()
    # HACK!! there's no obvious way to convert from timestamps to ms
    # except by dividing by the unit size manually, if this unit size
    # changes in a future version of numpy, then this code will no
    # longer work
    delays_ms = delays_ms.apply(lambda x: x.astype('float64') / 1e6)
    delays_ms[0] = delays_ms.median()

    for track_index in order:
        track_row = track.iloc[track_index,:]
        # provide an oportunity to exit/pause the program
        env['exp'].keyboard.check()
        env['exp'].screen.clear()
        env['exp'].screen.update()

        signal_interval = track_row['correct_response']
        if signal_interval == 0:
            stim_1 = env['sound'](transform(track_row['delta']))
            stim_2 = env['sound'](0)

        else:
            stim_1 = env['sound'](0)
            stim_2 = env['sound'](transform(track_row['delta']))

        stim_1.play()
        env['exp'].clock.wait(env['SOA_ms'])

        stim_2.play()

        delay = max((env['response_delay_ms']),
                    delays_ms[track_index] - env['SOA_ms'] -
                    env['feedback_delay_ms'])

        env['exp'].clock.wait(delay)

        line_info = {'delta': transform(track_row['delta']),
                     'signal_interval': signal_interval,
                     'timestamp': datetime.datetime.now()}

        order = ['delta','signal_interval','timestamp']

        write_line(line_info,order)

        env['exp'].clock.wait(env['feedback_delay_ms'])
