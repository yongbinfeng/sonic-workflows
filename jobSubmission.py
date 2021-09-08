"""
script to submit jobs to purdue cluster
"""
import os

def generateJobScript(nthreads, jobid, sonic=1):
    suffix = "sonic_" + str(nthreads) + "threads_" + str(jobid)
    if not suffix:
        suffix = "no" + suffix

    ofilename = "jobs/job_" + suffix + ".sub"
    jsonname = "results/json/" + suffix + ".json"
    outname = "results/out/" + suffix + ".root"
    logname = "results/log/" + suffix + ".log"

    ofile = open(ofilename, 'w')

    file_entries = []

    file_entries.append('#!/bin/bash')
    file_entries.append('')
    file_entries.append('# source the environment')
    file_entries.append('source ~/.bashrc')
    file_entries.append('')
    file_entries.append('cd /home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows')
    file_entries.append('eval `scramv1 runtime -sh`')
    file_entries.append('')

    command = 'cmsRun run.py config="step4_PAT_PU"'
    command += " threads={}".format(nthreads)
    command += " sonic={}".format(sonic)
    command += ' jsonName="{}"'.format(jsonname)
    command += ' outputName="{}"'.format(outname)
    command += ' >& {}'.format(logname)
    file_entries.append(command)

    file_entries.append('')
    file_entries.append('echo "SUCCESS"')

    ofile = open(ofilename, 'w')
    for line in file_entries :
        ofile.write( line + '\n' )

    ofile.close()

    return ofilename


if __name__ == "__main__":
    submit_commands = []
    
    for jobid in range(1,5):
        oname = generateJobScript(8, jobid, sonic=1)
        submit_commands.append('sbatch --account=cms --reservation=SONICCPU --partition=hammer-a --nodes=1 --time=05:00:00 ' + oname)

    submit_file = open('submit_jobs.sh', 'w' )
    submit_file.write( '#!/bin/bash\n' )
    submit_file.write( '\n')

    for cmd in submit_commands :
        submit_file.write(cmd + '\n' )
    os.system('chmod +x submit_jobs.sh')
    submit_file.close()

