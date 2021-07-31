#!/usr/bin/env python
#vvSubmitLimits.py workspace_JJ_ZprimeWW_HPHP_13TeV_2016.root -s 100 -m 1200 -M 1300 -C 1 -q workday/tomorrow

import ROOT
import os, sys, re, optparse,pickle,shutil,json,random

def makeSubmitFileCondor(exe,jobname,jobflavour,maxruntime,time):
    print "make options file for condor job submission "
    submitfile = open("submit.sub","w")
    submitfile.write("executable  = "+exe+"\n")
    submitfile.write("arguments             = $(ClusterID) $(ProcId)\n")
    submitfile.write("output                = "+jobname+".$(ClusterId).$(ProcId).out\n")
    submitfile.write("error                 = "+jobname+".$(ClusterId).$(ProcId).err\n")
    submitfile.write("log                   = "+jobname+".$(ClusterId).log\n")
    if maxruntime == False:
        submitfile.write('+JobFlavour           = "'+jobflavour+'"\n')
    else:
        submitfile.write('+MaxRuntime           = '+str(time)+'\n')
    submitfile.write("queue")
    submitfile.close() 


parser = optparse.OptionParser()
parser.add_option("-n","--name",dest="name",help="jobdir name",default='job')
parser.add_option("-s","--step",dest="step",type=float,help="step for mass points",default=1000.0)
parser.add_option("-m","--min",dest="min",type=float,help="minimum Mass point",default=1000.0)
parser.add_option("-M","--max",dest="max",type=float,help="maximum Mass point",default=5000.0)
parser.add_option("--rMin",dest="rMin",type=float,help="minimum r",default=0.)
parser.add_option("--rMax",dest="rMax",type=float,help="maximum r",default=50)
parser.add_option("-o","--options",dest="options",help="Combine Options",default='-M Significance')
parser.add_option("-q","--queue",dest="queue",help="Batch Queue",default='8nh')
parser.add_option("-r","--randomSeeds",dest="randomize",type=int, help="randomize seeds",default=0)
parser.add_option("-C","--condor",dest="condor",type=int, help="use condor",default=0)
parser.add_option("--maxruntime",dest="maxruntime",help="give a maximum runtime in seconds in stead of the usual queue options",action='store_true',default=False)
parser.add_option("-t","--time",dest="time",help="use it combined with maxruntime to specify a maximum running time in seconds",default=1296000)
(options,args) = parser.parse_args()


STEPS = int((options.max-options.min)/options.step)

massPoints=[]

for i in range(0,STEPS+1):
    massPoints.append(options.min+i*options.step)




for i,m in enumerate(massPoints):

    if options.randomize:
        suffixOpts=" -s {rndm}".format(rndm = int(random.random()*950000))
    else:
        suffixOpts=" "


    f=open("submit_{i}.sh".format(i=i),'w')
    execScript = "#!/bin/sh\n"
    execScript += "source /afs/cern.ch/cms/cmsset_default.sh\n"
    execScript += 'cd {cwd} \n'.format(cwd=os.getcwd())
    #execScript += 'eval `scramv1 runtime -sh` \n'
    execScript += "cmsenv\n"
    #execScript += "combine -m {mass} {options}  {file} --rMin {rMin} --rMax {rMax}\n".format(mass=m,options=options.options+suffixOpts,file=args[0],rMin=options.rMin,rMax=options.rMax)
    execScript += "combine -m {mass} {options}  {file}\n".format(mass=m,options=options.options+suffixOpts,file=args[0],rMin=options.rMin,rMax=options.rMax)
    f.write(execScript)
    f.close()
    os.system('chmod +x submit_{i}.sh'.format(i=i))

    if not options.condor:
     print "Use LXBATCH!"
     if options.queue!="local":
        os.system('bsub -q {queue} submit_{i}.sh '.format(queue=options.queue,i=i))
     else:    
        os.system('sh submit_{i}.sh '.format(i=i))
    else:
     print "Use CONDOR!"
     print 'rm -rf '+options.name+'_{i}'.format(i=i)
     print 'mkdir '+options.name+'_{i}'.format(i=i)
     os.system('rm -rf '+options.name+'_{i}'.format(i=i))
     os.system('mkdir '+options.name+'_{i}'.format(i=i))
     os.system('mv submit_{i}'.format(i=i)+'.sh '+options.name+'_{i}/submit.sh'.format(i=i))
     os.chdir( options.name+'_{i}'.format(i=i))
     makeSubmitFileCondor('submit.sh'.format(i=i),"job",options.queue,options.maxruntime,options.time)
     os.system("condor_submit submit.sub")
     os.chdir('../')





