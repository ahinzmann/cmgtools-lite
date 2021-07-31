#!/usr/bin/env python
# vvMakeLimitPlot.py Limits_BulkGVV_13TeV_Run2_data_ggDYVBF_VVVH_partial_newbaseline.root  -o ExpLimits -s BulkGVV -n test -p ALL --hvt 0  --HVTworkspace results_Run2/workspace_JJ_BulkGVV_VBF_VVVH_13TeV_Run2_data_newbaseline.root --theoryUnc
# vvMakeLimitPlot.py Limits_ZprimeWW_13TeV_Run2_data_ggDYVBF_VVVH_partial_newbaseline.root  -o ExpLimits -s ZprimeWW -n test -p ALL --hvt 0  --HVTworkspace results_Run2/workspace_JJ_ZprimeWW_VBF_VVVH_13TeV_Run2_data_newbaseline.root --theoryUnc


import ROOT
import optparse, time, sys, math
from CMGTools.VVResonances.plotting.CMS_lumi import *
from CMGTools.VVResonances.plotting.tdrstyle import *
from array import array
import numpy as np
ROOT.gROOT.SetBatch(True)
parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",default='limitPlot',help="Limit plot")
parser.add_option("-s","--signal",dest="sig",type=str,help="Signal sample",default='BulkGWW')
parser.add_option("--sigscale",dest="sigscale",type=float,help="maximum y",default=0.001)
parser.add_option("-x","--minX",dest="minX",type=float,help="minimum x",default=1.3)
parser.add_option("-X","--maxX",dest="maxX",type=float,help="maximum x",default=6.0)
parser.add_option("-y","--minY",dest="minY",type=float,help="minimum y",default=0.00001)
parser.add_option("-Y","--maxY",dest="maxY",type=float,help="maximum y",default=10)
parser.add_option("-b","--blind",dest="blind",type=int,help="Not do observed ",default=1)
parser.add_option("-l","--log",dest="log",type=int,help="Log plot",default=1)

parser.add_option("-t","--titleX",dest="titleX",default='M_{X} [GeV]',help="title of x axis")
parser.add_option("-T","--titleY",dest="titleY",default='#sigma x #bf{#it{#Beta}}(X #rightarrow WW) [pb]  ',help="title of y axis")
parser.add_option("-n","--name",dest="name",default='test',help="add a label to the output file name")
parser.add_option("--spline",dest="spline",action='store_true',default=False)
parser.add_option("-p","--period",dest="period",default='2016',help="period")
parser.add_option("-f","--final",dest="final",type=int, default=0,help="Preliminary or not")
parser.add_option("--hvt","--hvt",dest="hvt",type=int, default=0,help="do HVT (1) or do BulkG (2), (0) for single signal")
parser.add_option("--HVTworkspace","--HVTworkspace",dest="HVTworkspace",default="workspace_JJ_VprimeWV_13TeV.root",help="HVT workspace with spline interpolation")
parser.add_option("--debug",dest="debug",action='store_true',default=False)
parser.add_option("--theoryUnc",dest="theoryUnc",action='store_true',default=False)

(options,args) = parser.parse_args()
#define output dictionary
filename=options.output+"_"+options.sig+"_"+options.name
setTDRStyle()


oneSignal = True
if 'WW' in options.sig or 'ZZ' in options.sig or 'WH' in options.sig or 'ZH' in options.sig or 'WZ' in options.sig:
 oneSignal = True
else:
 oneSignal = False

 isvbf = ''
 if 'VBF' in options.sig: isvbf='VBF_'

 if 'VprimeWV' in options.sig:
   signal1 = '%sWprimeWZ'%isvbf
   signal2 = '%sZprimeWW'%isvbf
 elif 'VprimeVHinc' in options.sig:
   signal1 = '%sWprimeWH'%isvbf
   signal2 = '%sZprimeZH'%isvbf
 elif options.sig == 'Wprime' or options.sig == 'VBF_Wprime':
   signal1 = '%sWprimeWZ'%isvbf
   signal2 = '%sWprimeWH'%isvbf
 elif options.sig == 'Zprime' or options.sig == 'VBF_Zprime':
   signal1 = '%sZprimeWW'%isvbf
   signal2 = '%sZprimeZH'%isvbf
 elif options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
   signal1 = '%sWprimeWZ'%isvbf
   signal2 = '%sZprimeWW'%isvbf
   signal3 = '%sWprimeWH'%isvbf
   signal4 = '%sZprimeZH'%isvbf
 elif 'BulkGVV' in options.sig:
   signal1 = '%sBulkGWW'%isvbf
   signal2 = '%sBulkGZZ'%isvbf
 elif 'RadionVV' in options.sig:
   signal1 = '%sRadionWW'%isvbf
   signal2 = '%sRadionZZ'%isvbf

print " oneSignal ",oneSignal



masses = array('d',[i*100. for i in range(8,61)])
massesTeV = array('d',[i*0.1 for i in range(8,61)])
scaleLimits = {}
for m in masses:
 scaleLimits[str(int(m))] = options.sigscale

if options.hvt>=0: #the = is only needed to get the right xsec sf for the single signal
 fin = ROOT.TFile.Open(options.HVTworkspace,"READ")
 w = fin.Get("w")
  
 if oneSignal == False:
  filenameTHWp = "$CMSSW_BASE/src/CMGTools/VVResonances/scripts/theoryXsec/"+signal1+".root"
  filenameTHZp = "$CMSSW_BASE/src/CMGTools/VVResonances/scripts/theoryXsec/"+signal2+".root"
  filenameTHWHp = None
  filenameTHZHp = None

  if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
   filenameTHWHp = "$CMSSW_BASE/src/CMGTools/VVResonances/scripts/theoryXsec/"+signal3+".root"
   filenameTHZHp = "$CMSSW_BASE/src/CMGTools/VVResonances/scripts/theoryXsec/"+signal4+".root"

  if options.sig.find("VBF") !=-1:
   VBFstring="VBF_"
   if options.sig.find("prime") !=-1: VBFstring="HVTC_"
   filenameTHWp = filenameTHWp.replace("theoryXsec/","theoryXsec/"+VBFstring)
   filenameTHWp = filenameTHWp.replace("_VBF_","_")
   filenameTHZp = filenameTHZp.replace("theoryXsec/","theoryXsec/"+VBFstring)
   filenameTHZp = filenameTHZp.replace("_VBF_","_")
   if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
    filenameTHWHp = filenameTHWHp.replace("theoryXsec/","theoryXsec/"+VBFstring)
    filenameTHWHp = filenameTHWHp.replace("_VBF_","_")
    filenameTHZHp = filenameTHZHp.replace("theoryXsec/","theoryXsec/"+VBFstring)
    filenameTHZHp = filenameTHZHp.replace("_VBF_","_")

  if options.debug:
   print "filenameTHWp ",filenameTHWp
   print "filenameTHZp ",filenameTHZp
   print "filenameTHWHp ",filenameTHWHp
   print "filenameTHZHp ",filenameTHZHp
     
  thFileWp       = ROOT.TFile.Open(filenameTHWp,'READ')
  thFileZp       = ROOT.TFile.Open(filenameTHZp,'READ')
  print "Opening file " ,thFileWp.GetName()
  gtheoryWp      = thFileWp.Get("gtheory")
  if options.theoryUnc:
   gtheoryWpUP    = thFileWp.Get("gtheoryUP")
   gtheoryWpDOWN  = thFileWp.Get("gtheoryDOWN")
   gtheoryWpSHADE = thFileWp.Get("grshade")
  print "Opening file " ,thFileZp.GetName()
  gtheoryZp      = thFileZp.Get("gtheory")
  if options.theoryUnc:
   gtheoryZpUP    = thFileZp.Get("gtheoryUP")
   gtheoryZpDOWN  = thFileZp.Get("gtheoryDOWN")
   gtheoryZpSHADE = thFileZp.Get("grshade")

  if gtheoryZp.GetN() != gtheoryWp.GetN() and options.spline == False:
   print " length theory curve of "+signal1+" is "+str(gtheoryWp.GetN())+" and is different from "+signal2+" "+str(gtheoryZp.GetN())
   print " use options spline! "
   sys.exit()
  else:
   for i in range(gtheoryWp.GetN()):
    x = ROOT.Double(0.)
    y = ROOT.Double(0.)
    gtheoryWp.GetPoint(i,x,y)
    xz = ROOT.Double(0.)
    yz = ROOT.Double(0.)
    gtheoryZp.GetPoint(i,xz,yz)
    if x != xz:
     print signal1+" has mass "+str(x)+"different from "+str(xz)+" for signal "+signal2

  if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
   thFileWHp       = ROOT.TFile.Open(filenameTHWHp,'READ')
   thFileZHp       = ROOT.TFile.Open(filenameTHZHp,'READ')
   print "Opening file " ,thFileWHp.GetName()
   gtheoryWHp      = thFileWHp.Get("gtheory")
   if options.theoryUnc:
    gtheoryWHpUP    = thFileWHp.Get("gtheoryUP")
    gtheoryWHpDOWN  = thFileWHp.Get("gtheoryDOWN")
    gtheoryWHpSHADE = thFileWHp.Get("grshade")
   print "Opening file " ,thFileZHp.GetName()
   gtheoryZHp      = thFileZHp.Get("gtheory")
   if options.theoryUnc:
    gtheoryZHpUP    = thFileZHp.Get("gtheoryUP")
    gtheoryZHpDOWN  = thFileZHp.Get("gtheoryDOWN")
    gtheoryZHpSHADE = thFileZHp.Get("grshade")



 for m in masses:
  year=options.period
  if options.period == 'ALL': year = 'Run2'
  argset = ROOT.RooArgSet()
  MH=w.var("MH")
  argset.add(MH)
  MH.setVal(m)
  if oneSignal == False:
   func1 = w.function(signal1+'_JJ_VV_HPHP_13TeV_'+year+'_sigma')
   func2 = w.function(signal2+'_JJ_VV_HPHP_13TeV_'+year+'_sigma')
   if options.sig == 'VprimeVHinc' or options.sig == 'VBF_VprimeVHinc':
    func1 = w.function(signal1+'inc_JJ_VV_HPHP_13TeV_'+year+'_sigma')
    func2 = w.function(signal2+'inc_JJ_VV_HPHP_13TeV_'+year+'_sigma')
   scaleLimits[str(int(m))] = ROOT.TMath.Exp(func1.getVal(argset))+ROOT.TMath.Exp(func2.getVal(argset))
   if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
    try:
     func3 = w.function(signal3+'inc_JJ_VV_HPHP_13TeV_'+year+'_sigma')
     func4 = w.function(signal4+'inc_JJ_VV_HPHP_13TeV_'+year+'_sigma')
    except:
     func3 = w.function(signal3+'_JJ_VV_HPHP_13TeV_'+year+'_sigma')
     func4 = w.function(signal4+'_JJ_VV_HPHP_13TeV_'+year+'_sigma')
    scaleLimits[str(int(m))] = scaleLimits[str(int(m))]+ROOT.TMath.Exp(func3.getVal(argset))+ROOT.TMath.Exp(func4.getVal(argset))
  else:
   func = w.function(options.sig+'_JJ_VV_HPHP_13TeV_'+year+'_sigma')
   scaleLimits[str(int(m))] = ROOT.TMath.Exp(func.getVal(argset))

  if "prime" not in options.sig or "VBF" in options.sig:
   if options.debug:   print " rescaling limit !!!!! "
   scaleLimits[str(int(m))] = scaleLimits[str(int(m))]*10
   if (m > 3000. and "VBF" in options.sig) or m>5000.:
    if options.debug:    print "extra rescaling for high mx "
    scaleLimits[str(int(m))] = scaleLimits[str(int(m))]*10
    if (m > 5000. and "VBF" in options.sig) or (m == 5000. and "VBF_Radion" not in options.sig)  or (options.sig == "VBF_ZprimeWW" and m >= 4400.) or (options.sig == "VBF_WprimeWZ" and m >= 4800.) or (options.sig == "VBF_BulkGZZ" and m >= 5000.) or (options.sig == "VBF_ZprimeZHinc" and m >= 4500.) or (options.sig == "VBF_VprimeVHinc" and m >= 4600.) or (options.sig == "VBF_Vprime" and m >= 4600.):
     if options.debug:    print "double extra rescaling for high mx "
     scaleLimits[str(int(m))] = scaleLimits[str(int(m))]*10
     if (options.sig == "VBF_ZprimeWW" and m >= 5400.) or (options.sig == "VBF_BulkGZZ" and m >= 5700.) or (options.sig == "VBF_ZprimeZHinc" and m >= 5500.) or (options.sig == "VBF_VprimeVHinc" and m >= 5600.) or (options.sig == "VBF_BulkGZZ" and m >= 5700.) or (options.sig == "VBF_BulkGWW" and m >= 5800.) or (options.sig == "VBF_BulkGVV" and m == 6000.) or (options.sig == "VBF_WprimeWHinc" and m == 6000.)  or (options.sig == "VBF_VprimeWV" and m >= 5900.) or (options.sig == "VBF_Vprime" and m >= 5600. and m<6000.) or (options.sig == "VBF_WprimeWZ" and m == 6000.):
      if options.debug:    print "triple! extra rescaling for high mx "
      scaleLimits[str(int(m))] = scaleLimits[str(int(m))]*10

 if oneSignal == False:
  print " initializing theory for more than 1 signal!"


  xsecTot = array('d',[])
  xsecTotUp = array('d',[])
  xsecTotDown = array('d',[])
  shade_x = array('d',[])
  shade_y = array('d',[])

  if options.spline:
   print " using spline!!! "
   spline_x_wp = []
   spline_y_wp = []
   spline_y_wpUP = []
   spline_y_wpDOWN = []
   for i in range(gtheoryWp.GetN()):
    x = ROOT.Double(0.)
    y = ROOT.Double(0.)
    gtheoryWp.GetPoint(i,x,y)
    spline_y_wp.append(y)
    spline_x_wp.append(x)
    x = ROOT.Double(0.)
    y = ROOT.Double(0.)
    if options.theoryUnc:
     gtheoryWpUP.GetPoint(i,x,y)
     spline_y_wpUP.append(y)
    x = ROOT.Double(0.)
    y = ROOT.Double(0.)
    if options.theoryUnc:
     gtheoryWpDOWN.GetPoint(i,x,y)
     spline_y_wpDOWN.append(y)

   spline_y_zp = []
   spline_x_zp = []
   spline_y_zpUP = []
   spline_y_zpDOWN = []
   for i in range(gtheoryZp.GetN()):
    x = ROOT.Double(0.)
    y = ROOT.Double(0.)
    gtheoryZp.GetPoint(i,x,y)
    spline_y_zp.append(y)
    spline_x_zp.append(x)
    x = ROOT.Double(0.)
    y = ROOT.Double(0.)
    if options.theoryUnc:
     gtheoryZpUP.GetPoint(i,x,y)
     spline_y_zpUP.append(y)
    x = ROOT.Double(0.)
    y = ROOT.Double(0.)
    if options.theoryUnc:
     gtheoryZpDOWN.GetPoint(i,x,y)
     spline_y_zpDOWN.append(y)

    if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
     spline_x_whp = []
     spline_y_whp = []
     spline_y_whpUP = []
     spline_y_whpDOWN = []
     for i in range(gtheoryWHp.GetN()):
      x = ROOT.Double(0.)
      y = ROOT.Double(0.)
      gtheoryWHp.GetPoint(i,x,y)
      spline_y_whp.append(y)
      spline_x_whp.append(x)
      x = ROOT.Double(0.)
      y = ROOT.Double(0.)
      if options.theoryUnc:
       gtheoryWHpUP.GetPoint(i,x,y)
       spline_y_whpUP.append(y)
      x = ROOT.Double(0.)
      y = ROOT.Double(0.)
      if options.theoryUnc:
       gtheoryWHpDOWN.GetPoint(i,x,y)
       spline_y_whpDOWN.append(y)

     spline_y_zhp = []
     spline_x_zhp = []
     spline_y_zhpUP = []
     spline_y_zhpDOWN = []
     for i in range(gtheoryZHp.GetN()):
      x = ROOT.Double(0.)
      y = ROOT.Double(0.)
      gtheoryZHp.GetPoint(i,x,y)
      spline_y_zhp.append(y)
      spline_x_zhp.append(x)
      x = ROOT.Double(0.)
      y = ROOT.Double(0.)
      if options.theoryUnc:
       gtheoryZHpUP.GetPoint(i,x,y)
       spline_y_zhpUP.append(y)
      x = ROOT.Double(0.)
      y = ROOT.Double(0.)
      if options.theoryUnc:
       gtheoryZHpDOWN.GetPoint(i,x,y)
       spline_y_zhpDOWN.append(y)


   spline_zp=ROOT.RooSpline1D(signal2+"_sigma",signal2+"_sigma",MH,len(spline_x_zp),array('d',spline_x_zp),array('d',spline_y_zp))
   spline_wp=ROOT.RooSpline1D(signal1+"_sigma",signal1+"_sigma",MH,len(spline_x_wp),array('d',spline_x_wp),array('d',spline_y_wp))
   if options.theoryUnc:
    spline_zpUP=ROOT.RooSpline1D(signal2+"_sigmaUP",signal2+"_sigmaUP",MH,len(spline_x_zp),array('d',spline_x_zp),array('d',spline_y_zpUP))
    spline_wpUP=ROOT.RooSpline1D(signal1+"_sigmaUP",signal1+"_sigmaUP",MH,len(spline_x_wp),array('d',spline_x_wp),array('d',spline_y_wpUP))
    spline_zpDOWN=ROOT.RooSpline1D(signal2+"_sigmaDOWN",signal2+"_sigmaDOWN",MH,len(spline_x_zp),array('d',spline_x_zp),array('d',spline_y_zpDOWN))
    spline_wpDOWN=ROOT.RooSpline1D(signal1+"_sigmaDOWN",signal1+"_sigmaDOWN",MH,len(spline_x_wp),array('d',spline_x_wp),array('d',spline_y_wpDOWN))
    if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
     spline_zhp=ROOT.RooSpline1D(signal4+"_sigma",signal4+"_sigma",MH,len(spline_x_zhp),array('d',spline_x_zhp),array('d',spline_y_zhp))
     spline_whp=ROOT.RooSpline1D(signal3+"_sigma",signal3+"_sigma",MH,len(spline_x_whp),array('d',spline_x_whp),array('d',spline_y_whp))
     if options.theoryUnc:
      spline_zhpUP=ROOT.RooSpline1D(signal4+"_sigmaUP",signal4+"_sigmaUP",MH,len(spline_x_zhp),array('d',spline_x_zhp),array('d',spline_y_zhpUP))
      spline_whpUP=ROOT.RooSpline1D(signal3+"_sigmaUP",signal3+"_sigmaUP",MH,len(spline_x_whp),array('d',spline_x_whp),array('d',spline_y_whpUP))
      spline_zhpDOWN=ROOT.RooSpline1D(signal4+"_sigmaDOWN",signal4+"_sigmaDOWN",MH,len(spline_x_zhp),array('d',spline_x_zhp),array('d',spline_y_zhpDOWN))
      spline_whpDOWN=ROOT.RooSpline1D(signal3+"_sigmaDOWN",signal3+"_sigmaDOWN",MH,len(spline_x_whp),array('d',spline_x_whp),array('d',spline_y_whpDOWN))


   for m in masses:
    print " m ",m
    m = m/1000.
    MH.setVal(m)
    tot = spline_zp.getVal(argset)+spline_wp.getVal(argset)
    if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
     tot = tot + spline_zhp.getVal(argset)+spline_whp.getVal(argset)

    if options.theoryUnc:
     uncUp_zp = spline_zpUP.getVal(argset)-spline_zp.getVal(argset)
     uncUp_wp = spline_wpUP.getVal(argset)-spline_wp.getVal(argset)
     uncUp_zhp = 0
     uncUp_whp = 0
     if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
      uncUp_zhp = spline_zhpUP.getVal(argset)-spline_zhp.getVal(argset)
      uncUp_whp = spline_whpUP.getVal(argset)-spline_whp.getVal(argset)

     xsecTotUp.append( tot+math.sqrt(uncUp_zp*uncUp_zp+uncUp_wp*uncUp_wp + uncUp_zhp*uncUp_zhp+uncUp_whp*uncUp_whp) )

     uncDown_zp = spline_zp.getVal(argset)-spline_zpDOWN.getVal(argset)
     uncDown_wp = spline_wp.getVal(argset)-spline_wpDOWN.getVal(argset)
     uncDown_zhp =0
     uncDown_whp =0
     if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
      uncDown_zhp = spline_zhp.getVal(argset)-spline_zhpDOWN.getVal(argset)
      uncDown_whp = spline_whp.getVal(argset)-spline_whpDOWN.getVal(argset)

     xsecTotDown.append( tot-math.sqrt(uncDown_zp*uncDown_zp+uncDown_wp*uncDown_wp + uncDown_zhp*uncDown_zhp+uncDown_whp*uncDown_whp) )


     shade_x.append(m)
     shade_y.append( tot+math.sqrt(uncUp_zp*uncUp_zp+uncUp_wp*uncUp_wp + uncUp_zhp*uncUp_zhp+uncUp_whp*uncUp_whp) )
     
    print " tot ",tot
    xsecTot.append(tot)

   if options.theoryUnc:
    for i in range( len(massesTeV)-1, -1, -1 ):
     shade_x.append(massesTeV[i])
     shade_y.append(xsecTotDown[i])

   gtheory = ROOT.TGraphErrors(len(massesTeV),massesTeV,xsecTot)
   gtheory.SetLineColor(ROOT.kRed)
   gtheory.SetLineWidth(3)
   if options.theoryUnc:
    gtheoryUP = ROOT.TGraphErrors(len(massesTeV),massesTeV,xsecTotUp)
    gtheoryUP.SetLineColor(ROOT.kRed-2)
    gtheoryUP.SetLineWidth(3)
    gtheoryDOWN = ROOT.TGraphErrors(len(massesTeV),massesTeV,xsecTotDown)
    gtheoryDOWN.SetLineColor(ROOT.kRed-2)
    gtheoryDOWN.SetLineWidth(3)
    gtheorySHADE = ROOT.TGraphErrors(len(shade_x),shade_x,shade_y)
    gtheorySHADE.SetLineColor(ROOT.kRed-2)
    gtheorySHADE.SetLineWidth(3)

  elif not options.spline:
   print " using tgraph from theory file! "
   MassXsec = array('d',[])
   for i in range(gtheoryWp.GetN()):
    # W
    xw = ROOT.Double(0.)
    yw = ROOT.Double(0.)
    gtheoryWp.GetPoint(i,xw,yw)
    MassXsec.append(xw)
    xwUp = ROOT.Double(0.)
    ywUp = ROOT.Double(0.)
    if options.theoryUnc:
     gtheoryWpUP.GetPoint(i,xwUp,ywUp)
    xwDown = ROOT.Double(0.)
    ywDown = ROOT.Double(0.)
    if options.theoryUnc:
     gtheoryWpDOWN.GetPoint(i,xwDown,ywDown)

    #Z
    xz = ROOT.Double(0.)
    yz = ROOT.Double(0.)
    gtheoryZp.GetPoint(i,xz,yz)
    if xz != xw:
     print " masses are different!!!!! "
     print " xz "+str(xz)+" != xw "+str(xw)
     sys.exit()
    xzUp = ROOT.Double(0.)
    yzUp = ROOT.Double(0.)
    if options.theoryUnc:
     gtheoryZpUP.GetPoint(i,xzUp,yzUp)
    xzDown = ROOT.Double(0.)
    yzDown = ROOT.Double(0.)
    if options.theoryUnc:
     gtheoryZpDOWN.GetPoint(i,xzDown,yzDown)

    ywh = 0.
    yzh = 0.

    if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
     # WH
     xwh = ROOT.Double(0.)
     ywh = ROOT.Double(0.)
     gtheoryWHp.GetPoint(i,xwh,ywh)
     xwhUp = ROOT.Double(0.)
     ywhUp = ROOT.Double(0.)
     if options.theoryUnc:
      gtheoryWHpUP.GetPoint(i,xwhUp,ywhUp)
      xwhDown = ROOT.Double(0.)
      ywhDown = ROOT.Double(0.)
      if options.theoryUnc:
       gtheoryWHpDOWN.GetPoint(i,xwhDown,ywhDown)

     #ZH
     xzh = ROOT.Double(0.)
     yzh = ROOT.Double(0.)
     gtheoryZHp.GetPoint(i,xzh,yzh)
     if xzh != xwh:
      print " masses are different!!!!! "
      print " xzh "+str(xzh)+" != xwh "+str(xwh)
      sys.exit()
     xzhUp = ROOT.Double(0.)
     yzhUp = ROOT.Double(0.)
     if options.theoryUnc:
      gtheoryZHpUP.GetPoint(i,xzhUp,yzhUp)
     xzhDown = ROOT.Double(0.)
     yzhDown = ROOT.Double(0.)
     if options.theoryUnc:
      gtheoryZHpDOWN.GetPoint(i,xzhDown,yzhDown)



    tot = yz +yw + yzh + ywh
    print " tot ",tot
    if options.theoryUnc:
     uncUp_zp = yzUp-yz
     uncUp_wp = ywUp-yw
     uncUp_zhp = 0
     uncUp_whp = 0
     if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
      uncUp_zhp = yzhUp-yzh
      uncUp_whp = ywhUp-ywh

     xsecTotUp.append( tot+math.sqrt(uncUp_zp*uncUp_zp+uncUp_wp*uncUp_wp + uncUp_zhp*uncUp_zhp+uncUp_whp*uncUp_whp) )

     uncDown_zp = yz-yzDown
     uncDown_wp = yw-ywDown
     uncDown_zhp =0
     uncDown_whp =0
     if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
      uncDown_zhp = yzh-yzhDown
      uncDown_whp = ywh-ywhDown
 
     xsecTotDown.append( tot-math.sqrt(uncDown_zp*uncDown_zp+uncDown_wp*uncDown_wp + uncDown_zhp*uncDown_zhp+uncDown_whp*uncDown_whp) )


     shade_x.append(xw)
     shade_y.append( tot+math.sqrt(uncUp_zp*uncUp_zp+uncUp_wp*uncUp_wp + uncUp_zhp*uncUp_zhp+uncUp_whp*uncUp_whp) )


    if options.debug: print " tot ",tot
    xsecTot.append(tot)

   if options.theoryUnc:
    for i in range( len(MassXsec)-1, -1, -1 ):
     shade_x.append(MassXsec[i])
     shade_y.append(xsecTotDown[i])

   gtheory = ROOT.TGraphErrors(len(MassXsec),MassXsec,xsecTot)
   gtheory.SetLineColor(ROOT.kRed)
   gtheory.SetLineWidth(3)
   if options.theoryUnc:
    gtheoryUP = ROOT.TGraphErrors(len(MassXsec),MassXsec,xsecTotUp)
    gtheoryUP.SetLineColor(ROOT.kRed-2)
    gtheoryUP.SetLineWidth(3)
    gtheoryDOWN = ROOT.TGraphErrors(len(MassXsec),MassXsec,xsecTotDown)
    gtheoryDOWN.SetLineColor(ROOT.kRed-2)
    gtheoryDOWN.SetLineWidth(3)
    gtheorySHADE = ROOT.TGraphErrors(len(shade_x),shade_x,shade_y)
    gtheorySHADE.SetLineColor(ROOT.kRed-2)
    gtheorySHADE.SetLineWidth(3)


print " opening limit file ",args[0]
f=ROOT.TFile(args[0])
limit=f.Get("limit")
data={}

def rescaleaxis(g,scale=1000.):
    N = g.GetN()
    x = g.GetX()
    for i in range(N):
        x[i] *= scale
    g.GetHistogram().Delete()
    g.SetHistogram(0)
    return

print " going to loop on event in limit! "
for event in limit:
    mhTeV = event.mh/1000.
    if float(mhTeV)<options.minX or float(mhTeV)>options.maxX:
        continue
    
    if not (mhTeV in data.keys()):
        data[mhTeV]={}
    if options.debug:    print "mhTeV ",mhTeV
    lim = event.limit*scaleLimits[str(int(event.mh))]
    if event.quantileExpected<0:            
        data[mhTeV]['obs']=lim
    if event.quantileExpected>0.02 and event.quantileExpected<0.03:            
        data[mhTeV]['-2sigma']=lim
    if event.quantileExpected>0.15 and event.quantileExpected<0.17:            
        data[mhTeV]['-1sigma']=lim
    if event.quantileExpected>0.49 and event.quantileExpected<0.51:            
        if options.debug:
         print "event.limit ",event.limit
         print "scaleLimits[str(int(mhTeV))] ",scaleLimits[str(int(event.mh))]
         print "lim ",lim
        data[mhTeV]['exp']=lim
    if event.quantileExpected>0.83 and event.quantileExpected<0.85:            
        data[mhTeV]['+1sigma']=lim
    if event.quantileExpected>0.974 and event.quantileExpected<0.976:            
        data[mhTeV]['+2sigma']=lim

print "initializing TGraph"
mean=ROOT.TGraphAsymmErrors()
mean.SetName("mean")

band68=ROOT.TGraphAsymmErrors()
band68.SetName("band68")
band95=ROOT.TGraphAsymmErrors()
band95.SetName("band95")
bandObs=ROOT.TGraph()
bandObs.SetName("bandObs")

line_plus1=ROOT.TGraph()
line_plus1.SetName("line_plus1")

line_plus2=ROOT.TGraph()
line_plus2.SetName("line_plus2")

line_minus1=ROOT.TGraph()
line_minus1.SetName("line_minus1")

line_minus2=ROOT.TGraph()
line_minus2.SetName("line_minus2")


print " start loop on data"
N=0
my_data_file = open(filename+'.txt', 'w')
my_data_file.write('mass limit\n')

print " data ",data
print data.iteritems()

for mass,info in data.iteritems():
    print 'Setting mass',mass,info

    if not ('exp' in info.keys() and '+1sigma' in info.keys() and '+2sigma' in info.keys() and '-1sigma' in info.keys() and '-2sigma' in info.keys()):
        print 'Incomplete file'
        continue
    if options.blind==0 and not ('obs' in info.keys()):
        print 'Incomplete file'
        continue    
    
    mean.SetPoint(N,mass,info['exp'])    
    print "################# LIMIT ##################"
    print "mass ",mass
    print "exp ",info['exp']
    my_data_file.write(str(mass)+" "+str(info['exp'])+'\n')
    band68.SetPoint(N,mass,info['exp'])
    band95.SetPoint(N,mass,info['exp'])
    line_plus1.SetPoint(N,mass,info['+1sigma'])
    line_plus2.SetPoint(N,mass,info['+2sigma'])
    line_minus1.SetPoint(N,mass,info['-1sigma'])
    line_minus2.SetPoint(N,mass,info['-2sigma'])

    if options.blind==0: bandObs.SetPoint(N,mass,info['obs'])
    band68.SetPointError(N,0.0,0.0,info['exp']-info['-1sigma'],info['+1sigma']-info['exp'])
    band95.SetPointError(N,0.0,0.0,info['exp']-info['-2sigma'],info['+2sigma']-info['exp'])
    N=N+1

my_data_file.close()
mean.Sort()
band68.Sort()
band95.Sort()
if options.blind==0: bandObs.Sort()
line_plus1.Sort()    
line_plus2.Sort()    
line_minus1.Sort()    
line_minus2.Sort()    




band68.SetFillColor(ROOT.kGreen+1)
band68.SetLineWidth(3)
band68.SetLineColor(ROOT.kWhite)
band68.SetLineStyle(0)
band68.SetMarkerStyle(0)

band95.SetFillColor(ROOT.kOrange)
band95.SetLineColor(ROOT.kWhite)

bandObs.SetLineWidth(3)
bandObs.SetLineColor(ROOT.kBlack)
bandObs.SetMarkerStyle(20)

mean.SetLineWidth(2)
mean.SetLineColor(ROOT.kBlack)
mean.SetLineStyle(2)

line_plus1.SetLineWidth(1)
line_plus1.SetLineColor(ROOT.kGreen+1)

line_plus2.SetLineWidth(1)
line_plus2.SetLineColor(ROOT.kOrange)

line_minus1.SetLineWidth(1)
line_minus1.SetLineColor(ROOT.kGreen+1)

line_minus2.SetLineWidth(1)
line_minus2.SetLineColor(ROOT.kOrange)

if oneSignal == True:
 thesignal = options.sig.replace("inc","")
 filenameTH = "$CMSSW_BASE/src/CMGTools/VVResonances/scripts/theoryXsec/%s.root"%thesignal
 if options.sig.find("VBF") !=-1 and options.sig.find("prime") !=-1: filenameTH = filenameTH.replace("VBF","HVTC")
 thFile       = ROOT.TFile.Open(filenameTH,'READ')   
 print "Opening file " ,thFile.GetName()
 gtheory      = thFile.Get("gtheory")

 if options.theoryUnc:
  gtheoryUP    = thFile.Get("gtheoryUP")
  gtheoryDOWN  = thFile.Get("gtheoryDOWN")
  gtheorySHADE = thFile.Get("grshade")

 print " going to rescale axis"
 rescaleaxis(gtheory,1	)
 if options.theoryUnc:
  rescaleaxis(gtheoryUP,1	)
  rescaleaxis(gtheoryDOWN,1 )
  rescaleaxis(gtheorySHADE,1)

gtheory     .SetName("%s_gtheory"    %options.sig)
gtheory.SetLineColor(ROOT.kRed)
gtheory.SetLineWidth(3)
if options.theoryUnc:
 gtheoryUP   .SetName("%s_gtheoryUP"  %options.sig)
 gtheoryDOWN .SetName("%s_gtheoryDOWN"%options.sig)
 gtheorySHADE.SetName("%s_grshade"    %options.sig)
 gtheorySHADE.SetLineColor(0)
 gtheorySHADE.SetFillColor(ROOT.kRed)
 gtheorySHADE.SetFillStyle(3013)
 gtheoryUP.SetLineColor(ROOT.kRed)
 gtheoryDOWN.SetLineColor(ROOT.kRed)
 gtheoryUP.SetLineWidth(1)
 gtheoryDOWN.SetLineWidth(1)
# thFile.Close()

#plotting information
H_ref = 800; 
W_ref = 800;
W = W_ref
H = H_ref

T = 0.08*H_ref
B = 0.12*H_ref 
L = 0.15*W_ref
R = 0.04*W_ref
c=ROOT.TCanvas("c","c",50,50,W,H)
c.SetFillColor(0)
c.SetBorderMode(0)
c.SetFrameFillStyle(0)
c.SetFrameBorderMode(0)
c.SetLeftMargin( L/W )
c.SetRightMargin( R/W )
c.SetTopMargin( T/H )
c.SetBottomMargin( B/H )
#c.SetTickx(0)
#c.SetTicky(0)
c.GetWindowHeight()
c.GetWindowWidth()
c.SetLogy()
# c.SetGrid()
c.SetLogy()
c.cd()

Model = "B"
VBFtype="ggF "
if "prime" in options.sig: VBFtype="DY "
if "VBF" in options.sig:
 VBFtype="VBF "
 Model = "C"
if "WprimeWZ"  in options.sig:
  ltheory="#sigma_{TH}#times BR(W'#rightarrowWZ) HVT_{"+Model+"}"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"W' #rightarrow WZ) [pb]  "
  xtitle = "M_{"+VBFtype+"W'} [TeV]"
if "BulkGWW" in options.sig:
  ltheory="#sigma_{TH}#times BR(G_{Bulk}#rightarrowWW) #tilde{k}=0.5"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"G_{Bulk} #rightarrow WW) [pb]  "
  xtitle = "M_{G_{Bulk}} [TeV]"
if "BulkGZZ" in options.sig:
  ltheory="#sigma_{TH}#times BR(G_{Bulk}#rightarrowZZ) #tilde{k}=0.5"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"G_{Bulk} #rightarrow ZZ) [pb]  "
  xtitle = "M_{G_{Bulk}} [TeV]"
if "RadionWW" in options.sig:
  ltheory="#sigma_{TH}#times BR(Rad#rightarrowWW)"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"Rad #rightarrow WW) [pb]  "
  xtitle = "M_{Rad} [TeV]"
if "RadionZZ" in options.sig:
  ltheory="#sigma_{TH}#times BR(Rad#rightarrowZZ)"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"Rad #rightarrow ZZ) [pb]  "
  xtitle = "M_{Rad} [TeV]"
if "ZprimeWW"  in options.sig:
  ltheory="#sigma_{TH}#times BR(Z'#rightarrowWW) HVT_{"+Model+"}"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"Z' #rightarrow WW) [pb]  "
  xtitle = "M_{Z'} [TeV]"
if "Vprime"  in options.sig:
  ltheory="#sigma_{TH}#times BR(V'#rightarrowVV+VH) HVT_{"+Model+"}"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"V' #rightarrow VV+VH) [pb]  "
  xtitle = "M_{V'} [TeV]"
if "VprimeVH"  in options.sig:
  ltheory="#sigma_{TH}#times BR(V'#rightarrowVH) HVT_{"+Model+"}"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"V' #rightarrow VH) [pb]  "
  xtitle = "M_{V'} [TeV]"
if "VprimeWV"  in options.sig:
  ltheory="#sigma_{TH}#times BR(V'#rightarrowWV) HVT_{"+Model+"}"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"V' #rightarrow WV) [pb]  "
  xtitle = "M_{V'} [TeV]"
if "BulkGVV"  in options.sig:
  ltheory="#sigma_{TH}#times BR(G_{Bulk}#rightarrowVV) #tilde{k}=0.5"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"G_{Bulk} #rightarrow VV) [pb]  "
  xtitle = "M_{G_{Bulk}} [TeV]"
if "RadionVV"  in options.sig:
  ltheory="#sigma_{TH}#times BR(Rad#rightarrowVV)"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"Rad #rightarrow VV) [pb]  "
  xtitle = "M_{Rad} [TeV]"
if "ZprimeZH"  in options.sig:
  ltheory="#sigma_{TH}#times BR(Z'#rightarrowZH) HVT_{"+Model+"}"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"Z' #rightarrow ZH) [pb]  "
  xtitle = "M_{Z'} [TeV]"
if "WprimeWH"  in options.sig:
  ltheory="#sigma_{TH}#times BR(W'#rightarrowWH) HVT_{"+Model+"}"
  ytitle ="#sigma x #bf{#it{#Beta}}("+VBFtype+"W' #rightarrow WH) [pb]  "
  xtitle = "M_{W'} [TeV]"
    
frame=c.DrawFrame(options.minX,options.minY,options.maxX,options.maxY)
frame.GetXaxis().SetTitle(xtitle)
frame.GetXaxis().SetTitleOffset(0.9)
frame.GetXaxis().SetTitleSize(0.05)

frame.GetYaxis().SetTitle(ytitle)
frame.GetYaxis().SetTitleSize(0.05)
frame.GetYaxis().SetTitleOffset(1.15)

frame.Draw()

print " frame done "
band95.Draw("3same")
band68.Draw("3same")
# band68.Draw("XLsame")
line_plus1.Draw("Lsame")
line_plus2.Draw("Lsame")
line_minus1.Draw("Lsame")
line_minus2.Draw("Lsame")
if len(data) ==1:
 mean.SetMarkerStyle(20)
 mean.Draw("LPsame")
else:
 mean.Draw("Lsame")
if options.debug: print " mean should be there"
gtheory.Draw("Lsame")
if options.theoryUnc: gtheorySHADE.Draw("Fsame")

c.SetLogy(options.log)

if options.debug: print " I have c "

leg  = ROOT.TLegend(0.4,0.6602591,0.9446734,0.9011917)
leg2 = ROOT.TLegend(0.4,0.6602591,0.9446734,0.9011917)
leg.SetTextSize(0.028)
leg.SetLineColor(1)
leg.SetShadowColor(0)
leg.SetLineStyle(0)
leg.SetLineWidth(0)
leg.SetFillColor(ROOT.kWhite)
# leg.SetFillStyle(0)
leg.SetMargin(0.35)
leg2.SetTextSize(0.028)
leg2.SetLineColor(0)
leg2.SetShadowColor(0)
leg2.SetLineStyle(0)
leg2.SetLineWidth(0)
leg2.SetFillColor(0)
leg2.SetFillStyle(0)
leg2.SetMargin(0.35)
leg.SetBorderSize(0)

leg3 = ROOT.TLegend(0.4,0.5,0.9446734,0.6)
leg3.SetTextSize(0.028)
leg3.SetLineColor(0)
leg3.SetShadowColor(0)
leg3.SetLineStyle(0)
leg3.SetLineWidth(0)
leg3.SetFillColor(ROOT.kWhite)
leg3.SetBorderSize(0)

if options.blind==0: leg.AddEntry(bandObs, "Observed", "Lp")
leg.AddEntry(band68, "Expected #pm 1 std. deviation", "f")
leg.AddEntry(band95 , "Expected #pm 2 std. deviation", "f")
leg.AddEntry(gtheory, ltheory, "L")

if options.debug: print " now you have the band legend"
if not options.blind: leg2.AddEntry(bandObs, " ", "")
leg2.AddEntry(mean, " ", "L")
leg2.AddEntry(mean, " ", "L")
leg2.AddEntry(gtheorySHADE, " ", "F")
      
if options.debug: print " now you have the legend "

if options.final==1:
 cmslabel_final(c,options.period,11)
elif options.final==2:
 cmslabel_empty(c,options.period,10)
else:
 cmslabel_prelim(c,options.period,11)
leg.Draw()
leg2.Draw()
#leg3.Draw()
c.Update()
c.RedrawAxis()

if options.blind==0:
    bandObs.Draw("PLsame")

c.SaveAs(filename+".png")    
c.SaveAs(filename+".pdf")    
c.SaveAs(filename+".C")    

startmass = 1.3
outf = open('log_%s.txt'%filename,'w')
i=startmass
while i < 6.:
 i+=0.01 
 y_exp = mean.Eval(i)
 if y_exp > gtheory.Eval(i) and mean.Eval(startmass) < gtheory.Eval(startmass) :
   outf.write("Expected excluded mass is "+str(i)+" TeV with signal strenght "+str(y_exp)+", theory is "+str(gtheory.Eval(i))+"\n")
   print "Expected excluded mass is "+str(i)+" TeV with signal strenght "+str(y_exp)+", theory is "+str(gtheory.Eval(i))
   break

if options.blind==0:
 
 exclMass = 0
 i=startmass
 while i < 6.:
  i+=0.01 
  y_obs = bandObs.Eval(i)
  if y_obs > gtheory.Eval(i) and bandObs.Eval(startmass)< gtheory.Eval(startmass):
   outf.write("Observed excluded mass "+str(i)+" TeV with signal strenght "+str(y_obs)+", theory is "+str(gtheory.Eval(i))+"\n")
   print "Observed excluded mass "+str(i)+" TeV with signal strenght "+str(y_obs)+", theory is "+str(gtheory.Eval(i))
   exclMass = i
   break

 # these are needed because for some signals we are crossing the line multiple times
 for j in range(100):
  i=exclMass
  while i < 6.:
   i+=0.01
   y_obs = bandObs.Eval(i)
   if y_obs < gtheory.Eval(i) and bandObs.Eval(startmass)< gtheory.Eval(startmass):
    outf.write("Observed NOT excluded mass "+str(i)+" TeV with signal strenght "+str(y_obs)+"\n")
    exclMass = i
    break



outf.close()



fout=ROOT.TFile(filename+".root","RECREATE")
fout.cd()
c.Write()
band68.Write()
band95.Write()
bandObs.Write()
line_plus1.Write()    
line_plus2.Write()    
line_minus1.Write()    
line_minus2.Write()    

fout.Close()
f.Close()
