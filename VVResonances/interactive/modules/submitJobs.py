#!/usr/bin/env python
import os, re, copy
import commands
import math, time
import sys
import ROOT
from ROOT import *
import subprocess, thread
from array import array
ROOT.gROOT.SetBatch(True)

#reduced to speed the job sending, if jobs are not finished always enter "n" to the questions and rerun the same command with option "--sendjobs False" to merge once jobs are done
timeCheck = "1" 
userName=os.environ['USER']


def getBinning(binsMVV):
    l=[]
    if binsMVV=="":
        return l
    else:
        s = binsMVV.split(",")
        for w in s:
            l.append(int(w))
    return l

useCondorBatch = True
runinKA = False

def makeSubmitFileCondor(exe,jobname,jobflavour):
    print "make options file for condor job submission "
    if runinKA==False:
        submitfile = open("submit.sub","w")
        submitfile.write("executable  = "+exe+"\n")
        submitfile.write("arguments             = $(ClusterID) $(ProcId)\n")
        submitfile.write("output                = "+jobname+".$(ClusterId).$(ProcId).out\n")
        submitfile.write("error                 = "+jobname+".$(ClusterId).$(ProcId).err\n")
        submitfile.write("log                   = "+jobname+".$(ClusterId).log\n")
        submitfile.write('+JobFlavour           = "'+jobflavour+'"\n')
        submitfile.write("queue")
        submitfile.close()
    else:
        submitfile = open("submit.sub","w")
        submitfile.write("universe = vanilla\n")
        submitfile.write("executable  = "+exe+"\n")
        submitfile.write("arguments             = $(ClusterID) $(ProcId)\n")
        submitfile.write("output                = "+jobname+".$(ClusterId).$(ProcId).out\n")
        submitfile.write("error                 = "+jobname+".$(ClusterId).$(ProcId).err\n")
        submitfile.write("log                   = "+jobname+".$(ClusterId).log\n")
        submitfile.write('transfer_output_files = ""\n')
        submitfile.write("getenv = True\n")
        submitfile.write("Requirements =  ( (TARGET.ProvidesCPU) && (TARGET.ProvidesEkpResources) )\n") 
        submitfile.write("+RequestWalltime = 1800\n")
        submitfile.write("RequestMemory = 2500\n")
        submitfile.write("accounting_group = cms.top\n")
        submitfile.write("queue")
        submitfile.close()
    
def waitForBatchJobs( jobname, remainingjobs, listOfJobs, userName, timeCheck="30"):
    if listOfJobs-remainingjobs < listOfJobs:
        time.sleep(float(timeCheck))
        # nprocess = "bjobs -u %s | awk {'print $9'} | grep %s | wc -l" %(userName,jobname)
        if useCondorBatch:
                nprocess = "condor_q %s | grep %s | wc -l"%(userName,jobname)
        else:
                nprocess = "bjobs -u %s | grep %s | wc -l" %(userName,jobname)
        result = subprocess.Popen(nprocess, stdout=subprocess.PIPE, shell=True)
        runningJobs =  int(result.stdout.read())
        print "waiting for %d job(s) in the queue (out of total %d)" %(runningJobs,listOfJobs)
        waitForBatchJobs( jobname, runningJobs, listOfJobs, userName, timeCheck)  
    else:
        print "Jobs finished! Allow some time for files to be saved to your home directory"
        time.sleep(5)
        noutcmd = "ls res"+jobname+"/ | wc -l"
        result = subprocess.Popen(noutcmd, stdout=subprocess.PIPE, shell=True)
        nout =  int(result.stdout.read())
        if listOfJobs-nout > 0: 
            print "Uooh! Missing %i jobs. Resubmit when merging. Now return to main script" %int(listOfJobs-nout)
        else:
            print "Done! Have %i out of %i files in res%s directory. Return to main script"%(nout,listOfJobs,jobname)
        return
        
def submitJobs(minEv,maxEv,cmd,OutputFileNames,queue,jobname,path,submitjobs=True):
    joblist = []
    print "minEv ",minEv
    print " iteritems() ",minEv.iteritems()
    i=0
    for k,v in minEv.iteritems():
      removefile=k[k.rindex("/")+1:]
      directory = str(k).split(removefile)[0]
      year=directory.split("/")[-2]
      template = str(k).split("/")[-1]
      if submitjobs == True:
          for j in range(len(v)):
              os.system("mkdir tmp"+jobname+"/"+year+"_"+template.replace(".root","")+"_"+str(i+1))
              os.chdir("tmp"+jobname+"/"+year+"_"+template.replace(".root","")+"_"+str(i+1))
              with open('job_%s_%i.sh'%(year+"_"+template.replace(".root",""),i+1), 'w') as fout:
                  print " fout" , fout
                  fout.write("#!/bin/sh\n")
                  fout.write("echo\n")
                  fout.write("echo\n")
                  fout.write("echo 'START---------------'\n")
                  fout.write("echo 'WORKDIR ' ${PWD}\n")
                  if runinKA==False:
                      fout.write("source /afs/cern.ch/cms/cmsset_default.sh\n")
                  else: fout.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
                  fout.write("cd "+str(path)+"\n")
                  fout.write("cmsenv\n")
                  if runinKA==True: fout.write("mkdir -p /tmp/${USER}/\n")
                  fout.write(cmd+" -o res"+jobname+"/"+OutputFileNames+"_"+str(i+1)+"_"+year+"_"+template+" -e "+str(minEv[k][j])+" -E "+str(maxEv[k][j])+" "+directory+" -s "+template+"\n")
                  fout.write("echo 'STOP---------------'\n")
                  fout.write("echo\n")
                  fout.write("echo\n")
        
              if useCondorBatch:
                  os.system("mv  job_*.sh "+jobname+".sh")
                  makeSubmitFileCondor(jobname+".sh",jobname,"workday")
                  os.system("condor_submit submit.sub")
              else:
                  os.system("chmod 755 job_%s_%i.sh"%(k.replace(".root",""),i+1) )
                  os.system("bsub -q "+queue+" -o logs job_%s_%i.sh -J %s"%(k.replace(".root",""),i+1,jobname))
              print "job nr " + str(i+1) + " file " + k + " being submitted"
              os.chdir("../..")
      joblist.append("%s_%i"%(year+"_"+template.replace(".root",""),i+1))
      i+=1
    return joblist     

def getEvents(template,samples):
    files = []
    sampleTypes = template.split(',')
    for dirs in samples:
        for f in os.listdir(dirs):
            for t in sampleTypes:
                if f.find('.root') != -1 and f.find(t) != -1: files.append(dirs+f)

    minEv = {}
    maxEv = {}

    for f in files:
        inf = ROOT.TFile(f,'READ')
        print "opening file "+str(f)
        minEv[f] = []
        maxEv[f] = []
        intree = inf.Get('AnalysisTree')
        nentries = intree.GetEntries()
        print f,nentries,nentries/500000
        if nentries/500000 == 0:
            minEv[f].append(0)
            maxEv[f].append(500000)
        else:
            for i in range(nentries/500000):
                minEv[f].append(i*500000)
                maxEv[f].append(499999)
                
                
    NumberOfJobs = 0
    for k in maxEv.keys():
     NumberOfJobs += len(maxEv[k])

    return minEv, maxEv, NumberOfJobs, files
    
def Make2DDetectorParam(rootFile,template,cut,samples,jobname="DetPar",bins="200,250,300,350,400,450,500,600,700,800,900,1000,1500,2000,5000",wait=True,leg="l1"):
   
    print 
    print 'START: Make2DDetectorParam with parameters:'
    print
    print "rootFile = %s" %rootFile  
    print "template = %s" %template  
    print "cut      = %s" %cut       
    print "samples  = %s" %samples   
    print "jobname  = %s" %jobname 
    print "bins     = %s" %bins

    if leg == "l1": cmd='vvMake2DDetectorParam.py  -c "{cut}"  -v "jj_LV_mass,jj_l1_softDrop_mass"  -g "jj_gen_partialMass,jj_l1_gen_softDrop_mass,jj_l1_gen_pt"  -b {bins}   {infolder}'.format(rootFile=rootFile,samples=template,cut=cut,bins=bins,infolder=samples)
    if leg == "l2": cmd='vvMake2DDetectorParam.py  -c "{cut}"  -v "jj_LV_mass,jj_l2_softDrop_mass"  -g "jj_gen_partialMass,jj_l2_gen_softDrop_mass,jj_l2_gen_pt"  -b {bins}   {infolder}'.format(rootFile=rootFile,samples=template,cut=cut,bins=bins,infolder=samples)
    OutputFileNames = rootFile.replace(".root","") # base of the output file name, they will be saved in res directory
    queue = "8nh" # give bsub queue -- 8nm (8 minutes), 1nh (1 hour), 8nh, 1nd (1day), 2nd, 1nw (1 week), 2nw 
    
    files = []
    sampleTypes = template.split(',')
    for f in os.listdir(samples):
        for t in sampleTypes:
            if f.find('.root') != -1 and f.find(t) != -1:
                files.append(f)
                print "file "+str(f)+" appended to jobs"
 
    NumberOfJobs= len(files) 
    print
    print "Submitting %i number of jobs "  ,NumberOfJobs
    print
    
    path = os.getcwd()
    try: os.system("rm -r tmp"+jobname)
    except: print "No tmp/ directory"
    os.system("mkdir tmp"+jobname)
    try: os.stat("res"+jobname) 
    except: os.mkdir("res"+jobname)

    #### Creating and sending jobs #####
    joblist = []
    ##### loop for creating and sending jobs #####
    for x in range(1, int(NumberOfJobs)+1):
     
       os.system("mkdir tmp"+jobname+"/"+str(files[x-1]).replace(".root",""))
       os.chdir("tmp"+jobname+"/"+str(files[x-1]).replace(".root",""))
       with open('job_%s.sh'%files[x-1].replace(".root",""), 'w') as fout:
          fout.write("#!/bin/sh\n")
          fout.write("echo\n")
          fout.write("echo\n")
          fout.write("echo 'START---------------'\n")
          fout.write("echo 'WORKDIR ' ${PWD}\n")
          if runinKA==False:
            fout.write("source /afs/cern.ch/cms/cmsset_default.sh\n")
          else: fout.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
          fout.write("cd "+str(path)+"\n")
          fout.write("cmsenv\n")
          if runinKA==True: fout.write("mkdir -p /tmp/${USER}/\n")
          fout.write(cmd+" -o "+path+"/res"+jobname+"/"+OutputFileNames+"_"+files[x-1]+" -s "+files[x-1]+"\n")
          fout.write("echo 'STOP---------------'\n")
          fout.write("echo\n")
          fout.write("echo\n")
       if useCondorBatch:
         os.system("mv  job_*.sh "+jobname+".sh")
         makeSubmitFileCondor(jobname+".sh",jobname,"workday")
         os.system("condor_submit submit.sub")
       else:
         os.system("chmod 755 job_%s.sh"%(files[x-1].replace(".root","")) )
         os.system("bsub -q "+queue+" -o logs job_%s.sh -J %s"%(files[x-1].replace(".root",""),jobname))
       print "job nr " + str(x) + " submitted"
       joblist.append("%s"%(files[x-1].replace(".root","")))
       os.chdir("../..")
   
    print
    print "your jobs:"
    if useCondorBatch:
            os.system("condor_q")
    else:
            os.system("bjobs")
    userName=os.environ['USER']
    if wait: waitForBatchJobs(jobname,NumberOfJobs,NumberOfJobs, userName, timeCheck)
    
    print
    print 'END: Make2DDetectorParam'
    print
    return joblist, files   
    
def Make1DMVVTemplateWithKernels(rootFile,template,cut,resFile,binsMVV,minMVV,maxMVV,samples,jobName="1DMVV",wait=True,binning='',addOption="",sendjobs=True,doKfactors=False):

    command='vvMake1DMVVTemplateWithKernels.py'
    if rootFile.find("TT")!=-1: command='vvMake1DMVVTemplateTTbar.py'
    if doKfactors == True: command='vvMake1DMVVTemplateVjets.py'
    print 
    print 'START: Make1DMVVTemplateWithKernels with parameters:'
    print command
    print
    print "rootFile = %s" %rootFile  
    print "template = %s" %template  
    print "cut      = %s" %cut       
    print "resFile  = %s" %resFile   
    print "binsMVV  = %i" %binsMVV   
    print "minMVV   = %i" %minMVV    
    print "maxMVV   = %i" %maxMVV    
    print "samples  = %s" %samples   
    print "jobName  = %s" %jobName 
    print
    folders = samples.split(",")
    print "folders ",folders
    minEv, maxEv, NumberOfJobs, files = getEvents(template,folders) 
    print "Submitting %i number of jobs "%(NumberOfJobs)
    print "files involved are ", files
    print "minEv ",minEv
    print "maxEv ",maxEv
    print

    #cmd='vvMake1DMVVTemplateWithKernels.py -H "x" -c "{cut}"  -v "jj_gen_partialMass" {binning} -b {binsMVV}  -x {minMVV} -X {maxMVV} -r {res} {addOption} -d {infolder} '.format(rootFile=rootFile,cut=cut,res=resFile,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,infolder=samples,binning=binning,addOption=addOption)
    cmd=command+' -H "x" -c "{cut}"  -v "jj_gen_partialMass" {binning} -b {binsMVV}  -x {minMVV} -X {maxMVV} -r {res} {addOption} '.format(rootFile=rootFile,cut=cut,res=resFile,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,binning=binning,addOption=addOption)
    print "cmd ",cmd 
    OutputFileNames = rootFile.replace(".root","") # base of the output file name, they will be saved in res directory
    print "OutputFileNames ",OutputFileNames
    queue = "8nh" # give bsub queue -- 8nm (8 minutes), 1nh (1 hour), 8nh, 1nd (1day), 2nd, 1nw (1 week), 2nw 
    
    path = os.getcwd()
    if sendjobs == True:
        try: os.system("rm -r tmp"+jobName)
        except: print "No tmp"+jobName+"/ directory"
        os.system("mkdir tmp"+jobName)
        try: os.stat("res"+jobName)
        except: os.mkdir("res"+jobName)

    #### Creating and sending jobs #####
    print " Creating and sending jobs "
    joblist = submitJobs(minEv,maxEv,cmd,OutputFileNames,queue,jobName,path,sendjobs)
    print "job list made "
    with open('tmp'+jobName+'_joblist.txt','w') as outfile:
        outfile.write("jobList = %s\n" % joblist)
        outfile.write("files = %s\n" % files)
    outfile.close()
    print
    if sendjobs == True:
        print "your jobs:"
        if useCondorBatch:
            os.system("condor_q")
        else:
            os.system("bjobs")
        if wait: waitForBatchJobs(jobName,NumberOfJobs,NumberOfJobs, userName, timeCheck)
        print
    print 'END: Make1DMVVTemplateWithKernels'
    print 

    return joblist, files 


def Make2DTemplateWithKernels(rootFile,template,cut,leg,binsMVV,minMVV,maxMVV,resFile,binsMJ,minMJ,maxMJ,samples,jobName="2DMVV",wait=True,binning='',addOption=''):

    
    print 
    print 'START: Make2DTemplateWithKernels'
    print
    print "rootFile  = %s" %rootFile   
    print "template  = %s" %template   
    print "cut       = %s" %cut       
    print "leg       = %s" %leg       
    print "binsMVV   = %i" %binsMVV    
    print "minMVV    = %i" %minMVV     
    print "maxMVV    = %i" %maxMVV     
    print "resFile   = %s" %resFile    
    print "binsMJ    = %s" %binsMJ    
    print "minMJ     = %s" %minMJ 
    print "maxMJ     = %s" %maxMJ 
    print "samples   = %s" %samples   
    print "jobName   = %s" %jobName   
    print
    folders = samples.split(",")
    print "folders ",folders
    minEv, maxEv, NumberOfJobs, files = getEvents(template,folders) 
    print "Submitting %i number of jobs "%(NumberOfJobs)
    print "files involved are ", files
    print

    cmd='vvMake2DTemplateWithKernels.py -c "{cut}"  -v "jj_{leg}_gen_softDrop_mass,jj_gen_partialMass" {binning}  -b {binsMJ} -B {binsMVV} -x {minMJ} -X {maxMJ} -y {minMVV} -Y {maxMVV}  -r {res} {addOption} -s {samples}'.format(rootFile=rootFile,samples=template,cut=cut,leg=leg,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,res=resFile,binsMJ=binsMJ,minMJ=minMJ,maxMJ=maxMJ,binning=binning,addOption=addOption)
    OutputFileNames = rootFile.replace(".root","") # base of the output file name, they will be saved in res directory
    queue = "8nh" # give bsub queue -- 8nm (8 minutes), 1nh (1 hour), 8nh, 1nd (1day), 2nd, 1nw (1 week), 2nw 
    
    path = os.getcwd()
    try: os.system("rm -r tmp"+jobName)
    except: print "No tmp"+jobName+"/ directory"
    os.system("mkdir tmp"+jobName)
    try: os.stat("res"+jobName)
    except: os.mkdir("res"+jobName)

    #### Creating and sending jobs #####
    joblist = submitJobs(minEv,maxEv,cmd,OutputFileNames,queue,jobName,path)
    with open('tmp'+jobName+'_joblist.txt','w') as outfile:
        outfile.write("jobList = %s\n" % joblist)
        outfile.write("files = %s\n" % files)
    outfile.close()
    print
    print "your jobs:"
    if useCondorBatch:
        os.system("condor_q")
    else:
        os.system("bjobs")
    userName=os.environ['USER']
    if wait: waitForBatchJobs(jobName,NumberOfJobs,NumberOfJobs, userName, timeCheck)
    
    
      
    print
    print 'END: Make2DTemplateWithKernels'
    print

    return joblist, files

def unequalScale(histo,name,alpha,power=1,dim=1):
    newHistoU =copy.deepcopy(histo) 
    newHistoU.SetName(name+"Up")
    newHistoD =copy.deepcopy(histo) 
    newHistoD.SetName(name+"Down")
    if dim == 2:
	    maxFactor = max(pow(histo.GetXaxis().GetXmax(),power),pow(histo.GetXaxis().GetXmin(),power))
	    for i in range(1,histo.GetNbinsX()+1):
	        x= histo.GetXaxis().GetBinCenter(i)
	        for j in range(1,histo.GetNbinsY()+1):
	            nominal=histo.GetBinContent(i,j)
	            factor = 1+alpha*pow(x,power) 
	            newHistoU.SetBinContent(i,j,nominal*factor)
	            newHistoD.SetBinContent(i,j,nominal/factor)
	    if newHistoU.Integral()>0.0:        
	        newHistoU.Scale(1.0/newHistoU.Integral())        
	    if newHistoD.Integral()>0.0:        
	        newHistoD.Scale(1.0/newHistoD.Integral())        
    else:
	    for i in range(1,histo.GetNbinsX()+1):
	        x= histo.GetXaxis().GetBinCenter(i)
                nominal=histo.GetBinContent(i) #ROOT.TMath.Log10(histo.GetBinContent(i))
		factor = 1+alpha*pow(x,power)
		#print i,x,power,alpha,factor,nominal,nominal*factor,nominal/factor
	        newHistoU.SetBinContent(i,nominal*factor)
	        if factor != 0: newHistoD.SetBinContent(i,nominal/factor)
    return newHistoU,newHistoD 
    
def mirror(histo,histoNominal,name,dim=1):
    newHisto =copy.deepcopy(histoNominal) 
    newHisto.SetName(name)
    intNominal=histoNominal.Integral()
    intUp = histo.Integral()
    if dim == 2:
		for i in range(1,histo.GetNbinsX()+1):
			for j in range(1,histo.GetNbinsY()+1):
                                if intUp !=0: up=histo.GetBinContent(i,j)/intUp
                                else:
                                    up=histo.GetBinContent(i,j)
                                    print " ************* up hist not divided by intUp beacuse intUp =0 !!!!!! *******"
				if intNominal !=0 :  nominal=histoNominal.GetBinContent(i,j)/intNominal
                                else :
                                    nominal=histoNominal.GetBinContent(i,j)
                                    print " ************* nominal hist not divided by intNominal beacuse intNominal =0 !!!!!! *******"
				if up != 0: newHisto.SetBinContent(i,j,histoNominal.GetBinContent(i,j)*nominal/up)
    else:
		for i in range(1,histo.GetNbinsX()+1):
                        if intUp !=0: up=histo.GetBinContent(i)/intUp
                        else:	      up=histo.GetBinContent(i)
			nominal=histoNominal.GetBinContent(i)/intNominal
			if up!= 0: newHisto.SetBinContent(i,histoNominal.GetBinContent(i)*nominal/up)
			else: newHisto.SetBinContent(i,0)  	
    return newHisto       

def expandHisto(histo,suffix,binsMVV,binsMJ,minMVV,maxMVV,minMJ,maxMJ):
    histogram=ROOT.TH2F(histo.GetName()+suffix,"histo",binsMJ,minMJ,maxMJ,binsMVV,minMVV,maxMVV)
    for i in range(1,histo.GetNbinsX()+1):
        proje = histo.ProjectionY("q",i,i)
        graph=ROOT.TGraph(proje)
        for j in range(1,histogram.GetNbinsY()+1):
            x=histogram.GetYaxis().GetBinCenter(j)
            bin=histogram.GetBin(i,j)
            histogram.SetBinContent(bin,graph.Eval(x,0,"S"))
    return histogram

def expandHistoBinned(histo,suffix ,binsx,binsy):
    histogram=ROOT.TH2F(histo.GetName()+suffix,"histo",len(binsx)-1,array('f',binsx),len(binsy)-1,array('f',binsy))
    for i in range(1,histo.GetNbinsX()+1):
        proje = histo.ProjectionY("q",i,i)
        graph=ROOT.TGraph(proje)
        for j in range(1,histogram.GetNbinsY()+1):
            x=histogram.GetYaxis().GetBinCenter(j)
            bin=histogram.GetBin(i,j)
            histogram.SetBinContent(bin,graph.Eval(x,0,"S"))
    return histogram
        
def conditional(hist):
    for i in range(1,hist.GetNbinsY()+1):
        proj=hist.ProjectionX("q",i,i)
        integral=proj.Integral()
        if integral==0.0:
            print 'SLICE WITH NO EVENTS!!!!!!!!',hist.GetName()
            continue
        for j in range(1,hist.GetNbinsX()+1):
            hist.SetBinContent(j,i,hist.GetBinContent(j,i)/integral)

def getJobs(files,jobList,outdir,purity):
        print "getting jobs"
	resubmit = []
	jobsPerSample = {}
	exit_flag = False
        
	for s in files:
         y = s.split("/")[-2] 
         s = s.split("/")[-1]
	 s = s.replace('.root','')
         s = y+"_"+s
	 filelist = []
	 for t in jobList:
	  if t.find(s) == -1: 
              continue
	  jobid = t.split("_")[-1]
	  found = False
	  for o in os.listdir(outdir):
	   if o.find(s) != -1 and o.find('_'+jobid+'_') != -1 and o.find(purity)!=-1:
	    found = True
	    filelist.append(outdir+"/"+o)
	    break
	  if not found:
	   print "SAMPLE ",s," JOBID ",jobid," NOT FOUND"
	   exit_flag = True
	   resubmit.append(s+"_"+jobid)
	 if len(filelist) > 0: jobsPerSample[s] = filelist
	return resubmit, jobsPerSample,exit_flag	 

def getNormJobs(files,jobList,outdir,purity):
	resubmit = []
	jobsPerSample = {}
	exit_flag = False

	for s in files:
	 s = s.replace('.root','')
	 filelist = []
	 for t in jobList:
	  if t.find(s) == -1: continue
	  jobid = t
	  found = False
	  for o in os.listdir(outdir):
	   if o.find(s) != -1 and o.find(jobid) != -1 and o.find(purity)!=-1:
	    found = True
	    filelist.append(outdir+"/"+o)
	    break
	  if not found:
	   print "SAMPLE ",s," JOBID ",jobid," NOT FOUND"
	   exit_flag = True
	   resubmit.append(s+"_"+jobid)
	 if len(filelist) > 0: jobsPerSample[s] = filelist
	return resubmit, jobsPerSample,exit_flag	 

	
def reSubmit(jobdir,resubmit,jobname):
 jobs = []
 for o in os.listdir(jobdir):
     for jobs in resubmit:
         if o.find(jobs) != -1:
             jobfolder = jobdir+"/"+jobs+"/"
             os.chdir(jobfolder)
             if useCondorBatch:
                 cmd = "condor_submit submit.sub"
                 script = jobname+".sh"
             else:
                 script = "job_"+jobs+".sh"
                 cmd = "bsub -q 8nh -o logs %s -J %s"%(script,jobname)
             print cmd
             jobs += cmd
             os.system("chmod 755 %s"%script)
             os.system(cmd)
             os.chdir("../..")
 return jobs

def merge2DDetectorParam(jobList,files,resFile,binsxStr,jobname,template="QCD_Pt_"):
    
    print "Merging 2D detector parametrization"

    outdir = 'res'+jobname
    jobdir = 'tmp'+jobname
    print "jobname "+str(jobname)
    print "outdir "+str(outdir)
    print "jobdir "+str(jobdir)
   
    print "Jobs to merge :   " ,jobList
    print "Files ran over:   " ,files

    resubmit, jobsPerSample,exit_flag = getJobs(files,jobList,outdir,"")
    
    if exit_flag:
         submit = raw_input("The following files are missing: %s. Do you  want to resubmit the jobs to the batch system before merging? [y/n] "%resubmit)
         if submit == 'y' or submit=='Y':
             print "Resubmitting jobs:"
             jobs = reSubmit(jobdir,resubmit,jobname)
             waitForBatchJobs(jobname,len(resubmit),len(resubmit), userName, timeCheck)
             resubmit, jobsPerSample,exit_flag = getJobs(files,jobList,outdir,purity)
             if exit_flag: 
                 print "Job crashed again! Please resubmit manually before attempting to merge again"
                 for j in jobs: print j 
                 sys.exit()
         else:
             submit = raw_input("Some files are missing. [y] == Exit without merging, [n] == continue ? ")
             if submit == 'y' or submit=='Y':
                 print "Exit without merging!"
                 sys.exit()
             else:
                 print "Continuing merge!"
    


    filelist = os.listdir('./res'+jobname+'/')
    print "filelist "+str(filelist)



    pythia_files = []
    herwig_files = []
    mg_files = []
    pythia_template="QCD_Pt_"
    herwig_template="QCD_Pt-"
    mg_template="QCD_HT_"
    for f in filelist:
     if f.find(resFile.replace(".root",""))==-1: continue
     if f.find(pythia_template) != -1: pythia_files.append('./res'+jobname+'/'+f)
     elif f.find(mg_template) != -1: mg_files.append('./res'+jobname+'/'+f)
     elif f.find(herwig_template) != -1: herwig_files.append('./res'+jobname+'/'+f)
    

    #now hadd them
    tmp_files = []
    if len(pythia_files) > 0:
        print "doing pythia"
        cmd = 'hadd -f tmp_nominal.root '
        for f in pythia_files:
         cmd += f
         cmd += ' '
        print cmd
        os.system(cmd)
        tmp_files.append('tmp_nominal.root')
        
    if len(mg_files) > 0:
        print "doing mg"
        cmd = 'hadd -f tmp_altshape2.root '
        for f in mg_files:
         cmd += f
         cmd += ' '
        print cmd
        os.system(cmd)  
        tmp_files.append('tmp_altshape2.root')  

    if len(herwig_files) > 0:
        print "doing herwig"
        cmd = 'hadd -f tmp_altshapeUp.root '
        for f in herwig_files:
         cmd += f
         cmd += ' '
        print cmd
        os.system(cmd)  
        tmp_files.append('tmp_altshapeUp.root')
        
    #produce final det resolution files (one per sample, but at the end we use the pythia one in the following steps for all the samples)
    for f in tmp_files:
     print " file in tmp_files ",f 
    
     fin = ROOT.TFile.Open(f,'READ')
     print "WORKING ON FILE ", fin.GetName()
     label = fin.GetName().split('_')[1].split('.')[0]
     print "label ", label
     superHX = fin.Get("dataX")
     superHY = fin.Get("dataY")
     # superHNsubj = fin.Get("dataNsubj")
     
     binsx=[]
     for b in binsxStr.split(','):
         binsx.append(float(b))
     outname = resFile.replace(".root","")+f.split('_')[1]
     print "outname "+str(outname)
     fout = ROOT.TFile(outname,"RECREATE")
     
     scalexHisto=ROOT.TH1F("scalexHisto","scaleHisto",len(binsx)-1,array('d',binsx))
     resxHisto=ROOT.TH1F("resxHisto","resHisto",len(binsx)-1,array('d',binsx))
     scaleyHisto=ROOT.TH1F("scaleyHisto","scaleHisto",len(binsx)-1,array('d',binsx))
     resyHisto=ROOT.TH1F("resyHisto","resHisto",len(binsx)-1,array('d',binsx))
     #scaleNsubjHisto=ROOT.TH1F("scaleNsubjHisto","scaleHisto",len(binsx)-1,array('d',binsx))
     #resNsubjHisto=ROOT.TH1F("resNsubjHisto","resHisto",len(binsx)-1,array('d',binsx))
     
     for bin in range(1,superHX.GetNbinsX()+1):
        tmp=superHX.ProjectionY("q",bin,bin)
        if bin==1: 
                 scalexHisto.SetBinContent(bin,tmp.GetMean())
                 scalexHisto.SetBinError(bin,tmp.GetMeanError())
                 resxHisto.SetBinContent(bin,tmp.GetRMS())
                 resxHisto.SetBinError(bin,tmp.GetRMSError())
                 continue        
        startbin   = 0.
        maxcontent = 0.
        for b in range(tmp.GetXaxis().GetNbins()):
          if tmp.GetXaxis().GetBinCenter(b+1) > startbin and tmp.GetBinContent(b+1)>maxcontent:
            maxbin = b
            maxcontent = tmp.GetBinContent(b+1)
        tmpmean = tmp.GetXaxis().GetBinCenter(maxbin)
        tmpwidth = 0.5
        g1 = ROOT.TF1("g1","gaus", tmpmean-tmpwidth,tmpmean+tmpwidth)
        tmp.Fit(g1, "SR")
        c1 =ROOT.TCanvas("c","",800,800)
        tmp.Draw()
        c1.SaveAs("debug_%s_fit1_mvvres_%i.png"%(label,bin))
        tmpmean = g1.GetParameter(1)
        tmpwidth = g1.GetParameter(2)
        g1 = ROOT.TF1("g1","gaus", tmpmean-(tmpwidth*2),tmpmean+(tmpwidth*2))
        tmp.Fit(g1, "SR")
        c1 =ROOT.TCanvas("c","",800,800)
        tmp.Draw()
        c1.SaveAs("debug_%s_fit2_mvvres_%i.png"%(label,bin))
        tmpmean = g1.GetParameter(1)
        tmpmeanErr = g1.GetParError(1)
        tmpwidth = g1.GetParameter(2)
        tmpwidthErr = g1.GetParError(2)
        scalexHisto.SetBinContent(bin,tmpmean)
        scalexHisto.SetBinError  (bin,tmpmeanErr)
        resxHisto.SetBinContent  (bin,tmpwidth)
        resxHisto.SetBinError    (bin,tmpwidthErr)
     for bin in range(1,superHY.GetNbinsX()+1): 
        tmp=superHY.ProjectionY("q",bin,bin)
        if bin==1:
                 scaleyHisto.SetBinContent(bin,tmp.GetMean())
                 scaleyHisto.SetBinError(bin,tmp.GetMeanError())
                 resyHisto.SetBinContent(bin,tmp.GetRMS())
                 resyHisto.SetBinError(bin,tmp.GetRMSError())       
                 continue       
        startbin   = 0.
        maxcontent = 0.
        for b in range(tmp.GetXaxis().GetNbins()):
          if tmp.GetXaxis().GetBinCenter(b+1) > startbin and tmp.GetBinContent(b+1)>maxcontent:
            maxbin = b
            maxcontent = tmp.GetBinContent(b+1)
        tmpmean = tmp.GetXaxis().GetBinCenter(maxbin)
        tmpwidth = 0.3
        g1 = ROOT.TF1("g1","gaus", tmpmean-tmpwidth,tmpmean+tmpwidth)
        tmp.Fit(g1, "SR")
        c1 =ROOT.TCanvas("c","",800,800)
        tmp.Draw()
        c1.SaveAs("debug_%s_fit1_mjres_%i.png"%(label,bin))
        tmpmean = g1.GetParameter(1)
        tmpwidth = g1.GetParameter(2)
        g1 = ROOT.TF1("g1","gaus", tmpmean-(tmpwidth*1.1),tmpmean+(tmpwidth*1.1))
        tmp.Fit(g1, "SR")
        c1 =ROOT.TCanvas("c","",800,800)
        tmp.Draw()
        c1.SaveAs("debug_%s_fit2_mjres_%i.png"%(label,bin))
        tmpmean = g1.GetParameter(1)
        tmpmeanErr = g1.GetParError(1)
        tmpwidth = g1.GetParameter(2)
        tmpwidthErr = g1.GetParError(2)
        scaleyHisto.SetBinContent(bin,tmpmean)
        scaleyHisto.SetBinError  (bin,tmpmeanErr)
        resyHisto.SetBinContent  (bin,tmpwidth)
        resyHisto.SetBinError    (bin,tmpwidthErr)
         

         # tmp=superHX.ProjectionY("q",bin,bin)
#        scalexHisto.SetBinContent(bin,tmp.GetMean())
#        scalexHisto.SetBinError(bin,tmp.GetMeanError())
#        resxHisto.SetBinContent(bin,tmp.GetRMS())
#        resxHisto.SetBinError(bin,tmp.GetRMSError())
#
#        tmp=superHY.ProjectionY("q",bin,bin)
#        scaleyHisto.SetBinContent(bin,tmp.GetMean())
#        scaleyHisto.SetBinError(bin,tmp.GetMeanError())
#        resyHisto.SetBinContent(bin,tmp.GetRMS())
#        resyHisto.SetBinError(bin,tmp.GetRMSError())

         #tmp=superHNsubj.ProjectionY("q",bin,bin)
         #scaleNsubjHisto.SetBinContent(bin,tmp.GetMean())
         #scaleNsubjHisto.SetBinError(bin,tmp.GetMeanError())
         #resNsubjHisto.SetBinContent(bin,tmp.GetRMS())
         #resNsubjHisto.SetBinError(bin,tmp.GetRMSError())
         
     scalexHisto.Write()
     scaleyHisto.Write()
     #scaleNsubjHisto.Write()
     resxHisto.Write()
     resyHisto.Write()
     #resNsubjHisto.Write()
     superHX.Write("dataX")
     superHY.Write("dataY")
     #superHNsubj.Write("dataNsubj")

     fout.Close()
     fin.Close()
     
     os.system('rm '+f)
    
    #use the pythia det resolution for all the sample in the following steps
    if outname.find("nominal") != -1 and template==pythia_template :
        print " outname used for copy: "+str(outname)
        os.system( 'cp %s %s'%(outname,resFile) )
    elif outname.find("altshapeUp") != -1 and template==herwig_template:
        print " outname used for copy: "+str(outname)
        os.system( 'cp %s %s'%(outname,resFile) )
    elif outname.find("altshape2") != -1 and template==mg_template:
        print " outname used for copy: "+str(outname)
        os.system( 'cp %s %s'%(outname,resFile) )

def merge1DMVVTemplate(jobList,files,jobname,purity,binsMVV,minMVV,maxMVV,HCALbinsMVV,name,filename,doKfactors=False,doTau=False): # ,samples):
	print "Merging 1D templates"
	print
	print "Jobs to merge :   " ,jobList
	print "Files ran over:   " ,files
	print " doing k factors ? ",doKfactors
        print " jobname ",jobname
        outdir = 'res'+jobname
        jobdir = 'tmp'+jobname

        resubmit, jobsPerSample,exit_flag = getJobs(files,jobList,outdir,purity)

        if exit_flag:
            submit = raw_input("The following files are missing: %s. Do you  want to resubmit the jobs to the batch system before merging? [y/n] "%resubmit)
            if submit == 'y' or submit=='Y':
                print "Resubmitting jobs:"
                jobs = reSubmit(jobdir,resubmit,jobname)
                waitForBatchJobs(jobname,len(resubmit),len(resubmit), userName, timeCheck)
                resubmit, jobsPerSample,exit_flag = getJobs(files,jobList,outdir,purity)
                if exit_flag: 
                    print "Job crashed again! Please resubmit manually before attempting to merge again"
                    for j in jobs: print j 
                    sys.exit()
            else:
                submit = raw_input("Some files are missing. [y] == Exit without merging, [n] == continue ? ")
                if submit == 'y' or submit=='Y':
                    print "Exit without merging!"
                    sys.exit()
                else:
                    print "Continuing merge!"
 
        try: 
            os.stat(outdir+'_out') 
            os.system('rm -r '+outdir+'_out')
            os.mkdir(outdir+'_out')
        except: os.mkdir(outdir+'_out')
        
        for s in jobsPerSample.keys():
            factor = 1./float(len(jobsPerSample[s]))
            print "sample: ", s,"number of files:",len(jobsPerSample[s]),"adding histo with scale factor:",factor
            
            outf = ROOT.TFile.Open(outdir+'_out/%s_%s_MVV_%s_%s.root'%(filename,name,s,purity),'RECREATE')
            
            finalHistos = {}
            finalHistos['histo_nominal'] = ROOT.TH1F("histo_nominal_out","histo_nominal_out",binsMVV,minMVV,maxMVV)
            finalHistos['mvv_nominal'] = ROOT.TH1F("mvv_nominal_out","mvv_nominal_out",binsMVV,minMVV,maxMVV)
            if jobname.find("TT") !=-1 and doTau == False:
                finalHistos['histo_noreweight'] = ROOT.TH1F("histo_noreweight_out","histo_noreweight_out",binsMVV,minMVV,maxMVV)
                finalHistos['histo_doublereweight'] = ROOT.TH1F("histo_doublereweight_out","histo_doublereweight_out",binsMVV,minMVV,maxMVV)
            if (jobname.find("WJets") !=-1 or jobname.find("ZJets") !=-1)  and doKfactors == True:
                print " ******** adding kfactors hists "
                finalHistos['histo_noreweight'] = ROOT.TH1F("histo_noreweight_out","histo_noreweight_out",binsMVV,minMVV,maxMVV)
                finalHistos['histo_doublereweight'] = ROOT.TH1F("histo_doublereweight_out","histo_doublereweight_out",binsMVV,minMVV,maxMVV)
            if HCALbinsMVV!="":
                a,b,bins = HCALbinsMVV.split(" ")
                binning = getBinning(bins)
                binning = array("f",binning)
                finalHistos['histo_nominal'] = ROOT.TH1F("histo_nominal_out","histo_nominal_out",len(binning)-1,binning)
                finalHistos['mvv_nominal'] = ROOT.TH1F("mvv_nominal_out","mvv_nominal_out",len(binning)-1,binning)
                if jobname.find("TT") !=-1:
                    finalHistos['histo_noreweight'] = ROOT.TH1F("histo_noreweight_out","histo_noreweight_out",len(binning)-1,binning)
                    finalHistos['histo_doublereweight'] = ROOT.TH1F("histo_doublereweight_out","histo_doublereweight_out",len(binning)-1,binning)
                if (jobname.find("W") !=-1 or jobname.find("Z") !=-1)  and doKfactors == True:
                    print " ******** adding kfactors hists "
                    finalHistos['histo_noreweight'] = ROOT.TH1F("histo_noreweight_out","histo_noreweight_out",len(binning)-1,binning)
                    finalHistos['histo_doublereweight'] = ROOT.TH1F("histo_doublereweight_out","histo_doublereweight_out",len(binning)-1,binning)

            for f in jobsPerSample[s]:
                
                inf = ROOT.TFile.Open(f,'READ')

                for h in inf.GetListOfKeys():

                    if (h.GetName() == 'histo_nominal' and h.GetTitle() == 'histo_nominal') or (h.GetName() == 'mvv_nominal' and h.GetTitle() == 'mvv_nominal') or  (h.GetName() == 'histo_noreweight' and h.GetTitle() == 'histo_noreweight') or (h.GetName() == 'histo_doublereweight'and h.GetTitle() ==  'histo_doublereweight'):
                        
                        histo = ROOT.TH1F()
                        histo = inf.Get(h.GetName())
                        
                        finalHistos[h.GetName()].Add(histo,factor)
                        
                        
            print "Write file: ",outdir+'_out/%s_%s_MVV_%s_%s.root'%(filename,name,s,purity)
   
            outf.cd()  
            finalHistos['histo_nominal'].Write('histo_nominal')
            finalHistos['mvv_nominal'].Write('mvv_nominal')
            if jobname.find("TT") !=-1 and doTau == False:
                finalHistos['histo_noreweight'].Write('histo_noreweight')
                finalHistos['histo_doublereweight'].Write('histo_doublereweight')
            if (jobname.find("W") !=-1 or jobname.find("Z") !=-1)  and doKfactors == True:
                finalHistos['histo_noreweight'].Write('histo_noreweight')
                finalHistos['histo_doublereweight'].Write('histo_doublereweight')

            outf.Close()
            outf.Delete()

        # read out files
        filelist = os.listdir('./'+outdir+'_out'+'/')

        mg_files = []
        pythia_files = []
        herwig_files = []
        dijet_files = []
        tt_files=[]

        for f in filelist:
            if f.find('QCD_HT') != -1: mg_files.append('./'+outdir+'_out'+'/'+f)
            elif f.find('QCD_Pt_') != -1: pythia_files.append('./'+outdir+'_out'+'/'+f)
            elif f.find('QCD_Pt-') != -1: herwig_files.append('./'+outdir+'_out'+'/'+f)
            elif f.find("TT")!= -1 and doTau== False: tt_files.append('./'+outdir+'_out'+'/'+f)
            else: dijet_files.append('./'+outdir+'_out'+'/'+f)
	 
        doMadGraph = False
        doHerwig   = False
        doPythia   = False
        doDijet    = False
	doTT       = False

        #now hadd them
        if len(mg_files) > 0:
            cmd = 'hadd -f %s_%s_MVV_%s_altshape2.root '%(filename,name,purity)
            for f in mg_files:
                cmd += f
                cmd += ' '
            print cmd
            os.system(cmd)
		
            fhadd_madgraph = ROOT.TFile.Open('%s_%s_MVV_%s_altshape2.root'%(filename,name,purity),'READ')
            mvv_altshape2 = fhadd_madgraph.Get('mvv_nominal')
            mvv_altshape2.SetName('mvv_altshape2')
            mvv_altshape2.SetTitle('mvv_altshape2')
            histo_altshape2Up = fhadd_madgraph.Get('histo_nominal')
            histo_altshape2Up.SetName('histo_altshape2Up')
            histo_altshape2Up.SetTitle('histo_altshape2Up')
            
            doMadGraph = True
		
        if len(herwig_files) > 0:
            cmd = 'hadd -f %s_%s_MVV_%s_altshapeUp.root '%(filename,name,purity)
            for f in herwig_files:
                cmd += f
                cmd += ' '
            print cmd
            os.system(cmd)
		
            fhadd_herwig = ROOT.TFile.Open('%s_%s_MVV_%s_altshapeUp.root'%(filename,name,purity),'READ')
            mvv_altshapeUp = fhadd_herwig.Get('mvv_nominal')
            mvv_altshapeUp.SetName('mvv_altshapeUp')
            mvv_altshapeUp.SetTitle('mvv_altshapeUp')
            histo_altshapeUp = fhadd_herwig.Get('histo_nominal')
            histo_altshapeUp.SetName('histo_altshapeUp')
            histo_altshapeUp.SetTitle('histo_altshapeUp')
		
            doHerwig = True
 	
        if len(pythia_files) > 0:
            cmd = 'hadd -f %s_%s_MVV_%s_nominal.root '%(filename,name,purity)
            for f in pythia_files:
                cmd += f
                cmd += ' '
            print cmd
            os.system(cmd)
		
            fhadd_pythia = ROOT.TFile.Open('%s_%s_MVV_%s_nominal.root'%(filename,name,purity),'READ')
            mvv_nominal = fhadd_pythia.Get('mvv_nominal')
            mvv_nominal.SetName('mvv_nominal')
            mvv_nominal.SetTitle('mvv_nominal')
            histo_nominal = fhadd_pythia.Get('histo_nominal')
            histo_nominal.SetName('histo_nominal')
            histo_nominal.SetTitle('histo_nominal')
            
            doPythia = True
            
        if len(dijet_files) > 0:
            
            cmd = 'hadd -f %s_%s_MVV_%s.root '%(filename,name,purity)
            for f in dijet_files:
                cmd += f
                cmd += ' '
            print cmd
            os.system(cmd)
		
            fhadd_dijet = ROOT.TFile.Open('%s_%s_MVV_%s.root'%(filename,name,purity),'READ')
            mvv_NLO = fhadd_dijet.Get('mvv_nominal')
            mvv_NLO.SetName('mvv_nominal')
            mvv_NLO.SetTitle('mvv_nominal')
            histo_NLO = fhadd_dijet.Get('histo_nominal')
            histo_NLO.SetName('histo_nominal')
            histo_NLO.SetTitle('histo_nominal')
            if doKfactors == True:
                histo_noK = fhadd_dijet.Get('histo_noreweight')
                histo_noK.SetName('histo_noreweight')
                histo_noK.SetTitle('histo_noreweight')
                histo_2EW = fhadd_dijet.Get('histo_doublereweight')
                histo_2EW.SetName('histo_doublereweight')
                histo_2EW.SetTitle('histo_doublereweight')

            doDijet = True

        if len(tt_files) > 0:

            cmd = 'hadd -f %s_%s_MVV_%s.root '%(filename,name,purity)
            for f in tt_files:
                cmd += f
                cmd += ' '
            print cmd
            os.system(cmd)

            fhadd_tt = ROOT.TFile.Open('%s_%s_MVV_%s.root'%(filename,name,purity),'READ')
            mvv_nominal = fhadd_tt.Get('mvv_nominal')
            mvv_nominal.SetName('mvv_nominal')
            mvv_nominal.SetTitle('mvv_nominal')
            histo_nominal = fhadd_tt.Get('histo_nominal')
            histo_nominal.SetName('histo_nominal')
            histo_nominal.SetTitle('histo_nominal')
            histo_noreweight = fhadd_tt.Get('histo_noreweight')
            histo_noreweight.SetName('histo_noreweight')
            histo_noreweight.SetTitle('histo_noreweight')
            try:
                histo_doublereweight = fhadd_tt.Get('histo_doublereweight')
                histo_doublereweight.SetName('histo_doublereweight')
                histo_doublereweight.SetTitle('histo_doublereweight')
            except:
                print " no double reweight hist"

            doTT = True

        outf = ROOT.TFile.Open('%s_%s_MVV_%s.root'%(filename,name,purity),'RECREATE') 
        
        if doPythia:
            print "doing Pythia"
            mvv_nominal.Write('mvv_nominal')
            if histo_nominal.Integral() !=0 : histo_nominal.Scale(1./histo_nominal.Integral())
            else: print "************  histo_nominal.Integral() == 0 !!!!! Cannot scale!!! ************"
            histo_nominal.Write('histo_nominal')
			
            print "Now pT"
            alpha=1.5/float(maxMVV)
            histogram_pt_up,histogram_pt_down=unequalScale(histo_nominal,"histo_nominal_PT",alpha)
            histogram_pt_down.SetName('histo_nominal_PTDown')
            histogram_pt_down.SetTitle('histo_nominal_PTDown')
            histogram_pt_down.Write('histo_nominal_PTDown')
            histogram_pt_up.SetName('histo_nominal_PTUp')
            histogram_pt_up.SetTitle('histo_nominal_PTUp')
            histogram_pt_up.Write('histo_nominal_PTUp')
            
            print "Now OPT"
            alpha=1.5*float(minMVV)
            histogram_opt_up,histogram_opt_down=unequalScale(histo_nominal,"histo_nominal_OPT",alpha,-1)
            histogram_opt_down.SetName('histo_nominal_OPTDown')
            histogram_opt_down.SetTitle('histo_nominal_OPTDown')
            histogram_opt_down.Write('histo_nominal_OPTDown')
            histogram_opt_up.SetName('histo_nominal_OPTUp')
            histogram_opt_up.SetTitle('histo_nominal_OPTUp')
            histogram_opt_up.Write('histo_nominal_OPTUp')

            print "Now pT2"
            alpha=15./(5000.*5000.)
            histogram_pt2_up,histogram_pt2_down=unequalScale(histo_nominal,"histo_nominal_PT2",alpha,2)
            histogram_pt2_down.SetName('histo_nominal_PT2Down')
            histogram_pt2_down.SetTitle('histo_nominal_PT2Down')
            histogram_pt2_down.Write('histo_nominal_PT2Down')
            histogram_pt2_up.SetName('histo_nominal_PT2Up')
            histogram_pt2_up.SetTitle('histo_nominal_PT2Up')
            histogram_pt2_up.Write('histo_nominal_PT2Up')
            print "Now opT2"
            alpha=15.*1000.*1000.
            histogram_opt2_up,histogram_opt2_down=unequalScale(histo_nominal,"histo_nominal_OPT2",alpha,-2)
            histogram_opt2_up.SetName('histo_nominal_OPT2Up')
            histogram_opt2_up.SetTitle('histo_nominal_OPT2Up')
            histogram_opt2_up.Write('histo_nominal_OPT2Up')
            histogram_opt2_down.SetName('histo_nominal_OPT2Down')
            histogram_opt2_down.SetTitle('histo_nominal_OPT2Down')
            histogram_opt2_down.Write('histo_nominal_OPT2Down')

            #alpha=5000.*5000.*5000.
            alpha=150./(7000.*7000.*7000.)
            histogram_pt3_down,histogram_pt3_up=unequalScale(histo_nominal,"histo_nominal_PT3",alpha,3)
            histogram_pt3_down.SetName('histo_nominal_PT3Down')
            histogram_pt3_down.SetTitle('histo_nominal_PT3Down')
            histogram_pt3_down.Write('histo_nominal_PT3Down')
            histogram_pt3_up.SetName('histo_nominal_PT3Up')
            histogram_pt3_up.SetTitle('histo_nominal_PT3Up')
            histogram_pt3_up.Write('histo_nominal_PT3Up')
            alpha=150.*1000.*1000.*1000.
            histogram_opt3_down,histogram_opt3_up=unequalScale(histo_nominal,"histo_nominal_OPT3",alpha,-3)
            histogram_opt3_up.SetName('histo_nominal_OPT3Up')
            histogram_opt3_up.SetTitle('histo_nominal_OPT3Up')
            histogram_opt3_up.Write('histo_nominal_OPT3Up')
            histogram_opt3_down.SetName('histo_nominal_OPT3Down')
            histogram_opt3_down.SetTitle('histo_nominal_OPT3Down')
            histogram_opt3_down.Write('histo_nominal_OPT3Down')

            #alpha=5000.*5000.*5000.
            alpha=1500./(7000.*7000.*7000.*7000.)
            histogram_pt4_down,histogram_pt4_up=unequalScale(histo_nominal,"histo_nominal_PT4",alpha,4)
            histogram_pt4_down.SetName('histo_nominal_PT4Down')
            histogram_pt4_down.SetTitle('histo_nominal_PT4Down')
            histogram_pt4_down.Write('histo_nominal_PT4Down')
            histogram_pt4_up.SetName('histo_nominal_PT4Up')
            histogram_pt4_up.SetTitle('histo_nominal_PT4Up')
            histogram_pt4_up.Write('histo_nominal_PT4Up')
            alpha=1500.*1000.*1000.*1000.*1000.
            histogram_opt4_down,histogram_opt4_up=unequalScale(histo_nominal,"histo_nominal_OPT4",alpha,-4)
            histogram_opt4_up.SetName('histo_nominal_OPT4Up')
            histogram_opt4_up.SetTitle('histo_nominal_OPT4Up')
            histogram_opt4_up.Write('histo_nominal_OPT4Up')
            histogram_opt4_down.SetName('histo_nominal_OPT4Down')
            histogram_opt4_down.SetTitle('histo_nominal_OPT4Down')
            histogram_opt4_down.Write('histo_nominal_OPT4Down')
            #alpha=5000.*5000.*5000.
            alpha=15000./(7000.*7000.*7000.*7000.*7000.)
            histogram_pt5_down,histogram_pt5_up=unequalScale(histo_nominal,"histo_nominal_PT5",alpha,5)
            histogram_pt5_down.SetName('histo_nominal_PT5Down')
            histogram_pt5_down.SetTitle('histo_nominal_PT5Down')
            histogram_pt5_down.Write('histo_nominal_PT5Down')
            histogram_pt5_up.SetName('histo_nominal_PT5Up')
            histogram_pt5_up.SetTitle('histo_nominal_PT5Up')
            histogram_pt5_up.Write('histo_nominal_PT5Up')
            alpha=15000.*1000.*1000.*1000.*1000.*1000.
            histogram_opt5_down,histogram_opt5_up=unequalScale(histo_nominal,"histo_nominal_OPT5",alpha,-5)
            histogram_opt5_up.SetName('histo_nominal_OPT5Up')
            histogram_opt5_up.SetTitle('histo_nominal_OPT5Up')
            histogram_opt5_up.Write('histo_nominal_OPT5Up')
            histogram_opt5_down.SetName('histo_nominal_OPT5Down')
            histogram_opt5_down.SetTitle('histo_nominal_OPT5Down')
            histogram_opt5_down.Write('histo_nominal_OPT5Down')
            #alpha=5000.*5000.*5000.
            alpha=150000./(7000.*7000.*7000.*7000.*7000.*7000)
            histogram_pt6_down,histogram_pt6_up=unequalScale(histo_nominal,"histo_nominal_PT6",alpha,6)
            histogram_pt6_down.SetName('histo_nominal_PT6Down')
            histogram_pt6_down.SetTitle('histo_nominal_PT6Down')
            histogram_pt6_down.Write('histo_nominal_PT6Down')
            histogram_pt6_up.SetName('histo_nominal_PT6Up')
            histogram_pt6_up.SetTitle('histo_nominal_PT6Up')
            histogram_pt6_up.Write('histo_nominal_PT6Up')
            alpha=150000.*1000.*1000.*1000.*1000.*1000.*1000
            histogram_opt6_down,histogram_opt6_up=unequalScale(histo_nominal,"histo_nominal_OPT6",alpha,-6)
            histogram_opt6_up.SetName('histo_nominal_OPT6Up')
            histogram_opt6_up.SetTitle('histo_nominal_OPT6Up')
            histogram_opt6_up.Write('histo_nominal_OPT6Up')
            histogram_opt6_down.SetName('histo_nominal_OPT6Down')
            histogram_opt6_down.SetTitle('histo_nominal_OPT6Down')
            histogram_opt6_down.Write('histo_nominal_OPT6Down')
            #alpha=5000.*5000.*5000.
            alpha=0.
            histogram_ptn_down,histogram_ptn_up=unequalScale(histo_nominal,"histo_nominal_PTN",alpha,0)
            histogram_ptn_down.SetName('histo_nominal_PTNDown')
            histogram_ptn_down.SetTitle('histo_nominal_PTNDown')
            histogram_ptn_down.Write('histo_nominal_PTNDown')
            histogram_ptn_up.SetName('histo_nominal_PTNUp')
            histogram_ptn_up.SetTitle('histo_nominal_PTNUp')
            histogram_ptn_up.Write('histo_nominal_PTNUp')
            '''
            alpha=0.
            histogram_optn_down,histogram_optn_up=unequalScale(histo_nominal,"histo_nominal_OPTN",alpha,100)
            histogram_optn_up.SetName('histo_nominal_OPTNUp')
            histogram_optn_up.SetTitle('histo_nominal_OPTNUp')
            histogram_optn_up.Write('histo_nominal_OPTNUp')
            histogram_optn_down.SetName('histo_nominal_OPTNDown')
            histogram_optn_down.SetTitle('histo_nominal_OPTNDown')
            histogram_optn_down.Write('histo_nominal_OPTNDown')
            '''

        if doHerwig:
            print "doing Herwig"
            mvv_altshapeUp.Write('mvv_altshapeUp')
            histo_altshapeUp.Write('histo_altshapeUp')
            
            print "Now pT"
            alpha=1.5/float(maxMVV)
            histogram_altshapeUp_pt_up,histogram_altshapeUp_pt_down=unequalScale(histo_nominal,"histo_altshapeUp_PT",alpha)
            histogram_altshapeUp_pt_down.SetName('histo_altshapeUp_PTDown')
            histogram_altshapeUp_pt_down.SetTitle('histo_altshapeUp_PTDown')
            histogram_altshapeUp_pt_down.Write('histo_altshapeUp_PTDown')
            histogram_altshapeUp_pt_up.SetName('histo_altshapeUp_PTUp')
            histogram_altshapeUp_pt_up.SetTitle('histo_altshapeUp_PTUp')
            histogram_altshapeUp_pt_up.Write('histo_altshapeUp_PTUp')
            
            print "Now OPT"
            alpha=1.5*float(minMVV)
            histogram_altshapeUp_opt_up,histogram_altshapeUp_opt_down=unequalScale(histo_altshapeUp,"histo_altshapeUp_OPT",alpha,-1)
            histogram_altshapeUp_opt_down.SetName('histo_altshapeUp_OPTDown')
            histogram_altshapeUp_opt_down.SetTitle('histo_altshapeUp_OPTDown')
            histogram_altshapeUp_opt_down.Write('histo_altshapeUp_OPTDown')
            histogram_altshapeUp_opt_up.SetName('histo_altshapeUp_OPTUp')
            histogram_altshapeUp_opt_up.SetTitle('histo_altshapeUp_OPTUp')
            histogram_altshapeUp_opt_up.Write('histo_altshapeUp_OPTUp')

            if doPythia:
                histogram_altshapeDown=mirror(histo_altshapeUp,histo_nominal,"histo_altshapeDown")
                histogram_altshapeDown.SetName('histo_altshapeDown')
                histogram_altshapeDown.SetTitle('histo_altshapeDown')
                histogram_altshapeDown.Write('histo_altshapeDown')
		
        if doMadGraph:
            print "doing Madgraph"
            mvv_altshape2.Write('mvv_altshape2')
            histo_altshape2Up.Write('histo_altshape2Up')
            
            print "Now pT"
            alpha=1.5/float(maxMVV)
            histogram_altshape2_pt_up,histogram_altshape2_pt_down=unequalScale(histo_nominal,"histo_altshape2_PT",alpha)
            histogram_altshape2_pt_down.SetName('histo_altshape2_PTDown')
            histogram_altshape2_pt_down.SetTitle('histo_altshape2_PTDown')
            histogram_altshape2_pt_down.Write('histo_altshape2_PTDown')
            histogram_altshape2_pt_up.SetName('histo_altshape2_PTUp')
            histogram_altshape2_pt_up.SetTitle('histo_altshape2_PTUp')
            histogram_altshape2_pt_up.Write('histo_altshape2_PTUp')
            
            print "Now OPT"
            alpha=1.5*float(minMVV)
            histogram_altshape2_opt_up,histogram_altshape2_opt_down=unequalScale(histo_altshape2Up,"histo_altshape2_OPT",alpha,-1)
            histogram_altshape2_opt_down.SetName('histo_altshape2_OPTDown')
            histogram_altshape2_opt_down.SetTitle('histo_altshape2_OPTDown')
            histogram_altshape2_opt_down.Write('histo_altshape2_OPTDown')
            histogram_altshape2_opt_up.SetName('histo_altshape2_OPTUp')
            histogram_altshape2_opt_up.SetTitle('histo_altshape2_OPTUp')
            histogram_altshape2_opt_up.Write('histo_altshape2_OPTUp')
            
            if doPythia:
                histogram_altshape2Down=mirror(histo_altshape2Up,histo_nominal,"histo_altshape2Down")
                histogram_altshape2Down.SetName('histo_altshape2Down')
                histogram_altshape2Down.SetTitle('histo_altshape2Down')
                histogram_altshape2Down.Write('histo_altshape2Down')
                
        if doDijet:
            print "doing VJETS!!"
            mvv_NLO.Write('mvv_nominal')
            histo_NLO.Write('histo_nominal')
            if doKfactors == True:
                histo_noK.Write('histo_noreweight')
                histo_2EW.Write('histo_doublereweight')

            if doKfactors == False:
                print "Now pT"
                alpha=1.5/float(maxMVV)
                histogram_pt_up,histogram_pt_down=unequalScale(histo_NLO,"histo_nominal_PT",alpha)
                histogram_pt_down.SetName('histo_nominal_PTDown')
                histogram_pt_down.SetTitle('histo_nominal_PTDown')
                histogram_pt_down.Write('histo_nominal_PTDown')
                histogram_pt_up.SetName('histo_nominal_PTUp')
                histogram_pt_up.SetTitle('histo_nominal_PTUp')
                histogram_pt_up.Write('histo_nominal_PTUp')

                print "Now OPT"
                alpha=1.5*float(minMVV)
                histogram_opt_up,histogram_opt_down=unequalScale(histo_NLO,"histo_nominal_OPT",alpha,-1)
                histogram_opt_down.SetName('histo_nominal_OPTDown')
                histogram_opt_down.SetTitle('histo_nominal_OPTDown')
                histogram_opt_down.Write('histo_nominal_OPTDown')
                histogram_opt_up.SetName('histo_nominal_OPTUp')
                histogram_opt_up.SetTitle('histo_nominal_OPTUp')
                histogram_opt_up.Write('histo_nominal_OPTUp')


                if doPythia:
                    histogram_NLODown=mirror(histo_NLO,histo_nominal,"histo_NLODown")
                    histogram_NLODown.SetName('histo_NLODown')
                    histogram_NLODown.SetTitle('histo_NLODown')
                    histogram_NLODown.Write('histo_NLODown')


            c = ROOT.TCanvas("c","C",600,400)
            c.SetRightMargin(0.11)
            c.SetLeftMargin(0.11)
            c.SetTopMargin(0.11)
            histo_NLO.SetLineColor(ROOT.kBlue)
            histo_NLO.GetYaxis().SetTitle("arbitrary scale")
            histo_NLO.GetYaxis().SetTitleOffset(1.5)
            histo_NLO.GetXaxis().SetTitle("dijet mass")
            histo_NLO.Draw("hist")
            l = ROOT.TLegend(0.17,0.2,0.6,0.33)
            l.AddEntry(mvv_NLO,"simulation","lp")
            l.AddEntry(histo_NLO,"template","l")
            histo_NLO.SetMinimum(0.0000000000001)
            sf = histo_NLO.Integral()
            if doKfactors == False:
                if histogram_pt_up.Integral() !=0:
                    histogram_pt_up     .Scale(sf/histogram_pt_up.Integral())
                if histogram_pt_down.Integral() != 0:
                    histogram_pt_down   .Scale(sf/histogram_pt_down.Integral())
                if histogram_opt_up.Integral() !=0:
                    histogram_opt_up    .Scale(sf/histogram_opt_up.Integral())
                if histogram_opt_down.Integral() !=0:
                    histogram_opt_down  .Scale(sf/histogram_opt_down.Integral())

                histogram_pt_up.SetLineColor(ROOT.kRed)
                histogram_pt_up.SetLineWidth(2)
                histogram_pt_up.Draw("histsame")
                histogram_pt_down.SetLineColor(ROOT.kRed)
                histogram_pt_down.SetLineWidth(2)
                histogram_pt_down.Draw("histsame")
                histogram_opt_up.SetLineColor(ROOT.kGreen)
                histogram_opt_up.SetLineWidth(2)
                histogram_opt_up.Draw("histsame")
                histogram_opt_down.SetLineColor(ROOT.kGreen)
                histogram_opt_down.SetLineWidth(2)
                histogram_opt_down.Draw("histsame")
                l.AddEntry(histogram_pt_up,"#propto m_{jj}","l")
                l.AddEntry(histogram_opt_up,"#propto 1/m_{jj}","l")

            else:
                if histo_noK.Integral() !=0:
                    histo_noK     .Scale(sf/histo_noK.Integral())
                if histo_2EW.Integral() !=0:
                    histo_2EW     .Scale(sf/histo_2EW.Integral())
                histo_noK.SetLineColor(ROOT.kRed)
                histo_noK.SetLineWidth(2)
                histo_noK.SetLineStyle(2)
                histo_noK.Draw("histsame")
                histo_2EW.SetLineColor(ROOT.kGreen+1)
                histo_2EW.SetLineWidth(2)
                histo_2EW.SetLineStyle(3)
                histo_2EW.Draw("histsame")

                l.AddEntry(histo_noK,"no K-factors","l")
                l.AddEntry(histo_2EW,"2 EW factors","l")

            text = ROOT.TLatex()
            text.DrawLatexNDC(0.13,0.92,"#font[62]{CMS} #font[52]{Simulation}")
            if mvv_NLO.Integral() != 0:
                mvv_NLO.Scale(sf/mvv_NLO.Integral())
            mvv_NLO.SetMarkerColor(ROOT.kBlack)
            mvv_NLO.SetMarkerStyle(7)
            mvv_NLO.Draw("same")
            c.SetLogy()



            l.Draw("same")

            tmplabel = name
            label=filename.split("_")[1]
            print "label ",label
            tmplabel += "_"+label+"_"+purity
            c.SaveAs("debug_mVV_kernels_"+tmplabel+".pdf")
            print "for debugging save","debug_mVV_kernels_"+tmplabel+".pdf"


        if doTT:
            print "doing TTbar!!"
            mvv_nominal.Write('mvv_nominal')
            histo_nominal.Write('histo_nominal')
            histo_noreweight.Write('histo_noreweight')
            try:
                histo_doublereweight.Write('histo_doublereweight')
            except:
                print " no double"
            c = ROOT.TCanvas("c","C",600,400)
            c.SetRightMargin(0.11)
            c.SetLeftMargin(0.11)
            c.SetTopMargin(0.11)
            histo_nominal.SetLineColor(ROOT.kBlue)
            sf=histo_nominal.Integral()
            #if(sf != 0): histo_nominal.Scale(1./sf)
            histo_nominal.GetYaxis().SetTitle("arbitrary scale")
            histo_nominal.GetYaxis().SetTitleOffset(1.5)
            histo_nominal.GetXaxis().SetTitle("dijet mass")
            histo_nominal.SetMinimum(0.0000000000001)
            if histo_noreweight.Integral() !=0 :
                histo_noreweight     .Scale(sf/histo_noreweight.Integral())
            else: print "histo_noreweight  not scaled! !!!!!!!!!!!!!!!!!!!!!!!!!!!    Integral = 0!!!!! "
            try:
                if histo_doublereweight.Integral() !=0 :
                    histo_doublereweight     .Scale(sf/histo_doublereweight.Integral())
                else: print "histo_noreweight  not scaled! !!!!!!!!!!!!!!!!!!!!!!!!!!!    Integral = 0!!!!! "
            except:
                print " no double"
            histo_nominal.SetLineColor(ROOT.kRed)
            histo_nominal.SetLineWidth(2)
            histo_nominal.Draw("hist")
            histo_noreweight.SetLineColor(ROOT.kBlue)
            histo_noreweight.SetLineWidth(2)
            histo_noreweight.SetLineStyle(2)
            histo_noreweight.Draw("histsame")
            try:
                histo_doublereweight.SetLineColor(ROOT.kRed)
                histo_doublereweight.SetLineWidth(2)
                histo_doublereweight.SetLineStyle(2)
                histo_doublereweight.Draw("histsame")
            except:
                print " no double"

            text = ROOT.TLatex()
            text.DrawLatexNDC(0.13,0.92,"#font[62]{CMS} #font[52]{Simulation}")
            if mvv_nominal.Integral() !=0:
                mvv_nominal.Scale(sf/mvv_nominal.Integral())
            else: print "mvv_nominal  not scaled! !!!!!!!!!!!!!!!!!!!!!!!!!!!    Integral = 0!!!!! "
            mvv_nominal.SetMarkerColor(ROOT.kBlack)
            mvv_nominal.SetMarkerStyle(7)
            mvv_nominal.Draw("same")
            c.SetLogy()


            l = ROOT.TLegend(0.17,0.2,0.6,0.33)
            l.AddEntry(mvv_nominal,"simulation","lp")
            l.AddEntry(histo_nominal,"template","l")
            l.AddEntry(histo_noreweight,"no pt reweigh","l")
            #try:
            #    l.AddEntry(histo_doublereweight,"double pt reweigh","l")
            #except:
            #    print " no double"

            l.Draw("same")


            tmplabel = name
            label=filename.split("_")[1]
            print "label ",label
            tmplabel += "_"+label+"_"+purity
            c.SaveAs("debug_mVV_kernels_"+tmplabel+".pdf")
            print "for debugging save","debug_mVV_kernels_"+tmplabel+".pdf"


        os.system('rm -rf '+outdir+'_out/')
                
def merge2DTemplate(jobList,files,jobname,purity,leg,binsMVV,binsMJ,minMVV,maxMVV,minMJ,maxMJ,HCALbinsMVV,name,filename,samples):  
  
  print "Merging 2D templates"
  print
  print "Jobs to merge :   " ,jobList
  print "Files ran over:   " ,files
  
  outdir = 'res'+jobname
  jobdir = 'tmp'+jobname

  resubmit, jobsPerSample,exit_flag = getJobs(files,jobList,outdir,purity)
  
  if exit_flag:
      submit = raw_input("The following files are missing: %s. Do you  want to resubmit the jobs to the batch system before merging? [y/n] "%resubmit)
      if submit == 'y' or submit=='Y':
          print "Resubmitting jobs:"
          jobs = reSubmit(jobdir,resubmit,jobname)
          waitForBatchJobs(jobname,len(resubmit),len(resubmit), userName, timeCheck)
          resubmit, jobsPerSample,exit_flag = getJobs(files,jobList,outdir,purity)
          if exit_flag: 
              print "Job crashed again! Please resubmit manually before attempting to merge again"
              for j in jobs: print j 
              sys.exit()
      else:
          submit = raw_input("Some files are missing. [y] == Exit without merging, [n] == continue ? ")
          if submit == 'y' or submit=='Y':
              print "Exit without merging!"
              sys.exit()
          else:
              print "Continuing merge!"
  
 
  try: 
      os.stat(outdir+'_out') 
      os.system('rm -r '+outdir+'_out')
      os.mkdir(outdir+'_out')
  except: os.mkdir(outdir+'_out')

  for s in jobsPerSample.keys():

        factor = 1./float(len(jobsPerSample[s]))
        print "sample: ", s,"number of files:",len(jobsPerSample[s]),"adding histo with scale factor:",factor
 
        outf = ROOT.TFile.Open(outdir+'_out/%s_%s_COND2D_%s_%s_%s.root'%(filename,name,s,leg,purity),'RECREATE')
  
        finalHistos = {}
        finalHistos['histo_nominal_coarse'] = ROOT.TH2F("histo_nominal_coarse_out","histo_nominal_coarse_out",binsMJ,minMJ,maxMJ,binsMVV,minMVV,maxMVV)
        finalHistos['mjet_mvv_nominal'] = ROOT.TH2F("mjet_mvv_nominal_out","mjet_mvv_nominal_out",binsMJ,minMJ,maxMJ,binsMVV,minMVV,maxMVV)
        finalHistos['mjet_mvv_nominal_3D'] = ROOT.TH3F("mjet_mvv_nominal_3D_out","mjet_mvv_nominal_3D_out",binsMJ,minMJ,maxMJ,binsMJ,minMJ,maxMJ,binsMVV,minMVV,maxMVV)
        if HCALbinsMVV!="":
            a,b,bins = HCALbinsMVV.split(" ")
            binning = getBinning(bins)
            binning = array("d",binning)
            xbins = []
            for i in range(0,binsMJ+1):
                xbins.append(minMJ + i* (maxMJ - minMJ)/binsMJ)
            xbins = array("d",xbins)
            finalHistos['histo_nominal_coarse'] = ROOT.TH2F("histo_nominal_coarse_out","histo_nominal_coarse_out",len(xbins)-1,xbins,len(binning)-1,binning)
            finalHistos['mjet_mvv_nominal'] = ROOT.TH2F("mjet_mvv_nominal_out","mjet_mvv_nominal_out",len(xbins)-1,xbins,len(binning)-1,binning)
            finalHistos['mjet_mvv_nominal_3D'] = ROOT.TH3F("mjet_mvv_nominal_3D_out","mjet_mvv_nominal_3D_out",len(xbins)-1,xbins,len(xbins)-1,xbins,len(binning)-1,binning)
            print "use binning "+str(binning)
        print binsMVV
        print finalHistos['histo_nominal_coarse'].GetNbinsY()
        for f in jobsPerSample[s]:

            inf = ROOT.TFile.Open(f,'READ')
            #print "open file "+f
    
            for h in inf.GetListOfKeys():
  
                for k in finalHistos.keys():
        
                    if h.GetName() == k:
                        histo = ROOT.TH1F()
                        histo = inf.Get(h.GetName())

                        finalHistos[h.GetName()].Add(histo,factor)
   
        print "Write file: ",outdir+'_out/%s_%s_COND2D_%s_%s_%s.root'%(filename,name,s,leg,purity)
   
        outf.cd()  
 
        for k in finalHistos.keys():
            finalHistos[k].SetTitle(k)
            finalHistos[k].Write(k)
   
        outf.Close()
        outf.Delete()


        # read out files
        filelist = os.listdir('./'+outdir+'_out'+'/')

        mg_files = []
        pythia_files = []
        herwig_files = []
        dijet_files = []
        
        for f in filelist:
           if f.find('COND2D') == -1: continue
           if f.find('QCD_HT') != -1: mg_files.append('./'+outdir+'_out'+'/'+f)
           elif f.find('QCD_Pt_') != -1: pythia_files.append('./'+outdir+'_out'+'/'+f)
           elif f.find('QCD_Pt-') != -1: herwig_files.append('./'+outdir+'_out'+'/'+f)
           else: dijet_files.append('./'+outdir+'_out'+'/'+f)
   
   
        doMadGraph = False
        doHerwig   = False
        doPythia   = False
        doDijet    = False
  
        #now hadd them
        if len(mg_files) > 0:
            print "doing MadGraph "
            cmd = 'hadd -f %s_%s_COND2D_%s_%s_altshape2.root '%(filename,name,purity,leg)
            for f in mg_files:
                cmd += f
                cmd += ' '
            print cmd
            os.system(cmd)


            fhadd_madgraph = ROOT.TFile.Open('%s_%s_COND2D_%s_%s_altshape2.root'%(filename,name,purity,leg),'READ')
            mjet_mvv_altshape2_3D = fhadd_madgraph.Get('mjet_mvv_nominal_3D') 
            mjet_mvv_altshape2_3D.SetName('mjet_mvv_altshape2_3D')
            mjet_mvv_altshape2_3D.SetTitle('mjet_mvv_altshape2_3D')
            mjet_mvv_altshape2 = fhadd_madgraph.Get('mjet_mvv_nominal')
            mjet_mvv_altshape2.SetName('mjet_mvv_altshape2')
            mjet_mvv_altshape2.SetTitle('mjet_mvv_altshape2')
            histo_altshape2Up = fhadd_madgraph.Get('histo_nominal_coarse')
            histo_altshape2Up.SetName('histo_altshape2_coarse')
            histo_altshape2Up.SetTitle('histo_altshape2_coarse')
            #histo_altshape2 = fhadd_madgraph.Get('histo_nominal')
            #histo_altshape2.SetName('histo_altshape2')
            #histo_altshape2.SetTitle('histo_altshape2')
            
            doMadGraph = True
            
            
        if len(herwig_files) > 0:
            print "doing Herwig"
            cmd = 'hadd -f %s_%s_COND2D_%s_%s_altshapeUp.root '%(filename,name,purity,leg)
            for f in herwig_files:
                cmd += f
                cmd += ' '
            print cmd
            os.system(cmd)

            fhadd_herwig = ROOT.TFile.Open('%s_%s_COND2D_%s_%s_altshapeUp.root'%(filename,name,purity,leg),'READ')
            mjet_mvv_altshapeUp_3D = fhadd_herwig.Get('mjet_mvv_nominal_3D') 
            mjet_mvv_altshapeUp_3D.SetName('mjet_mvv_altshapeUp_3D')
            mjet_mvv_altshapeUp_3D.SetTitle('mjet_mvv_altshapeUp_3D')
            mjet_mvv_altshapeUp = fhadd_herwig.Get('mjet_mvv_nominal')
            mjet_mvv_altshapeUp.SetName('mjet_mvv_altshapeUp')
            mjet_mvv_altshapeUp.SetTitle('mjet_mvv_altshapeUp')
            histo_altshapeUp = fhadd_herwig.Get('histo_nominal_coarse')
            histo_altshapeUp.SetName('histo_altshapeUp_coarse')
            histo_altshapeUp.SetTitle('histo_altshapeUp_coarse')
            #histo_altshapeUp = fhadd_herwig.Get('histo_nominal')
            #histo_altshapeUp.SetName('histo_altshapeUp')
            #histo_altshapeUp.SetTitle('histo_altshapeUp')
            doHerwig = True

        if len(pythia_files) > 0:
            print "doing pythia"
            cmd = 'hadd -f %s_%s_COND2D_%s_%s_nominal.root '%(filename,name,purity,leg)
            for f in pythia_files:
                cmd += f
                cmd += ' '
            print cmd
            os.system(cmd)
    
            fhadd_pythia = ROOT.TFile.Open('%s_%s_COND2D_%s_%s_nominal.root'%(filename,name,purity,leg),'READ')
            mjet_mvv_nominal_3D = fhadd_pythia.Get('mjet_mvv_nominal_3D') 
            mjet_mvv_nominal_3D.SetName('mjet_mvv_nominal_3D')
            mjet_mvv_nominal_3D.SetTitle('mjet_mvv_nominal_3D')
            mjet_mvv_nominal = fhadd_pythia.Get('mjet_mvv_nominal')
            mjet_mvv_nominal.SetName('mjet_mvv_nominal')
            mjet_mvv_nominal.SetTitle('mjet_mvv_nominal')
            fhadd_pythia.Print()
            histo_nominal = fhadd_pythia.Get('histo_nominal_coarse')
            histo_nominal.SetName('histo_nominal_coarse')
            histo_nominal.SetTitle('histo_nominal_coarse')
            #histo_nominal = fhadd_pythia.Get('histo_nominal')
            #histo_nominal.SetName('histo_nominal')
            #histo_nominal.SetTitle('histo_nominal')
            
            doPythia = True
            
        if len(dijet_files) > 0:
            cmd = 'hadd -f %s_%s_COND2D_%s_%s_NLO.root '%(filename,name,purity,leg)
            for f in dijet_files:
                cmd += f
                cmd += ' '
            print cmd
            os.system(cmd)

            fhadd_dijet = ROOT.TFile.Open('%s_%s_COND2D_%s_%s_NLO.root'%(filename,name,purity,leg),'READ')
            mjet_mvv_NLO_3D = fhadd_dijet.Get('mjet_mvv_nominal_3D') 
            mjet_mvv_NLO_3D.SetName('mjet_mvv_NLO_3D')
            mjet_mvv_NLO_3D.SetTitle('mjet_mvv_NLO_3D')
            mjet_mvv_NLO = fhadd_dijet.Get('mjet_mvv_nominal')
            mjet_mvv_NLO.SetName('mjet_mvv_NLO')
            mjet_mvv_NLO.SetTitle('mjet_mvv_NLO')
            histo_NLO = fhadd_dijet.Get('histo_nominal_coarse')
            histo_NLO.SetName('histo_NLO_coarse')
            histo_NLO.SetTitle('histo_NLO_coarse')
            doDijet = True
            
    
        outf = ROOT.TFile.Open('%s_%s_COND2D_%s_%s.root'%(filename,name,purity,leg),'RECREATE') 
        finalHistograms = {}
  
        if doPythia:
            mjet_mvv_nominal.Write('mjet_mvv_nominal')
            mjet_mvv_nominal_3D.Write('mjet_mvv_nominal_3D')
            
            histo_nominal.Write('histo_nominal_coarse')
            print "make conditional histogram"
            conditional(histo_nominal)
            
            if HCALbinsMVV!="":
                expanded=expandHistoBinned(histo_nominal,"",xbins,binning)
            else:
                expanded=expandHisto(histo_nominal,"",binsMVV,binsMJ,minMVV,maxMVV,minMJ,maxMJ)
            conditional(expanded)
            expanded.SetName('histo_nominal')
            expanded.SetTitle('histo_nominal')
            expanded.Write('histo_nominal')
            finalHistograms['histo_nominal'] = histo_nominal
        
            alpha=1.5/float(maxMJ)
            histogram_pt_up,histogram_pt_down=unequalScale(finalHistograms['histo_nominal'],"histo_nominal_PT",alpha,1,2)
            conditional(histogram_pt_down)
            histogram_pt_down.SetName('histo_nominal_PTDown')
            histogram_pt_down.SetTitle('histo_nominal_PTDown')


            histogram_pt_down.Write('histo_nominal_PTDown')
            conditional(histogram_pt_up)
            histogram_pt_up.SetName('histo_nominal_PTUp')
            histogram_pt_up.SetTitle('histo_nominal_PTUp')
            histogram_pt_up.Write('histo_nominal_PTUp')
            
            alpha=1.5*float(minMJ)
            h1,h2=unequalScale(finalHistograms['histo_nominal'],"histo_nominal_OPT",alpha,-1,2)
            conditional(h1)
            h1.SetName('histo_nominal_OPTUp')
            h1.SetTitle('histo_nominal_OPTUp')
            h1.Write('histo_nominal_OPTUp')
            conditional(h2)
            h2.SetName('histo_nominal_OPTDown')
            h2.SetTitle('histo_nominal_OPTDown')
            h2.Write('histo_nominal_OPTDown')
            
            alpha=float(maxMJ)*float(maxMJ)
            histogram_pt2_up,histogram_pt2_down=unequalScale(finalHistograms['histo_nominal'],"histo_nominal_PT2",alpha,2,2)
            conditional(histogram_pt2_down)
            histogram_pt2_down.SetName('histo_nominal_PT2Down')
            histogram_pt2_down.SetTitle('histo_nominal_PT2Down')
            histogram_pt2_down.Write('histo_nominal_PT2Down')
            conditional(histogram_pt2_up)
            histogram_pt2_up.SetName('histo_nominal_PT2Up')
            histogram_pt2_up.SetTitle('histo_nominal_PT2Up')
            histogram_pt2_up.Write('histo_nominal_PT2Up')
            
            alpha=float(minMJ)*float(minMJ)
            histogram_opt2_up,histogram_opt2_down=unequalScale(finalHistograms['histo_nominal'],"histo_nominal_OPT2",alpha,-2,2)
            conditional(histogram_opt2_down)
            histogram_opt2_down.SetName('histo_nominal_OPT2Down')
            histogram_opt2_down.SetTitle('histo_nominal_OPT2Down')
            histogram_opt2_down.Write('histo_nominal_OPT2Down')
            conditional(histogram_opt2_up)
            histogram_opt2_up.SetName('histo_nominal_OPT2Up')
            histogram_opt2_up.SetTitle('histo_nominal_OPT2Up')
            histogram_opt2_up.Write('histo_nominal_OPT2Up')

            #alpha=5000.*5000.*5000.
            alpha=150./(7000.*7000.*7000.)
            histogram_pt3_down,histogram_pt3_up=unequalScale(histo_nominal,"histo_nominal_PT3",alpha,3)
            histogram_pt3_down.SetName('histo_nominal_PT3Down')
            histogram_pt3_down.SetTitle('histo_nominal_PT3Down')
            histogram_pt3_down.Write('histo_nominal_PT3Down')
            histogram_pt3_up.SetName('histo_nominal_PT3Up')
            histogram_pt3_up.SetTitle('histo_nominal_PT3Up')
            histogram_pt3_up.Write('histo_nominal_PT3Up')
            alpha=150.*1000.*1000.*1000.
            histogram_opt3_down,histogram_opt3_up=unequalScale(histo_nominal,"histo_nominal_OPT3",alpha,-3)
            histogram_opt3_up.SetName('histo_nominal_OPT3Up')
            histogram_opt3_up.SetTitle('histo_nominal_OPT3Up')
            histogram_opt3_up.Write('histo_nominal_OPT3Up')
            histogram_opt3_down.SetName('histo_nominal_OPT3Down')
            histogram_opt3_down.SetTitle('histo_nominal_OPT3Down')
            histogram_opt3_down.Write('histo_nominal_OPT3Down')

            #alpha=5000.*5000.*5000.
            alpha=1500./(7000.*7000.*7000.*7000.)
            histogram_pt4_down,histogram_pt4_up=unequalScale(histo_nominal,"histo_nominal_PT4",alpha,4)
            histogram_pt4_down.SetName('histo_nominal_PT4Down')
            histogram_pt4_down.SetTitle('histo_nominal_PT4Down')
            histogram_pt4_down.Write('histo_nominal_PT4Down')
            histogram_pt4_up.SetName('histo_nominal_PT4Up')
            histogram_pt4_up.SetTitle('histo_nominal_PT4Up')
            histogram_pt4_up.Write('histo_nominal_PT4Up')
            alpha=1500.*1000.*1000.*1000.*1000.
            histogram_opt4_down,histogram_opt4_up=unequalScale(histo_nominal,"histo_nominal_OPT4",alpha,-4)
            histogram_opt4_up.SetName('histo_nominal_OPT4Up')
            histogram_opt4_up.SetTitle('histo_nominal_OPT4Up')
            histogram_opt4_up.Write('histo_nominal_OPT4Up')
            histogram_opt4_down.SetName('histo_nominal_OPT4Down')
            histogram_opt4_down.SetTitle('histo_nominal_OPT4Down')
            histogram_opt4_down.Write('histo_nominal_OPT4Down')
            #alpha=5000.*5000.*5000.
            alpha=15000./(7000.*7000.*7000.*7000.*7000.)
            histogram_pt5_down,histogram_pt5_up=unequalScale(histo_nominal,"histo_nominal_PT5",alpha,5)
            histogram_pt5_down.SetName('histo_nominal_PT5Down')
            histogram_pt5_down.SetTitle('histo_nominal_PT5Down')
            histogram_pt5_down.Write('histo_nominal_PT5Down')
            histogram_pt5_up.SetName('histo_nominal_PT5Up')
            histogram_pt5_up.SetTitle('histo_nominal_PT5Up')
            histogram_pt5_up.Write('histo_nominal_PT5Up')
            alpha=15000.*1000.*1000.*1000.*1000.*1000.
            histogram_opt5_down,histogram_opt5_up=unequalScale(histo_nominal,"histo_nominal_OPT5",alpha,-5)
            histogram_opt5_up.SetName('histo_nominal_OPT5Up')
            histogram_opt5_up.SetTitle('histo_nominal_OPT5Up')
            histogram_opt5_up.Write('histo_nominal_OPT5Up')
            histogram_opt5_down.SetName('histo_nominal_OPT5Down')
            histogram_opt5_down.SetTitle('histo_nominal_OPT5Down')
            histogram_opt5_down.Write('histo_nominal_OPT5Down')
            #alpha=5000.*5000.*5000.
            alpha=150000./(7000.*7000.*7000.*7000.*7000.*7000)
            histogram_pt6_down,histogram_pt6_up=unequalScale(histo_nominal,"histo_nominal_PT6",alpha,6)
            histogram_pt6_down.SetName('histo_nominal_PT6Down')
            histogram_pt6_down.SetTitle('histo_nominal_PT6Down')
            histogram_pt6_down.Write('histo_nominal_PT6Down')
            histogram_pt6_up.SetName('histo_nominal_PT6Up')
            histogram_pt6_up.SetTitle('histo_nominal_PT6Up')
            histogram_pt6_up.Write('histo_nominal_PT6Up')
            alpha=150000.*1000.*1000.*1000.*1000.*1000.*1000
            histogram_opt6_down,histogram_opt6_up=unequalScale(histo_nominal,"histo_nominal_OPT6",alpha,-6)
            histogram_opt6_up.SetName('histo_nominal_OPT6Up')
            histogram_opt6_up.SetTitle('histo_nominal_OPT6Up')
            histogram_opt6_up.Write('histo_nominal_OPT6Up')
            histogram_opt6_down.SetName('histo_nominal_OPT6Down')
            histogram_opt6_down.SetTitle('histo_nominal_OPT6Down')
            histogram_opt6_down.Write('histo_nominal_OPT6Down')
            #alpha=5000.*5000.*5000.
            alpha=0.
            histogram_ptn_down,histogram_ptn_up=unequalScale(histo_nominal,"histo_nominal_PTN",alpha,0)
            histogram_ptn_down.SetName('histo_nominal_PTNDown')
            histogram_ptn_down.SetTitle('histo_nominal_PTNDown')
            histogram_ptn_down.Write('histo_nominal_PTNDown')
            histogram_ptn_up.SetName('histo_nominal_PTNUp')
            histogram_ptn_up.SetTitle('histo_nominal_PTNUp')
            histogram_ptn_up.Write('histo_nominal_PTNUp')
            alpha=0.
            histogram_optn_down,histogram_optn_up=unequalScale(histo_nominal,"histo_nominal_OPTN",alpha,100)
            histogram_optn_up.SetName('histo_nominal_OPTNUp')
            histogram_optn_up.SetTitle('histo_nominal_OPTNUp')
            histogram_optn_up.Write('histo_nominal_OPTNUp')
            histogram_optn_down.SetName('histo_nominal_OPTNDown')
            histogram_optn_down.SetTitle('histo_nominal_OPTNDown')
            histogram_optn_down.Write('histo_nominal_OPTNDown')

            
        if doHerwig:
            histo_altshapeUp.Write('histo_altshapeUp_coarse')
            conditional(histo_altshapeUp)
            expanded=expandHisto(histo_altshapeUp,"herwig",binsMVV,binsMJ,minMVV,maxMVV,minMJ,maxMJ)
            if HCALbinsMVV!="":
                expanded=expandHistoBinned(histo_altshapeUp,"",xbins,binning)
            conditional(expanded)
            expanded.SetName('histo_altshapeUp')
            expanded.SetTitle('histo_altshapeUp')
            expanded.Write('histo_altshapeUp')
            finalHistograms['histo_altshapeUp'] = expanded
            
            
            alpha=1.5/float(maxMJ)
            histogram_pt_up,histogram_pt_down=unequalScale(finalHistograms['histo_altshapeUp'],"histo_altshapeUp_PT",alpha,1,2)
            conditional(histogram_pt_down)
            histogram_pt_down.SetName('histo_altshapeUp_PTDown')
            histogram_pt_down.SetTitle('histo_altshapeUp_PTDown')
            histogram_pt_down.Write('histo_altshapeUp_PTDown')
            conditional(histogram_pt_up)
            histogram_pt_up.SetName('histo_altshapeUp_PTUp')
            histogram_pt_up.SetTitle('histo_altshapeUp_PTUp')
            histogram_pt_up.Write('histo_altshapeUp_PTUp')
            
            alpha=1.5*float(minMJ)
            h1,h2=unequalScale(finalHistograms['histo_altshapeUp'],"histo_altshapeUp_OPT",alpha,-1,2)
            conditional(h1)
            h1.SetName('histo_altshapeUp_OPTUp')
            h1.SetTitle('histo_altshapeUp_OPTUp')
            h1.Write('histo_altshapeUp_OPTUp')
            conditional(h2)
            h2.SetName('histo_altshapeUp_OPTDown')
            h2.SetTitle('histo_altshapeUp_OPTDown')
            h2.Write('histo_altshapeUp_OPTDown')
            
            alpha=float(maxMJ)*float(maxMJ)
            histogram_pt2_up,histogram_pt2_down=unequalScale(finalHistograms['histo_altshapeUp'],"histo_altshapeUp_PT2",alpha,2,2)
            conditional(histogram_pt2_down)
            histogram_pt2_down.SetName('histo_altshapeUp_PT2Down')
            histogram_pt2_down.SetTitle('histo_altshapeUp_PT2Down')
            histogram_pt2_down.Write('histo_altshapeUp_PT2Down')
            conditional(histogram_pt2_up)
            histogram_pt2_up.SetName('histo_altshapeUp_PT2Up')
            histogram_pt2_up.SetTitle('histo_altshapeUp_PT2Up')
            histogram_pt2_up.Write('histo_altshapeUp_PT2Up')
            
            alpha=float(minMJ)*float(minMJ)
            histogram_opt2_up,histogram_opt2_down=unequalScale(finalHistograms['histo_altshapeUp'],"histo_altshapeUp_OPT2",alpha,-2,2)
            conditional(histogram_opt2_down)
            histogram_opt2_down.SetName('histo_altshapeUp_OPT2Down')
            histogram_opt2_down.SetTitle('histo_altshapeUp_OPT2Down')
            histogram_opt2_down.Write('histo_altshapeUp_OPT2Down')
            conditional(histogram_opt2_up)
            histogram_opt2_up.SetName('histo_altshapeUp_OPT2Up')
            histogram_opt2_up.SetTitle('histo_altshapeUp_OPT2Up')
            histogram_opt2_up.Write('histo_altshapeUp_OPT2Up')
            
            if doPythia:
                histogram_altshapeDown=mirror(finalHistograms['histo_altshapeUp'],finalHistograms['histo_nominal'],"histo_altshapeDown",2)
                conditional(histogram_altshapeDown)
                histogram_altshapeDown.SetName('histo_altshapeDown')
                histogram_altshapeDown.SetTitle('histo_altshapeDown')
                histogram_altshapeDown.Write()
                
        if doMadGraph:
            histo_altshape2Up.Write('histo_altshape2_coarse')
            conditional(histo_altshape2Up)
            expanded=expandHisto(histo_altshape2Up,"madgraph",binsMVV,binsMJ,minMVV,maxMVV,minMJ,maxMJ)
            if HCALbinsMVV!="":
                expanded=expandHistoBinned(histo_altshape2Up,"",xbins,binning)
            conditional(expanded)
            expanded.SetName('histo_altshape2Up')
            expanded.SetTitle('histo_altshape2Up')
            expanded.Write('histo_altshape2Up')
            finalHistograms['histo_altshape2Up'] = expanded
        
            alpha=1.5/float(maxMJ)
            histogram_pt_up,histogram_pt_down=unequalScale(finalHistograms['histo_altshape2Up'],"histo_altshape2_PT",alpha,1,2)
            conditional(histogram_pt_down)
            histogram_pt_down.SetName('histo_altshape2_PTDown')
            histogram_pt_down.SetTitle('histo_altshape2_PTDown')
            histogram_pt_down.Write('histo_altshape2_PTDown')
            conditional(histogram_pt_up)
            histogram_pt_up.SetName('histo_altshape2_PTUp')
            histogram_pt_up.SetTitle('histo_altshape2_PTUp')
            histogram_pt_up.Write('histo_altshape2_PTUp')
            
            alpha=1.5*float(minMJ)
            h1,h2=unequalScale(finalHistograms['histo_altshape2Up'],"histo_altshape2_OPT",alpha,-1,2)
            conditional(h1)
            h1.SetName('histo_altshape2_OPTUp')
            h1.SetTitle('histo_altshape2_OPTUp')
            h1.Write('histo_altshape2_OPTUp')
            conditional(h2)
            h2.SetName('histo_altshape2_OPTDown')
            h2.SetTitle('histo_altshape2_OPTDown')
            h2.Write('histo_altshape2_OPTDown')
            
            alpha=float(maxMJ)*float(maxMJ)
            histogram_pt2_up,histogram_pt2_down=unequalScale(finalHistograms['histo_altshape2Up'],"histo_altshape2_PT2",alpha,2,2)
            conditional(histogram_pt2_down)
            histogram_pt2_down.SetName('histo_altshape2_PT2Down')
            histogram_pt2_down.SetTitle('histo_altshape2_PT2Down')
            histogram_pt2_down.Write('histo_altshape2_PT2Down')
            conditional(histogram_pt2_up)
            histogram_pt2_up.SetName('histo_altshape2_PT2Up')
            histogram_pt2_up.SetTitle('histo_altshape2_PT2Up')
            histogram_pt2_up.Write('histo_altshape2_PT2Up')
            
            alpha=float(minMJ)*float(minMJ)
            histogram_opt2_up,histogram_opt2_down=unequalScale(finalHistograms['histo_altshape2Up'],"histo_altshape2_OPT2",alpha,-2,2)
            conditional(histogram_opt2_down)
            histogram_opt2_down.SetName('histo_altshape2_OPT2Down')
            histogram_opt2_down.SetTitle('histo_altshape2_OPT2Down')
            histogram_opt2_down.Write('histo_altshape2_OPT2Down')
            conditional(histogram_opt2_up)
            histogram_opt2_up.SetName('histo_altshape2_OPT2Up')
            histogram_opt2_up.SetTitle('histo_altshape2_OPT2Up')
            histogram_opt2_up.Write('histo_altshape2_OPT2Up')
            
            if doPythia:
                histogram_altshape2Down=mirror(finalHistograms['histo_altshape2Up'],finalHistograms['histo_nominal'],"histo_altshape2Down",2)
                conditional(histogram_altshape2Down)
                histogram_altshape2Down.SetName('histo_altshape2Down')
                histogram_altshape2Down.SetTitle('histo_altshape2Down')
                histogram_altshape2Down.Write()
                
        if doDijet:
            histo_NLO.Write('histo_NLO_coarse')
            conditional(histo_NLO)
            expanded=expandHisto(histo_NLO,"NLO",binsMVV,binsMJ,minMVV,maxMVV,minMJ,maxMJ)
            if HCALbinsMVV!="":
                expanded=expandHistoBinned(histo_NLO,"",xbins,binning)
            conditional(expanded)
            expanded.SetName('histo_NLO')
            expanded.SetTitle('histo_NLO')
            expanded.Write('histo_NLO')
            finalHistograms['histo_NLO'] = expanded
            if doPythia:
                histogram_NLODown=mirror(finalHistograms['histo_NLO'],finalHistograms['histo_nominal'],"histo_NLODown",2)
                conditional(histogram_NLODown)
                histogram_NLODown.SetName('histo_NLODown')
                histogram_NLODown.SetTitle('histo_NLODown')
                histogram_NLODown.Write()
                
  os.system('rm -r '+outdir+'_out')
  # os.system('rm -r '+outdir)
  
def makeData(template,cut,rootFile,binsMVV,binsMJ,minMVV,maxMVV,minMJ,maxMJ,factors,name,data,jobname,samples,wait=True,binning='',addOption="",sendjobs=True):
    print 
    print 'START: makeData'
    print "template = ",template
    print "cut      = ",cut
    print "rootFile = ",rootFile
    print "binsMVV  = ",binsMVV
    print "binsMJ   = ",binsMJ
    print "minMVV   = ",minMVV
    print "maxMVV   = ",maxMVV
    print "minMJ    = ",minMJ
    print "maxMJ    = ",maxMJ
    print "factor   = ",factors
    print "name     = ",name
    print "data     = ",data
    print "jobname  = ",jobname
    print "samples  = ",samples
    print 
    files = []
    sampleTypes = template.split(',')
    folders = samples.split(",")
    for folder in folders:
        for f in os.listdir(folder):
            for t in sampleTypes:
                if f.find('.root') != -1 and f.find(t) != -1: files.append(folder+f)
    print " files ",files
    NumberOfJobs= len(files)
    print " ###### total number of files ",NumberOfJobs 
    OutputFileNames = rootFile.replace(".root","")
    cmd='vvMakeData.py -d {data} -c "{cut}"  -v "jj_l1_softDrop_mass,jj_l2_softDrop_mass,jj_LV_mass" {binning} -b "{bins},{bins},{BINS}" -m "{mini},{mini},{MINI}" -M "{maxi},{maxi},{MAXI}" -f "{factors}" -n "{name}" {addOption} '.format(cut=cut,BINS=binsMVV,bins=binsMJ,MINI=minMVV,MAXI=maxMVV,mini=minMJ,maxi=maxMJ,factors=factors,name=name,data=data,infolder=samples,binning=binning,addOption=addOption)
    queue = "1nd" # give bsub queue -- 8nm (8 minutes), 1nh (1 hour), 8nh, 1nd (1day), 2nd, 1nw (1 week), 2nw 
    if sendjobs == True:
        path = os.getcwd()
        try:
            os.system("rm -r tmp"+jobname)
        except:
            print "No tmp/ directory"
        os.system("mkdir tmp"+jobname)
        try:
            os.stat("res"+jobname)
        except:
            os.mkdir("res"+jobname)
        
    


    ##### Creating and sending jobs #####
    joblist = []
    ###### loop for creating and sending jobs #####
    for x in range(1, int(NumberOfJobs)+1):
       removefile=files[x-1][files[x-1].rindex("/")+1:]
       directory = str(files[x-1]).split(removefile)[0]
       print " directory ",directory
       year=directory.split("/")[-2]
       print "year ",year
       template = str(files[x-1]).split("/")[-1]
       print "template ",template
       if sendjobs == True:
           os.system("mkdir tmp"+jobname+"/"+year+"_"+template.replace(".root",""))
           os.chdir("tmp"+jobname+"/"+year+"_"+template.replace(".root",""))
           #os.system("mkdir tmp"+jobname+"/"+str(files[x-1]).replace(".root",""))
           #os.chdir(path+"tmp"+jobname+"/"+str(files[x-1]).replace(".root",""))

           with open('job_%s_%s.sh'%(year,template.replace(".root","")), 'w') as fout:
               fout.write("#!/bin/sh\n")
               fout.write("echo\n")
               fout.write("echo\n")
               fout.write("echo 'START---------------'\n")
               fout.write("echo 'WORKDIR ' ${PWD}\n")
               if runinKA==False:
                   fout.write("source /afs/cern.ch/cms/cmsset_default.sh\n")
               else: fout.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
               fout.write("cd "+str(path)+"\n")
               fout.write("cmsenv\n")
               if runinKA==True: fout.write("mkdir -p /tmp/${USER}/\n")
               fout.write(cmd+" -o "+path+"/res"+jobname+"/"+OutputFileNames+"_"+year+"_"+template+" -s "+template+" "+directory+"\n")
               fout.write("echo 'STOP---------------'\n")
               fout.write("echo\n")
               fout.write("echo\n")
           os.system("chmod 755 job_%s.sh"%(year+"_"+template.replace(".root","")) )

           if useCondorBatch:
               os.system("mv  job_*.sh "+jobname+".sh")
               makeSubmitFileCondor(jobname+".sh",jobname,"workday")
               os.system("condor_submit submit.sub")
           else:
               os.system("bsub -q "+queue+" -o logs job_%s.sh -J %s"%(template.replace(".root",""),jobname))
               print "job nr " + str(x) + " submitted"
           os.chdir("../..")
       joblist.append("%s"%(year+"_"+template.replace(".root","")))

   
    print
    if sendjobs == True:
        print "your jobs:"
        if useCondorBatch:
            os.system("condor_q")
        else:
            os.system("bjobs")
        userName=os.environ['USER']
        if wait: waitForBatchJobs(jobname,NumberOfJobs,NumberOfJobs, userName, timeCheck)
    
    print
    print 'END: makeData'
    print
    return joblist, files

def mergeData(jobList, files,jobname,purity,rootFile,filename,name,year=""):
    
    print "Merging data from job " ,jobname
    print "Purity is " ,purity
    print "Jobs to merge :   " ,jobList
    print "Files ran over:   " ,files

    outdir = 'res'+jobname
    jobdir = 'tmp'+jobname

    resubmit, jobsPerSample,exit_flag = getNormJobs(files,jobList,outdir,purity)

    print "getJobs done"

    if exit_flag:
        submit = raw_input("The following files are missing: %s. Do you  want to resubmit the jobs to the batch system before merging? [y/n] "%resubmit)
        if submit == 'y' or submit=='Y':
            print "Resubmitting jobs:"
            jobs = reSubmit(jobdir,resubmit,jobname)
            waitForBatchJobs(jobname,len(resubmit),len(resubmit), userName, timeCheck)
            resubmit, jobsPerSample,exit_flag = getNormJobs(files,jobList,outdir,purity)
            if exit_flag:
                print "Job crashed again! Please resubmit manually before attempting to merge again"
                for j in jobs: print j
                sys.exit()
            else:
                submit = raw_input("Some files are missing. [y] == Exit without merging, [n] == continue ? ")
                if submit == 'y' or submit=='Y':
                    print "Exit without merging!"
                    sys.exit()
                else:
                    print "Continuing merge!"
            
    # read out files
    filelist = os.listdir('./'+outdir+'/')
    print "filelist ",filelist

    mg_files     = []
    pythia_files = []
    herwig_files = []
    data_files   = []
    vjets_files  = []

    for f in filelist:
     if year == "":
     #if f.find('COND2D') == -1: continue
         if f.find(purity)==-1:
             continue
         if f.find(filename)==-1:
             print " f.find(filename)==-1 -> continue "
             continue
         if f.find('QCD_HT')    != -1: mg_files.append('./res'+jobname+'/'+f)
         elif f.find('QCD_Pt_') != -1: pythia_files.append('./res'+jobname+'/'+f)
         elif f.find('JetHT')   != -1: data_files.append('./res'+jobname+'/'+f)
         elif f.find('Jets')   != -1: vjets_files.append('./res'+jobname+'/'+f)
         else: herwig_files.append('./res'+jobname+'/'+f)
     else: 
         filename = filename.replace("Run2",year)
         rootFile = rootFile.replace("Run2",year)
         if f.find(purity)==-1:
             continue
         elif f.find(year) !=-1:
              print " file ",f
              if f.find('QCD_HT')    != -1: mg_files.append('./res'+jobname+'/'+f)
              elif f.find('QCD_Pt_') != -1: pythia_files.append('./res'+jobname+'/'+f)
              elif f.find('JetHT')   != -1: data_files.append('./res'+jobname+'/'+f)
              elif f.find('Jets')   != -1: vjets_files.append('./res'+jobname+'/'+f)
              else: herwig_files.append('./res'+jobname+'/'+f)
    
    print "filename ",filename
    print "rootFile ",rootFile 
    #now hadd them
    if len(mg_files) > 0:
        cmd = 'hadd -f %s_%s_%s_altshape2.root '%(filename,name,purity)
        for f in mg_files:
         cmd += f
         cmd += ' '
        print cmd
        os.system(cmd)

    if len(herwig_files) > 0:
        cmd = 'hadd -f %s_%s_%s_altshapeUp.root '%(filename,name,purity)
        for f in herwig_files:
         cmd += f
         cmd += ' '
        print cmd
        os.system(cmd)

    if len(pythia_files) > 0:
        cmd = 'hadd -f %s '%rootFile
        for f in pythia_files:
         cmd += f
         cmd += ' '
        print cmd
        os.system(cmd)


    if len(vjets_files) > 0:
        cmd = 'hadd -f %s '%rootFile
        for f in vjets_files:
         cmd += f
         cmd += ' '
        print cmd
        os.system(cmd)

    
    if len(data_files) > 0:
        cmd = 'hadd -f JJ_%s.root '%purity
        for f in data_files:
         cmd += f
         cmd += ' '
        print cmd
        os.system(cmd)
    print "Done merging data!"

def getListOfBinsLowEdge(hist,dim):
    axis =0
    N = 0
    if dim =="x":
        axis= hist.GetXaxis()
        N = hist.GetNbinsX()
    if dim =="y":
        axis = hist.GetYaxis()
        N = hist.GetNbinsY()
    if dim =="z":
        axis = hist.GetZaxis()
        N = hist.GetNbinsZ()
    if axis==0:
        return {}
    
    mmin = axis.GetXmin()
    mmax = axis.GetXmax()
    r =[]
    for i in range(1,N+2):
        #v = mmin + i * (mmax-mmin)/float(N)
        r.append(axis.GetBinLowEdge(i))
    return r

def makePseudoData(input="JJ_nonRes_LPLP.root",kernel="JJ_nonRes_3D_LPLP.root",mc="pythia",output="JJ_LPLP.root",lumi=35900):
 print " makind pseudodata with lumi ",lumi 
 pwd = os.getcwd()
 
 ROOT.gRandom.SetSeed(123)
 
 finmc = ROOT.TFile.Open(pwd+'/'+input,'READ')
 hmcin = finmc.Get('nonRes')
 print " mc file = ",pwd+'/'+input
 print " mc events ", hmcin.GetEntries() , " and integral ", hmcin.Integral()

 findata = ROOT.TFile.Open(pwd+'/'+kernel,'READ')
 #findata.ls()
 hdata = ROOT.TH3F()
 print " data/kernel file ",pwd+'/'+kernel
 
 if   mc == 'pythia': hdata = findata.Get('histo')
 elif mc == 'herwig': hdata = findata.Get('histo_altshapeUp')
 elif mc == 'madgraph': hdata = findata.Get('histo_altshape2')
 elif mc == 'powheg': hdata = findata.Get('histo_NLO')
 
 print "  events ", hdata.GetEntries() , " and integral ", hdata.Integral()

 fout = ROOT.TFile.Open(output,'RECREATE')
 #hmcin.Scale(10.)
 hmcin.Write('nonRes')

 xbins = array("f",getListOfBinsLowEdge(hmcin,"x"))
 zbins = array("f",getListOfBinsLowEdge(hmcin,"z"))
 hout = ROOT.TH3F('datah','datah',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)
# hout.FillRandom(hdata,int(hmcin.Integral())) #irene making test
 hout.FillRandom(hdata,int(hmcin.Integral()*lumi))
 print "hout data integral ",hout.Integral()
 hout.Write('datah')
 print "Writing histograms nonRes and data to file ", output
 fout.Write()

 finmc.Close()
 findata.Close()
 fout.Close()
 

def submitCPs(samples,template,wait,jobname="CPs",rootFile="controlplots_2017.root"):
  print 
  print 'START: submitCPs'
  print "template = ",template
  print "jobname  = ",jobname
  print "samples  = ",samples
  print 
  files = []
  sampleTypes = template.split(',')
  for f in os.listdir(samples):
    for t in sampleTypes:
      if f.find(t) == -1: continue 
      if f.startswith('.'): continue
      if f.find('.root') != -1 and f.find('rawPUMC') == -1: 
        print f
        files.append(f)
  
  NumberOfJobs= len(files)
  OutputFileNames = rootFile.replace(".root","")
  cmd = "python submit_CP.py"
  queue = "8nh" # give bsub queue -- 8nm (8 minutes), 1nh (1 hour), 8nh, 1nd (1day), 2nd, 1nw (1 week), 2nw

  try: os.system("rm -r tmp"+jobname)
  except: print "No tmp/ directory"
  os.system("mkdir tmp"+jobname)
  try: os.stat("res"+jobname)
  except: os.mkdir("res"+jobname)


  ##### Creating and sending jobs #####
  joblist = []
  ###### loop for creating and sending jobs #####
  path = os.getcwd()
  for x in range(1, int(NumberOfJobs)+1):
     os.system("mkdir tmp"+jobname+"/"+str(files[x-1]).replace(".root",""))
     os.chdir("tmp"+jobname+"/"+str(files[x-1]).replace(".root",""))
     #os.system("mkdir tmp"+jobname+"/"+str(files[x-1]).replace(".root",""))
     os.chdir(path+"/tmp"+jobname+"/"+str(files[x-1]).replace(".root",""))

     with open('job_%s.sh'%files[x-1].replace(".root",""), 'w') as fout:
        fout.write("#!/bin/sh\n")
        fout.write("echo\n")
        fout.write("echo\n")
        fout.write("echo 'START---------------'\n")
        fout.write("echo 'WORKDIR ' ${PWD}\n")
        if runinKA==False:
            fout.write("source /afs/cern.ch/cms/cmsset_default.sh\n")
        else: fout.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
        fout.write("cd "+str(path)+"\n")
        fout.write("cmsenv\n")
        if runinKA==True: fout.write("mkdir -p /tmp/${USER}/\n")
        fout.write(cmd+" "+files[x-1]+" "+path+"/res"+jobname+"/"+OutputFileNames+"_"+files[x-1]+" "+samples+"\n")
        print "EXECUTING: ",cmd+" "+files[x-1]+" "+path+"/res"+jobname+"/"+OutputFileNames+"_"+files[x-1]+" "+samples+"\n"
        fout.write("echo 'STOP---------------'\n")
        fout.write("echo\n")
        fout.write("echo\n")
     os.system("chmod 755 job_%s.sh"%(files[x-1].replace(".root","")) )

     if useCondorBatch:
       os.system("mv  job_*.sh "+jobname+".sh")
       makeSubmitFileCondor(jobname+".sh",jobname,"workday")
       os.system("condor_submit submit.sub")
     else:
       os.system("bsub -q "+queue+" -o logs job_%s.sh -J %s"%(files[x-1].replace(".root",""),jobname))
     print "job nr " + str(x) + " submitted: " + files[x-1].replace(".root","")
     joblist.append("%s"%(files[x-1].replace(".root","")))
     os.chdir("../..")

  print
  print "your jobs:"
  if useCondorBatch: os.system("condor_q")
  else: os.system("bjobs")
  userName=os.environ['USER']
  if wait: waitForBatchJobs(jobname,NumberOfJobs,NumberOfJobs, userName, timeCheck)

  print
  print 'END: makeData'
  print
  return joblist, files

# def mergeCPs(template,jobname="CPs"):
#
#   dir = "res"+jobname+"/"
#
#   print "Merging data from job " ,jobname
#   # read out files
#   resDir = 'res'+jobname+'/'
#   filelist = os.listdir('./'+resDir)
#
#   samples = {}
#   sampleTypes = template.split(',')
#   samples = {}
#   sampleTypes = template.split(',')
#   for t in sampleTypes:
#     print "For sample: ",t
#     files = []
#     for f in os.listdir(dir):
#       if f.find('.root') != -1 and f.find(t) != -1 and f.find("hadd") == -1:
#          print "Adding file = ",dir+f
#          files.append(dir+f)
#       samples[t] = files
#
#   vars =[]
#   ftest = ROOT.TFile(samples[sampleTypes[0]][0],"READ")
#   for h in ftest.GetListOfKeys():
#     vars.append(h.GetName())
#   ftest.Close()
#
#   print "Doing histograms for the following variables: "
#   print [v for v in vars]; print "" ;
#   # vars = ["looseSel_Dijet_invariant_mass"]
#
#   for t in sampleTypes:
#     print "For sample: " ,t
#     histlist = []
#     for v in vars:
#       print "For variable: " ,v
#       hZero = ROOT.TH1D()
#       for i,j in enumerate(samples[t]):
#         f1 = ROOT.TFile(j,"READ")
#         print "Opened file ", f1.GetName()
#         h1 = ROOT.TH1D(f1.Get(v))
#         h1.SetFillColor(36)
#         if i==0: hZero = copy.deepcopy(h1); continue
#         ROOT.gROOT.cd()
#         hnew = h1.Clone()
#         hZero.Add(hnew)
#       hClone   = copy.deepcopy(hZero)
#       histlist.append(hClone)
#
#     outf = ROOT.TFile.Open(dir+"/out_"+t+'.root','RECREATE')
#     outf.cd()
#     for h in histlist:
#       h.Write()
#     outf.Write()
#     outf.Close()

def mergeCPs(template,jobname="CPs"):
  
  dir = "res"+jobname+"/"

  print "Merging data from job " ,jobname
  # read out files
  resDir = 'res'+jobname+'/'

  sampleTypes = template.split(',')
  for t in sampleTypes:
    cmd = "hadd %s/%s.root %s/controlplots_*%s*.root" %(resDir,t,resDir,t)
    os.system(cmd)

def makePseudoDataVjets(input,kernel,mc,output,lumi,workspace,year,purity,rescale=False,rescalefactor=1.):
 print " year ",year, " lumi ",lumi
 pwd = os.getcwd()
 pwd = "/"
 ROOT.gRandom.SetSeed(123)
 
 finmc = ROOT.TFile.Open(pwd+'/'+input,'READ')
 hmcin = finmc.Get('nonRes')

 findata = ROOT.TFile.Open(pwd+'/'+kernel,'READ')
 #findata.ls()
 hdata = ROOT.TH3F()
 
 if   mc == 'pythia': hdata = findata.Get('histo')
 elif mc == 'herwig': hdata = findata.Get('histo_altshapeUp')
 elif mc == 'madgraph': hdata = findata.Get('histo_altshape2')
 elif mc == 'powheg': hdata = findata.Get('histo_NLO')
 
 fout = ROOT.TFile.Open(output,'RECREATE')
 #hmcin.Scale(10.)
 hmcin.Write('nonRes')
 xbins = array("f",getListOfBinsLowEdge(hmcin,"x"))
 zbins = array("f",getListOfBinsLowEdge(hmcin,"z"))
 hout = ROOT.TH3F('data','data',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)
 print " hmcin Integral ",hmcin.Integral(), " Entries ",hmcin.GetEntries()
 nEventsQCD = int(hmcin.Integral()*lumi)
 print "Expected QCD events: ",nEventsQCD
 hout.FillRandom(hdata,nEventsQCD)
 
 ws_file = ROOT.TFile.Open(workspace,'READ')
 ws = ws_file.Get('w')
 ws_file.Close()
 ws.Print()

 modelWjets = ws.pdf('shapeBkg_Wjets_JJ_%s_13TeV_%s'%(purity,year))
 modelZjets = ws.pdf('shapeBkg_Zjets_JJ_%s_13TeV_%s'%(purity,year))
 category = ws.obj("CMS_channel==CMS_channel::JJ_"+purity+"_13TeV_%s"%year)

 MJ1= ws.var("MJ1");
 MJ2= ws.var("MJ2");
 MJJ= ws.var("MJJ");
 args = ROOT.RooArgSet(MJ1,MJ2,MJJ)
 ### Wjets
 print "n_exp_binJJ_"+purity+"_13TeV_%s_proc_Wjets"%year
 o_norm_wjets = ws.obj("n_exp_binJJ_"+purity+"_13TeV_%s_proc_Wjets"%year)
 hout_wjets = ROOT.TH3F('wjets','wjets',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)
 
 nEventsW = o_norm_wjets.getVal()
 if rescale==True: nEventsW=nEventsW*rescalefactor/lumi
 print "Expected W+jets events: ",nEventsW
 wjets = modelWjets.generate(args,int(nEventsW))
 if wjets!=None:
  #print signal.sumEntries()
  for i in range(0,int(wjets.sumEntries())):
   a = wjets.get(i)
   it = a.createIterator()
   var = it.Next()
   x=[]
   while var:
       x.append(var.getVal())
       var = it.Next()
   #print x
   hout_wjets.Fill(x[0],x[1],x[2])
      
 hout.Add(hout_wjets)

 ### Zjets
 print "n_exp_binJJ_"+purity+"_13TeV_%s_proc_Zjets"%year
 o_norm_zjets = ws.obj("n_exp_binJJ_"+purity+"_13TeV_%s_proc_Zjets"%year)
 hout_zjets = ROOT.TH3F('zjets','zjets',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)
 
 nEventsZ = o_norm_zjets.getVal()
 if rescale==True: nEventsZ=nEventsZ*rescalefactor/lumi
 print "Expected Z+jets events: ",nEventsZ
 zjets = modelZjets.generate(args,int(nEventsZ))
 if zjets!=None:
  #print signal.sumEntries()
  for i in range(0,int(zjets.sumEntries())):
   a = zjets.get(i)
   it = a.createIterator()
   var = it.Next()
   x=[]
   while var:
       x.append(var.getVal())
       var = it.Next()
   #print x
   hout_zjets.Fill(x[0],x[1],x[2])
      
 hout.Add(hout_zjets)
 
 fout.cd()
 hout.Write('data')
 
 print "input    ", input
 print "kernel   ", kernel
 print "mc       ", mc
 print "output   ", output
 print "lumi     ", lumi
 print "workspace", workspace
 print "year     ", year
 print "purity   ", purity
 print "Expected W+jets events: ",nEventsW
 print "Expected Z+jets events: ",nEventsZ
 print "Expected QCD events: ",nEventsQCD
 print "Writing histograms nonRes and data to file ", output

 finmc.Close()
 findata.Close()
 fout.Close()    






def makePseudoDataVjetsTT(input,input_tt,kernel,mc,output,lumi,workspace,year,purity,rescale,qcdsf,totalscale=1.):
 cat = purity
 if "VBF" in input and purity.find("VBF") == -1: cat = "VBF_"+purity
 pwd = os.getcwd()
 pwd = "/"
 ROOT.gRandom.SetSeed(123)

 finmc = ROOT.TFile.Open(pwd+'/'+input,'READ')
 hmcin = finmc.Get('nonRes')

 findata = ROOT.TFile.Open(pwd+'/'+kernel,'READ')
 #findata.ls()
 hdata = ROOT.TH3F()
 
 if   mc == 'pythia': hdata = findata.Get('histo')
 elif mc == 'herwig': hdata = findata.Get('histo_altshapeUp')
 elif mc == 'madgraph': hdata = findata.Get('histo_altshape2')
 elif mc == 'powheg': hdata = findata.Get('histo_NLO')
 
 fout = ROOT.TFile.Open(output,'RECREATE')
 #hmcin.Scale(10.)
 hmcin.Write('nonRes')
 xbins = array("f",getListOfBinsLowEdge(hmcin,"x"))
 zbins = array("f",getListOfBinsLowEdge(hmcin,"z"))
 hout = ROOT.TH3F('data','data',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)
 nEventsQCD = int(hmcin.Integral()*lumi)
 if rescale == True: 
     print "QCD will be riscale by ",qcdsf
     nEventsQCD = int(hmcin.Integral()*lumi*qcdsf)
 print "Expected QCD events: ",nEventsQCD
 hout.FillRandom(hdata,int(nEventsQCD*totalscale))
 
 print "Vjets from WS"
 ws_file = ROOT.TFile.Open(workspace,'READ')
 ws = ws_file.Get('w')
 ws_file.Close()
 #ws.Print()

 modelWjets = ws.pdf('shapeBkg_Wjets_JJ_%s_13TeV_%s'%(cat,year))
 modelZjets = ws.pdf('shapeBkg_Zjets_JJ_%s_13TeV_%s'%(cat,year))
 print " TT from WS "
 TTcon = ["Top","W","WNonResT","TNonResT","ResWResT","NonRes"]
 modelTTJets = {}
 for t in TTcon:
     modelTTJets[t]= ws.pdf('shapeBkg_TTJets'+t+'_JJ_%s_13TeV_%s'%(cat,year))
     print "model "+t+" ok"

 MJ1= ws.var("MJ1");
 MJ2= ws.var("MJ2");
 MJJ= ws.var("MJJ");
 args = ROOT.RooArgSet(MJ1,MJ2,MJJ)
 ### Wjets
 print "n_exp_binJJ_"+cat+"_13TeV_%s_proc_Wjets"%year
 o_norm_wjets = ws.obj("n_exp_binJJ_"+cat+"_13TeV_%s_proc_Wjets"%year)
 hout_wjets = ROOT.TH3F('wjets','wjets',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)

 nEventsW = o_norm_wjets.getVal()
 print "Expected W+jets events: ",nEventsW
 wjets = modelWjets.generate(args,int(nEventsW*totalscale))
 if wjets!=None:
     #print signal.sumEntries()
     for i in range(0,int(wjets.sumEntries())):
         a = wjets.get(i)
         it = a.createIterator()
         var = it.Next()
         x=[]
         while var:
             x.append(var.getVal())
             var = it.Next()
             #print x
         hout_wjets.Fill(x[0],x[1],x[2])

 hout.Add(hout_wjets)

 ### Zjets
 print "n_exp_binJJ_"+cat+"_13TeV_%s_proc_Zjets"%year
 o_norm_zjets = ws.obj("n_exp_binJJ_"+cat+"_13TeV_%s_proc_Zjets"%year)
 hout_zjets = ROOT.TH3F('zjets','zjets',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)
 
 nEventsZ = o_norm_zjets.getVal()
 print "Expected Z+jets events: ",nEventsZ
 zjets = modelZjets.generate(args,int(nEventsZ*totalscale))
 if zjets!=None:
     #print signal.sumEntries()
     for i in range(0,int(zjets.sumEntries())):
         a = zjets.get(i)
         it = a.createIterator()
         var = it.Next()
         x=[]
         while var:
             x.append(var.getVal())
             var = it.Next()
             #print x
         hout_zjets.Fill(x[0],x[1],x[2])

 hout.Add(hout_zjets)



 ### TTbar
 nEventsTT = {}
 ttjets = {}
 hout_ttjets = {}
 for t in TTcon:
     print "n_exp_binJJ_"+cat+"_13TeV_%s_proc_TTJets%s"%(year,t)
     o_norm_ttjets = ws.obj("n_exp_binJJ_"+cat+"_13TeV_%s_proc_TTJets%s"%(year,t))
     hout_ttjets[t] = ROOT.TH3F('TTJets'+t,'TTJets'+t,len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)

     nEventsTT[t] = o_norm_ttjets.getVal()
     print "Expected TTJets "+t+" events: ",nEventsTT[t]
     ttjets[t] = modelTTJets[t].generate(args,int(nEventsTT[t]*totalscale))
     if ttjets[t]!=None:
         #print signal.sumEntries()
         for i in range(0,int(ttjets[t].sumEntries())):
             a = ttjets[t].get(i)
             it = a.createIterator()
             var = it.Next()
             x=[]
             while var:
                 x.append(var.getVal())
                 var = it.Next()
                 #print x
             hout_ttjets[t].Fill(x[0],x[1],x[2])

     hout.Add(hout_ttjets[t])


 '''
 ftt = ROOT.TFile.Open(input_tt,'READ')
 hin_tt = ftt.Get('TTJets')
 hout_tt = ROOT.TH3F('data_tt','data_tt',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins) 
 hout_tt.FillRandom(hin_tt,int(hin_tt.Integral()*lumi))
 hout.Add(hout_tt)
 '''



 fout.cd()
 hout.Write('data')
 
 print "input    ", input
 print "kernel   ", kernel
 print "mc       ", mc
 print "output   ", output
 print "lumi     ", lumi
 print "workspace", workspace
 print "year     ", year
 print "purity   ", purity
 print "Expected W+jets events: ",nEventsW
 print "Expected Z+jets events: ",nEventsZ
 tttotal = 0
 for t in TTcon:
     tttotal+=nEventsTT[t]
     print "Expected TTJets "+t+" events:",nEventsTT[t]
 print "Expected total TTJets events:",tttotal
 print "Expected QCD events: ",nEventsQCD
 print "Writing histograms nonRes and data to file ", output

 finmc.Close()
 findata.Close()
 fout.Close()    

def makePseudoDataNoQCD(input_tt,output,lumi,workspace,year,purity):
 
 pwd = os.getcwd()
 pwd = "/"
 ROOT.gRandom.SetSeed(123)
 
 fout = ROOT.TFile.Open(output,'RECREATE')
 #hmcin.Scale(10.)
 ftt = ROOT.TFile.Open(input_tt,'READ')
 hin_tt = ftt.Get('TTJets')
 xbins = array("f",getListOfBinsLowEdge(hin_tt,"x"))
 zbins = array("f",getListOfBinsLowEdge(hin_tt,"z"))

 hout = ROOT.TH3F('data','data',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)
 
 
 ws_file = ROOT.TFile.Open(workspace,'READ')
 ws = ws_file.Get('w')
 ws_file.Close()
 ws.Print()

 modelWjets = ws.pdf('shapeBkg_Wjets_JJ_%s_13TeV_%i'%(purity,year))
 modelZjets = ws.pdf('shapeBkg_Zjets_JJ_%s_13TeV_%i'%(purity,year))
 category = ws.obj("CMS_channel==CMS_channel::JJ_"+purity+"_13TeV_%i"%year)

 MJ1= ws.var("MJ1");
 MJ2= ws.var("MJ2");
 MJJ= ws.var("MJJ");
 args = ROOT.RooArgSet(MJ1,MJ2,MJJ)
 ### Wjets
 print "n_exp_binJJ_"+purity+"_13TeV_%i_proc_Wjets"%year
 o_norm_wjets = ws.obj("n_exp_binJJ_"+purity+"_13TeV_%i_proc_Wjets"%year)
 hout_wjets = ROOT.TH3F('wjets','wjets',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)
 
 nEventsW = o_norm_wjets.getVal()
 print "Expected W+jets events: ",nEventsW
 wjets = modelWjets.generate(args,int(nEventsW))
 if wjets!=None:
  #print signal.sumEntries()
  for i in range(0,int(wjets.sumEntries())):
   a = wjets.get(i)
   it = a.createIterator()
   var = it.Next()
   x=[]
   while var:
       x.append(var.getVal())
       var = it.Next()
   #print x
   hout_wjets.Fill(x[0],x[1],x[2])
      
 hout.Add(hout_wjets)
 ### Zjets
 print "n_exp_binJJ_"+purity+"_13TeV_%i_proc_Zjets"%year
 o_norm_zjets = ws.obj("n_exp_binJJ_"+purity+"_13TeV_%i_proc_Zjets"%year)
 hout_zjets = ROOT.TH3F('zjets','zjets',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins)
 
 nEventsZ = o_norm_zjets.getVal()
 print "Expected Z+jets events: ",nEventsZ
 zjets = modelZjets.generate(args,int(nEventsZ))
 if zjets!=None:
  #print signal.sumEntries()
  for i in range(0,int(zjets.sumEntries())):
   a = zjets.get(i)
   it = a.createIterator()
   var = it.Next()
   x=[]
   while var:
       x.append(var.getVal())
       var = it.Next()
   #print x
   hout_zjets.Fill(x[0],x[1],x[2])
      
 hout.Add(hout_zjets)
 
 hout_tt = ROOT.TH3F('data_tt','data_tt',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins) 
 hout_tt.FillRandom(hin_tt,int(hin_tt.Integral()*lumi))
 hout.Add(hout_tt)
 
 fout.cd()
 hout.Write('data')
 
 print "output   ", output
 print "lumi     ", lumi
 print "workspace", workspace
 print "year     ", year
 print "purity   ", purity
 print "Expected W+jets events: ",nEventsW
 print "Expected Z+jets events: ",nEventsZ
 print "Expected TTJets events:",int(hin_tt.Integral()*lumi)
 print "Writing histograms nonRes and data to file ", output

 fout.Close()    

def makePseudoDataTT(input_tt,output,lumi,year,purity,hist):

 pwd = os.getcwd()
 pwd = "/"
 ROOT.gRandom.SetSeed(123)
 fout = ROOT.TFile.Open(output,'RECREATE')
 
 ftt = ROOT.TFile.Open(input_tt,'READ')
 hin_tt = ftt.Get(hist)
 xbins = array("f",getListOfBinsLowEdge(hin_tt,"x"))
 zbins = array("f",getListOfBinsLowEdge(hin_tt,"z"))

 hout_tt = ROOT.TH3F('data','data',len(xbins)-1,xbins,len(xbins)-1,xbins,len(zbins)-1,zbins) 
 hout_tt.FillRandom(hin_tt,int(hin_tt.Integral()*lumi))
 
 fout.cd()
 hout_tt.Write('data')
 

 print "output   ", output
 print "lumi     ", lumi
 print "year     ", year
 print "purity   ", purity
 print "Expected "+hist+" events:",int(hin_tt.Integral()*lumi)
 print "Writing histograms nonRes and data to file ", output


 ftt.Close()
 fout.Close()    
