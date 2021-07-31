#!/usr/bin/env python

import ROOT
from array import array
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
from CMGTools.VVResonances.plotting.StackPlotter import StackPlotter
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log
import os, sys, re, optparse,pickle,shutil,json, copy
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.v5.TFormula.SetMaxima(10000) #otherwise we get an error that the TFormula called by the TTree draw has too many operators when running on the CR
from time import sleep
from  CMGTools.VVResonances.plotting.CMS_lumi import *
sys.path.insert(0, "../interactive/")
import cuts

parser = optparse.OptionParser()
parser.add_option("-s","--sample",dest="sample",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for shape",default='')
parser.add_option("-o","--output",dest="output",help="outname",default='')
parser.add_option("-m","--min",dest="mini",type=float,help="min MJJ",default=40)
parser.add_option("-M","--max",dest="maxi",type=float,help="max MJJ",default=160)
parser.add_option("--store",dest="store",type=str,help="store fitted parameters in this file",default="")
parser.add_option("--corrFactor",dest="corrFactor",type=float,help="add correction factor xsec",default=1.)
# parser.add_option("-f","--fix",dest="fixPars",help="Fixed parameters",default="c_1:430.")
parser.add_option("-f","--fix",dest="fixPars",help="Fixed parameters",default="1")
parser.add_option("--minMVV","--minMVV",dest="minMVV",type=float,help="mVV variable",default=1)
parser.add_option("--maxMVV","--maxMVV",dest="maxMVV",type=float, help="mVV variable",default=1)
parser.add_option("--binsMVV",dest="binsMVV",help="use special binning",default="")
parser.add_option("-t","--triggerweight",dest="triggerW",action="store_true",help="Use trigger weights",default=False)
parser.add_option("--prelim",dest="prelim",help="which CMS labels?",default='prelim')
(options,args) = parser.parse_args()

print " prelim? ",options.prelim

debug_out = "debug_TT/"
if not os.path.exists(debug_out): 
  os.system('mkdir '+debug_out)

def getPaveText(x1=0.15,y1=0.15,x2=0.25,y2=0.35):
  addInfo = ROOT.TPaveText(x1,y1,x2,y2,"NDC")
  addInfo.SetFillColor(0)
  addInfo.SetLineColor(0)
  addInfo.SetFillStyle(0)
  addInfo.SetBorderSize(0)
  addInfo.SetTextFont(42)
  addInfo.SetTextSize(0.040)
  addInfo.SetTextAlign(12)
  return addInfo
      
def getCanvasPaper(cname):
 ROOT.gStyle.SetOptStat(0)

 H_ref = 700 
 W_ref = 600 
 W = W_ref
 H  = H_ref
 T = 0.08*H_ref
 B = 0.12*H_ref
 L = 0.14*W_ref
 R = 0.04*W_ref
 canvas = ROOT.TCanvas(cname,cname,50,50,W,H)
 canvas.SetFillColor(0)
 canvas.SetBorderMode(0)
 canvas.SetFrameFillStyle(0)
 canvas.SetFrameBorderMode(0)
 canvas.SetLeftMargin( L/W )
 canvas.SetRightMargin( R/W )
 canvas.SetTopMargin( T/H )
 canvas.SetBottomMargin( B/H )
 canvas.SetTickx()
 canvas.SetTicky()

 pt = ROOT.TPaveText(0.1746231,0.7331469,0.5251256,0.7817483,"NDC")
 pt.SetTextFont(42)
 pt.SetTextSize(0.04)
 pt.SetTextAlign(12)
 pt.SetFillColor(0)
 pt.SetBorderSize(0)
 pt.SetFillStyle(0)
 
 return canvas, pt
 
def drawFromJson(jsonfile,category,outname):
  evalPoints = [1250,1300,1400,1500,2000,2500,3000,3500,5500]
  fitter=Fitter(['MJ[80,55,215]'])
  #fitter.threeGaus('model','MJ')
  #fitter.twoCBplusGaus('model','MJ')
  #fitter.CBplus2Gaus('model','MJ')
  #fitter.erfexp2CB('model','MJ')
  fitter.erfexp2Gaus('model','MJ')

  var = fitter.w.var('MJJ')
  frame = fitter.w.var('MJ').frame()
  with open(jsonfile) as jsonFile:
    j = json.load(jsonFile)
    leg = ROOT.TLegend(0.1746231, 0.43, 0.5251256, 0.73)
    leg.SetBorderSize(0)
    c, pt =getCanvasPaper('ttMJ')

    for i,MJJ in enumerate(evalPoints):
      # parametrize non resonant part with exp-err
      fitter.w.var("c_0")   .setVal( eval(j["c_0"   ]) );  fitter.w.var("c_0")   .setConstant(ROOT.kTRUE)
      fitter.w.var("c_1")   .setVal( eval(j["c_1"   ]) );  fitter.w.var("c_1")   .setConstant(ROOT.kTRUE)
      fitter.w.var("c_2")   .setVal( eval(j["c_2"   ]) );  fitter.w.var("c_2")   .setConstant(ROOT.kTRUE)
      # parametrise non resonant part with a gaussian
      #fitter.w.var("meanN") .setVal( eval(j["meanN" ]) );  fitter.w.var("meanN") .setConstant(ROOT.kTRUE)
      #fitter.w.var("sigmaN").setVal( eval(j["sigmaN"]) );  fitter.w.var("sigmaN").setConstant(ROOT.kTRUE)
      # ratio parameters
      fitter.w.var("f_g1")  .setVal( eval(j["f_g1"  ]) );  fitter.w.var("f_g1")  .setConstant(ROOT.kTRUE)
      fitter.w.var("f_res") .setVal( eval(j["f_res" ]) );  fitter.w.var("f_res") .setConstant(ROOT.kTRUE)
      # parametrize W with a gaussian
      fitter.w.var("meanW") .setVal( eval(j["meanW" ]) );  fitter.w.var("meanW") .setConstant(ROOT.kTRUE)
      fitter.w.var("sigmaW").setVal( eval(j["sigmaW"]) );  fitter.w.var("sigmaW").setConstant(ROOT.kTRUE)
      # parametrize T with a gaussian
      fitter.w.var("meanT") .setVal( eval(j["meanT" ]) );  fitter.w.var("meanT") .setConstant(ROOT.kTRUE)
      fitter.w.var("sigmaT").setVal( eval(j["sigmaT"]) );  fitter.w.var("sigmaT").setConstant(ROOT.kTRUE)
      # parametrize W with a CB
      #fitter.w.var("meanW") .setVal( eval(j["meanW" ]) );  fitter.w.var("meanW") .setConstant(ROOT.kTRUE)
      #fitter.w.var("sigmaW").setVal( eval(j["sigmaW"]) );  fitter.w.var("sigmaW").setConstant(ROOT.kTRUE)
      #fitter.w.var("alpha1W") .setVal( eval(j["alpha1W" ]) );  fitter.w.var("alpha1W") .setConstant(ROOT.kTRUE)
      #fitter.w.var("n1W").setVal( eval(j["n1W"]) );  fitter.w.var("n1W").setConstant(ROOT.kTRUE)
      #fitter.w.var("alpha2W") .setVal( eval(j["alpha2W" ]) );  fitter.w.var("alpha2W") .setConstant(ROOT.kTRUE)
      #fitter.w.var("n2W").setVal( eval(j["n2W"]) );  fitter.w.var("n2W").setConstant(ROOT.kTRUE)
      # parametrize T with a CB
      #fitter.w.var("meanT") .setVal( eval(j["meanT" ]) );  fitter.w.var("meanT") .setConstant(ROOT.kTRUE)
      #fitter.w.var("sigmaT").setVal( eval(j["sigmaT"]) );  fitter.w.var("sigmaT").setConstant(ROOT.kTRUE)
      #fitter.w.var("alpha1T") .setVal( eval(j["alpha1T" ]) );  fitter.w.var("alpha1T") .setConstant(ROOT.kTRUE)
      #fitter.w.var("n1T").setVal( eval(j["n1T"]) );  fitter.w.var("n1T").setConstant(ROOT.kTRUE)
      #fitter.w.var("alpha2T") .setVal( eval(j["alpha2T" ]) );  fitter.w.var("alpha2T") .setConstant(ROOT.kTRUE)
      #fitter.w.var("n2T").setVal( eval(j["n2T"]) );  fitter.w.var("n2T").setConstant(ROOT.kTRUE)

      
      fitter.w.pdf('model').plotOn(frame, ROOT.RooFit.LineColor(ROOT.TColor.GetColor(colors[i])),ROOT.RooFit.Name(str(MJJ)))
      leg.AddEntry(frame.findObject(str(MJJ)), "%.1f TeV" %(MJJ/1000.), "L")
    frame.Draw()
    frame.SetTitle("")
    frame.GetYaxis().SetTitle("A.U")
    frame.GetXaxis().SetTitle("M_{jet} (GeV)")
    frame.GetYaxis().SetNdivisions(4,5,0)
    frame.SetMaximum(0.06)
    cmslabel_sim_prelim(c,'sim',11)
    leg.Draw('same')
    pt.AddText(category)

    pt.Draw()
    c.SaveAs(outname,"RECREATE")

def doClosure(histos,xaxis,jsonfile,category):
  coarse_bins_low  = [2,6,11]
  coarse_bins_high = [4,8,79]
  
  i = -1
  for h,xax in zip(histos,xaxis):
    for binL,binH in zip(coarse_bins_low,coarse_bins_high):
      i +=1
      
      c, pt =getCanvasPaper('ttMJ')
      leg = ROOT.TLegend(0.1746231, 0.33, 0.5251256, 0.63)
      leg.SetBorderSize(0)
      
      tmp = h.ProjectionY("binL%i_binH%i"%(binL,binH),binL,binH)
      tmp.Draw()
      
      projX = h.ProjectionX()
      mjjbinL = int(projX.GetBinLowEdge(binL))
      mjjbinH = int(projX.GetBinLowEdge(binH)+projX.GetBinWidth(binH))
      MJJ = int((mjjbinH+mjjbinL)/2)

      fitter=Fitter(['MJ'])
      fitter.importBinnedData(tmp,['MJ'],'data')
      fitter.erfexp2Gaus('model','MJ')
      #fitter.threeGaus('model','MJ')
      #fitter.twoCBplusGaus('model','MJ')
      #fitter.CBplus2Gaus('model','MJ')
      #fitter.erfexp2CB('model','MJ')
      with open(jsonfile) as jsonFile:
        j = json.load(jsonFile)
      
      #parametrise non res part with exp err
      fitter.w.var("c_0")   .setVal( eval(j["c_0"   ]) ); print eval(j["c_0"   ])
      fitter.w.var("c_1")   .setVal( eval(j["c_1"   ]) ); print eval(j["c_1"   ])
      fitter.w.var("c_2")   .setVal( eval(j["c_2"   ]) ); print eval(j["c_2"   ])
      # parametrise non res part with a gaussian
      #fitter.w.var("meanN") .setVal( eval(j["meanN" ]) ); print eval(j["meanN" ])
      #fitter.w.var("sigmaN").setVal( eval(j["sigmaN"]) ); print eval(j["sigmaN"])
      # ratio parameters
      fitter.w.var("f_g1")  .setVal( eval(j["f_g1"  ]) ); print eval(j["f_g1"  ])
      fitter.w.var("f_res") .setVal( eval(j["f_res" ]) ); print eval(j["f_res" ])
      # parametrise W with Gaussian
      fitter.w.var("meanW") .setVal( eval(j["meanW" ]) ); print eval(j["meanW" ])
      fitter.w.var("sigmaW").setVal( eval(j["sigmaW"]) ); print eval(j["sigmaW"])
      # parametrise T with Gaussian
      fitter.w.var("meanT") .setVal( eval(j["meanT" ]) ); print eval(j["meanT" ])
      fitter.w.var("sigmaT").setVal( eval(j["sigmaT"]) ); print eval(j["sigmaT"])
      # parametrise W with CB
      #fitter.w.var("meanW") .setVal( eval(j["meanW" ]) ); print eval(j["meanW" ])
      #fitter.w.var("sigmaW").setVal( eval(j["sigmaW"]) ); print eval(j["sigmaW"])
      #fitter.w.var("alpha1W") .setVal( eval(j["alpha1W" ]) );  print eval(j["alpha1W"])
      #fitter.w.var("n1W").setVal( eval(j["n1W"]) );  print eval(j["n1W"])
      #fitter.w.var("alpha2W") .setVal( eval(j["alpha2W" ]) );  print eval(j["alpha2W"])
      #fitter.w.var("n2W").setVal( eval(j["n2W"]) );  print eval(j["n2W"])
      # parametrise T with CB
      #fitter.w.var("meanT") .setVal( eval(j["meanT" ]) ); print eval(j["meanT" ])
      #fitter.w.var("sigmaT").setVal( eval(j["sigmaT"]) ); print eval(j["sigmaT"])
      #fitter.w.var("alpha1T") .setVal( eval(j["alpha1T" ]) );  print eval(j["alpha1T"])
      #fitter.w.var("n1T").setVal( eval(j["n1T"]) );  print eval(j["n1T"])
      #fitter.w.var("alpha2T") .setVal( eval(j["alpha2T" ]) );  print eval(j["alpha2T"])
      #fitter.w.var("n2T").setVal( eval(j["n2T"]) );  print eval(j["n2T"])
      
      fitter.fit('model','data',[ROOT.RooFit.SumW2Error(1),ROOT.RooFit.Save(1)]) #55,140 works well with fitting only the resonant part 
      fitter.projection_ratioplot("model","data","MJ","debug_TT/%s_closure_%s_binL%s_binH%s.pdf"%(options.output,xax.replace("{","").replace("}",""),mjjbinL,mjjbinH),0,False,"%s (GeV)"%xax,category,55,215)
      fitter.projection_ratioplot("model","data","MJ","debug_TT/%s_closure_%s_binL%s_binH%s.C"%(options.output,xax.replace("{","").replace("}",""),mjjbinL,mjjbinH),0,False,"%s (GeV)"%xax,category,55,215)
    
def getMean(h2,binL,binH):
  nbins = h2.GetYaxis().GetNbins()
  h1 = h2.ProjectionX("",0,nbins)
  h1.GetXaxis().SetRange(binL,binH)
  return h1.GetMean() 
  
def getFileList():
  samples={}
  samplenames = options.sample.split(",")
  folders = str(args[0]).split(",")
  print "folders ",folders

  for folder in folders:
    samples[folder] = []

    for filename in os.listdir(folder):
      if filename.find("root") ==-1:
        continue
      for samplename in samplenames:
        if not (filename.find(samplename)!=-1):
          continue
        fnameParts=filename.split('.')
        try:
          fname=filename.split('.')[0]
          samples[folder].append(folder+fname)
          print 'Fitting ttbar using file(s) ',folder+fname
        except AssertionError as error:
          print(error)
          print('Root files does not have proper . separator')
  if len(samples) == 0:
    raise Exception('No input files found for samplename(s) {}'.format(options.sample))
  print "samples ",samples
  return samples

def getPlotters(samples_in):
  plotters_ = []
  for folder in samples_in.keys():
    for name in samples_in[folder]:
      print " samples name ",name
      year=name.split("/")[-2]
      print "year ",year
      ctx = cuts.cuts("init_VV_VH.json",year,"dijetbins_random")
      lumi = ctx.lumi[year]
      print "lumi ",lumi
      plotters_.append(TreePlotter(name+'.root','AnalysisTree'))
      plotters_[-1].setupFromFile(name+'.pck')
      plotters_[-1].addCorrectionFactor('xsec','tree')
      genweight='genWeight'
      #if (year == "2017" or year == "2018") and name.find("TT") !=-1:  genweight='genWeight_LO'
      plotters_[-1].addCorrectionFactor(genweight,'tree')
      plotters_[-1].addCorrectionFactor('puWeight','tree')
      plotters_[-1].addCorrectionFactor(lumi,'flat')
      print "applying top pt reweight"
      plotters_[-1].addCorrectionFactor('TopPTWeight','tree')
      if options.triggerW: 
        plotters_[-1].addCorrectionFactor('triggerWeight','tree')	
      plotters_[-1].addCorrectionFactor(options.corrFactor,'flat')
  return plotters_
  
def get2DHist(plts,category):
  mergedPlotter = MergedPlotter(plts)
  histo2D_l1 = mergedPlotter.drawTH2("jj_l1_softDrop_mass:jj_LV_mass",options.cut,"1",80,options.minMVV,options.maxMVV,80,options.mini,options.maxi) #y:x
  histo2D_l2 = mergedPlotter.drawTH2("jj_l2_softDrop_mass:jj_LV_mass",options.cut,"1",80,options.minMVV,options.maxMVV,80,options.mini,options.maxi)  
  histo2D    = copy.deepcopy(histo2D_l1)
  histo2D.Add(histo2D_l2)
  #histo2D.Scale(float(lumi_))
  #histo2D_l1.Scale(float(lumi_))
  #histo2D_l2.Scale(float(lumi_))
  c, pt = getCanvasPaper('2D')
  histo2D.Draw("COLZ")
  addInfo = getPaveText(x1=0.71,y1=0.15,x2=0.81,y2=0.35)
  addInfo.AddText(category)
  addInfo.Draw()
  histo2D.GetXaxis().SetTitle("m_{jj}")
  histo2D.GetYaxis().SetTitle("m_{j}")
  cmslabel_sim_prelim(c,'sim',12)
  c.SaveAs(debug_out+"/%s_2D.pdf"%options.output)
  return histo2D_l1,histo2D_l2,histo2D

def doFit(th1_projY,mjj_mean,mjj_error,N,category):

  fitter=Fitter(['x'])
  fitter.erfexp2Gaus('model','x')
  #fitter.erfexp2CB('model','x')
  #fitter.threeGaus('model','x')
  #fitter.twoCBplusGaus('model','x')
  #fitter.CBplus2Gaus('model','x')
  projY.Rebin(2)
  if N == 0:
    # ****      Initial value
    # parametrise non res part with exp err
    fitter.w.var("c_0").setVal(-5.8573e-02)
    fitter.w.var("c_1").setVal(350.) #offset
    fitter.w.var("c_2").setVal(1.0707e+02) #width
    # parametrise non res part with gaus
    #fitter.w.var("meanN").setVal(1.45e+02)
    #fitter.w.var("sigmaN").setVal(5e+01)

    fitter.w.var("f_g1").setVal(7.8678e-02)
    fitter.w.var("f_res").setVal(5.9669e-01)

    # parametrise W with Gaussian
    fitter.w.var("meanW").setVal(8.1225e+01)
    fitter.w.var("sigmaW").setVal(6.7507e+00)
    # parametrise T with Gaussian
    fitter.w.var("meanT").setVal(1.7409e+02)
    fitter.w.var("sigmaT").setVal(1.3369e+01)


    # parametrise W with CB
    #fitter.w.var("meanW").setVal(8.1225e+01)
    #fitter.w.var("sigmaW").setVal(6.7507e+00)
    #fitter.w.var("alpha1W").setVal(1.5)
    #fitter.w.var("n1W").setVal(15)
    #fitter.w.var("alpha2W").setVal(1)
    #fitter.w.var("n2W").setVal(10)
    # parametrise T with CB
    #fitter.w.var("meanT").setVal(1.7409e+02)
    #fitter.w.var("sigmaT").setVal(1.3369e+01)
    #fitter.w.var("alpha1T").setVal(2)
    #fitter.w.var("n1T").setVal(100)
    #fitter.w.var("alpha2T").setVal(1)
    #fitter.w.var("n2T").setVal(10)

    # ****      Lower value
    # parametrise non res part with exp err
    fitter.w.var("c_0")   .setMax(0.2)
    fitter.w.var("c_1")   .setMin(100) #offset
    fitter.w.var("c_2")   .setMin(50) #width
    # parametrise non res part with gaus
    #fitter.w.var("meanN") .setMin(90.)
    #fitter.w.var("sigmaN").setMin(15.)

    fitter.w.var("f_g1")  .setMin(0.05)
    #fitter.w.var("f_res") .setMin(0.55) #following Thea's suggestion to set the minimum to a higher value to make the fit converge #0.55 for VH HPLP
    fitter.w.var("f_res") .setMin(0.4) #this is a good valueeee!!!!
    # parametrise W with Gaussian
    fitter.w.var("meanW") .setMin(75.)
    fitter.w.var("sigmaW").setMin(5)
    # parametrise T with Gaussian
    fitter.w.var("meanT") .setMin(160.)
    fitter.w.var("sigmaT").setMin(8)

    # parametrise W with CB
    #fitter.w.var("meanW") .setMin(75.)
    #fitter.w.var("sigmaW").setMin(5)
    #fitter.w.var("alpha1W").setMin(1.2)
    #fitter.w.var("n1W").setMin(10)
    #fitter.w.var("alpha2W").setMin(1)
    #fitter.w.var("n2W").setMin(1)
    # parametrise T with CB
    #fitter.w.var("meanT") .setMin(160.)
    #fitter.w.var("sigmaT").setMin(8)
    #fitter.w.var("alpha1T").setMin(0)
    #fitter.w.var("n1T").setMin(90)
    #fitter.w.var("alpha2T").setMin(1)
    #fitter.w.var("n2T").setMin(1)

    # ****      Higher value
    # parametrise non res part with exp err
    fitter.w.var("c_0")   .setMin(-0.20)
    fitter.w.var("c_1")   .setMax(600) #offset
    fitter.w.var("c_2")   .setMax(200) #width
    # parametrise non res part with gaus
    #fitter.w.var("meanN") .setMax(160)
    #fitter.w.var("sigmaN").setMax(150.)
    fitter.w.var("f_g1")  .setMax(0.9)
    fitter.w.var("f_res") .setMax(0.9)
    # parametrise W with Gaussian
    fitter.w.var("meanW") .setMax(90)
    fitter.w.var("sigmaW").setMax(9.)
    # parametrise T with Gaussian
    fitter.w.var("meanT") .setMax(180)
    fitter.w.var("sigmaT").setMax(16.)

    # parametrise W with CB
    #fitter.w.var("meanW") .setMax(90)
    #fitter.w.var("sigmaW").setMax(9.)
    #fitter.w.var("alpha1W").setMax(1.8)
    #fitter.w.var("n1W").setMax(20)
    #fitter.w.var("alpha2W").setMax(1)
    #fitter.w.var("n2W").setMax(100)
    # parametrise T with CB
    #fitter.w.var("meanT") .setMax(180)
    #fitter.w.var("sigmaT").setMax(16.)
    #fitter.w.var("alpha1T").setMax(3)
    #fitter.w.var("n1T").setMax(110)
    #fitter.w.var("alpha2T").setMax(1)
    #fitter.w.var("n2T").setMax(100)
    
    
    fitter.importBinnedData(projY,['x'],'data_full')
    fitter.fit('model','data_full',[ROOT.RooFit.SumW2Error(False),ROOT.RooFit.Save(1),ROOT.RooFit.Range(options.mini,options.maxi),ROOT.RooFit.Minimizer('Minuit2','migrad'), ROOT.RooFit.Extended(True)],requireConvergence=False) #55,140 works well with fitting only the resonant part
    fitter.projection_ratioplot("model","data_full","x","%s/%s_fullMjjSpectra.pdf"%(debug_out,options.output),0,False,"m_{jet} (GeV)",category)
    fitter.projection_ratioplot("model","data_full","x","%s/%s_fullMjjSpectra.C"%(debug_out,options.output),0,False,"m_{jet} (GeV)",category)
    string = '{'
    for var,graph in graphs.iteritems():
        value,error=fitter.fetch(var)
        string = string+'"%s": "%f %f",'%(var,value,error)
    string = string +'}'
    f=open(options.output+"_inclusive.json","w")
    json.dump(string,f)
    f.close()
    print "Output name is %s" %options.output+"_inclusive.json"
  else:
    for var,graph in graphs.iteritems():
      yvalues = graphs[var].GetY()
      yvalues = [yvalues[index] for index in xrange(graphs[var].GetN())]
      print"For %s: Setting starting values of fit to values from previous bin:%f"%(var,yvalues[-1])
      fitter.w.var(var).setVal(yvalues[-1])
      
  if options.fixPars!="1":
    fixedPars =options.fixPars.split(',')
    if len(fixedPars) > 0:
      print "   - Fix parameters: ", fixedPars
    for par in fixedPars:
      parVal = par.split(':')
      fitter.w.var(parVal[0]).setVal(float(parVal[1]))
      fitter.w.var(parVal[0]).setConstant(1)
  th1_projY.Rebin(2)
  fitter.importBinnedData(th1_projY,['x'],'data')
  fitter.fit('model','data',[ROOT.RooFit.SumW2Error(False),ROOT.RooFit.Save(1),ROOT.RooFit.Range(options.mini,options.maxi),ROOT.RooFit.Minimizer('Minuit2','migrad'), ROOT.RooFit.Extended(True)],requireConvergence=False) #Set SumW2 false for cov matrix to converge, see https://root-forum.cern.ch/t/covqual-with-sumw2error/17662/6
  fitter.projection_ratioplot("model","data","x","%s/%s_%s.pdf"%(debug_out,options.output,th1_projY.GetName()),0,False,"m_{jet} (GeV)",category,options.mini,options.maxi)
  fitter.projection_ratioplot("model","data","x","%s/%s_%s.C"%(debug_out,options.output,th1_projY.GetName()),0,False,"m_{jet} (GeV)",category,options.mini,options.maxi)
  
  for var,graph in graphs.iteritems():
      value,error=fitter.fetch(var)
      graph.SetPoint(N,mjj_mean,value)
      graph.SetPointError(N,0.0,error) #No error x
      # graph.SetPointError(N,mjj_error,error) #error x is number of bins in mVV

  fitter.delete()    

def doParametrizations(graphs,ff,category):
  ranges = {}
  # parametrise non res part with exp err
  ranges["c_0"   ]= [-0.2,0.2]
  ranges["c_1"   ]= [100.,600.]
  ranges["c_2"   ]= [40.,200.]
  # parametrise non res part with exp gauss
  #ranges["meanN" ]= [100.,160.]
  #ranges["sigmaN" ]= [0.,80.]

  ranges["f_g1"  ]= [0.,0.8]
  ranges["f_res" ]= [0.0,0.9]
  ranges["meanW" ]= [77.,87.]
  ranges["meanT" ]= [160.,190.]
  ranges["sigmaW"]= [0.,14.]
  ranges["sigmaT"]= [6.,20.]

  #CB
  #ranges["alpha1W" ]= [0.,2.]
  #ranges["n1W" ]= [0.,200.]
  #ranges["alpha2W"]= [0.,2.]
  #ranges["n2W"]= [0.,100.]
  #ranges["alpha1T" ]= [0.,40.]
  #ranges["n1T" ]= [0.,200.]
  #ranges["alpha2T"]= [0.,2.]
  #ranges["n2T"]= [0.,100.]
  
  inits = {}
  # parametrise non res part with exp err
  inits["c_0"   ]= [0.,9.7E07,3]
  inits["c_1"   ]= [350.,0.,0.]
  inits["c_2"   ]= [98.,-4E14,4.] #erf + 2gaus
  #inits["c_2"   ]= [60.,-4E10,4] #erf + 2CB
  # parametrise non res part with gauss
  #inits["meanN" ]= [100.,-1.6E19,5]
  #inits["sigmaN"]= [100.,9.7E16,5,12.]

  inits["f_g1"  ]= [0.,3.4E16,5]
  inits["f_res" ]= [0.,-5.3E16,5]
  inits["meanW" ]= [81.,1.4E18,5]
  inits["meanT" ]= [176.,-1.6E19,5]
  inits["sigmaW"]= [6,9.7E16,5,12.]
  inits["sigmaT"]= [13.,2.5E15,5]

  #CB
  #inits["alpha1W" ]= [1.3,1E21,5]
  #inits["n1W" ]= [4.,-6E11,3]
  #inits["alpha2W"]= [1.,0.,1.]
  #inits["n2W"]= [10.,1.,1,]
  #inits["alpha1T" ]= [20.,3.4E16,5]
  #inits["n1T" ]= [80,0,-1]
  #inits["alpha2T"]= [1.,0.,1.]
  #inits["n2T"]= [10.,1.,1,]
  

  titles = {}
  # parametrise non res part with exp err
  titles["c_0"   ] = "c_{0} (ErfExp)"   
  titles["c_1"   ] = "c_{1} (ErfExp)"   
  titles["c_2"   ] = "c_{2} (ErfExp)"   
  # parametrise non res part with exp gauss
  #titles["meanN" ] = "mean-non res"
  #titles["sigmaN"] = "width-non res"
  titles["f_g1"  ] = "F(Gauss_{W}, Gauss_{t})"
  titles["f_res" ] = "F(res., non-res.)"
  titles["meanW" ] = "<m>_{W}"
  titles["meanT" ] = "<m>_{t}"
  titles["sigmaW"] = "#sigma_{W}"
  titles["sigmaT"] = "#sigma_{t}"
  #titles["alpha1W" ] = "#alpha1_{W}"
  #titles["alpha2W" ] = "#alpha2_{W}"
  #titles["n1W" ] = "n1_{W}"
  #titles["n2W" ] = "n2_{W}"
  #titles["alpha1T" ] = "#alpha1_{t}"
  #titles["alpha2T" ] = "#alpha2_{t}"
  #titles["n1T" ] = "n1_{t}"
  #titles["n2T" ] = "n2_{t}"


  parametrisation = "[0]+[1]*pow(x,-[2])"

  ff.cd()
  parametrizations = {}
  for var,graph in graphs.iteritems():
    func=ROOT.TF1(var+"_func",parametrisation,options.minMVV,options.maxMVV)
    func.SetParameters(graph.Eval(options.minMVV), inits[var][1],inits[var][2])
    r = graph.Fit(func,"S R M","",options.minMVV,options.maxMVV)
    graph.Write(var)
    func.Write(var+"_func")
    c = ROOT.TCanvas()
    colors = ["#4292c6","#41ab5d","#ef3b2c","#ffd300","#D02090","#fdae61","#abd9e9","#2c7bb6"]
    mstyle = [8,4]
    graph.SetLineWidth(3)
    graph.SetLineStyle(1)
    graph.SetMarkerStyle(8)
    graph.Draw("APE")
    graph.GetXaxis().SetRangeUser(options.minMVV,options.maxMVV)
    graph.GetYaxis().SetRangeUser(ranges[var][0],ranges[var][1])
    graph.GetXaxis().SetTitle("M_{jj}")
    graph.GetYaxis().SetTitle(titles[var])
    cmslabel_sim_prelim(c,'sim',11)
    leg = ROOT.TLegend(0.55, 0.75, 0.85, 0.85)
    ROOT.SetOwnership(leg, False)
    leg.SetBorderSize(0)
    leg.AddEntry(graph, titles[var], "")
    leg.SetTextSize(0.04)
    leg.Draw()
    
    pavePars = ( [ int(func.GetParameter(i)) for i in range(func.GetNpar()) ])
    paveStr='y(x)=A+B#times x^{-C}'
    paveStr1='A=%i'%(pavePars[0])
    paveStr2='B=%.2g'  %(pavePars[1])
    paveStr3='C=%i'  %(pavePars[2])
    
    addInfo = getPaveText()
    addInfo.AddText(category)
    addInfo.AddText(paveStr)
    addInfo.AddText(paveStr1)
    addInfo.AddText(paveStr2)
    addInfo.AddText(paveStr3)
    addInfo.Draw()

    c.SaveAs(debug_out+options.output+"_"+var+".pdf")
    c.SaveAs(debug_out+options.output+"_"+var+".C")

    fittedPars = ( [ func.GetParameter(i) for i in range(func.GetNpar()) ])
    st='(0+({}+{}*pow(MJJ,-{})))'.format(*fittedPars)
    parametrizations[var] = st
  return parametrizations
              
  
if __name__ == "__main__":
  
  graphs={'meanW':ROOT.TGraphErrors(),'sigmaW':ROOT.TGraphErrors(),'meanT':ROOT.TGraphErrors(),'sigmaT':ROOT.TGraphErrors(),'f_g1':ROOT.TGraphErrors(),'f_res':ROOT.TGraphErrors(),
          #'meanN':ROOT.TGraphErrors(),'sigmaN':ROOT.TGraphErrors(),
          #'alpha1W':ROOT.TGraphErrors(),'n1W':ROOT.TGraphErrors(),#'alpha2W':ROOT.TGraphErrors(),'n2W':ROOT.TGraphErrors(),
          #'alpha1T':ROOT.TGraphErrors(),'n1T':ROOT.TGraphErrors()} #, #'alpha2T':ROOT.TGraphErrors(),'n2T':ROOT.TGraphErrors()}
          'c_0':ROOT.TGraphErrors(),'c_1':ROOT.TGraphErrors(),'c_2':ROOT.TGraphErrors()}

  category = options.output.split("_")[-2]+" "+options.output.split("_")[-1]
  if options.output.find("VBF") !=-1:
    category = "VBF "+category


  samples = getFileList()
  plotters = getPlotters(samples)
  h2D_l1,h2D_l2,h2D = get2DHist(plotters,category)
  tmpfile = ROOT.TFile("testTT.root","RECREATE")


  
  coarse_bins_low  = [1,3,5,7,7,7]
  coarse_bins_high = [2,4,6,79,79,79]
  if options.output.find("VBF") !=-1:
    coarse_bins_low  = [1,3,5,5,5,5]
    coarse_bins_high = [2,4,79,79,79,79]

  projX = h2D.ProjectionX()
  projY = h2D.ProjectionY()
  for bin in range(0,len(coarse_bins_low)):
    binL = float(projX.GetBinLowEdge(coarse_bins_low[bin]))
    binH = float(projX.GetBinLowEdge(coarse_bins_high[bin])+projX.GetBinWidth(coarse_bins_high[bin]))
    mjj_mean = getMean(h2D,coarse_bins_low[bin],coarse_bins_high[bin])
    mjj_error = (binH-binL)/2
    if bin == (len(coarse_bins_low)-2):
      mjj_mean = options.maxMVV-mjj_mean
    if bin == (len(coarse_bins_low)-1):
      mjj_mean = options.maxMVV
    tmp = h2D.ProjectionY("mjjmean%i_binL%i_binH%i"%(mjj_mean,binL,binH),coarse_bins_low[bin],coarse_bins_high[bin])
    doFit(tmp,mjj_mean,mjj_error,bin,category)
    tmpfile.cd()
    tmp.Write()
  tmpfile.cd()
  h2D.Write("h2D")
  h2D_l1.Write("h2D_l1")
  h2D_l2.Write("h2D_l2")
  for name,graph in graphs.iteritems():
      graph.Write(name)
  tmpfile.Close()
  ff=ROOT.TFile(debug_out+options.output+".root","RECREATE")
  parametrizations = doParametrizations(graphs,ff,category)
  ff.Close()
  f=open(options.output+".json","w")
  json.dump(parametrizations,f)
  f.close()
  print "Output name is %s" %options.output+".json"
  
  colors = ["#CD3700","#EE4000","#FF4500","#CD4F39","#EE5C42","#EE6A50","#FF7256","#FA8072","#FFA07A","#EEB4B4"]*3
  jsonfile_ = options.output+".json"
  drawFromJson(jsonfile_, category,debug_out+options.output+"_draw_from_json.pdf")
  drawFromJson(jsonfile_, category,debug_out+options.output+"_draw_from_json.C")
  doClosure([h2D_l1,h2D_l2],['m_{jet1}','m_{jet2}'],jsonfile_, category)
  
  
  
