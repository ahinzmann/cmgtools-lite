#!/usr/bin/env python

import ROOT
from array import array
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
from CMGTools.VVResonances.plotting.StackPlotter import StackPlotter
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log
from collections import defaultdict
import os, sys, re, optparse,pickle,shutil,json
sys.path.insert(0, "../interactive/")
import cuts
ROOT.gROOT.SetBatch(True)
ROOT.v5.TFormula.SetMaxima(10000) #otherwise we get an error that the TFormula called by the TTree draw has too many operators when running on the CR
def returnString(func):
    st='0'
    for i in range(0,func.GetNpar()):
        st=st+"+("+str(func.GetParameter(i))+")"+("*MH"*i)
    return st    



parser = optparse.OptionParser()
parser.add_option("-s","--sample",dest="sample",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for shape",default='')
parser.add_option("-o","--output",dest="output",help="Output JSON",default='')
parser.add_option("-V","--MVV",dest="mvv",help="mVV variable",default='')
parser.add_option("-m","--min",dest="mini",type=float,help="min MJJ",default=40)
parser.add_option("-M","--max",dest="maxi",type=float,help="max MJJ",default=160)
parser.add_option("-e","--exp",dest="doExp",type=int,help="useExponential",default=0)
parser.add_option("-f","--fix",dest="fixPars",help="Fixed parameters",default="1")
parser.add_option("-r","--minMX",dest="minMX",type=float, help="smallest Mx to fit ",default=1000.0)
parser.add_option("-R","--maxMX",dest="maxMX",type=float, help="largest Mx to fit " ,default=7000.0)
parser.add_option("-t","--triggerweight",dest="triggerW",action="store_true",help="Use trigger weights",default=False)

(options,args) = parser.parse_args()
#define output dictionary

isVH = False
isHH = False
samples={}

folders = str(args[0]).split(",")
for folder in folders:
    samples[folder] = {}
    for filename in os.listdir(folder):
        if not (filename.find(options.sample)!=-1):
            continue
        if filename.find(".")==-1:
            print "in "+str(filename)+"the separator . was not found. -> continue!"
            continue
        if filename.find("VBF")!=-1 and options.sample.find("VBF")==-1:
            continue

     
        fnameParts=filename.split('.')
        fname=fnameParts[0]
        ext=fnameParts[1]
        if ext.find("root") ==-1:
            continue
            
        mass = float(fname.split('_')[-1])
        if mass < options.minMX or mass > options.maxMX: continue	

        # the 2500.0 mass point of the VBF_BulkGravToZZ signal in one of the three year has only a small number of events. It was used in the analysis but here it was tested the effect of removing it.
        #if mass == 2500.0 and fname.find("VBF_BulkGravToZZ") !=-1:
        #    continue

        samples[folder].update({mass : folder+fname})

        print 'found',filename,'mass',str(mass) 
        if filename.find('hbb')!=-1 or filename.find('hinc')!=-1: isVH=True;
        if filename.find("HH")!=-1: isHH=True; 


leg = options.mvv.split('_')[1]
graphs={'mean':ROOT.TGraphErrors(),'sigma':ROOT.TGraphErrors(),'alpha':ROOT.TGraphErrors(),'n':ROOT.TGraphErrors(),'f':ROOT.TGraphErrors(),'slope':ROOT.TGraphErrors(),'alpha2':ROOT.TGraphErrors(),'n2':ROOT.TGraphErrors(),
        'meanH':ROOT.TGraphErrors(),'sigmaH':ROOT.TGraphErrors(),'alphaH':ROOT.TGraphErrors(),'nH':ROOT.TGraphErrors(),'fH':ROOT.TGraphErrors(),'slopeH':ROOT.TGraphErrors(),'alpha2H':ROOT.TGraphErrors(),'n2H':ROOT.TGraphErrors() }


flipped = defaultdict(dict)
for key, val in samples.items():
    for subkey, subval in val.items():
        flipped[subkey][key] = subval



complete_mass = defaultdict(dict)
for mass in flipped.keys():
    print mass
    if options.sample == "WprimeToWhToWhadhinc_" and mass == 1400.0 and options.output.find("Vjet") != -1:
        print " skipping WprimeWH at 1.4 TeV when doing the Vjet because for no clear reason its sigma explodes! "
        continue
    i= 0
    for folder in folders:
        try:
            x = flipped[mass][folder]
            print " x ", x
            i+=1
        except KeyError:
            print "!!!!    folder ", folder, " missing for mass", mass ," !!!!!!!!"
            pass
    print i
    if i == len(folders):
        for folder in folders:
            x = flipped[mass][folder]
            complete_mass[mass][folder] = x


print " complete ",complete_mass


if options.output.find('NP')!=-1:
    category='NP'
else:
    category=options.output.split("_")[-3]+"_"+options.output.split("_")[-2]
print "category ",category

mvv,maxi,mini = options.mvv,options.maxi,options.mini

#Now we have the samples: Sort the masses and run the fits
N=0
for mass in sorted(complete_mass.keys()):
    print "#############    mass ",mass,"       ###########"
    
    histo = None
    plotter = []
    for folder in sorted(complete_mass[mass].keys()):
        year=folder.split("/")[-2]
        print "year ",year
        ctx = cuts.cuts("init_VV_VH.json",year,"dijetbins_random")
        luminosity = 1 #ctx.lumi[year]/ctx.lumi["Run2"]
        if options.output.find("1617") !=-1:
            luminosity = ctx.lumi[year]/ctx.lumi["1617"]
            print "1617"
        elif options.output.find("Run2") !=-1:
            luminosity = ctx.lumi[year]/ctx.lumi["Run2"]
            print "ctx.lumi[year]/ctx.lumi['Run2'] "
        print " fraction of lumi ",luminosity
        plotter.append(TreePlotter(complete_mass[mass][folder]+'.root','AnalysisTree'))
        if year == "2016": plotter[-1].addCorrectionFactor('genWeight','tree')
        else :
            print "using LO weight to avoid negative weights!"
            plotter[-1].addCorrectionFactor('genWeight_LO','tree')
        plotter[-1].addCorrectionFactor(luminosity,'flat')
        plotter[-1].addCorrectionFactor('puWeight','tree')
        if options.triggerW:
            plotter[-1].addCorrectionFactor('jj_triggerWeight','tree')
            print "Using triggerweight"

        print "ATTENTION: "+str(mvv)
        if mvv.find("l1")!=-1 or mvv.find("l2")!=-1:
           if histo == None : 
               histo = plotter[-1].drawTH1(mvv,options.cut,"1",int((maxi-mini)/4),mini,maxi)
           else:
               histo.Add(plotter[-1].drawTH1(mvv,options.cut,"1",int((maxi-mini)/4),mini,maxi)) 
        else:
            if histo == None :
                histo = plotter[-1].drawTH1(mvv.replace("random","l1"),options.cut.replace("random","l1"),"1",int((maxi-mini)/4),mini,maxi) 
            else:
                histo.Add(plotter[-1].drawTH1(mvv.replace("random","l1"),options.cut.replace("random","l1"),"1",int((maxi-mini)/4),mini,maxi))
            tmp = plotter[-1].drawTH1(mvv.replace("random","l2"),options.cut.replace("random","l2"),"1",int((maxi-mini)/4),options.mini,options.maxi)
            histo.Add(tmp)
              

    
    fitter=Fitter(['x'])
    if isVH and options.cut.find('Truth')==-1: fitter.jetDoublePeakVH('model','x'); print "INFO: fit jet double peak";
    if (not isVH and not isHH) or (options.cut.find('VTruth')!=-1 and options.cut.find('VVTruth') ==-1): fitter.jetResonanceNOEXP('model','x'); print "INFO: fit jetmass no exp ";
    if (isVH and options.cut.find('HbbTruth')) or isHH: fitter.jetResonanceHiggs('model','x'); print "INFO: fit jetResonanceHiggs";
    
    if options.fixPars!="1":
        fixedPars =options.fixPars.split(',')
        for par in fixedPars:
            parVal = par.split(':')
	    if len(parVal) > 1:
             fitter.w.var(parVal[0]).setVal(float(parVal[1]))
             fitter.w.var(parVal[0]).setConstant(1)

    fitter.importBinnedData(histo,['x'],'data')
    fitter.fit('model','data',[ROOT.RooFit.SumW2Error(0),ROOT.RooFit.Save()])
    fitter.fit('model','data',[ROOT.RooFit.SumW2Error(0),ROOT.RooFit.Minos(1),ROOT.RooFit.Save()])
    fitter.projection("model","data","x","debugJ"+leg+"_"+options.output+"_"+str(mass)+".png")
    fitter.projection("model","data","x","debugJ"+leg+"_"+options.output+"_"+str(mass)+".C")

    for var,graph in graphs.iteritems():
        value,error=fitter.fetch(var)
        graph.SetPoint(N,mass,value)
        graph.SetPointError(N,0.0,error)
                
    N=N+1
    fitter.delete()
        
F=ROOT.TFile(options.output,"RECREATE")
F.cd()
for name,graph in graphs.iteritems():
    graph.Write(name)
F.Close()
            
