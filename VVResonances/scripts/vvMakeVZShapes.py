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
parser.add_option("-r","--minMVV",dest="minMx",type=float, help="smallest Mx to fit ",default=1000.0)
parser.add_option("-R","--maxMVV",dest="maxMx",type=float, help="largest Mx to fit " ,default=7000.0)
parser.add_option("-t","--triggerweight",dest="triggerW",action="store_true",help="Use trigger weights",default=False)
parser.add_option("--store",dest="store",type=str,help="store fitted parameters in this file",default="")
parser.add_option("--binsMVV",dest="binsMVV",help="use special binning",default="")
(options,args) = parser.parse_args()
#define output dictionary

samples={}

folders = str(args[0]).split(",")
for folder in folders:
    samples[folder] = []
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
        name = fname.split('_')[0]
        samples[folder].append(folder+fname)
        
        print 'found',filename, " and stored in ",samples[folder]
            


leg = options.mvv.split('_')[1]


if options.output.find('NP')!=-1:
    category='NP'
else:
    category=options.output.split("_")[-3]+"_"+options.output.split("_")[-2]
print "category ",category

mvv,maxi,mini = options.mvv,options.maxi,options.mini
plotter=[]
names = []
for files in samples.keys():
    for f in samples[files]:
        print " samples name ",f
        histo = None

        print " samples name ",f
        year=f.split("/")[-2]
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

        plotter.append(TreePlotter(f+'.root','AnalysisTree'))
        plotter[-1].setupFromFile(f+'.pck')
        plotter[-1].addCorrectionFactor('xsec','tree')
        plotter[-1].addCorrectionFactor('genWeight','tree')
        plotter[-1].addCorrectionFactor('puWeight','tree')
        plotter[-1].addCorrectionFactor(luminosity,'flat')
        if options.triggerW: plotters[-1].addCorrectionFactor('triggerWeight','tree')
        names.append(f)


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
    fitter.jetResonanceNOEXP('model','x'); print "INFO: fit jetmass no exp ";
    
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
    fitter.projection("model","data","x","debugJ"+leg+"_"+options.output+".png")
    fitter.projection("model","data","x","debugJ"+leg+"_"+options.output+".C")
    params = {}
    params["Res_"+leg]={"mean": {"val": fitter.w.var("mean").getVal(), "err": fitter.w.var("mean").getError()}, "sigma": {"val": fitter.w.var("sigma").getVal(), "err": fitter.w.var("sigma").getError()}, "alpha":{ "val": fitter.w.var("alpha").getVal(), "err": fitter.w.var("alpha").getError()},"alpha2":{"val": fitter.w.var("alpha2").getVal(),"err": fitter.w.var("alpha2").getError()},"n":{ "val": fitter.w.var("n").getVal(), "err": fitter.w.var("n").getError()},"n2": {"val": fitter.w.var("n2").getVal(), "err": fitter.w.var("n2").getError()}
}


    #fitter.drawVjets(options.sample+"_mjetRes_NP_"+period+".pdf",histos,histos_nonRes,scales,scales_nonRes)

    if options.store!="":
        print "write to file "+options.store
        f=open(options.store,"w")
        for par in params:
            f.write(str(par)+ " = " +str(params[par])+"\n")



    fitter.delete()
        
            
