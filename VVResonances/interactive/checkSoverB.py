import os, pickle, time, sys, math
import ROOT

doSignalEffWW = False
doSignalEffZH = False
doMistagRate = False
doSoverB = True
doPlots = False

files = []
filesBKG = []
filesZH = []
filesWW = []
signalinuse="ZprimeZH"
year='2018'
tt_templ='TT_Mtt'
directory='deepAK8V2/'+year
for f in os.listdir(directory):
 if 'QCD_Pt_' in f and '.root' in f: files.append(f)
 #all BKG together
 if 'QCD_Pt_' in f and '.root' in f: filesBKG.append(f)
 if 'ZJetsToQQ' in f and '.root' in f: filesBKG.append(f)
 if 'WJetsToQQ' in f and '.root' in f: filesBKG.append(f)
 if tt_templ in f and '.root' in f: filesBKG.append(f)
 #signals
 if 'BulkGravToWW' in f and '.root' in f and 'VBF' not in f: filesWW.append(f)
 if 'ZprimeToZhToZhadhbb' in f and '.root' in f and 'VBF' not in f: filesZH.append(f)

print files
print filesBKG
print filesZH
if year == '2016':
 tag= '16'
 lumi = 35900.
if year == '2018':
 lumi =  59740.
 tag = '18'

minMVV = 1126.
maxMVV = 7600.
minMJ=55.0
maxMJ=215.0

catHtag = {}
catVtag = {}

'''
# For retuned DDT tau 21, use this                                                                                                                                                                                                                                             
cat['HP1'] = '(jj_l1_tau2/jj_l1_tau1+(0.080*TMath::Log((jj_l1_softDrop_mass*jj_l1_softDrop_mass)/jj_l1_pt)))<0.43'
cat['HP2'] = '(jj_l2_tau2/jj_l2_tau1+(0.080*TMath::Log((jj_l2_softDrop_mass*jj_l2_softDrop_mass)/jj_l2_pt)))<0.43'
cat['LP1'] = '(jj_l1_tau2/jj_l1_tau1+(0.080*TMath::Log((jj_l1_softDrop_mass*jj_l1_softDrop_mass)/jj_l1_pt)))>0.43&&(jj_l1_tau2/jj_l1_tau1+(0.080*TMath::Log((jj_l1_softDrop_mass*jj_l1_softDrop_mass)/jj_l1_pt)))<0.79'
cat['LP2'] = '(jj_l2_tau2/jj_l2_tau1+(0.080*TMath::Log((jj_l2_softDrop_mass*jj_l2_softDrop_mass)/jj_l2_pt)))>0.43&&(jj_l2_tau2/jj_l2_tau1+(0.080*TMath::Log((jj_l2_softDrop_mass*jj_l2_softDrop_mass)/jj_l2_pt)))<0.79'
'''

catVtag['HP1'] = '(jj_l1_DeepBoosted_WvsQCD>jj_l1_DeepBoosted_WvsQCD__0p05_default_'+tag+')'
catVtag['HP2'] = '(jj_l2_DeepBoosted_WvsQCD>jj_l2_DeepBoosted_WvsQCD__0p05_default_'+tag+')'
catVtag['LP1'] = '((jj_l1_DeepBoosted_WvsQCD<jj_l1_DeepBoosted_WvsQCD__0p05_default_'+tag+')&&(jj_l1_DeepBoosted_WvsQCD>jj_l1_DeepBoosted_WvsQCD__0p10_default_'+tag+'))'
catVtag['LP2'] = '((jj_l2_DeepBoosted_WvsQCD<jj_l2_DeepBoosted_WvsQCD__0p05_default_'+tag+')&&(jj_l2_DeepBoosted_WvsQCD>jj_l2_DeepBoosted_WvsQCD__0p10_default_'+tag+'))'
catVtag['NP1'] = '(jj_l1_DeepBoosted_WvsQCD<jj_l1_DeepBoosted_WvsQCD__0p10_default_'+tag+')' #&&(jj_l1_DeepBoosted_WvsQCD>jj_l1_DeepBoosted_WvsQCD__0p50_default_'+tag+'))'
catVtag['NP2'] = '(jj_l2_DeepBoosted_WvsQCD<jj_l2_DeepBoosted_WvsQCD__0p10_default_'+tag+')' #&&(jj_l2_DeepBoosted_WvsQCD>jj_l2_DeepBoosted_WvsQCD__0p50_default_'+tag+'))'

catHtag['HP1'] = '(jj_l1_DeepBoosted_ZHbbvsQCD>jj_l1_DeepBoosted_ZHbbvsQCD__0p02_default_'+tag+')'
catHtag['HP2'] = '(jj_l2_DeepBoosted_ZHbbvsQCD>jj_l2_DeepBoosted_ZHbbvsQCD__0p02_default_'+tag+')'
catHtag['LP1'] = '(jj_l1_DeepBoosted_ZHbbvsQCD<jj_l1_DeepBoosted_ZHbbvsQCD__0p02_default_'+tag+'&&jj_l1_DeepBoosted_ZHbbvsQCD>jj_l1_DeepBoosted_ZHbbvsQCD__0p10_default_'+tag+')'
catHtag['LP2'] = '(jj_l2_DeepBoosted_ZHbbvsQCD<jj_l2_DeepBoosted_ZHbbvsQCD__0p02_default_'+tag+'&&jj_l2_DeepBoosted_ZHbbvsQCD>jj_l2_DeepBoosted_ZHbbvsQCD__0p10_default_'+tag+')'
catHtag['NP1'] = '(jj_l1_DeepBoosted_ZHbbvsQCD<jj_l1_DeepBoosted_ZHbbvsQCD__0p10_default_'+tag+'&&jj_l1_DeepBoosted_ZHbbvsQCD>jj_l1_DeepBoosted_ZHbbvsQCD__0p30_default_'+tag+')'
catHtag['NP2'] = '(jj_l2_DeepBoosted_ZHbbvsQCD<jj_l2_DeepBoosted_ZHbbvsQCD__0p10_default_'+tag+'&&jj_l2_DeepBoosted_ZHbbvsQCD>jj_l2_DeepBoosted_ZHbbvsQCD__0p30_default_'+tag+')'


cuts={}
cuts['common'] = '((HLT_JJ)*(run>500) + (run<500))*(passed_METfilters&&passed_PVfilter&&njj>0&&jj_LV_mass>700&&abs(jj_l1_eta-jj_l2_eta)<1.3&&jj_l1_softDrop_mass>0.&&jj_l2_softDrop_mass>0.&&TMath::Log(jj_l1_softDrop_mass**2/jj_l1_pt**2)<-1.8&&TMath::Log(jj_l2_softDrop_mass**2/jj_l2_pt**2)<-1.8)'
cuts['acceptance']= "(jj_LV_mass>{minMVV}&&jj_LV_mass<{maxMVV}&&jj_l1_softDrop_mass>{minMJ}&&jj_l1_softDrop_mass<{maxMJ}&&jj_l2_softDrop_mass>{minMJ}&&jj_l2_softDrop_mass<{maxMJ})".format(minMVV=minMVV,maxMVV=maxMVV,minMJ=minMJ,maxMJ=maxMJ)



catsAll = {}
#scheme 2: improves VV HPHP (VH_HPHP -> VV_HPHP -> VH_LPHP,VH_HPLP -> VV_HPLP)                                                                                                                                                

#at least one H tag HP (+ one V/H tag HP)  
catsAll['VH_HPHP'] = '('+'&&'.join([catVtag['HP1'],catHtag['HP2']])+')'
catsAll['HV_HPHP'] = '('+'&&'.join([catHtag['HP1'],catVtag['HP2']])+')'
catsAll['HH_HPHP'] = '('+'&&'.join([catHtag['HP1'],catHtag['HP2']])+')'
cuts['VH_HPHP'] = '('+'||'.join([catsAll['VH_HPHP'],catsAll['HV_HPHP'],catsAll['HH_HPHP']])+')'

# two V tag HP 
cuts['VV_HPHP'] = '('+'!'+cuts['VH_HPHP']+'&&'+'(' +  '&&'.join([catVtag['HP1'],catVtag['HP2']]) + ')' + ')'

#at least one H-tag HP (+one V OR H-tag LP) 
catsAll['VH_LPHP'] = '('+'&&'.join([catVtag['LP1'],catHtag['HP2']])+')'
catsAll['HV_HPLP'] = '('+'&&'.join([catHtag['HP1'],catVtag['LP2']])+')'
catsAll['HH_HPLP'] = '('+'&&'.join([catHtag['HP1'],catHtag['LP2']])+')'
catsAll['HH_LPHP'] = '('+'&&'.join([catHtag['LP1'],catHtag['HP2']])+')'
cuts['VH_LPHP'] = '('+'('+'!'+cuts['VH_HPHP']+'&&!'+cuts['VV_HPHP']+')&&('+'||'.join([catsAll['VH_LPHP'],catsAll['HV_HPLP'],catsAll['HH_HPLP'],catsAll['HH_LPHP']])+')'+')'

#at least one V-tag HP (+ one H-tag LP)                                                                                                                                                                                       
catsAll['VH_HPLP'] = '('+'&&'.join([catVtag['HP1'],catHtag['LP2']])+')'
catsAll['HV_LPHP'] = '('+'&&'.join([catHtag['LP1'],catVtag['HP2']])+')'
cuts['VH_HPLP'] = '('+'('+'!'+cuts['VH_LPHP']+'&&!'+cuts['VH_HPHP']+'&&!'+cuts['VV_HPHP']+')&&('+'||'.join([catsAll['VH_HPLP'],catsAll['HV_LPHP']])+')'+')'

cuts['VH_all'] =  '('+  '||'.join([cuts['VH_HPHP'],cuts['VH_LPHP'],cuts['VH_HPLP']]) + ')'

cuts['VV_HPLP'] = '(' +'('+'!'+cuts['VH_all']+') &&' + '(' + '('+  '&&'.join([catVtag['HP1'],catVtag['LP2']]) + ')' + '||' + '(' + '&&'.join([catVtag['HP2'],catVtag['LP1']]) + ')' + ')' + ')'
cuts['VV_all'] =  '('+  '||'.join([cuts['VV_HPHP'],cuts['VV_HPLP']]) + ')'

#all categories
cuts['VV_VH']= '('+  '||'.join([cuts['VH_all'],cuts['VV_HPHP'],cuts['VV_HPLP']]) + ')'

cut_tagger_1 = '('+'&&'.join([catVtag['HP1'],catVtag['NP2']])+')'
cut_tagger_2 = '('+'&&'.join([catVtag['HP2'],catVtag['NP1']])+')'
cuts['VV_HPNP_control_region'] = '('+'('+'||'.join([cut_tagger_1,cut_tagger_2])+')'+'&&'+'('+'!'+cuts['VH_all']+')'+')' 


lp_cut_1 = catVtag['LP1']
lp_cut_1 = lp_cut_1.replace('0p05','0p15').replace('0p10','0p50')
lp_cut_2 = catVtag['LP2']
lp_cut_2 = lp_cut_2.replace('0p05','0p15').replace('0p10','0p50')
cut_tagger_1h = '('+'&&'.join([catHtag['HP1'],lp_cut_2])+')'
cut_tagger_2h = '('+'&&'.join([catHtag['HP2'],lp_cut_1])+')'
cuts['VH_NPHP_control_region'] = '('+'('+'||'.join([cut_tagger_1h,cut_tagger_2h])+')'+'&&'+'('+'!'+cuts['VV_VH']+')'+')'


'''
#control region (invert w-tag)                                                                                                                                                                                                
catsAll['VH_NPHP'] = '('+'&&'.join([catVtag['NP1'],catHtag['HP2']])+')'
catsAll['HV_HPNP'] = '('+'&&'.join([catHtag['HP1'],catVtag['NP2']])+')'
#cuts['VH_NPHP_control_region'] = '('+'('+'||'.join([catsAll['VH_NPHP'],catsAll['HV_HPNP']])+')'+'&&'+'('+'!'+'('+ '||'.join([cuts['VV_VH'],cuts['VH_HPNP_control_region']]) + ')'+')'+')'                     
cuts['VH_NPHP_control_region'] = '('+'('+'||'.join([catsAll['VH_NPHP'],catsAll['HV_HPNP']])+')'+'&&'+'('+'!'+cuts['VH_all']+')'+')'#     '('+ '||'.join([cuts['VV_VH'],cuts['VH_HPNP_control_region']]) + ')'+')'+')'

#control region (invert h-tag)                                                                                                                                                                                                
catsAll['VH_HPNP'] = '('+'&&'.join([catVtag['HP1'],catHtag['NP2']])+')'
catsAll['HV_NPHP'] = '('+'&&'.join([catHtag['NP1'],catVtag['HP2']])+')'
cuts['VH_HPNP_control_region'] = '('+'('+'||'.join([catsAll['VH_HPNP'],catsAll['HV_NPHP']])+')'+'&&'+'('+'!'+'('+ '||'.join([cuts['VV_all'],cuts['VH_NPHP_control_region']]) +')'+')'+')'
'''


#################### FOR S/B ################
if doSoverB:
 files_sig = filesZH
 categories = ["VV_HPHP","VH_HPHP","VV_VH"] #,'VH_HPNP_control_region',"VH_NPHP_control_region"]
 masses = [1600,4000]

 for whichCat in categories :
  print " *******    ",whichCat , " *******    "
  #whichCat='VV_HPHP'
  #files_sig = filesWW
  outfile = open("signal_"+signalinuse+"_overAllB_"+whichCat+"_"+year+".txt","w")
  outfile.write("*** "+whichCat+"\n")
 
  eff = 0.
  num = 0.
  den = 0.

  hrate = {}
  effSig = {}
  numSigInteg = {}

  for m in masses:
   hrate[m] = ROOT.TH1F('hrate_M%i'%m,'hrate_M%i'%m,3,0,3)

  print " Reading BKG files"
  for f in filesBKG:
   print f  
   fpck=open(directory+'/'+f.replace('.root','.pck'))
   dpck=pickle.load(fpck)
   weightinv = float(dpck['events'])
   print " fpck file done " 
   tf = ROOT.TFile.Open(directory+'/'+f,'READ')
   tree = tf.AnalysisTree
   print "loaded ttree"   
   fout = ROOT.TFile.Open('ftmp.root','RECREATE')   
   fout.cd()
  
   cut = "*".join([cuts['common'],cuts['acceptance']])
   reduced = tree.CopyTree(cut,"")
   reduced.Write("reduced")
   print "wrote reduced tree "
   for m in masses:

    print "######### mass ",m
    mjjcut = '(jj_LV_mass>%f&&jj_LV_mass<%f)'%(m-m*0.15,m+m*0.15)
    pden = float(reduced.GetEntries(mjjcut))
    den += float(reduced.GetEntries(mjjcut))
    print " partial den ",pden," temporary den ",den
    
    htmp = ROOT.gROOT.FindObject('htmp')
    if htmp: htmp.Delete()
    
    cut = "*".join([cuts[whichCat],mjjcut])
    print "going to change root tformula maxima"
    ROOT.v5.TFormula.SetMaxima(10000)
    print " set to 10000"
    reduced.Draw('njj>>htmp(3,0,3)','(genWeight*xsec*puWeight*%.20f)*'%(lumi/weightinv)+cut,"goff")
    print " drew htmp "
    htmp = ROOT.gROOT.FindObject('htmp')
    try:
     print htmp.GetEntries()
     hrate[m].Add(htmp)
    except:
     print " this time I didn't find htmp!"
    hrate[m].SetDirectory(0)

    pnum = float(reduced.GetEntries(cut))
    num += float(reduced.GetEntries(cut))
    print " partial num ",num," temporary num ",num
  
    peff = 0
    if pden!=0: peff=pnum/pden

    print "Mass:",m,"File:",f,"Partial rate:",hrate[m].Integral(),"Partial Den:",pden,"Partial Num:",pnum,"Partial Bkg Eff:",peff
   
    #now calculate signal eff for Punzi
    for fs in files_sig:
     mass = float(fs.split('_')[-1].replace('.root',''))
     if mass!=m: continue
     print "now signal ",fs

     fpckSig=open('2016trainingV2/'+fs.replace('.root','.pck'))
     dpckSig=pickle.load(fpckSig)
     weightinv = float(dpckSig['events'])
         
     tfSig = ROOT.TFile.Open('2016trainingV2/'+fs,'READ')
     treeSig = tfSig.AnalysisTree
     print "got tree "

     cut = "*".join([cuts['common'],cuts['acceptance'],mjjcut])    
     denSig = float(treeSig.GetEntries(cut))
    
     cut = "*".join([cuts['common'],cuts['acceptance'],mjjcut,cuts[whichCat]])    
     numSig = float(treeSig.GetEntries(cut))
     effSig[m] = numSig/denSig
        
     htmpSig = ROOT.gROOT.FindObject('htmpSig')
     if htmpSig: htmpSig.Delete()

     print "going to change root tformula maxima"
     ROOT.v5.TFormula.SetMaxima(10000)
     print " set to 10000"

     treeSig.Draw('njj>>htmpSig(3,0,3)','(genWeight*xsec*puWeight*%.20f)*'%(lumi/weightinv)+cut,"goff")

     print " drew htmpSig "
     htmpSig = ROOT.gROOT.FindObject('htmpSig')
     numSigInteg[m] = htmpSig.Integral()

     print "hrate[m].Integral() ",hrate[m].Integral()
     print "Signal Eff:",numSig/denSig,"Partial Punzi:",(effSig[m])/(1+math.sqrt(hrate[m].Integral()))
  

     #outfile.write("S B S/B punzi \n")
     #outfile.write(str(numSigInteg)+" "+str(hrate[m].Integral())+" "+str(numSigInteg/hrate[m].Integral())+" "+str(effSig[m]/(1+math.sqrt(hrate[m].Integral())))+"\n") 
  
   fout.Close()

  for m in masses:
   print "mass ",m
   outfile.write("    "+str(m)+"\n")
   outfile.write("S B S/B punzi \n")
   print "numSigInteg[m] ",numSigInteg[m]
   print "hrate[m].Integral() ",hrate[m].Integral()
   print "effSig[m] ",effSig[m]
   outfile.write(str(numSigInteg[m])+" "+str(hrate[m].Integral())+" "+str(numSigInteg[m]/hrate[m].Integral())+" "+str(effSig[m]/(1+math.sqrt(hrate[m].Integral())))+"\n")

   print "----> Final Punzi for mass",m," - cat.",whichCat,":",effSig[m]/(1+math.sqrt(hrate[m].Integral())),"Final Back eff:",num/den
   print "----> Final S/B for mass",m," - cat.",whichCat,":",numSigInteg[m]/hrate[m].Integral()


  outfile.close()

#################### FOR MISTAG RATE ################
whichCat = 'VH_HPHP'
if doMistagRate:

 eff = 0.
 num = 0.
 den = 0.

 for f in files:

  tf = ROOT.TFile.Open('2016trainingV2/'+f,'READ')
  tree = tf.AnalysisTree
     
  cut = "*".join([cuts['common'],cuts['acceptance']])
  pden = float(tree.GetEntries(cut))
  den += float(tree.GetEntries(cut))
 
  cut = "*".join([cuts[whichCat],cuts['common'],cuts['acceptance']])
  pnum = float(tree.GetEntries(cut))
  num += float(tree.GetEntries(cut))    

  print "File:",f,"Partial Num:",pnum,"Partial Den:",pden,"Partial Eff:",pnum/pden

 print "----> Final mistag rate for cat.",whichCat,":",num/den




##################### FOR SIGNAL EFF ###################
print ""
num = {}
if doSignalEffWW or doSignalEffZH:

 files_sig = filesZH
 if doSignalEffWW: files_sig = filesWW
 
 for f in files_sig:
 
  numALL = 0
  
  tf = ROOT.TFile.Open('2016trainingV2/'+f,'READ')
  tree = tf.AnalysisTree

  cut = "*".join([cuts['common'],cuts['acceptance']])
  den = float(tree.GetEntries(cut))
 
  cut = "*".join([cuts['VH_HPHP'],cuts['common'],cuts['acceptance']])
  num['VH_HPHP'] = float(tree.GetEntries(cut))

  cut = "*".join([cuts['VH_LPHP'],cuts['common'],cuts['acceptance']])
  num['VH_LPHP'] = float(tree.GetEntries(cut))

  cut = "*".join([cuts['VH_HPLP'],cuts['common'],cuts['acceptance']])
  #num['VH_HPLP'] = float(tree.GetEntries(cut))
 
  cut = "*".join([cuts['VH_all'],cuts['common'],cuts['acceptance']])
  num['VH_all'] = float(tree.GetEntries(cut))

  cut = "*".join(['('+cuts['VV_HPHP']+'||'+cuts['VH_HPLP']+')',cuts['common'],cuts['acceptance']]) #if I add VH_HPLP to VV_HPHP how much background I am picking up?
  num['VV_HPHP'] = float(tree.GetEntries(cut))

  cut = "*".join([cuts['VV_HPLP'],cuts['common'],cuts['acceptance']])
  num['VV_HPLP'] = float(tree.GetEntries(cut))

  cut = "*".join([cuts['VV_HPHP_noVeto'],cuts['common'],cuts['acceptance']])
  #num['VV_HPHP_noVeto'] = float(tree.GetEntries(cut))
      
  print "File:",f
  for k in num.keys():
   print "    -",k,num[k]/den
   if not 'all' in k: numALL+=num[k]

  print "--> Total eff (cross check):",numALL/den
  print ""
