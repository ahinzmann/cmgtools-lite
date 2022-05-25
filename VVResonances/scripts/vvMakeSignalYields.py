#!/usr/bin/env python

import ROOT
from array import array
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
from CMGTools.VVResonances.plotting.StackPlotter import StackPlotter
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log
from collections import defaultdict
from CMGTools.VVResonances.plotting.VarTools import returnString
import os, sys, re, optparse,pickle,shutil,json
ROOT.v5.TFormula.SetMaxima(10000) #otherwise we get an error that the TFormula called by the TTree draw has too many operators when running on the CR                                                                                                                          
sys.path.insert(0, "../interactive/")
import cuts


parser = optparse.OptionParser()
parser.add_option("-s","--sample",dest="sample",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for shape",default='')
parser.add_option("-o","--output",dest="output",help="Output JSON",default='')
parser.add_option("-V","--MVV",dest="mvv",help="mVV variable",default='')
parser.add_option("-m","--minMVV",dest="min",type=float,help="mVV variable",default=1)
parser.add_option("-M","--maxMVV",dest="max",type=float, help="mVV variable",default=1)
parser.add_option("-f","--function",dest="function",help="interpolating function",default='')
parser.add_option("-b","--BR",dest="BR",type=float, help="branching ratio",default=1)
parser.add_option("-r","--minMX",dest="minMX",type=float, help="smallest Mx to fit ",default=1000.0)
parser.add_option("-R","--maxMX",dest="maxMX",type=float, help="largest Mx to fit " ,default=7000.0)
parser.add_option("-t","--triggerweight",dest="triggerW",action="store_true",help="Use trigger weights",default=False)
parser.add_option("--tau",dest="tau",action="store_true",help="use tau21?")

(options,args) = parser.parse_args()

samples={}
yieldgraph=ROOT.TGraphErrors()


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

        #found sample. get the mass
        fnameParts=filename.split('.')
        fname=fnameParts[0]
        ext=fnameParts[1]
        if ext.find("root") ==-1:
            continue
        if filename.find("private")!=-1:
            continue

        mass = float(fname.split('_')[-1])
        if mass < options.minMX or mass > options.maxMX: continue

        # the 2500.0 mass point of the VBF_BulkGravToZZ signal in one of the three year has only a small number of events. It was used in the analysis but here it was tested the effect of removing it.
        #if mass == 2500.0 and fname.find("VBF_BulkGravToZZ") !=-1:
        #    continue


        samples[folder].update({mass : folder+fname})
        print 'found ',folder+fname,' mass',str(mass) 



flipped = defaultdict(dict)
for key, val in samples.items():
    for subkey, subval in val.items():
        flipped[subkey][key] = subval



complete_mass = defaultdict(dict)
for mass in flipped.keys():
    print mass
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


category=options.output.split("_")[-3]+"_"+options.output.split("_")[-2]
print "category ",category

luminosity_tot=0
for folder in folders:
    year=folder.split("/")[-2]
    ctx = cuts.cuts("init_VV_VH.json",year,"dijetbins_random")
    luminosity_tot += ctx.lumi[year]
    
print "Total lumi ",luminosity_tot



#Now we have the samples: Sort the masses and run the fits
fn=open(options.output+".txt","w")
fn.write("mass N 1/sqrt(N)*100\n")
N=0
for mass in sorted(complete_mass.keys()):
    print "#############    mass ",mass,"       ###########"

    histo = None
    plotter = []
    for folder in sorted(complete_mass[mass].keys()):
        year=folder.split("/")[-2]        
        print "year ",year
        ctx = cuts.cuts("init_VV_VH.json",year,"dijetbins_random")
        print " fraction of lumi ",ctx.lumi[year]/luminosity_tot 
        luminosity=   ctx.lumi[year]/luminosity_tot #str(ctx.lumi[year]/luminosity_tot)
        plotter.append(TreePlotter(complete_mass[mass][folder]+'.root','AnalysisTree'))
        plotter[-1].setupFromFile(complete_mass[mass][folder]+'.pck')
        if year == "2016": plotter[-1].addCorrectionFactor('genWeight','tree')
        else :
            print "using LO weight to avoid negative weights!" 
            plotter[-1].addCorrectionFactor('genWeight_LO','tree')
        plotter[-1].addCorrectionFactor('xsec','tree')
        plotter[-1].addCorrectionFactor('puWeight','tree')
        plotter[-1].addCorrectionFactor(luminosity,'flat')
        if not options.tau:
            print "using SF from tree"
            plotter[-1].addFriend("all","../interactive/migrationunc/"+complete_mass[mass][folder].split("/")[-1]+"_"+year+".root")
            plotter[-1].addCorrectionFactor("all.SF",'tree')
        else:
            print " using tau21 SF"
            if "HPHP" in category:
                SF=ctx.HPSF_vtag[year]*ctx.HPSF_vtag[year]
            elif "HPLP" in category:
                SF=ctx.HPSF_vtag[year]*ctx.LPSF_vtag[year]
            print SF
            plotter[-1].addCorrectionFactor(SF,'flat')
        plotter[-1].addCorrectionFactor('L1prefWeight','tree')
        if options.triggerW:
            plotter[-1].addCorrectionFactor('jj_triggerWeight','tree')	
            print "Using triggerweight"
        if histo == None :
            histo = plotter[-1].drawTH1(options.mvv,options.cut,"1.",500,options.min,options.max)
        else:
            histo.Add(plotter[-1].drawTH1(options.mvv,options.cut,"1.",500,options.min,options.max))


    err=ROOT.Double(0)
    integral=histo.IntegralAndError(1,histo.GetNbinsX(),err) 
    print " mass ",mass," integral ",integral
    fn.write("%d %f %f \n"%(mass,integral*luminosity_tot,ROOT.TMath.Sqrt(1./(integral*luminosity_tot))*100.))
    yieldgraph.SetPoint(N,mass,integral*options.BR)
    yieldgraph.SetPointError(N,0.0,err*options.BR)
    N=N+1
    print " done with mass ",mass 



fn.close()
if options.function != "spline":
    func = ROOT.TF1("func",options.function,options.min,options.max)
    yieldgraph.Fit(func,"R")
else:
    func = ROOT.TSpline3("func",yieldgraph)
    func.SetLineColor(ROOT.kRed)

parameterization={'yield':returnString(func,options.function)}
f=open(options.output+".json","w")
json.dump(parameterization,f)
f.close()

f=ROOT.TFile(options.output+".root","RECREATE")
f.cd()
yieldgraph.Write("yield")
f.Close()

c=ROOT.TCanvas("c")
c.cd()
yieldgraph.Draw("AP")
func.Draw("lsame")
c.SaveAs("debug_"+options.output+".png")

#F=ROOT.TFile(options.output+".root",'RECREATE')
#F.cd()
#yieldgraph.Write("yield")
#F.Close()

