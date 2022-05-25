#!/usr/bin/env python

import ROOT
import optparse
from CMGTools.VVResonances.plotting.CMS_lumi import *
from CMGTools.VVResonances.plotting.tdrstyle import *
from time import sleep
from array import array
import numpy as np
ROOT.gROOT.SetBatch(True)
parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",default='limit_compare.root',help="Limit plot")
parser.add_option("-n","--name",dest="name",default='comparisons',help="additional name for output file (include compareB2G18002 with signal BGWW to compare this analysis with 16+17 also)")
parser.add_option("-x","--minX",dest="minX",type=float,help="minimum x",default=1.3)
parser.add_option("-X","--maxX",dest="maxX",type=float,help="maximum x",default=6.0)
parser.add_option("-y","--minY",dest="minY",type=float,help="minimum y",default=0.00001)
parser.add_option("-Y","--maxY",dest="maxY",type=float,help="maximum y",default=0.1)
parser.add_option("-b","--blind",dest="blind",type=int,help="Not do observed ",default=1)
parser.add_option("-l","--log",dest="log",type=int,help="Log plot",default=1)
parser.add_option("-s","--signal",dest="sig",type=str,help="Signal sample",default='BulkGWW')
parser.add_option("-t","--titleX",dest="titleX",default='M_{X} (GeV)',help="title of x axis")
parser.add_option("-T","--titleY",dest="titleY",default="#sigma x BR(G_{Bulk} #rightarrow WW) (pb)  ",help="title of y axis")
parser.add_option("--limitname",dest="limitname",default="newbaseline")
parser.add_option("-p","--period",dest="period",default='ALL',help="period")
parser.add_option("-f","--final",dest="final",type=int, default=1,help="Preliminary or not")

plotB2G18002 = False # B2G-18-002 VV CMS all had - Eur. Phys. J. C 80 (2020) 237
plotATLASVVsemilep=False # https://www.hepdata.net/record/ins1793572 - Eur.Phys.J.C 80 (2020) 1165, 2020.
plotATLASVVhad=False  # https://www.hepdata.net/record/91052 - JHEP 09 (2019) 091, 2019.
plotATLASVHhad = False # https://www.hepdata.net/record/ins1806507 - Phys.Rev.D 102 (2020) 112008, 2020.
plotCMSsemilep = False # B2G-19-002 pas CMS semi lep Run2 WV/WH
plotCMSsemilepZnunu = False # B2G-20-008 CMS Z(nunu)V(qq) semilep Run2
plotCMSZHsemilep = False # B2G-19-006 CMS Z(lep) H(had) semilep Run2 http://cms-results.web.cern.ch/cms-results/public-results/publications/B2G-19-006/index.html
plotCMS2016DIBcombo = False # B2G-18-006 2016 diboson combination https://www.hepdata.net/record/ins1737724 
plotB2G17002 = False #B2G-17-002 2016 VH had https://cms-results.web.cern.ch/cms-results/public-results/publications/B2G-17-002/index.html
(options,args) = parser.parse_args()
#define output dictionary

scaleBR = True
limitname=options.limitname
setTDRStyle()

def getLegend(x1=0.50650010112,y1=0.523362,x2=0.8790202143,y2=0.8279833):
  legend = ROOT.TLegend(x1,y1,x2,y2)
  legend.SetTextSize(0.032)
  legend.SetLineColor(0)
  legend.SetShadowColor(0)
  legend.SetLineStyle(1)
  legend.SetLineWidth(1)
  legend.SetFillColor(0)
  legend.SetFillStyle(0)
  legend.SetMargin(0.35)
  return legend

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




oname = options.sig+"_"+options.period+"_"+options.name

Model = "B"
VBFtype="ggF "
if "prime" in options.sig: VBFtype="DY "
if "VBF" in options.sig:
 VBFtype="VBF "
 Model = "C"
if "WprimeWZ"  in options.sig:
  ltheory="#sigma_{TH}#times BR(W'#rightarrowWZ) HVT_{"+Model+"}"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"W' #rightarrow WZ) [pb]  "
  titleX = "M_{"+VBFtype+"W'} [TeV]"
  plotCMSsemilep = True
  plotATLASVVsemilep=True
  plotCMSsemilepZnunu = True
  if "VBF" not in options.sig:
    plotB2G18002 = True
    plotATLASVVhad=True
if "BulkGWW" in options.sig:
  ltheory="#sigma_{TH}#times BR(G_{Bulk}#rightarrowWW) #tilde{k}=0.5"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"G_{Bulk} #rightarrow WW) [pb]  "
  titleX = "M_{G_{Bulk}} [TeV]"
  if "compareB2G18002" not in options.name:
    plotCMSsemilep = True
  if "VBF" not in options.sig:
    plotB2G18002 = True
if "BulkGZZ" in options.sig:
  ltheory="#sigma_{TH}#times BR(G_{Bulk}#rightarrowZZ) #tilde{k}=0.5"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"G_{Bulk} #rightarrow ZZ) [pb]  "
  titleX = "M_{G_{Bulk}} [TeV]"
  if "compareB2G18002" not in options.name:
  #if "compareB2G18002" not in options.name and "no2p5TeV" not in options.name:
    plotCMSsemilepZnunu = True
    if "VBF" not in options.sig:
      plotCMS2016DIBcombo = True
  if "VBF" not in options.sig:
    plotB2G18002 = True
if "RadionWW" in options.sig:
  ltheory="#sigma_{TH}#times BR(Rad#rightarrowWW)"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"Rad #rightarrow WW) [pb]  "
  titleX = "M_{Rad} [TeV]"
  plotCMSsemilep = True
  plotATLASVVsemilep = True
if "RadionZZ" in options.sig:
  ltheory="#sigma_{TH}#times BR(Rad#rightarrowZZ)"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"Rad #rightarrow ZZ) [pb]  "
  titleX = "M_{Rad} [TeV]"
  plotATLASVVsemilep = True
  plotCMSsemilepZnunu = True
if "ZprimeWW"  in options.sig:
  ltheory="#sigma_{TH}#times BR(Z'#rightarrowWW) HVT_{"+Model+"}"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"Z' #rightarrow WW) [pb]  "
  titleX = "M_{Z'} [TeV]"
  plotCMSsemilep = True
  plotATLASVVsemilep=True
  if "VBF" not in options.sig:
    plotB2G18002= True
    plotATLASVVhad=True
if "VprimeWV"  in options.sig:
  ltheory="#sigma_{TH}#times BR(V'#rightarrow(WV)) HVT_{"+Model+"}"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"V' #rightarrow WV) [pb]  "
  titleX = "M_{V'} [TeV]"
  if "VBF" not in options.sig:
    plotATLASVVhad=True
if "Vprime"  in options.sig and "WV" not in options.sig and "VHinc" not in options.sig:
  ltheory="#sigma_{TH}#times BR(V'#rightarrow(VV+VH)) HVT_{"+Model+"}"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"V' #rightarrow VV+VH) [pb]  "
  titleX = "M_{V'} [TeV]"
  if "VBF" not in options.sig:
    plotCMS2016DIBcombo = True
if "VprimeVH"  in options.sig: 
  ltheory="#sigma_{TH}#times BR(V'#rightarrow(VH)) HVT_{"+Model+"}"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"V' #rightarrow VH) [pb]  "
  titleX = "M_{V'} [TeV]"
  if "VBF" not in options.sig:
    #plotATLASVHhad=True
    plotB2G17002=True
    #  plotCMS2016DIBcombo = True
if "BulkGVV"  in options.sig:
  ltheory="#sigma_{TH}#times BR(G_{Bulk}#rightarrowVV) #tilde{k}=0.5"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"G_{Bulk} #rightarrow VV) [pb]  "
  titleX = "M_{G_{Bulk}} [TeV]"
  if "VBF" not in options.sig:
    plotCMS2016DIBcombo = True # NB remember dib combination has both VV & HH
if "RadionVV"  in options.sig:
  ltheory="#sigma_{TH}#times BR(Rad#rightarrowVV)"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"Rad #rightarrow VV) [pb]  "
  titleX = "M_{Rad} [TeV]"
  plotATLASVVsemilep = True
if "ZprimeZH"  in options.sig:
  ltheory="#sigma_{TH}#times BR(Z'#rightarrowZH) HVT_{"+Model+"}"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"Z' #rightarrow ZH) [pb]  "
  titleX = "M_{Z'} [TeV]"
  plotCMSZHsemilep = True
  if "VBF" not in options.sig:
    plotCMS2016DIBcombo = True
    plotATLASVHhad = True
    plotB2G17002 = True
if "WprimeWH"  in options.sig:
  ltheory="#sigma_{TH}#times BR(W'#rightarrowWH) HVT_{"+Model+"}"
  titleY ="#sigma x #bf{#it{#Beta}}("+VBFtype+"W' #rightarrow WH) [pb]  "
  titleX = "M_{W'} [TeV]"
  if "VBF" not in options.sig:
    plotCMS2016DIBcombo = True
    plotCMSsemilep = True
    plotATLASVHhad = True
    plotB2G17002= True
title = ["This analysis"]
files = ["Limits_"+options.sig+"_13TeV_Run2_data_ggDYVBF_VVVH_"+limitname+".root"]

if options.name.find("compareB2G18002") !=-1:
  title = ["This analysis (78 fb^{-1})","This analysis (138 fb^{-1})"]
  files = ["Limits_"+options.sig+"_13TeV_1617_data_ggDYVBF_VVVH_partial_"+limitname+".root","Limits_"+options.sig+"_13TeV_Run2_data_ggDYVBF_VVVH_"+limitname+".root"]
#if options.name.find("no2p5TeV") !=-1:
#  title = ["with","without"]
#  files = ["Limits_"+options.sig+"_13TeV_Run2_data_ggDYVBF_VVVH_"+limitname+".root","Limits_VBF_BulkGZZ_data_VBFggDY_VVVH_Run2_afterpreapproval_no2p5TeV.root"]


scaleLimits = {}
masses = array('d',[i*100. for i in range(8,61)])
massesTeV = array('d',[i*0.1 for i in range(8,61)])
if scaleBR:
  x, y = array( 'd' ), array( 'd' )

  fin = ROOT.TFile.Open("results_Run2/AllCat_workspace/workspace_JJ_"+options.sig+"_VBF_VVVH_13TeV_Run2_data_newbaseline.root","READ")
  w = fin.Get("w")


  for m in masses:
    scaleLimits[str(int(m))] =0.001 
    argset = ROOT.RooArgSet()
    MH=w.var("MH")
    argset.add(MH)
    MH.setVal(m)



    if oneSignal == False:
      func1 = w.function(signal1+'_JJ_VV_HPHP_13TeV_Run2_sigma')
      func2 = w.function(signal2+'_JJ_VV_HPHP_13TeV_Run2_sigma')
      if  options.sig == 'VprimeVHinc' or options.sig == 'VBF_VprimeVHinc':
        func1 = w.function(signal1+'inc_JJ_VV_HPHP_13TeV_Run2_sigma')
        func2 = w.function(signal2+'inc_JJ_VV_HPHP_13TeV_Run2_sigma')
      scaleLimits[str(int(m))] = ROOT.TMath.Exp(func1.getVal(argset))+ROOT.TMath.Exp(func2.getVal(argset))
      if options.sig == 'Vprime' or options.sig == 'VBF_Vprime':
        try:
          func3 = w.function(signal3+'inc_JJ_VV_HPHP_13TeV_Run2_sigma')
          func4 = w.function(signal4+'inc_JJ_VV_HPHP_13TeV_Run2_sigma')
        except:
          func3 = w.function(signal3+'_JJ_VV_HPHP_13TeV_Run2_sigma')
          func4 = w.function(signal4+'_JJ_VV_HPHP_13TeV_Run2_sigma')
        scaleLimits[str(int(m))] = scaleLimits[str(int(m))]+ROOT.TMath.Exp(func3.getVal(argset))+ROOT.TMath.Exp(func4.getVal(argset))
    else:
      func = w.function(options.sig+'_JJ_VV_HPHP_13TeV_Run2_sigma')
      scaleLimits[str(int(m))] = ROOT.TMath.Exp(func.getVal(argset))

    print "scaleLimits["+str(int(m))+"]", scaleLimits[str(int(m))] 
    if "prime" not in options.sig or "VBF" in options.sig:
      print " rescaling limit !!!!! "
      scaleLimits[str(int(m))] = scaleLimits[str(int(m))]*10
      if (m > 3000. and "VBF" in options.sig) or m>5000.:
        print "extra rescaling for high mx "
        scaleLimits[str(int(m))] = scaleLimits[str(int(m))]*10
        if (m > 5000. and "VBF" in options.sig) or (m == 5000. and "VBF_Radion" not in options.sig)  or (options.sig == "VBF_ZprimeWW" and m >= 4400.)or (options.sig == "VBF_WprimeWZ" and m >= 4800.) or (options.sig == "VBF_BulkGZZ" and m > 4900.)  or (options.sig == "VBF_ZprimeZHinc" and m >= 4500.) :
          #if m > 5000. and "VBF" in options.sig:
          print "double extra rescaling for high mx "
          scaleLimits[str(int(m))] = scaleLimits[str(int(m))]*10
          if (options.sig == "VBF_ZprimeWW" and m >= 5400.) or (options.sig == "VBF_BulkGZZ" and m >= 5700.) or (options.sig == "VBF_ZprimeZHinc" and m >= 5500.) or (options.sig == "VBF_VprimeVHinc" and m >= 5600.) or (options.sig == "VBF_BulkGZZ" and m >= 5700.) or (options.sig == "VBF_BulkGWW" and m >= 5800.) or (options.sig == "VBF_BulkGVV" and m == 6000.) or (options.sig == "VBF_WprimeWHinc" and m == 6000.) or (options.sig == "VBF_VprimeWV" and m >= 5900.) or (options.sig == "VBF_Vprime" and m >= 5600. and m<6000.)  or (options.sig == "VBF_WprimeWZ" and m == 6000.) :
            print "triple! extra rescaling for high mx "
            scaleLimits[str(int(m))] = scaleLimits[str(int(m))]*10


else:
  for m in masses:
    print " m ",m
    #scaleLimits[str(int(m))] = 1.*0.001 #NB this is a quick fix for ZprimeZH!
    scaleLimits[str(int(m))] = 1.*0.001*0.584 #multiply by H BR


leg = getLegend(0.3,0.6,0.8,0.9)
leg.AddEntry(0,"95% CL exp. upper limits","")
leg.SetLineWidth(0)
#leg.AddEntry(0,"upper limits","")
tgraphs = []
for t,fname in zip(title,files):
        print "*************** fname ",fname
	f=ROOT.TFile(fname)
        #print fname
	limit=f.Get("limit")
	data={}
	for event in limit:
                mhTeV = event.mh/1000.
		if float(mhTeV)<options.minX or float(mhTeV)>options.maxX:
		    continue
		
		if not (mhTeV in data.keys()):
		    data[mhTeV]={}

                print "mhTeV ",mhTeV

                lim = event.limit*scaleLimits[str(int(event.mh))]
		if event.quantileExpected>0.49 and event.quantileExpected<0.51:            
                  print "event.limit 0.5",event.limit
 
                  print "lim ",lim
                  data[mhTeV]['exp']=lim
		
		
		
	line_plus1=ROOT.TGraph()
	line_plus1.SetName(f.GetName().replace(".root",""))



	N=0
	for mass,info in data.iteritems():
	    print 'Setting mass',mass,info

	    if not ('exp' in info.keys()):
	        print 'Incomplete file'
	        continue
    

	    line_plus1.SetPoint(N,mass,info['exp'])
	    N=N+1
	
	line_plus1.Sort()    
	tgraphs.append(line_plus1)  
	leg.AddEntry(line_plus1,t,"L")


######## Add here limits from other Analyses to compare


# B2G-18-002 had 16+17 #https://gitlab.cern.ch/tdr/papers/B2G-18-002/-/blob/master/figures/limits_signal_combo_2016_2017.C                                                          
if plotB2G18002:
  VV18002 = ROOT.TGraph("limitsB2G_18_002/limit_"+options.sig+"_1617_B2G_18_002.txt","%lg %lg")
  VV18002.SetLineColor(1);
  VV18002.SetLineStyle(2);
  VV18002.SetLineWidth(3);
  VV18002.SetMarkerStyle(20);
  leg.AddEntry(VV18002,"EPJC 80 (2020) 237 (77fb^{-1})","L") # "B2G-18-002 (16+17)","L")

### ATLAS VH all had Run2                                                                                                                                                             
if plotATLASVHhad:
  thesignal=options.sig.replace("inc","")
  VHhadATLAS = ROOT.TGraph("ATLASresults/ATLAS_"+thesignal+"_HAD.txt","%lg %lg")
  VHhadATLAS.SetLineColor(591)
  VHhadATLAS.SetLineStyle(1);
  VHhadATLAS.SetLineWidth(3);
  leg.AddEntry(VHhadATLAS,"Phys.Rev.D 102 (2020) 112008 (139 fb^{-1})","L")


# ATLAS VV (HVT) all had Run2
if plotATLASVVhad:
  thesignal=options.sig.replace("inc","")
  VVhadATLAS = ROOT.TGraph("ATLASresults/ATLAS_"+thesignal+"_HVT_HAD.txt","%lg %lg")
  VVhadATLAS.SetLineColor(880)
  VVhadATLAS.SetLineStyle(1);
  VVhadATLAS.SetLineWidth(3);
  leg.AddEntry(VVhadATLAS,"JHEP 09 (2019) 091 (139 fb^{-1})","L")


### ATLAS VV (HVT) semilep Run2                                                                                                                                                      
if plotATLASVVsemilep:
  VVsemilepATLAS = ROOT.TGraph("ATLASresults/ATLAS_"+options.sig+"_SEMILEP.txt","%lg %lg")
  VVsemilepATLAS.SetLineColor(591)
  VVsemilepATLAS.SetLineStyle(2);
  VVsemilepATLAS.SetLineWidth(3);
  leg.AddEntry(VVsemilepATLAS,"EPJC 80 (2020) 1165 (139 fb^{-1})","L") # ATLAS semilep (Run2)","L")

#### CMS B2G-19-002 semilep Run2
if plotCMSsemilep:
  thesignal=options.sig.replace("inc","")
  CMS19002semilep = ROOT.TGraph("Limits_B2G-19-002-pas/limit_"+thesignal+"_Run2_B2G_19_002.txt","%lg %lg")
  CMS19002semilep.SetLineColor(417);
  CMS19002semilep.SetLineStyle(4);
  CMS19002semilep.SetLineWidth(3);
  CMS19002semilep.SetMarkerStyle(20);
  leg.AddEntry(CMS19002semilep,"CMS-PAS-B2G-19-002 (137 fb^{-1})","L")


##### CMS B2G-20-008 semilep Run2 Z(nunu)V(qq)
if plotCMSsemilepZnunu:
  CMSZnunuV20008=ROOT.TGraph("Limits_B2G-20-008-pas/limit_"+options.sig+"_Run2_B2G_20_008.txt","%lg %lg")
  CMSZnunuV20008.SetTitle("");
  CMSZnunuV20008.SetLineColor(797);
  CMSZnunuV20008.SetLineStyle(5);
  CMSZnunuV20008.SetLineWidth(3);
  CMSZnunuV20008.SetMarkerStyle(20);
  leg.AddEntry(CMSZnunuV20008,"CMS-PAS-B2G-20-008 (137 fb^{-1})","L")

##### CMS B2G-19-006 semilep Z(lep)H(had) Run2
if plotCMSZHsemilep:
  thesignal=options.sig.replace("inc","")
  CMSZlepH19006=ROOT.TGraph("Limits_B2G-19-006/limit_"+thesignal+"_Run2_B2G_19_006.txt","%lg %lg")
  CMSZlepH19006.SetTitle("");
  CMSZlepH19006.SetLineColor(404);
  CMSZlepH19006.SetLineStyle(4);
  CMSZlepH19006.SetLineWidth(3);
  CMSZlepH19006.SetMarkerStyle(20);
  leg.AddEntry(CMSZlepH19006,"CMS-B2G-19-006 (137 fb^{-1})","L")

#### CMS 2016 DIB combination
if plotCMS2016DIBcombo:
  thesignal=options.sig.replace("inc","")
  CMSdib2016combo=ROOT.TGraph("Limits_DIB_combo2016/limit_"+thesignal+"_2016_B2G_18_006.txt","%lg %lg")
  CMSdib2016combo.SetTitle("");
  CMSdib2016combo.SetLineColor(616);
  CMSdib2016combo.SetLineStyle(6);
  CMSdib2016combo.SetLineWidth(3);
  CMSdib2016combo.SetMarkerStyle(20);
  leg.AddEntry(CMSdib2016combo,"Phys.Lett.B 798 (2019) 134952 (36 fb^{-1})","L")


### CMS 2016 VH had 
if plotB2G17002:
  thesignal=options.sig.replace("inc","")
  CMS2016VHhad=ROOT.TGraph("Limits_B2G-17-002/limit_"+thesignal+"_2016_B2G_17_002.txt","%lg %lg")
  CMS2016VHhad.SetTitle("");
  CMS2016VHhad.SetLineColor(594);
  CMS2016VHhad.SetLineStyle(6);
  CMS2016VHhad.SetLineWidth(3);
  CMS2016VHhad.SetMarkerStyle(20);
  leg.AddEntry(CMS2016VHhad,"EPJ C 77 (2017) 636 (36 fb^{-1})","L")

#plotting information
H_ref = 800; 
W_ref = 800; 
W = W_ref
H = H_ref

T = 0.08*H_ref
B = 0.15*H_ref 
L = 0.12*W_ref
R = 0.04*W_ref
c=ROOT.TCanvas("c","c",W,H)
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
#c.SetLogy()
#c.SetGrid()
#c.SetLogy()
	
frame=c.DrawFrame(options.minX,options.minY,options.maxX,options.maxY)
	
ROOT.gPad.SetTopMargin(0.08)
frame.GetXaxis().SetTitle(titleX)
frame.GetXaxis().SetTitleOffset(0.9)
frame.GetXaxis().SetTitleSize(0.05)

frame.GetYaxis().SetTitle(titleY)
frame.GetYaxis().SetTitleSize(0.05)
frame.GetYaxis().SetTitleOffset(1.15)





c.cd()
frame.Draw()
#cols  = [42,46,49,32,36,39]*3
#tline = [10,9,1,10,9,1]*3
cols  = [632,600,631,615,604,608,634,624,620]*3
tline = [1,3,2,2,3,2]*3
markers = [20,24,23,32,25,21,25,26,29,21,25,31,21,25,23,24,24,31,22]*3
#cols  = [42,46,49,1]*3
#tline = [10,9,1,2]*3

if plotB2G18002: VV18002.Draw("Lsame")
if plotATLASVVhad: VVhadATLAS.Draw("Lsame")
if plotATLASVVsemilep: VVsemilepATLAS.Draw("Lsame")
if plotATLASVHhad: VHhadATLAS.Draw("Lsame")
if plotCMSsemilep: CMS19002semilep.Draw("Lsame")
if plotCMSsemilepZnunu: CMSZnunuV20008.Draw("Lsame")
if plotCMSZHsemilep: CMSZlepH19006.Draw("Lsame")
if plotCMS2016DIBcombo: CMSdib2016combo.Draw("Lsame")
if plotB2G17002: CMS2016VHhad.Draw("Lsame")

for i,g in enumerate(tgraphs):
	g.SetLineStyle(tline[i])
	g.SetLineColor(cols[i])
        g.SetMarkerStyle(markers[i])
        g.SetMarkerColor(cols[i])
	g.SetLineWidth(3)
        if g.GetN() ==1:
          g.Draw("LPsame")
        else:
          g.Draw("Lsame")

c.SetLogy(options.log)
#c.Draw()
leg.Draw("same")
cmslabel_prelim(c,options.period,11)

#c.Update()
#c.RedrawAxis()

c.SaveAs("compareLimits_"+oname+".png")
c.SaveAs("compareLimits_"+oname+".pdf")
c.SaveAs("compareLimits_"+oname+".root")
c.SaveAs("compareLimits_"+oname+".C")
sleep(2)
f.Close()


