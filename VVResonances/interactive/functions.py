import os,sys

class AllFunctions():

 def __init__(self,parameters):
  self.cuts = parameters[0]
  self.minMVV = parameters[1]
  self.maxMVV = parameters[2]
  self.minMX = parameters[3]
  self.maxMX = parameters[4]
  self.binsMVV = parameters[5]
  self.HCALbinsMVV = parameters[6]
  self.samples = parameters[7]
  self.categories = parameters[8]
  self.minMJ = parameters[9]
  self.maxMJ = parameters[10]
  self.binsMJ = parameters[11]
  self.lumi = parameters[12]
  self.submitToBatch = parameters[13]


  self.printAllParameters()
  
 def makeSignalShapesMVV(self,filename,template,fixParsMVV,addcuts="1"):
  if 'VBF' in template: cut='*'.join([self.cuts['common_VBF'],self.cuts['acceptanceMJ'],addcuts])
  else: cut='*'.join([self.cuts['common_VV'],self.cuts['acceptanceMJ'],addcuts])
  ##the parameters to be fixed should be optimized
  rootFile=filename+"_MVV.root"
  fixPars = fixParsMVV["fixPars"]  
  cmd='vvMakeSignalMVVShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "jj_LV_mass" --fix "{fixPars}"   -m {minMVV} -M {maxMVV} --minMX {minMX} --maxMX {maxMX} {samples} --addcut "{addcut}"  '.format(template=template,cut=cut,rootFile=rootFile,minMVV=self.minMVV,maxMVV=self.maxMVV,minMX=self.minMX,maxMX=self.maxMX,fixPars=fixPars,samples=self.samples,addcut=addcuts,binsMVV=self.HCALbinsMVV)
  print cmd
  os.system(cmd)
  jsonFile=filename+"_MVV.json"
  cmd='vvMakeJSON.py  -o "{jsonFile}" -g {pols} -m {minMX} -M {maxMX} {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile,minMX=self.minMX,maxMX=self.maxMX,pols=fixParsMVV["pol"])
  print "########## Going to make json ######" 
  print cmd
  os.system(cmd)


 def makeSignalShapesMJ(self,filename,template,leg,fixPars,addcuts="1"):
   cut = '*'.join([self.cuts['common'],addcuts])

   rootFile=filename+"_MJ"+leg+"_NP.root" 
   cmd='vvMakeSignalMJShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "jj_{leg}_softDrop_mass" -m {minMJ} -M {maxMJ} -f "{fixPars}" --minMX {minMX} --maxMX {maxMX} {samples} '.format(template=template,cut=cut,rootFile=rootFile,leg=leg,minMJ=self.minMJ,maxMJ=self.maxMJ,minMX=self.minMX,maxMX=self.maxMX,fixPars=fixPars["NP"]["fixPars"],samples=self.samples)
   os.system(cmd)
    
   jsonFile=filename+"_MJ"+leg+"_NP.json"
   cmd='vvMakeJSON.py  -o "{jsonFile}" -g {pols} -m {minMX} -M {maxMX} {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile,minMX=self.minMX,maxMX=self.maxMX,pols=fixPars["NP"]["pol"])
   os.system(cmd)

 def makeSignalShapesMVV_cat(self,filename,template,fixParsMVV,addcuts="1"):
  for cat in self.categories:
   if 'VBF' in template: cut='*'.join([self.cuts['common_VBF'],self.cuts['acceptanceMJ'],self.cuts[cat],addcuts])
   else: cut='*'.join([self.cuts['common_VV'],self.cuts['acceptanceMJ'],self.cuts[cat],addcuts])
   ##the parameters to be fixed should be optimized
   rootFile=filename+"_MVV_"+cat+".root"
   fixPars = fixParsMVV["fixPars"]
   cmd='vvMakeSignalMVVShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "jj_LV_mass" --fix "{fixPars}"   -m {minMVV} -M {maxMVV} --minMX {minMX} --maxMX {maxMX} {samples} --addcut "{addcut}"  '.format(template=template,cut=cut,rootFile=rootFile,minMVV=self.minMVV,maxMVV=self.maxMVV,minMX=self.minMX,maxMX=self.maxMX,fixPars=fixPars,samples=self.samples,addcut=addcuts,binsMVV=self.HCALbinsMVV)
   print cmd
   os.system(cmd)
   jsonFile=filename+"_MVV_"+cat+".json"
   cmd='vvMakeJSON.py  -o "{jsonFile}" -g {pols} -m {minMX} -M {maxMX} {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile,minMX=self.minMX,maxMX=self.maxMX,pols=fixParsMVV["pol"])
   print "########## Going to make json ######"
   print cmd
   os.system(cmd)


 def makeSignalShapesMJ_cat(self,filename,template,leg,fixPars,addcuts="1"):
  for cat in self.categories:
   cut = '*'.join([self.cuts['common'],addcuts,self.cuts[cat]])

   rootFile=filename+"_MJ"+leg+"_"+cat+".root"
   cmd='vvMakeSignalMJShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "jj_{leg}_softDrop_mass" -m {minMJ} -M {maxMJ} -f "{fixPars}" --minMX {minMX} --maxMX {maxMX} {samples} '.format(template=template,cut=cut,rootFile=rootFile,leg=leg,minMJ=self.minMJ,maxMJ=self.maxMJ,minMX=self.minMX,maxMX=self.maxMX,fixPars=fixPars["NP"]["fixPars"],samples=self.samples)
   os.system(cmd)

   jsonFile=filename+"_MJ"+leg+"_"+cat+".json"
   cmd='vvMakeJSON.py  -o "{jsonFile}" -g {pols} -m {minMX} -M {maxMX} {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile,minMX=self.minMX,maxMX=self.maxMX,pols=fixPars["NP"]["pol"])
   os.system(cmd)


 def makeSignalYields(self,filename,template,branchingFraction,functype="pol5",doTau=False):
  
  for c in self.categories:
   if 'VBF' in c: cut = "*".join([self.cuts[c.replace('VBF_','')],self.cuts['common_VBF'],self.cuts['acceptance']])
   else: cut = "*".join([self.cuts[c],self.cuts['common_VV'],self.cuts['acceptance']]) #,str(sfP[c])])
   yieldFile=filename+"_"+c+"_yield"
   fnc = functype
   cmd='vvMakeSignalYields.py -s {template} -c "{cut}" -o {output} -V "jj_LV_mass" -m {minMVV} -M {maxMVV} -f {fnc} -b {BR} --minMX {minMX} --maxMX {maxMX} {samples} '.format(template=template, cut=cut, output=yieldFile,minMVV=self.minMVV,maxMVV=self.maxMVV,fnc=fnc,BR=branchingFraction,minMX=self.minMX,maxMX=self.maxMX,samples=self.samples)
   print "&&&&&&&&&&&&&&&&&&&&&&&&   command         &&&&&&&&&&&&&&&&&&&&&&&&&&&"
   if doTau==True: cmd = cmd+" --tau"
   print cmd
   os.system(cmd)

 def makeDetectorResponse(self,name,filename,template,addCut="1",jobName="DetPar",wait=True):
 
   cut='*'.join([self.cuts['common'],addCut,self.cuts['acceptanceGEN'],self.cuts['looseacceptanceMJ']])
   resFile=filename+"_"+name+"_detectorResponse.root"	    
   print "Saving detector resolution to file: " ,resFile
   #bins = "200,250,300,350,400,450,500,600,700,800,900,1000,1200,1500,1800,2200,2600,3000,3400,3800,5000"#4200,4600,5000,7000"#TODO: The last three bins are empty, remove next iteration!
   bins = "200,250,300,350,400,450,500,600,700,800,900,1000,1200,1500,1800,2200,2600,3000,5000"#4200,4600,5000,7000"#TODO: The last three bins are empty, remove next iteration!
   if self.submitToBatch:
    from modules.submitJobs import Make2DDetectorParam,merge2DDetectorParam 
    jobList, files = Make2DDetectorParam(resFile,template,cut,self.samples,jobName,bins)
    if wait: merge2DDetectorParam(jobList,files,resFile,bins,jobName,template)
   else:
    cmd='vvMake2DDetectorParam.py  -o "{rootFile}" -s "{template}" -c "{cut}"  -v "jj_LV_mass,jj_l1_softDrop_mass,jj_l2_softDrop_mass"  -g "jj_gen_partialMass,jj_l1_gen_softDrop_mass,jj_l1_gen_pt,jj_l2_gen_softDrop_mass,jj_l2_gen_pt"  -b {bins} -d  {samples} '.format(rootFile=resFile,template=template,cut=cut,minMVV=self.minMVV,maxMVV=self.maxMVV,tag=name,bins=bins,samples=self.samples)
    print cmd
    os.system(cmd)
   
   print "Done with ",resFile

 def makeMinorBkgShapesMVV(self,name,filename,template,addcuts="1",label="",corrFactorW=1.,corrFactorZ=1.,VBF=False):
    #for c in self.categories:
        '''
        if VBF==True:
            cut='*'.join([self.cuts['common_VBF'],self.cuts['acceptanceMJ'],addcuts,self.cuts[c]])
        else:
            cut='*'.join([self.cuts['common_VV'],self.cuts['acceptanceMJ'],addcuts,self.cuts[c]])
        rootFile=filename+"_"+name+"_MVV_"+c+".json"
        '''
        if VBF==True:
            cut='*'.join([self.cuts['common_VBF'],self.cuts['acceptanceMJ'],addcuts])
        else:
            cut='*'.join([self.cuts['common_VV'],self.cuts['acceptanceMJ'],addcuts])
        rootFile=filename+"_"+name+"_MVV_NP.json"
        print template
        cmd='vvMakeMJJShapesMinorBkg.py {samples} -s "{template}" -c "{cut}"  -o "{outFile}"  {binsMVV}  -x {minMVV} -X {maxMVV}  --corrFactorW {corrFactorW} --corrFactorZ {corrFactorZ} '.format(template=template,cut=cut,outFile=rootFile,minMVV=self.minMVV,maxMVV=self.maxMVV,samples=self.samples,binsMVV=self.HCALbinsMVV,corrFactorW=corrFactorW,corrFactorZ=corrFactorZ)
        os.system(cmd)
 

 def makeBackgroundShapesMVVKernel(self,name,filename,template,addCut="1",jobName="1DMVV",wait=True,corrFactorW=1,corrFactorZ=1,sendjobs=True,doFitTempl=False,doTau=False,doKfactors=False):
  command="vvMake1DMVVTemplateWithKernels.py"
  if name.find("TT")!=-1 and doTau ==False:
   command='vvMake1DMVVTemplateTTbar.py'
   if doFitTempl ==True : command ='vvMake1DMVVfitTemplateTTbar.py'
  if (name.find("WJets")!=-1 or name.find("ZJets")!=-1) and doKfactors==True:
   print "!!!!!! using k-factor templates implementation!!! "
   command = "vvMake1DMVVTemplateVjets.py"
  if (name.find("WJets")!=-1 or name.find("ZJets")!=-1) and doFitTempl==True:
   command = "vvMake1DMVVfitTemplateVjets.py"
  if (name.find("WZ")!=-1 or name.find("ZZ")!=-1) and doFitTempl==True:
   command = "vvMake1DMVVfitTemplateVZ.py"
  print command

  pwd = os.getcwd()
  print "samples ",self.samples
  for c in self.categories:
   period=filename.split("_")[1]  
   jobname = jobName+"_"+period+"_"+c
   print "Working on purity: ", c
   print "Working on period: ", period
   
   resFile=filename+"_nonRes_detectorResponse.root"
   print "Reading " ,resFile

   rootFile = filename+"_"+name+"_MVV_"+c+".root"
   print "Saving to ",rootFile
   
   if 'VBF' in c: cut='*'.join([self.cuts['common_VBF'],self.cuts[c.replace('VBF_','')],addCut,self.cuts['acceptanceGEN'],self.cuts['looseacceptanceMJ']])
   else: cut='*'.join([self.cuts['common_VV'],self.cuts[c],addCut,self.cuts['acceptanceGEN'],self.cuts['looseacceptanceMJ']])
   if (name.find("TT")!=-1 or name.find("WJets")!=-1 or name.find("ZJets")!=-1) and doFitTempl==True:
    print " ****** using acceptance selection for fits!!! ********"
    if 'VBF' in c: cut='*'.join([self.cuts['common_VBF'],self.cuts[c.replace('VBF_','')],addCut,self.cuts['acceptance']])
    else: cut='*'.join([self.cuts['common_VV'],self.cuts[c],addCut,self.cuts['acceptance']])

   folders=[]
   folders= self.samples.split(',')
   smp= ""
   for s in folders:
    smp+=pwd +"/"+s
    if s != folders[-1]: smp+=","
   print " smp ",smp
   if self.submitToBatch:
    if name.find("Jets") == -1: template += ",QCD_Pt-,QCD_HT" 
    #if name.find("Jets") == -1: template += ",QCD_HT" #irene because QCD Pt- should go without spike killer!!
    #print " ***************    not doing QCD_HT & QCD_Pt- because not ready yet!! *************** "
    from modules.submitJobs import Make1DMVVTemplateWithKernels,merge1DMVVTemplate
    jobList, files = Make1DMVVTemplateWithKernels(rootFile,template,cut,resFile,self.binsMVV,self.minMVV,self.maxMVV,smp,jobname,wait,self.HCALbinsMVV,"",sendjobs,doKfactors) #irene
    if wait: merge1DMVVTemplate(jobList,files,jobname,c,self.binsMVV,self.minMVV,self.maxMVV,self.HCALbinsMVV,name,filename,doKfactors,doTau)
   else:
    cmd=command+' -H "x" -o "{rootFile}" -s "{template}" -c "{cut}"  -v "jj_gen_partialMass" -b {binsMVV}  -x {minMVV} -X {maxMVV} -r {res} {directory} --corrFactorW {corrFactorW} --corrFactorZ {corrFactorZ} '.format(rootFile=rootFile,template=template,cut=cut,res=resFile,binsMVV=self.binsMVV,minMVV=self.minMVV,maxMVV=self.maxMVV,corrFactorW=corrFactorW,corrFactorZ=corrFactorZ,directory=smp)
    cmd = cmd+self.HCALbinsMVV
    os.system(cmd)    

 
 def makeBackgroundShapesMVVConditional(self,name,filename,template,leg,addCut="",jobName="2DMVV",wait=True):

  pwd = os.getcwd()  
  period=filename.split("_")[1]

  for c in self.categories:
   print "Working on period: ", period
   print " Working on purity: ", c

   jobname = jobName+"_"+period+"_"+c

   resFile=filename+"_"+name+"_detectorResponse.root"
   rootFile=filename+"_"+name+"_COND2D_"+c+"_"+leg+".root"       
   print "Reading " ,resFile
   print "Saving to ",rootFile
   
   if 'VBF' in c: cut='*'.join([self.cuts['common_VBF'],self.cuts[c.replace('VBF_','')],addCut])#,cuts['acceptanceGEN'],cuts['looseacceptanceMJ']])
   else: cut='*'.join([self.cuts['common_VV'],self.cuts[c],addCut])#,cuts['acceptanceGEN'],cuts['looseacceptanceMJ']])

   folders=[]
   folders= self.samples.split(',')
   smp= ""
   for s in folders:
    smp+=pwd +"/"+s
    if s != folders[-1]: smp+=","
   print " smp ",smp

 
   if self.submitToBatch:
    if name.find("VJets")== -1: template += ",QCD_Pt-,QCD_HT"
    #if name.find("VJets")== -1: template += ",QCD_HT"  #irene because QCD Pt- should go without spike killer!! 
    from modules.submitJobs import Make2DTemplateWithKernels,merge2DTemplate
    jobList, files = Make2DTemplateWithKernels(rootFile,template,cut,leg,self.binsMVV,self.minMVV,self.maxMVV,resFile,self.binsMJ,self.minMJ,self.maxMJ,smp,jobname,wait,self.HCALbinsMVV) #,addOption) #irene
    if wait: merge2DTemplate(jobList,files,jobname,c,leg,self.binsMVV,self.binsMJ,self.minMVV,self.maxMVV,self.minMJ,self.maxMJ,self.HCALbinsMVV,name,filename)
   else:
      cmd='vvMake2DTemplateWithKernels.py -o "{rootFile}" -s "{template}" -c "{cut}"  -v "jj_{leg}_gen_softDrop_mass,jj_gen_partialMass"  -b {binsMJ} -B {binsMVV} -x {minMJ} -X {maxMJ} -y {minMVV} -Y {maxMVV}  -r {res} {samples}'.format(rootFile=rootFile,template=template,cut=cut,leg=leg,binsMVV=self.binsMVV,minMVV=self.minMVV,maxMVV=self.maxMVV,res=resFile,binsMJ=self.binsMJ,minMJ=self.minMJ,maxMJ=self.maxMJ,samples=smp)
      cmd=cmd+self.HCALbinsMVV
      os.system(cmd)


 def mergeBackgroundShapes(self,name,filename,makesingle):

  for c in self.categories:

   inputx=filename+"_"+name+"_COND2D_"+c+"_l1.root"
   inputy=filename+"_"+name+"_COND2D_"+c+"_l2.root"
   inputz=filename+"_"+name+"_MVV_"+c+".root"  


   rootFile=filename+"_"+name+"_3D_"+c+".root"
   
   print "Reading " ,inputx
   print "Reading " ,inputy
   print "Reading " ,inputz
   print "Saving to ",rootFile 
   
   cmd='vvMergeHistosToPDF3D.py -i "{inputx}" -I "{inputy}" -z "{inputz}" -o "{rootFile}"'.format(rootFile=rootFile,inputx=inputx,inputy=inputy,inputz=inputz)
   print "going to execute "+str(cmd)
   os.system(cmd)
   
   if filename.find("Run2") != -1 and makesingle:
      years = ["2016","2017","2018"]
      for year in years:
       print " doing also single year ",year
       newfilename=filename.replace("Run2",year)


       inputx=newfilename+"_"+name+"_COND2D_"+c+"_l1.root"
       inputy=newfilename+"_"+name+"_COND2D_"+c+"_l2.root"
       inputz=newfilename+"_"+name+"_MVV_"+c+".root"


       rootFile=newfilename+"_"+name+"_3D_"+c+".root"

       print "Reading " ,inputx
       print "Reading " ,inputy
       print "Reading " ,inputz
       print "Saving to ",rootFile

       cmd='vvMergeHistosToPDF3D.py -i "{inputx}" -I "{inputy}" -z "{inputz}" -o "{rootFile}"'.format(rootFile=rootFile,inputx=inputx,inputy=inputy,inputz=inputz)
       print "going to execute "+str(cmd)
       os.system(cmd)

   if filename.find("1617") != -1 and makesingle:
      years = ["2016","2017"]
      for year in years:
       print " doing also single year ",year
       newfilename=filename.replace("1617",year)


       inputx=newfilename+"_"+name+"_COND2D_"+c+"_l1.root"
       inputy=newfilename+"_"+name+"_COND2D_"+c+"_l2.root"
       inputz=newfilename+"_"+name+"_MVV_"+c+".root"


       rootFile=newfilename+"_"+name+"_3D_"+c+".root"

       print "Reading " ,inputx
       print "Reading " ,inputy
       print "Reading " ,inputz
       print "Saving to ",rootFile

       cmd='vvMergeHistosToPDF3D.py -i "{inputx}" -I "{inputy}" -z "{inputz}" -o "{rootFile}"'.format(rootFile=rootFile,inputx=inputx,inputy=inputy,inputz=inputz)
       print "going to execute "+str(cmd)
       os.system(cmd)



   #print "Adding trigger shape uncertainties"
   #if useTriggerWeights: 
   #   cmd='vvMakeTriggerShapes.py -i "{rootFile}"'.format(rootFile=rootFile)
   #   os.system(cmd)

 def makeSF(self,template,isSignal=False,isVV=False,isFour=False,useTau=False):

  pwd = os.getcwd()
  folders=[]
  folders= self.samples.split(',')
  sam= ""
  for s in folders:
   sam+=pwd +"/"+s
   if s != folders[-1]: sam+=","
  print "Using files in" , sam

  print " TEMPLATE ",template

  print "making categorization "
  dirs = sam.split(",")
  for d in dirs:
   print " dir ",d
   for filen in os.listdir(d):
    if filen.find(".")==-1:
     print "in "+str(filen)+"the separator . was not found. -> continue!"
     continue
    samplelist = template.split(",")
    #print samplelist
    for sampleType in samplelist:
     if filen.find(sampleType)!=-1 and filen.find(".root")!=-1:
      if filen.find("VBF")!=-1 and sampleType.find("VBF")==-1: continue
      print " sample ",sampleType
      if isSignal == True:
       print " is signal !"
       fnameParts=filen.split('.')
       fname=fnameParts[0]
       mass = float(fname.split('_')[-1])
       if mass <self. minMX or mass > self.maxMX: continue
       else: sampleType=sampleType+"narrow_"+fname.split('_')[-1]

      cmd='vvMakeCategorisation.py -s "{sample}" -d "{directory}" -y "{year}"'.format(sample=sampleType,directory=d,year=d.split('/')[-2])
      if isVV == True:
       cmd = cmd+" --vv"
       if useTau: cmd=cmd+" --tau"
      elif isFour == True: cmd = cmd+" --four"
      print " going to execute ",cmd
      os.system(cmd)
      #else: print sampleType+" NOT FOUND IN "+filen


 def makeMigrationUnc(self,template,outname,year,isSignal=False,isVV=False,isFour=False,directory='migrationunc/'):
  print "Using files in" , directory
  print " TEMPLATE ",template
  print "making migration uncertainties "
  cmd='vvMakeMigrationUncertainties.py -s "{sample}" -d "{directory}" -y "{year}" -o "{outname}" '.format(sample=template,directory=directory,year=year,outname=outname)
  if isSignal ==True:
   cmd+=' --isSignal {isSignal}'.format(isSignal=isSignal)
  if isVV==True:
   cmd+=" --vv "
  elif isFour==True:
   cmd+=" --four "
  print " going to execute ",cmd
  os.system(cmd)


 def makeNormalizations(self,name,filename,template,data=0,addCut='1',jobName="nR",makesingle=False,factors="1",sendjobs=True,doTau=False,wait=True): #,HPSF=1.,LPSF=1.):

  pwd = os.getcwd()
  period=filename.split("_")[1]
  folders=[]
  folders= self.samples.split(',')
  sam= ""
  for s in folders:
   sam+=pwd +"/"+s
   if s != folders[-1]: sam+=","
  print "Using files in" , sam
  addoption = ""
  if doTau == True: addoption = " --tau"
  for c in self.categories:
   jobname = jobName+"_"+period+"_"+c
   rootFile=filename+"_"+name+"_"+c+".root"
   print "Saving to ",rootFile  
   
   if 'VBF' in c: cut='*'.join([self.cuts['common_VBF'],self.cuts[c.replace('VBF_','')],addCut,self.cuts['acceptance']])
   else: cut='*'.join([self.cuts['common_VV'],self.cuts[c],addCut,self.cuts['acceptance']])

   if self.submitToBatch:
       if name.find("nonRes")!= -1: template += ",QCD_Pt-,QCD_HT"
       #if name.find("nonRes")!= -1: template += ",QCD_HT"  #irene because QCD Pt- should go without spike killer!! 
       #print " ***************    not doing QCD_HT &  QCD_Pt- because not ready yet!! *************** "
       from modules.submitJobs import makeData,mergeData
       jobList, files = makeData(template,cut,rootFile,self.binsMVV,self.binsMJ,self.minMVV,self.maxMVV,self.minMJ,self.maxMJ,factors,name,data,jobname,sam,wait,self.HCALbinsMVV,addoption,sendjobs) #irene
       wait = True
       if sendjobs == False:
        wait = False
        mergeData(jobList, files,jobname,c,rootFile,filename,name)
       if wait: mergeData(jobList, files,jobname,c,rootFile,filename,name)
       if makesingle and period == "Run2":
             print " ########    making norms also for single years ##############"
             years = ["2016","2017","2018"]
             for year in years:
                print " year ",year
                newjoblist = []
                newfiles   = []
                for job in jobList:
                 if job.split("_")[0].replace("'","").replace(" ","") == year :
                  print " condition ",job.split('_')[0]," = ",year, " verified "
                  newjoblist.append(job.replace("'","").replace(" ",""))
                for f in files: 
                 if f.split("/")[-2] == year :
                  newfiles.append(f.replace("'","").replace(" ",""))
                mergeData(newjoblist, newfiles,jobname,c,rootFile,filename,name,year)
       if makesingle and period == "1617":
             print " ########    making norms also for single years ##############"
             years = ["2016","2017"]
             for year in years:
                print " year ",year
                newjoblist = []
                newfiles   = []
                for job in jobList:
                 if job.split("_")[0].replace("'","").replace(" ","") == year :
                  print " condition ",job.split('_')[0]," = ",year, " verified "
                  newjoblist.append(job.replace("'","").replace(" ",""))
                for f in files:
                 if f.split("/")[-2] == year :
                  newfiles.append(f.replace("'","").replace(" ",""))
                  filename2 = filename.replace("1617",year)
                  rootFile2 = rootFile.replace("1617",year)
                mergeData(newjoblist, newfiles,jobname,c,rootFile2,filename2,name,year)
   else:
        if filename.find("gen")!=-1:
            cmd='vvMakeData.py -s "{template}" -d {data} -c "{cut}"  -o "{rootFile}" -v "jj_l1_gen_softDrop_mass,jj_l2_gen_softDrop_mass,jj_gen_partialMass" -b "{bins},{bins},{BINS}" -m "{mini},{mini},{MINI}" -M "{maxi},{maxi},{MAXI}" -f {factors} -n "{name}" {samples}'.format(template=template,cut=cut,rootFile=rootFile,BINS=self.binsMVV,bins=self.binsMJ,MINI=self.minMVV,MAXI=self.maxMVV,mini=self.minMJ,maxi=self.maxMJ,factors=factors,name=name,data=data,samples=sam)
        else:
            cmd='vvMakeData.py -s "{template}" -d {data} -c "{cut}"  -o "{rootFile}" -v "jj_l1_softDrop_mass,jj_l2_softDrop_mass,jj_LV_mass" -b "{bins},{bins},{BINS}" -m "{mini},{mini},{MINI}" -M "{maxi},{maxi},{MAXI}" -f "{factors}" -n "{name}" {samples}'.format(template=template,cut=cut,rootFile=rootFile,BINS=self.binsMVV,bins=self.binsMJ,MINI=self.minMVV,MAXI=self.maxMVV,mini=self.minMJ,maxi=self.maxMJ,factors=factors,name=name,data=data,samples=sam)
        cmd=cmd+self.HCALbinsMVV
        if doTau == True: cmd = cmd+" --tau"
        print "going to execute command "+str(cmd)
        print " "
        os.system(cmd)


 def fitVJets(self,filename,template,Wxsec=1,Zxsec=1):
   for c in self.categories:
     if 'VBF' in c: cut='*'.join([self.cuts['common_VBF'],self.cuts[c.replace('VBF_','')],self.cuts['acceptance']])
     else: cut='*'.join([self.cuts['common_VV'],self.cuts[c],self.cuts['acceptance']])
     rootFile=filename+"_"+c+".root"
     pwd = os.getcwd()
     folders=[]
     folders= self.samples.split(',')
     directory= ""
     for s in folders:
      if filename.find("Run2")!=-1:
       if s.find("2016")!=-1: continue #we do not have Wjets and Zjets sample for 2016, so it is useless to run twice on the same files when running on full Run2, 2017 is rescaled by 2016+2017 lumi
      directory+=pwd +"/"+s
      if s != folders[-1]: directory+=","
      print "Using files in" , directory

     print self.cuts["acceptance"]
     fixPars="1"  #"n:0.8,alpha:1.9"
     cmd='vvMakeVjetsShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -m {minMJ} -M {maxMJ} --store "{filename}_{purity}.py" --minMVV {minMVV} --maxMVV {maxMVV} {addOption} --corrFactorW {Wxsec} --corrFactorZ {Zxsec} {samples} '.format(template=template,cut=cut,rootFile=rootFile,minMJ=self.minMJ,maxMJ=self.maxMJ,filename=filename,purity=c,minMVV=self.minMVV,maxMVV=self.maxMVV,addOption="",Wxsec=Wxsec,Zxsec=Zxsec,samples=directory)
     cmd+=self.HCALbinsMVV
     print "going to execute command: "
     print str(cmd)
     os.system(cmd)

 def fitVZJets(self,filename,template,leg,fixPars,addcuts="1"):
   for c in self.categories:
     if 'VBF' in c: cut='*'.join([self.cuts['common_VBF'],self.cuts[c.replace('VBF_','')],self.cuts['acceptance']])
     else: cut='*'.join([self.cuts['common_VV'],self.cuts[c],self.cuts['acceptance']])
     rootFile=filename+"_MJ"+leg+"_NP.root"
     pwd = os.getcwd()
     folders=[]
     folders= self.samples.split(',')
     directory= ""
     for s in folders:
      directory+=pwd +"/"+s
      if s != folders[-1]: directory+=","
      print "Using files in" , directory

     print self.cuts["acceptance"]
     fixPars="1"  #"n:0.8,alpha:1.9"
     #fixPars=fixPars["NP"]["fixPars"]
     cmd='vvMakeVZShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "jj_{leg}_softDrop_mass"  -m {minMJ} -M {maxMJ} -f "{fixPars}"  --store "{filename}_{purity}.py" --minMVV {minMVV} --maxMVV {maxMVV} {addOption} {samples} '.format(template=template,cut=cut,rootFile=rootFile,leg=leg,minMJ=self.minMJ,maxMJ=self.maxMJ,filename=filename,purity="NP",minMVV=self.minMVV,maxMVV=self.maxMVV,addOption="",samples=directory,fixPars=fixPars)
     cmd+=self.HCALbinsMVV
     print "going to execute command: "
     print str(cmd)
     os.system(cmd)


 def fitTT(self,filename,template,xsec=1,prelim="prelim"):
   for c in self.categories:
     print("\r"+"Fitting ttbar in category %s for template %s" %(c,template))
     if 'VBF' in c: 
       cut='*'.join([self.cuts['common_VBF'],self.cuts[c.replace('VBF_','')],self.cuts['acceptance']])
     else: 
       cut='*'.join([self.cuts['common_VV'],self.cuts[c],self.cuts['acceptance']])
     outname=filename+"_"+c
     pwd = os.getcwd()
     folders=[]
     folders= self.samples.split(',')
     directory= ""
     for s in folders:
      directory+=pwd +"/"+s
      if s != folders[-1]: directory+=","
     print "Using files in" , directory

     fixPars="1" 
     cmd='vvMakeTTShapes.py -s "{template}" -c "{cut}"  -o "{outname}" -m {minMJ} -M {maxMJ} --store "{filename}_{purity}.py" --minMVV {minMVV} --maxMVV {maxMVV} {addOption} --corrFactor {xsec} {samples} --prelim {prelim}'.format(template=template,cut=cut,outname=outname,minMJ=self.minMJ,maxMJ=self.maxMJ,filename=filename,purity=c,minMVV=self.minMVV,maxMVV=self.maxMVV,addOption="",xsec=xsec, samples=directory, prelim=prelim)
     cmd+=self.HCALbinsMVV
     os.system(cmd)
     

 def mergeKernelJobs(self,name,filename,makesingle):
    period=filename.split("_")[1]     
    for c in self.categories:
        jobList = []
        files   = []
        with open("tmp1D_%s_%s_joblist.txt"%(period,c),'r') as infile:
            for line in infile:
                if line.startswith("job"):
                    for job in line.split("[")[1].split("]")[0].split(","):
                        jobList.append(job.replace("'","").replace(" ",""))
                if line.startswith("file"):
                    for job in line.split("[")[1].split("]")[0].split(","):
                        files.append(job.replace("'","").replace(" ",""))
        from modules.submitJobs import merge1DMVVTemplate
        merge1DMVVTemplate(jobList,files,"1D"+"_"+period+"_"+c,c,self.binsMVV,self.minMVV,self.maxMVV,self.HCALbinsMVV,name,filename) #,self.samples)
      
        jobList = []
        files   = []
        with open("tmp2Dl1_%s_%s_joblist.txt"%(period,c),'r') as infile:
            for line in infile:
                if line.startswith("job"):
                    for job in line.split("[")[1].split("]")[0].split(","):
                        jobList.append(job.replace("'","").replace(" ",""))
                if line.startswith("file"):
                    for job in line.split("[")[1].split("]")[0].split(","):
                        files.append(job.replace("'","").replace(" ",""))

        from modules.submitJobs import merge2DTemplate
        merge2DTemplate(jobList,files,"2Dl1"+"_"+period+"_"+c,c,"l1",self.binsMVV,self.binsMJ,self.minMVV,self.maxMVV,self.minMJ,self.maxMJ,self.HCALbinsMVV,name,filename,self.samples)
        merge2DTemplate(jobList,files,"2Dl2"+"_"+period+"_"+c,c,"l2",self.binsMVV,self.binsMJ,self.minMVV,self.maxMVV,self.minMJ,self.maxMJ,self.HCALbinsMVV,name,filename,self.samples)

        if period == "Run2":
            if makesingle:
             print " ########    making kernels also for single years ##############"
             years = ["2016","2017","2018"]
             for year in years:
                print " year ",year
                jobList = []
                files   = []
                with open("tmp1D_%s_%s_joblist.txt"%(period,c),'r') as infile:
                     for line in infile:
                         if line.startswith("job"):
                            for job in line.split("[")[1].split("]")[0].split(","):
                                if job.split("_")[0].replace("'","").replace(" ","") == year :
                                   print " condition ",job.split('_')[0]," = ",year, " verified "
                                   jobList.append(job.replace("'","").replace(" ",""))
                         if line.startswith("file"):
                            for job in line.split("[")[1].split("]")[0].split(","):
                                if job.split("/")[-2] == year :
                                   files.append(job.replace("'","").replace(" ",""))
                from modules.submitJobs import merge1DMVVTemplate
                newfilename=filename.replace("Run2",year)
                print "newfilename ",newfilename
                merge1DMVVTemplate(jobList,files,"1D"+"_"+period+"_"+c,c,self.binsMVV,self.minMVV,self.maxMVV,self.HCALbinsMVV,name,newfilename)

                jobList = []
                files   = []
                with open("tmp2Dl1_%s_%s_joblist.txt"%(period,c),'r') as infile:
                     for line in infile:
                         if line.startswith("job"):
                            for job in line.split("[")[1].split("]")[0].split(","):
                                if job.split("_")[0].replace("'","").replace(" ","") == year :
                                   print " condition ",job.split('_')[0]," = ",year, " verified "
                                   jobList.append(job.replace("'","").replace(" ",""))
                         if line.startswith("file"):
                             for job in line.split("[")[1].split("]")[0].split(","):
                                 if job.split("/")[-2] == year :
                                    files.append(job.replace("'","").replace(" ",""))

                from modules.submitJobs import merge2DTemplate
                merge2DTemplate(jobList,files,"2Dl1"+"_"+period+"_"+c,c,"l1",self.binsMVV,self.binsMJ,self.minMVV,self.maxMVV,self.minMJ,self.maxMJ,self.HCALbinsMVV,name,newfilename,self.samples)
                merge2DTemplate(jobList,files,"2Dl2"+"_"+period+"_"+c,c,"l2",self.binsMVV,self.binsMJ,self.minMVV,self.maxMVV,self.minMJ,self.maxMJ,self.HCALbinsMVV,name,newfilename,self.samples)
           

    print " done merging jobs "       

		            	    
 def printAllParameters(self):
 
  print "--------------------------------------------------------------------------"  
  print "Cuts:"
  print "--------------------------------------------------------------------------"
  print self.cuts
  print "--------------------------------------------------------------------------"
  print "mjj ranges: min ",self.minMVV,"max",self.maxMVV, "nbins",self.binsMVV
  print "--------------------------------------------------------------------------"
  print "reonance mX ranges: min ",self.minMX,"max",self.maxMX
  print "--------------------------------------------------------------------------" 
  print "mjj binning for bkg/data templates"
  print "--------------------------------------------------------------------------" 
  print self.HCALbinsMVV
  print "--------------------------------------------------------------------------" 
  print "Samples directory:",self.samples
  print "--------------------------------------------------------------------------" 
  print "Categories:",self.categories
  print "--------------------------------------------------------------------------" 
  print "mjet ranges: min ",self.minMJ,"max",self.maxMJ,"nbins",self.binsMJ
  print "--------------------------------------------------------------------------" 
  print "Submit to condor batch:",self.submitToBatch
  print "--------------------------------------------------------------------------" 
