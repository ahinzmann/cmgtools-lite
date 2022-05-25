#!/usr/bin/env python
import ROOT
from array import array
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log
import os, sys, re, optparse,pickle,shutil,json
from CMGTools.VVResonances.plotting.tdrstyle import *
setTDRStyle()
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
sys.path.insert(0, "../interactive/") 
import cuts 
ROOT.gROOT.SetBatch(True)


parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output",default='')
parser.add_option("-s","--samples",dest="samples",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for yield in gen sample",default='')
parser.add_option("-v","--vars",dest="vars",help="variable for gen",default='')
parser.add_option("-b","--binsx",dest="binsx",help="bins",default='')
parser.add_option("-g","--genVars",dest="genVars",help="variable for gen",default='')
parser.add_option("-d","--directories",dest="directories",help="list of input directories",default="2016")
#parser.add_option("-l","--lumi",dest="lumi",help="luminosity",default="1.")

(options,args) = parser.parse_args()



binsxStr=options.binsx.split(',')
binsx=[]
for b in binsxStr:
    binsx.append(float(b))

binsz_x=[]
binsz_y=[]
for b in range(0,51): binsz_x.append(0.7+0.7*b/50.0)
for b in range(0,51): binsz_y.append(0.6+0.6*b/50.0)
    
scalexHisto=ROOT.TH1F("scalexHisto","scaleHisto",len(binsx)-1,array('d',binsx))
resxHisto=ROOT.TH1F("resxHisto","resHisto",len(binsx)-1,array('d',binsx))

scaleyHisto=ROOT.TH1F("scaleyHisto","scaleHisto",len(binsx)-1,array('d',binsx))
resyHisto=ROOT.TH1F("resyHisto","resHisto",len(binsx)-1,array('d',binsx))
 
variables=options.vars.split(',')
genVariables=options.genVars.split(',')

doBothLegs = False
leg="l1"
if len(variables)==3 and len(genVariables)==5: 
    doBothLegs = True
    leg="l1l2"

gaussian=ROOT.TF1("gaussian","gaus",0.5,1.5)


superHX= None
superHX_l2= None
superHY= None
superHY_l2= None

print 
sampleTypes=options.samples.split(',')
dataPlotters=[]
folders=[]
folders= options.directories.split(',')
print "folders ",folders
for folder in folders:
    print "folder ",folder
    print "split ",folder.split("/")
    year=folder.split("/")[-2]
    print "year ",year
    print "now working with cuts "
    ctx = cuts.cuts("init_VV_VH.json",year,"dijetbins_random")
    print "lumi for year "+year+" = ",ctx.lumi[year]
    lumirescale=ctx.lumi["Run2"]
    if "," in options.directories and "2018" not in options.directories: lumirescale=ctx.lumi["1617"]
    print "lumirescale ",lumirescale
    luminosity = ctx.lumi[year]/lumirescale

    if len(folders) ==1: luminosity = 1.

    for filename in os.listdir(folder):
        for sampleType in sampleTypes:
            if filename.find(sampleType)!=-1:
                fnameParts=filename.split('.')
                if len(fnameParts)<2: continue
                fname=fnameParts[0]
                ext=fnameParts[1]
                if ext.find("root") ==-1: continue
                dataPlotters.append(TreePlotter(folder+'/'+fname+'.root','AnalysisTree'))
                dataPlotters[-1].setupFromFile(folder+'/'+fname+'.pck')
                dataPlotters[-1].addCorrectionFactor('xsec','tree')
                dataPlotters[-1].addCorrectionFactor('genWeight','tree')
                dataPlotters[-1].addCorrectionFactor('puWeight','tree')
                dataPlotters[-1].addCorrectionFactor(luminosity,'flat')
                if fname.find("QCD_Pt_") !=-1 or fname.find("QCD_HT") !=-1:
                    print "going to apply spikekiller for ",fname
                    dataPlotters[-1].addCorrectionFactor('b_spikekiller','tree')

    data=MergedPlotter(dataPlotters)
    if superHX==None:
        print "create superHX"    
        superHX=data.drawTH2Binned(variables[0]+'/'+genVariables[0]+':'+genVariables[2],options.cut,"1.",binsx,binsz_x) #mvv
        print "created superHX ",superHX
    else: 
        print "Add to superHX"
        superHX.Add(data.drawTH2Binned(variables[0]+'/'+genVariables[0]+':'+genVariables[2],options.cut,"1.",binsx,binsz_x)) 
    if superHY == None:  
        superHY=data.drawTH2Binned(variables[1]+'/'+genVariables[1]+':'+genVariables[2],options.cut,"1.",binsx,binsz_y) #mjet
    else:
        superHY.Add(data.drawTH2Binned(variables[1]+'/'+genVariables[1]+':'+genVariables[2],options.cut,"1.",binsx,binsz_y))    
    if doBothLegs == True:
        if superHX_l2 == None:
            superHX_l2=data.drawTH2Binned(variables[0]+'/'+genVariables[0]+':'+genVariables[4],options.cut,"1.",binsx,binsz_x) #mvv
        else:
            superHX_l2.Add(data.drawTH2Binned(variables[0]+'/'+genVariables[0]+':'+genVariables[4],options.cut,"1.",binsx,binsz_x))
        if superHY_l2 == None: 
            superHY_l2=data.drawTH2Binned(variables[2]+'/'+genVariables[3]+':'+genVariables[4],options.cut,"1.",binsx,binsz_y) #mjet
        else:  superHY_l2.Add(data.drawTH2Binned(variables[2]+'/'+genVariables[3]+':'+genVariables[4],options.cut,"1.",binsx,binsz_y))
    print " done with folder ",folder

print " all folders done"

if doBothLegs == True:
    superHX.Add(superHX_l2)
    print " Added mvv hists"
    superHY.Add(superHY_l2)
    print " Added mjet hists"

label=options.output.split("_")[1]
print "label ",label
f=ROOT.TFile(options.output,"RECREATE")
f.cd()
   

print "########## mvv ###############"
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
   maxbin=0
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
   c1.SaveAs("debug_fit1_mvvres_%s_%s_%i.png"%(label,leg,bin))
   tmpmean = g1.GetParameter(1)
   tmpwidth = g1.GetParameter(2)
   g1 = ROOT.TF1("g1","gaus", tmpmean-(tmpwidth*2),tmpmean+(tmpwidth*2))
   tmp.Fit(g1, "SR")
   c1 =ROOT.TCanvas("c","",800,800)
   tmp.Draw()
   c1.SaveAs("debug_fit2_mvvres_%s_%s_%i.png"%(label,leg,bin))
   tmpmean = g1.GetParameter(1)
   tmpmeanErr = g1.GetParError(1)
   tmpwidth = g1.GetParameter(2)
   tmpwidthErr = g1.GetParError(2)
   scalexHisto.SetBinContent(bin,tmpmean)
   scalexHisto.SetBinError  (bin,tmpmeanErr)
   resxHisto.SetBinContent  (bin,tmpwidth)
   resxHisto.SetBinError    (bin,tmpwidthErr)

print "########## mjet ###############"
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
   c1.SaveAs("debug_fit1_mjres_%s_%s_%i.png"%(label,leg,bin))
   tmpmean = g1.GetParameter(1)
   tmpwidth = g1.GetParameter(2)
   g1 = ROOT.TF1("g1","gaus", tmpmean-(tmpwidth*1.1),tmpmean+(tmpwidth*1.1))
   tmp.Fit(g1, "SR")
   c1 =ROOT.TCanvas("c","",800,800)
   tmp.Draw()
   c1.SaveAs("debug_fit2_mjres_%s_%s_%i.png"%(label,leg,bin))
   tmpmean = g1.GetParameter(1)
   tmpmeanErr = g1.GetParError(1)
   tmpwidth = g1.GetParameter(2)
   tmpwidthErr = g1.GetParError(2)
   scaleyHisto.SetBinContent(bin,tmpmean)
   scaleyHisto.SetBinError  (bin,tmpmeanErr)
   resyHisto.SetBinContent  (bin,tmpwidth)
   resyHisto.SetBinError    (bin,tmpwidthErr)

         
scalexHisto.Write()
scaleyHisto.Write()
resxHisto.Write()
resyHisto.Write()
superHX.Write("dataX")
superHY.Write("dataY")
f.Close()    
