"""
script to submit jobs to purdue cluster
"""
import os

def generateJobScript(nthreads, jobid, sonic=1):
    suffix = "sonic_" + str(nthreads) + "threads_" + str(jobid)
    if not sonic:
        suffix = "no" + suffix

    ofilename = "jobs/job_" + suffix + ".sub"
    jsonname = suffix + ".json"
    outname = suffix + ".root"
    logname = suffix + ".log"

    ofile = open(ofilename, 'w')

    file_entries = []

    file_entries.append('#!/bin/bash')
    file_entries.append('')
    file_entries.append('# source the environment')
    file_entries.append('source ~/.bashrc')
    file_entries.append('')

    ## clean the CMSSW environment
    tmpdir = "/tmp/cmssw_" + suffix
    file_entries.append('if [ -d {} ]; then'.format(tmpdir))
    file_entries.append(' echo "Clean the CMSSW environment"')
    file_entries.append(' rm -rf {}'.format(tmpdir))
    file_entries.append('fi')
    file_entries.append('')

    # copy the tar CMSSW to local directory, and setup the environment there
    file_entries.append('mkdir {}'.format(tmpdir))
    file_entries.append('cp /home/feng356/CMSSW_12_0_0_pre5.tar.gz {}'.format(tmpdir))
    file_entries.append('# set up CMSSW')
    file_entries.append('cd {}'.format(tmpdir))
    file_entries.append('tar -xf CMSSW_12_0_0_pre5.tar.gz')
    file_entries.append('cd CMSSW_12_0_0_pre5/src')
    file_entries.append('scram b ProjectRename # this handles linking the already compiled code - do NOT recompile')
    file_entries.append('eval `scramv1 runtime -sh`')
    file_entries.append('cd sonic-workflows')
    # copy the config files as they might get changed frequently
    file_entries.append('cp /home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/run.py ./')
    file_entries.append('cp /home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/step4_PAT_PU.py ./')
    file_entries.append('cp /home/feng356/CMSSW_12_0_0_pre5/src/sonic-workflows/step2_PAT.py ./')
    file_entries.append('')

    # copy the files to the local directory
    file_entries.append('if [ ! -d /tmp/relvar_data/ ]; then')
    file_entries.append('   # copy files to the local /tmp directory')
    file_entries.append('   mkdir /tmp/relvar_data/')
    file_entries.append('   cp /depot/cms/users/feng356/relvar/63718711-dca3-488a-b6dc-6989dfa81707.root /tmp/relvar_data/')
    file_entries.append('   cp /depot/cms/users/feng356/relvar/8164cd2c-6382-4f17-8a06-efdc9654f17b.root /tmp/relvar_data/')
    file_entries.append('   cp /depot/cms/users/feng356/relvar/8ef2d442-2742-44f3-9a3a-98c01436f16f.root /tmp/relvar_data/')
    file_entries.append('   cp /depot/cms/users/feng356/relvar/b9d51ca4-e359-4598-92f7-1192501ba179.root /tmp/relvar_data/')
    file_entries.append('   echo "done copy"')
    file_entries.append('fi')
    file_entries.append('')

    command = 'cmsRun run.py config="step4_PAT_PU"'
    command += " threads={}".format(nthreads)
    command += " sonic={}".format(sonic)
    command += ' jsonName="{}"'.format(jsonname)
    command += ' outputName="{}"'.format(outname)
    command += ' >& {}'.format(logname)
    file_entries.append(command)

    file_entries.append('')
    file_entries.append('echo "Running SUCCESS. Now copy files back"')
    file_entries.append('cp {} $SLURM_SUBMIT_DIR/results/json/'.format(jsonname))
    file_entries.append('cp {} $SLURM_SUBMIT_DIR/results/log/'.format(logname))

    ofile = open(ofilename, 'w')
    for line in file_entries :
        ofile.write( line + '\n' )

    ofile.close()

    return ofilename


if __name__ == "__main__":
    submit_commands = []
    nthreads = 4
    # removed '041'
    nodes_org = ['000', '001', '002', '003', '004', '005', '006', '007', '008', '009', '010', '011', '012', '014', '015', '017', '018', '019', '020', '022', '023', '024', '025', '028', '029', '030', '031', '032', '034', '036', '037', '038', '039', '041', '043', '044', '046', '047', '048', '050', '051', '052', '053', '054', '055', '056', '057', '059', '060', '061']
    nodes = sorted(nodes_org*2)
    #nodes = sorted(nodes_org)

    inode = 0
    for jobid in range(1,9):
        oname = generateJobScript(nthreads, jobid, sonic=1)
        submit_commands.append('sbatch --account=cms --reservation=SONICCPU --partition=hammer-a --nodes=1 --ntasks={} --time=05:00:00 -w hammer-a{} '.format(nthreads, nodes[inode]) + oname)
        inode += 1


    inode = 0
    for jobid in range(1,9):
        oname = generateJobScript(nthreads, jobid, sonic=0)
        submit_commands.append('sbatch --account=cms --reservation=SONICCPU --partition=hammer-a --nodes=1 --ntasks={} --time=05:00:00 -w hammer-a{} '.format(nthreads, nodes[inode]) + oname)
        inode += 1

    submit_file = open('submit_jobs.sh', 'w' )
    submit_file.write( '#!/bin/bash\n' )
    submit_file.write( '\n')

    for cmd in submit_commands :
        submit_file.write(cmd + '\n' )
    os.system('chmod +x submit_jobs.sh')
    submit_file.close()

