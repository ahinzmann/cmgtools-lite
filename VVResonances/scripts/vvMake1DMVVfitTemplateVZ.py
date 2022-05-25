#!/usr/bin/env python
import ROOT
from array import array
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log,exp,sqrt
import os, sys, re, optparse,pickle,shutil,json
import copy
import json
from CMGTools.VVResonances.plotting.tdrstyle import *
setTDRStyle()
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
sys.path.insert(0, "../interactive/")
import cuts
ROOT.gSystem.Load("libCMGToolsVVResonances")
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
ROOT.v5.TFormula.SetMaxima(10000) #otherwise we get an error that the TFormula called by the TTree draw has too many operators when running on the CR

parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output",default='')
parser.add_option("-p","--period",dest="period",help="run period",default=2016)
parser.add_option("-r","--res",dest="res",help="res",default='')
parser.add_option("-H","--resHisto",dest="resHisto",help="res",default='')
parser.add_option("-s","--samples",dest="samples",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for yield in gen sample",default='')
parser.add_option("-v","--var",dest="var",help="variable for x",default='')
parser.add_option("-b","--bins",dest="binsx",type=int,help="bins",default=1)
parser.add_option("-x","--minx",dest="minx",type=float,help="bins",default=0)
parser.add_option("-X","--maxx",dest="maxx",type=float,help="conditional bins split by comma",default=1)
parser.add_option("-w","--weights",dest="weights",help="additional weights",default='')
parser.add_option("-u","--usegenmass",dest="usegenmass",action="store_true",help="use gen mass for det resolution",default=False)
parser.add_option("-e","--firstEv",dest="firstEv",type=int,help="first event",default=0)
parser.add_option("-E","--lastEv",dest="lastEv",type=int,help="last event",default=-1)
parser.add_option("--binsMVV",dest="binsMVV",help="use special binning",default="")
parser.add_option("-t","--triggerweight",dest="triggerW",action="store_true",help="Use trigger weights",default=False)
parser.add_option("--corrFactorW",dest="corrFactorW",type=float,help="add correction factor xsec",default=1.)
parser.add_option("--corrFactorZ",dest="corrFactorZ",type=float,help="add correction factor xsec",default=1.)

(options,args) = parser.parse_args()


def getBinning(binsMVV,minx,maxx,bins):
    l=[]
    if binsMVV=="":
        for i in range(0,bins+1):
            l.append(minx + i* (maxx - minx)/bins)
    else:
        s = binsMVV.split(",")
        for w in s:
            l.append(int(w))
    return l


def unequalScale(histo,name,alpha,power=1):
    newHistoU =copy.deepcopy(histo) 
    newHistoU.SetName(name+"Up")
    newHistoD =copy.deepcopy(histo) 
    newHistoD.SetName(name+"Down")
    for i in range(1,histo.GetNbinsX()+1):
        x= histo.GetXaxis().GetBinCenter(i)
        nominal=histo.GetBinContent(i)
        factor = 1+alpha*pow(x,power) 
        newHistoU.SetBinContent(i,nominal*factor)
        newHistoD.SetBinContent(i,nominal/factor)
    return newHistoU,newHistoD 
    
def mirror(histo,histoNominal,name):
    newHisto =copy.deepcopy(histoNominal) 
    newHisto.SetName(name)
    intNominal=histoNominal.Integral()
    intUp = histo.Integral()
    for i in range(1,histo.GetNbinsX()+1):
        up=histo.GetBinContent(i)/intUp
        nominal=histoNominal.GetBinContent(i)/intNominal
        newHisto.SetBinContent(i,histoNominal.GetBinContent(i)*nominal/up)
    return newHisto      

def histoMaker(h,binning,name):
    xmin = h.GetXaxis().GetXmin()
    xmax = h.GetXaxis().GetXmax()
    print xmin,xmax

    expo=ROOT.TF1("expo","[0]*(1-x/13000.)^[1]/(x/13000)^[2]",xmin,xmax)
    #expo.SetParameters(0,16.,2.)                                                                                                                                                       
    #expo.SetParLimits(2,1.,20.)
    #expo.SetParLimits(1,20.,40.)

    #for 16+17 VH HPHP
    #expo=ROOT.TF1("expo","exp(-x/([0]+[1]*x))",xmin,xmax)
    #expo.SetParameters(16.,0.1)

    h.Fit(expo,"MR","",xmin,xmax)
    h.Fit(expo,"MR","",xmin,xmax)
    hint = ROOT.TH1F("hint","hint",options.binsx,xmin,xmax)
    ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(hint)
    hint.SetStats(ROOT.kFALSE);
    hint.SetFillColor(2);
    hint.SetFillStyle(3001)

    h_smooth = ROOT.TH1F(name,name,options.binsx,array('f',binning))
    for b in range(1,options.binsx+1):
        h_smooth.SetBinContent(b,expo.Eval(h.GetBinCenter(b)))
        h_smooth.SetBinError(b,hint.GetBinError(b))

    return h_smooth,hint



  
def smoothTail1D(proj):
    if proj.Integral() == 0:
        print "histogram has zero integral "+proj.GetName()
        return 0
    scale = proj.Integral()
    proj.Scale(1.0/scale)


    #beginFitX = 2100#1500
    #endX = 2800
    #if options.output.find("HPHP")!=-1:
    #    beginFitX=1100
    #    endX = 1500
    
    beginFitX = 1600 #2100#1500
    endX = 1800 #2800
    #beginFitX = 1246 #2100#1500
    #endX = 2000 #2800
    #if options.output.find("LP")!=-1: 
    #    beginFitX=1246
    #    endX = 1800
    #expo=ROOT.TF1("expo","[0]*(1-x/13000.)^[1]/(x/13000)^[2]",2000,8000)
    expo=ROOT.TF1("expo","[0]*(1-x/13000.)^(min([1],[2]))/(x/13000)^[2]",2000,8000)
    expo.SetParameters(0,16.,2.)
    expo.SetParLimits(2,1.,20.)
    proj.Fit(expo,"LLMR","",beginFitX,8000)
    beginsmooth = False
    print proj.GetNbinsX()+1
    for j in range(1,proj.GetNbinsX()+1):
        x=proj.GetXaxis().GetBinCenter(j)
        if x>beginFitX:
            if beginsmooth==False:
                if x< endX: #2100: 
                   if abs(proj.GetBinContent(j) - expo.Eval(x)) < 0.00009:# and abs(expo.Derivative(x)- (hist.GetBinContent(j):
                    print beginFitX
                    print "begin smoothing at " +str(x)
                    beginsmooth = True 
               #if abs(proj.GetBinContent(j) - expo.Eval(x)) < 0.00001:# and abs(expo.Derivative(x)- (hist.GetBinContent(j):
                   #print beginFitX
                   #print "begin smoothing at " +str(x)

                   #beginsmooth = True 
                else: beginsmooth = True
            if beginsmooth:
                proj.SetBinContent(j,expo.Eval(x))
    proj.Scale(scale)
    return 1

weights_ = options.weights.split(',')

random=ROOT.TRandom3(101082)

sampleTypes=options.samples.split(',')
period=options.period

stack = ROOT.THStack("stack","")
print "Creating datasets for samples: " ,sampleTypes
dataPlotters=[]

print "args[0] ",args[0]
folders = args[0].split(',')
print "folders ",folders
ctx = cuts.cuts("init_VV_VH.json","2016","dijetbins_random")

for folder in folders:
    print " folder "
    for filename in os.listdir(folder):
        for sampleType in sampleTypes:
            if filename.find(sampleType)!=-1:
                fnameParts=filename.split('.')
                fname=fnameParts[0]
                ext=fnameParts[1]
                if ext.find("root") ==-1: continue
                dataPlotters.append(TreePlotter(folder+'/'+fname+'.root','AnalysisTree'))
                dataPlotters[-1].setupFromFile(folder+'/'+fname+'.pck')
                dataPlotters[-1].addCorrectionFactor('xsec','tree')
                dataPlotters[-1].addCorrectionFactor('genWeight','tree')
                dataPlotters[-1].addCorrectionFactor('puWeight','tree')
                print "split ",folder.split("/")
                year=folder.split("/")[-2]
                print "year ",year
                print "now working with cuts "
                ctx = cuts.cuts("init_VV_VH.json",year,"dijetbins_random")
                print "lumi for year "+year+" = ",ctx.lumi[year]
                luminosity = 1 #ctx.lumi[year]/ctx.lumi["Run2"]
                if options.output.find("1617") !=-1:
                    luminosity = ctx.lumi[year]/ctx.lumi["1617"]
                    print "1617"
                elif options.output.find("Run2") !=-1:
                    luminosity = ctx.lumi[year]/ctx.lumi["Run2"]
                    print "ctx.lumi[year]/ctx.lumi['Run2'] "
                else:
                    luminosity = 1
                print " lumi rewight ",luminosity
                dataPlotters[-1].addCorrectionFactor(luminosity,'flat')
                if fname.find("QCD_Pt_") !=-1 or fname.find("QCD_HT") !=-1: 
                    print "going to apply spikekiller for ",fname
                    dataPlotters[-1].addCorrectionFactor('b_spikekiller','tree')
                if options.triggerW:
                    dataPlotters[-1].addCorrectionFactor('triggerWeight','tree')
                    print "Using trigger weights from tree"
                for w in weights_:
                    if w != '': dataPlotters[-1].addCorrectionFactor(w,'branch')
                
                dataPlotters[-1].filename=fname



data=MergedPlotter(dataPlotters)
fcorr=ROOT.TFile(options.res)

scale = fcorr.Get("scale"+options.resHisto+"Histo")
res   = fcorr.Get("res"  +options.resHisto+"Histo")

binning = getBinning(options.binsMVV,options.minx,options.maxx,options.binsx)
print binning


#distribution of mjet from simulation --> use to validate kernel
mvv_nominal=ROOT.TH1F("mvv_nominal","mvv_nominal",options.binsx,array('f',binning))
mvv_nominal.Sumw2()

histogram_nominal=ROOT.TH1F("histo_nominal","histo_nominal",options.binsx,array('f',binning))
histogram_nominal.Sumw2()

histograms=[
    histogram_nominal,
    mvv_nominal,
  ]

maxEvents = -1
#ok lets populate!
for plotter in dataPlotters:
 #first V+jets sample
 c=0
 if plotter.filename.find(sampleTypes[0].replace('.root','')) != -1 : #and plotter.filename.find("Jets") == -1 and plotter.filename.find("TT") ==-1: 
   print "Preparing  histogram for sampletype " ,sampleTypes[0]
   print "filename: ", plotter.filename
   histI2=plotter.drawTH1Binned('jj_LV_mass',options.cut,"1",array('f',binning))
   if histI2.Integral()>0:
    mvv_nominal.Add(histI2)

   histI2.Delete()

 # second V+jets sample
 if len(sampleTypes)<2: continue
 elif plotter.filename.find(sampleTypes[1].replace('.root','')) != -1 : #and plotter.filename.find("Jets") == -1 and plotter.filename.find("TT") ==-1: #alternative shape Herwig
   print "Preparing histogram for sampletype " ,sampleTypes[1]
   print "filename: ", plotter.filename
   histI2=plotter.drawTH1Binned('jj_LV_mass',options.cut,"1",array('f',binning))
   if histI2.Integral()>0:
    mvv_nominal.Add(histI2)

   histI2.Delete()

 # third V+jets sample
 if len(sampleTypes)<3: continue
 elif plotter.filename.find(sampleTypes[2].replace('.root','')) != -1 : 
   print "Preparing histogram for sampletype " ,sampleTypes[2]
   print "filename: ", plotter.filename
   
   histI2=plotter.drawTH1Binned('jj_LV_mass',options.cut,"1",array('f',binning))
   if histI2.Integral()>0:
    mvv_nominal.Add(histI2)
    
   histI2.Delete()


print "<><><><><><><><><><><><><><> now make fits & templates from them <><><><><><><><><><><><><><><><><>"
print "********* ",options.output
print "nominal (with pt weights)"
histogram_nominal,hint_nominal=histoMaker(mvv_nominal,binning,histogram_nominal.GetName())


print " ********** ALL DONE, now save in output file ", options.output
f=ROOT.TFile(options.output,"RECREATE")
f.cd()
finalHistograms={histogram_nominal.GetName(): histogram_nominal,
                 mvv_nominal.GetName(): mvv_nominal
}

for hist in finalHistograms.itervalues():
 # hist.Write(hist.GetName()+"_raw")
 if (options.output).find("Z")!=-1 and hist.GetName()=="histo_nominal":
     if hist.Integral() > 0:
        if hist.GetName().find("histogram_nominal")!=-1:
            hist.Scale(scale)
        #if hist.GetName().find("mvv_nominal")!=-1:
        #    hist.Scale(scale2)

 hist.Write(hist.GetName())
 finalHistograms[hist.GetName()]=hist



########################################################

options.minx,options.maxx
alpha=1.5/float(options.maxx)
histogram_pt_down,histogram_pt_up=unequalScale(finalHistograms["histo_nominal"],"histo_nominal_PT",alpha)
histogram_pt_down.Write()
histogram_pt_up.Write()

alpha=1.5*float(options.minx)
histogram_opt_down,histogram_opt_up=unequalScale(finalHistograms["histo_nominal"],"histo_nominal_OPT",alpha,-1)
histogram_opt_down.Write()
histogram_opt_up.Write()

alpha=float(options.maxx)*float(options.maxx)
histogram_pt2_down,histogram_pt2_up=unequalScale(finalHistograms["histo_nominal"],"histo_nominal_PT2",alpha,2)
histogram_pt2_down.Write()
histogram_pt2_up.Write()

alpha=float(options.minx)*float(options.minx)
histogram_opt2_down,histogram_opt2_up=unequalScale(finalHistograms["histo_nominal"],"histo_nominal_OPT2",alpha,-2)
histogram_opt2_down.Write()
histogram_opt2_up.Write() 

#################################





if histogram_pt_up.Integral()!=0 and histogram_pt_down.Integral()!=0 and histogram_opt_up.Integral()!=0 and histogram_opt_down.Integral()!=0:
    c = ROOT.TCanvas("c","C",600,400)
    c.SetRightMargin(0.11)
    c.SetLeftMargin(0.11)
    c.SetTopMargin(0.11)
    finalHistograms["histo_nominal"].SetLineColor(ROOT.kBlue)
    finalHistograms["histo_nominal"].GetYaxis().SetTitle("arbitrary scale")
    finalHistograms["histo_nominal"].GetYaxis().SetTitleOffset(1.5)
    finalHistograms["histo_nominal"].GetXaxis().SetTitle("dijet mass")
    sf = finalHistograms["histo_nominal"].Integral()
    histogram_pt_up     .Scale(sf/histogram_pt_up.Integral())
    histogram_pt_down   .Scale(sf/histogram_pt_down.Integral())
    histogram_opt_up    .Scale(sf/histogram_opt_up.Integral())
    histogram_opt_down  .Scale(sf/histogram_opt_down.Integral())
    finalHistograms["histo_nominal"].Draw("hist")
    #stack.Draw("histsame")
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
    text = ROOT.TLatex()
    text.DrawLatexNDC(0.13,0.92,"#font[62]{CMS} #font[52]{Simulation}")
    data = finalHistograms["mvv_nominal"]
    data.Scale(sf/data.Integral())
    data.SetMarkerColor(ROOT.kBlack)
    data.SetMarkerStyle(7)
    data.Draw("same")
    c.SetLogy()


    l = ROOT.TLegend(0.17,0.2,0.6,0.33)
    l.AddEntry(data,"simulation","lp")
    l.AddEntry(finalHistograms["histo_nominal"],"template","l")
    l.AddEntry(histogram_pt_up,"#propto m_{jj}","l")
    l.AddEntry(histogram_opt_up,"#propto 1/m_{jj}","l")
    l.Draw("same")

    tmplabel = "Res"
    label=options.output.split("_")[1]
    print "label ",label
    
    if 'Jets' in options.output: tmplabel="Jets"
    if 'WZ' in options.output: tmplabel="WZ"+tmplabel
    if 'ZZ' in options.output: tmplabel="ZZ"+tmplabel
    if 'TT' in options.output: tmplabel="TTbar"
    tmplabel += "_"+label+"_"
    if options.output.find('VV_HPLP')!=-1: tmplabel+='VV_HPLP'
    if options.output.find('VV_HPHP')!=-1: tmplabel+='VV_HPHP'
    if options.output.find('VH_HPLP')!=-1: tmplabel+='VH_HPLP'
    if options.output.find('VH_HPHP')!=-1: tmplabel+='VH_HPHP'
    if options.output.find('VH_LPHP')!=-1: tmplabel+='VH_LPHP'
    if options.output.find('NP')!=-1: tmplabel+='NP'
    c.SaveAs("debug_mVV_kernels_"+tmplabel+".pdf")
    print "for debugging save","debug_mVV_kernels_"+tmplabel+".pdf"

    ########################################################


f.Close()



