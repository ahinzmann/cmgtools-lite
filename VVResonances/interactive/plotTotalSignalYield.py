#!/bin/env python
import ROOT
import json
import math
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
from time import sleep
import optparse, sys
from  CMGTools.VVResonances.plotting.CMS_lumi import *
from array import array
   
# ROOT.gROOT.SetBatch(True)

path = "../plots/"

def getLegend(x1=0.2,y1=0.7,x2=0.4,y2=0.9):
#def getLegend(x1=0.70010112,y1=0.693362,x2=0.90202143,y2=0.829833):
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
  
def getCanvasPaper(cname):
        ROOT.gStyle.SetOptStat(0)

        H_ref = 600
        W_ref = 600
        W = W_ref
        H  = H_ref
        iPeriod = 0
        # references for T, B, L, R
        T = 0.08*H_ref
        B = 0.15*H_ref
        L = 0.15*W_ref
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
        legend = getLegend()

        pt = ROOT.TPaveText(0.1746231,0.6031469,0.5251256,0.7517483,"NDC")
        pt.SetTextFont(42)
        pt.SetTextSize(0.04)
        pt.SetTextAlign(12)
        pt.SetFillColor(0)
        pt.SetBorderSize(0)
        pt.SetFillStyle(0)

        return canvas, legend, pt
'''
def getMVVPdf(j,MH,postfix=""):

        var = w.var(options.var)

        pdfName 	= "signal_%d%s" %(MH,postfix)
        Jmean 		= eval(j['MEAN'])
        Jsigma		= eval(j['SIGMA'])
        Jalpha1     = eval(j['ALPHA1'])
        Jalpha2     = eval(j['ALPHA2'])
        Jn1 		= eval(j['N1'])
        Jn2 		= eval(j['N2'])
        
        mean        = ROOT.RooRealVar("mean_%d%s"%(MH,postfix),"mean_%d%s"%(MH,postfix),Jmean)
        sigma       = ROOT.RooRealVar("sigma_%d%s"%(MH,postfix),"sigma_%d%s"%(MH,postfix),Jsigma)        
        alpha1      = ROOT.RooRealVar("alpha1_%d%s"%(MH,postfix),"alpha1_%d%s"%(MH,postfix),Jalpha1)
        alpha2      = ROOT.RooRealVar("alpha2_%d%s"%(MH,postfix),"alpha2_%d%s"%(MH,postfix),Jalpha2)
        n1          = ROOT.RooRealVar("n1_%d%s"%(MH,postfix),"n1_%d%s"%(MH,postfix),Jn1)
        n2          = ROOT.RooRealVar("n2_%d%s"%(MH,postfix),"n2_%d%s"%(MH,postfix),Jn2)
        

        alpha1.setConstant(ROOT.kTRUE)
        alpha2.setConstant(ROOT.kTRUE)
        n2.setConstant(ROOT.kTRUE)
        n1.setConstant(ROOT.kTRUE)
        mean.setConstant(ROOT.kTRUE)
        sigma.setConstant(ROOT.kTRUE)
                
        # gauss     = ROOT.RooGaussian("gauss_%d%s"%(MH,postfix), "gauss_%d%s"%(MH,postfix), var, mean, gsigma)
        # cb        = ROOT.RooCBShape("cb_%d%s"%(MH,postfix), "cb_%d%s"%(MH,postfix),var, mean, sigma, alpha, sign)
        # function = ROOT.RooAddPdf(pdfName, pdfName,gauss, cb, sigfrac)
        function = ROOT.RooDoubleCB(pdfName, pdfName,var, mean,sigma,alpha1,n1,alpha2,n2)
        getattr(w,'import')(function,ROOT.RooFit.Rename(pdfName))

def getMJPdf(j,MH,postfix=""):
 
        var = w.var(options.var)
	
        pdfName 	= "signal_%d%s" %(MH,postfix)
        Jmean 		= eval(j['mean'])
        Jsigma		= eval(j['sigma'])
        Jalpha 		= eval(j['alpha'])
        Jalpha2 	= eval(j['alpha2'])
        Jn 		= eval(j['n'])
        Jn2 		= eval(j['n2'])

        mean        = ROOT.RooRealVar("mean_%d%s"%(MH,postfix),"mean_%d%s"%(MH,postfix),Jmean)
        sigma       = ROOT.RooRealVar("sigma_%d%s"%(MH,postfix),"sigma_%d%s"%(MH,postfix),Jsigma)
        alpha       = ROOT.RooRealVar("alpha_%d%s"%(MH,postfix),"alpha_%d%s"%(MH,postfix),Jalpha)
        alpha2      = ROOT.RooRealVar("alpha2_%d%s"%(MH,postfix),"alpha2_%d%s"%(MH,postfix),Jalpha2)
        sign        = ROOT.RooRealVar("sign_%d%s"%(MH,postfix),"sign_%d%s"%(MH,postfix),Jn)
        sign2        = ROOT.RooRealVar("sign2_%d%s"%(MH,postfix),"sign2_%d%s"%(MH,postfix),Jn2)        

        alpha.setConstant(ROOT.kTRUE)
        sign.setConstant(ROOT.kTRUE)
        alpha2.setConstant(ROOT.kTRUE)
        sign2.setConstant(ROOT.kTRUE)
        mean.setConstant(ROOT.kTRUE)
        sigma.setConstant(ROOT.kTRUE)
        
	function = ROOT.RooDoubleCB(pdfName, pdfName, var, mean, sigma, alpha, sign,  alpha2, sign2)  
	getattr(w,'import')(function,ROOT.RooFit.Rename(pdfName))
'''		
parser = optparse.OptionParser()

parser.add_option("-v","--var",dest="var",help="mVV or mJ",default='mVV')
parser.add_option("-l","--leg",dest="leg",help="l1 or l2",default='l1')
parser.add_option("-p","--period",dest="period",help="2016 or 2017 or 2018 or Run2",default='Run2')
parser.add_option("-c","--category",dest="category",help="VV_HPHP or VV_HPLP or VH_HPHP etc",default='VV_HPLP')
parser.add_option("-s","--signal",dest="signal",help="signal",default='BulkGWW')
parser.add_option("-f","--folder",dest="folder",help="input directory",default='')
parser.add_option("-n","--name",dest="name",help="specify a label for the output file name",default='All')

postfix = "Jet 1 "
(options,args) = parser.parse_args()
if options.leg == "l2" !=-1: postfix = "Jet 2 "
purity  = options.category


#inFileName = options.file
#massPoints = [1000,1200,1400,1600,1800,2000,2500,3000,3500,4000,4500]
massPoints = [1200,1400,1600,1800,2000,2500,3000,3500,4000,4500]
#massPoints = [1200,1400,1600,1800,2000,2200,2400,2600,2800,3000,3200,3400,3600,3800,4000,4200,4400,4600,4800,5000,5200]
varName = {'mVV':'M_{VV} (GeV)','mJ':'%ssoftdrop mass (GeV)'%postfix}
varBins = {'mVV':'[37,1000,5500]','mJ':'[80,55,215]'}
w=ROOT.RooWorkspace("w","w")
w.factory(options.var+varBins[options.var])
w.var(options.var).SetTitle(varName[options.var])
colors= []
colors.append(["#f9c677","#f9d077","#f9f577","#ffd300","#f9fe77","#f9fe64","#f9fe43","#f9fe17"]*3)
colors.append(["#fee0d2","#fcbba1","#fc9272","#ef3b2c","#ef3b2c","#cb181d","#a50f15","#67000d"]*3) 
colors.append(["#e5f5e0","#c7e9c0","#a1d99b","#41ab5d","#41ab5d","#238b45","#006d2c","#00441b"]*3) 
colors.append(["#02fefe","#02e5fe","#02d7fe","#4292c6","#02b5fe","#02a8fe","#0282fe","#0300fc"]*3)  
colors.append(["#e6a3e1","#d987e6","#ce5ce0","#822391","#8526bd","#9b20e3","#a87eed","#8649eb"]*3)  
colors.append(["#45444B","#6B6974","#807D8D","#8F8BA2","#A39EBB","#AEA7D1","#B2A9E2","#B2A6F5"]*3)

'''
def doSingle():
    with open(inFileName) as jsonFile:
      j = json.load(jsonFile)
    
      c1 = getCanvas()
      c1.Draw()
      leg = ROOT.TLegend(0.8, 0.2, 0.95, 0.8)
      frame = w.var(options.var).frame()   
      
      for i, MH in enumerate(massPoints):  # mind that MH is evaluated below
        if options.var == 'mVV': getMVVPdf(j,MH)
        else: getMJPdf(j,MH)
        w.pdf('signal_%d'%MH).plotOn(frame, ROOT.RooFit.LineColor(ROOT.TColor.GetColor(colors[0][i])),ROOT.RooFit.Name(str(MH)))#,ROOT.RooFit.Range(MH*0.8,1.2*MH))#ROOT.RooFit.Normalization(1, ROOT.RooAbsReal.RelativeExpected),
        leg.AddEntry(frame.findObject(str(MH)), "%d GeV" % MH, "L")
      frame.GetYaxis().SetTitle("A.U")
      frame.GetYaxis().SetNdivisions(4,5,0)
      frame.SetMaximum(0.1)
      if options.var == 'mVV':frame.SetMaximum(0.5)
      frame.Draw()
      # leg.Draw("same")
      model = "G_{B} #rightarrow WW"
      if options.file.find("ZZ")!=-1:
          model = "G_{B} #rightarrow ZZ"
      if options.file.find("WZ")!=-1:
          model = "W' #rightarrow WZ"
      if options.file.find("Zprime")!=-1:
          model = "Z' #rightarrow WW"
      if   options.file.find("HPHP")!=-1: purity = "HPHP"
      elif options.file.find("HPLP")!=-1: purity = "HPLP"
      else:purity = "HPLP+HPHP"
      c1.cd()
      pt =ROOT.TPaveText(0.81,0.82,0.84,0.89,"brNDC")
      pt.SetBorderSize(0)
      pt.SetTextAlign(12)
      pt.SetFillStyle(0)
      pt.SetTextFont(42)
      pt.SetTextSize(0.04)
      pt.AddText(model)
      # pt.AddText(purity)

      pt.Draw()
      cmslabel_sim(c1,'2016',11)
      c1.Update()
      
      c1.SaveAs(path+"signalShapes%s_%s.png" %(options.var, inFileName.rsplit(".", 1)[0]))
      c1.SaveAs(path+"signalShapes%s_%s.pdf" %(options.var, inFileName.rsplit(".", 1)[0]))
      c1.SaveAs(path+"signalShapes%s_%s.C" %(options.var, inFileName.rsplit(".", 1)[0]))
      c1.SaveAs(path+"signalShapes%s_%s.root" %(options.var, inFileName.rsplit(".", 1)[0]))
'''
def doAll(signal,legend,colorindex):

#    directorypaper="results_QCD_pythia_signals_2016_tau21DDT_rho_VVpaper_HPHP_HPLP/"
#    directoryVV="doubleB_signalYield/VVVH_HPLP/"+options.name+"/"
#    directoryVH="doubleB_signalYield/VVVH_HPLP/"+options.name+"/"
    directoryVV="results_Run2/" #_VV_VH_scheme2_deepAK8_W_0p05_0p10_ZHbb_0p02_0p10_DDT_deltaEtaMaps/"
    directoryVH="results_Run2/" #_VV_VH_scheme2_deepAK8_W_0p05_0p10_ZHbb_0p02_0p10_DDT_deltaEtaMaps/"
    purities=["VV_HPHP","VV_HPLP","VH_HPHP","VH_HPLP","VH_LPHP"]
#    purities=["VV_HPHP","VV_HPLP","VH_HPHP","VH_LPHP"]
    c1,leg,pt = getCanvasPaper("c1")
    c1.Draw()
    gr=[]

    tot,Mass = array( 'd' ), array( 'd' )
    VV_HPHP=[]
    VV_HPLP=[]
    VH_HPHP=[]
    VH_HPLP=[]
    VH_LPHP=[]

    r_file_VV_HPHP = ROOT.TFile(directoryVV+"JJ_"+signal+"_"+str(options.period)+"_VV_HPHP_yield.root","READ")
    gr_VV_HPHP = r_file_VV_HPHP.Get("yield")
    print " get number of points ", gr_VV_HPHP.GetN()
    for i in range(gr_VV_HPHP.GetN()) :
      print gr_VV_HPHP.GetY()[i]
      gr_VV_HPHP.GetY()[i] *= 1000
      VV_HPHP.append( gr_VV_HPHP.GetY()[i])
      Mass.append( gr_VV_HPHP.GetX()[i])
      print gr_VV_HPHP.GetY()[i]

    gr_VV_HPHP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VV_HPHP.SetLineStyle(2)
    gr_VV_HPHP.SetLineWidth(2)
    gr_VV_HPHP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VV_HPHP.SetMarkerStyle(22)
    gr_VV_HPHP.GetYaxis().SetTitle("a.u.")
    gr_VV_HPHP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VV_HPHP.GetYaxis().SetTitleOffset(1.3)
    gr_VV_HPHP.GetYaxis().SetNdivisions(4,5,0)
    gr_VV_HPHP.GetXaxis().SetNdivisions(3,5,0)
    gr_VV_HPHP.SetMinimum(0.)
    gr_VV_HPHP.SetMaximum(0.3)
    gr_VV_HPHP.GetXaxis().SetTitleSize(0.055)
    gr_VV_HPHP.GetYaxis().SetTitleSize(0.055)
    gr_VV_HPHP.GetYaxis().SetLabelSize(0.05)
    gr_VV_HPHP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VV_HPHP.GetFunction("func")
    gr_VV_HPHP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VV_HPHP.Draw("APL")
#    gr_VV_HPHP.Draw("AP")

    r_file_VV_HPLP = ROOT.TFile(directoryVV+"JJ_"+signal+"_"+str(options.period)+"_VV_HPLP_yield.root","READ")
    gr_VV_HPLP = r_file_VV_HPLP.Get("yield")
    print " get number of points ", gr_VV_HPLP.GetN()
    for i in range(gr_VV_HPLP.GetN()) :
      print gr_VV_HPLP.GetY()[i]
      gr_VV_HPLP.GetY()[i] *= 1000
      VV_HPLP.append(gr_VV_HPLP.GetY()[i])
      print gr_VV_HPLP.GetY()[i]

    gr_VV_HPLP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VV_HPLP.SetLineStyle(3)
    gr_VV_HPLP.SetLineWidth(2)
    gr_VV_HPLP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VV_HPLP.SetMarkerStyle(23)
    gr_VV_HPLP.GetYaxis().SetTitle("a.u.")
    gr_VV_HPLP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VV_HPLP.GetYaxis().SetTitleOffset(1.3)
    gr_VV_HPLP.GetYaxis().SetNdivisions(4,5,0)
    gr_VV_HPLP.GetXaxis().SetNdivisions(3,5,0)
    gr_VV_HPLP.SetMinimum(0.)
    gr_VV_HPLP.SetMaximum(0.4)
    gr_VV_HPLP.GetXaxis().SetTitleSize(0.055)
    gr_VV_HPLP.GetYaxis().SetTitleSize(0.055)
    gr_VV_HPLP.GetYaxis().SetLabelSize(0.05)
    gr_VV_HPLP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VV_HPLP.GetFunction("func")
    gr_VV_HPLP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VV_HPLP.Draw("PL")

    r_file_VH_HPHP = ROOT.TFile(directoryVH+"JJ_"+signal+"_"+str(options.period)+"_VH_HPHP_yield.root","READ")
    gr_VH_HPHP = r_file_VH_HPHP.Get("yield")
    print " get number of points ", gr_VH_HPHP.GetN()
    for i in range(gr_VH_HPHP.GetN()) :
      print gr_VH_HPHP.GetY()[i]
      gr_VH_HPHP.GetY()[i] *= 1000
      VH_HPHP.append( gr_VH_HPHP.GetY()[i])
      Mass.append( gr_VH_HPHP.GetX()[i])
      print gr_VH_HPHP.GetY()[i]

    gr_VH_HPHP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_HPHP.SetLineStyle(2)
    gr_VH_HPHP.SetLineWidth(2)
    gr_VH_HPHP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_HPHP.SetMarkerStyle(26)
    gr_VH_HPHP.GetYaxis().SetTitle("a.u.")
    gr_VH_HPHP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VH_HPHP.GetYaxis().SetTitleOffset(1.3)
    gr_VH_HPHP.GetYaxis().SetNdivisions(4,5,0)
    gr_VH_HPHP.GetXaxis().SetNdivisions(3,5,0)
    gr_VH_HPHP.SetMinimum(0.)
    gr_VH_HPHP.SetMaximum(0.225)
    gr_VH_HPHP.GetXaxis().SetTitleSize(0.055)
    gr_VH_HPHP.GetYaxis().SetTitleSize(0.055)
    gr_VH_HPHP.GetYaxis().SetLabelSize(0.05)
    gr_VH_HPHP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VH_HPHP.GetFunction("func")
    gr_VH_HPHP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VH_HPHP.Draw("PL")

 
    r_file_VH_HPLP = ROOT.TFile(directoryVH+"JJ_"+signal+"_"+str(options.period)+"_VH_HPLP_yield.root","READ")
    gr_VH_HPLP = r_file_VH_HPLP.Get("yield")
    print " get number of points ", gr_VH_HPLP.GetN()
    for i in range(gr_VH_HPLP.GetN()) :
      print gr_VH_HPLP.GetY()[i]
      gr_VH_HPLP.GetY()[i] *= 1000
      VH_HPLP.append(gr_VH_HPLP.GetY()[i])
      print gr_VH_HPLP.GetY()[i]

    gr_VH_HPLP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_HPLP.SetLineStyle(3)
    gr_VH_HPLP.SetLineWidth(2)
    gr_VH_HPLP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_HPLP.SetMarkerStyle(21)
    gr_VH_HPLP.GetYaxis().SetTitle("a.u.")
    gr_VH_HPLP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VH_HPLP.GetYaxis().SetTitleOffset(1.3)
    gr_VH_HPLP.GetYaxis().SetNdivisions(4,5,0)
    gr_VH_HPLP.GetXaxis().SetNdivisions(3,5,0)
    gr_VH_HPLP.SetMinimum(0.)
    gr_VH_HPLP.SetMaximum(0.225)
    gr_VH_HPLP.GetXaxis().SetTitleSize(0.055)
    gr_VH_HPLP.GetYaxis().SetTitleSize(0.055)
    gr_VH_HPLP.GetYaxis().SetLabelSize(0.05)
    gr_VH_HPLP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VH_HPLP.GetFunction("func")
    gr_VH_HPLP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VH_HPLP.Draw("PL")
 

    r_file_VH_LPHP = ROOT.TFile(directoryVH+"JJ_"+signal+"_"+str(options.period)+"_VH_LPHP_yield.root","READ")
    gr_VH_LPHP = r_file_VH_LPHP.Get("yield")
    print " get number of points ", gr_VH_LPHP.GetN()
    for i in range(gr_VH_LPHP.GetN()) :
      print gr_VH_LPHP.GetY()[i]
      gr_VH_LPHP.GetY()[i] *= 1000
      VH_LPHP.append(gr_VH_LPHP.GetY()[i])
      print gr_VH_LPHP.GetY()[i]

    gr_VH_LPHP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_LPHP.SetLineStyle(4)
    gr_VH_LPHP.SetLineWidth(2)
    gr_VH_LPHP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_LPHP.SetMarkerStyle(25)
    gr_VH_LPHP.GetYaxis().SetTitle("a.u.")
    gr_VH_LPHP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VH_LPHP.GetYaxis().SetTitleOffset(1.3)
    gr_VH_LPHP.GetYaxis().SetNdivisions(4,5,0)
    gr_VH_LPHP.GetXaxis().SetNdivisions(3,5,0)
    gr_VH_LPHP.SetMinimum(0.)
    gr_VH_LPHP.SetMaximum(0.225)
    gr_VH_LPHP.GetXaxis().SetTitleSize(0.055)
    gr_VH_LPHP.GetYaxis().SetTitleSize(0.055)
    gr_VH_LPHP.GetYaxis().SetLabelSize(0.05)
    gr_VH_LPHP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VH_LPHP.GetFunction("func")
    gr_VH_LPHP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VH_LPHP.Draw("PL")

    for i in range(gr_VV_HPHP.GetN()) :
      tot.append( VV_HPHP[i]+VV_HPLP[i]+VH_HPHP[i]+VH_HPLP[i]+VH_LPHP[i])
      #tot.append( VV_HPHP[i]+VV_HPLP[i]+VH_HPHP[i]+VH_LPHP[i])
      print tot[i]

    gr_tot = ROOT.TGraph(gr_VV_HPHP.GetN(),Mass,tot)
    gr_tot.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_tot.SetLineStyle(1)
    gr_tot.SetLineWidth(2)
    gr_tot.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_tot.SetMarkerStyle(20)
    gr_tot.Draw("PL")

    leg.AddEntry(gr_tot, "VV+VH tot", "LP")
    leg.AddEntry(gr_VV_HPLP, "VV_HPLP", "LP")
    leg.AddEntry(gr_VV_HPHP, "VV_HPHP", "LP")
    leg.AddEntry(gr_VH_HPLP, "VH_HPLP", "LP")
    leg.AddEntry(gr_VH_LPHP, "VH_LPHP", "LP")
    leg.AddEntry(gr_VH_HPHP, "VH_HPHP", "LP")
    leg.Draw("same")

    
    pt2 = ROOT.TPaveText(0.7,0.8,0.8,0.9,"NDC")
    pt2.SetTextFont(42)
    pt2.SetTextSize(0.05)
    pt2.SetTextAlign(12)
    pt2.SetFillColor(0)
    pt2.SetBorderSize(0)
    pt2.SetFillStyle(0)
    pt2.AddText(legend)
    pt2.Draw()


    name = path+"signalYelds_compareTotalVVVH_%s_%s_%s"  %(options.period,options.name,signal)
    c1.SaveAs(name+".png")
    c1.SaveAs(name+".pdf" )
    c1.SaveAs(name+".C"   )
    c1.SaveAs(name+".root")

def doAllTestVHLPLP(signal,legend,colorindex):

#    directorypaper="results_QCD_pythia_signals_2016_tau21DDT_rho_VVpaper_HPHP_HPLP/"
#    directoryVV="doubleB_signalYield/VVVH_HPLP/"+options.name+"/"
#    directoryVH="doubleB_signalYield/VVVH_HPLP/"+options.name+"/"
    directoryVV="results_2016/" #_VV_VH_deepAK8_WZH_0p8_0p4_trainingV2/"
    directoryVH="results_2016/" #_VV_VH_deepAK8_WZH_0p8_0p4_trainingV2/"
    purities=["VV_HPHP","VV_HPLP","VH_HPHP","VH_HPLP","VH_LPHP,VH_LPLP"]
#    purities=["VV_HPHP","VV_HPLP","VH_HPHP","VH_LPHP"]
    c1,leg,pt = getCanvasPaper("c1")
    c1.Draw()
    gr=[]

    tot,Mass = array( 'd' ), array( 'd' )
    VV_HPHP=[]
    VV_HPLP=[]
    VH_HPHP=[]
    VH_HPLP=[]
    VH_LPHP=[]
    VH_LPLP=[]

    r_file_VV_HPHP = ROOT.TFile(directoryVV+"JJ_"+signal+"_"+str(options.period)+"_VV_HPHP_yield.root","READ")
    gr_VV_HPHP = r_file_VV_HPHP.Get("yield")
    print " get number of points ", gr_VV_HPHP.GetN()
    for i in range(gr_VV_HPHP.GetN()) :
      print gr_VV_HPHP.GetY()[i]
      gr_VV_HPHP.GetY()[i] *= 1000
      VV_HPHP.append( gr_VV_HPHP.GetY()[i])
      Mass.append( gr_VV_HPHP.GetX()[i])
      print gr_VV_HPHP.GetY()[i]

    gr_VV_HPHP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VV_HPHP.SetLineStyle(2)
    gr_VV_HPHP.SetLineWidth(2)
    gr_VV_HPHP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VV_HPHP.SetMarkerStyle(22)
    gr_VV_HPHP.GetYaxis().SetTitle("a.u.")
    gr_VV_HPHP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VV_HPHP.GetYaxis().SetTitleOffset(1.3)
    gr_VV_HPHP.GetYaxis().SetNdivisions(4,5,0)
    gr_VV_HPHP.GetXaxis().SetNdivisions(3,5,0)
    gr_VV_HPHP.SetMinimum(0.)
    gr_VV_HPHP.SetMaximum(0.3)
    gr_VV_HPHP.GetXaxis().SetTitleSize(0.055)
    gr_VV_HPHP.GetYaxis().SetTitleSize(0.055)
    gr_VV_HPHP.GetYaxis().SetLabelSize(0.05)
    gr_VV_HPHP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VV_HPHP.GetFunction("func")
    gr_VV_HPHP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VV_HPHP.Draw("APL")

    r_file_VV_HPLP = ROOT.TFile(directoryVV+"JJ_"+signal+"_"+str(options.period)+"_VV_HPLP_yield.root","READ")
    gr_VV_HPLP = r_file_VV_HPLP.Get("yield")
    print " get number of points ", gr_VV_HPLP.GetN()
    for i in range(gr_VV_HPLP.GetN()) :
      print gr_VV_HPLP.GetY()[i]
      gr_VV_HPLP.GetY()[i] *= 1000
      VV_HPLP.append(gr_VV_HPLP.GetY()[i])
      print gr_VV_HPLP.GetY()[i]

    gr_VV_HPLP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VV_HPLP.SetLineStyle(3)
    gr_VV_HPLP.SetLineWidth(2)
    gr_VV_HPLP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VV_HPLP.SetMarkerStyle(23)
    gr_VV_HPLP.GetYaxis().SetTitle("a.u.")
    gr_VV_HPLP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VV_HPLP.GetYaxis().SetTitleOffset(1.3)
    gr_VV_HPLP.GetYaxis().SetNdivisions(4,5,0)
    gr_VV_HPLP.GetXaxis().SetNdivisions(3,5,0)
    gr_VV_HPLP.SetMinimum(0.)
    gr_VV_HPLP.SetMaximum(0.4)
    gr_VV_HPLP.GetXaxis().SetTitleSize(0.055)
    gr_VV_HPLP.GetYaxis().SetTitleSize(0.055)
    gr_VV_HPLP.GetYaxis().SetLabelSize(0.05)
    gr_VV_HPLP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VV_HPLP.GetFunction("func")
    gr_VV_HPLP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VV_HPLP.Draw("PL")

    r_file_VH_HPHP = ROOT.TFile(directoryVH+"JJ_"+signal+"_"+str(options.period)+"_VH_HPHP_yield.root","READ")
    gr_VH_HPHP = r_file_VH_HPHP.Get("yield")
    print " get number of points ", gr_VH_HPHP.GetN()
    for i in range(gr_VH_HPHP.GetN()) :
      print gr_VH_HPHP.GetY()[i]
      gr_VH_HPHP.GetY()[i] *= 1000
      VH_HPHP.append( gr_VH_HPHP.GetY()[i])
      Mass.append( gr_VH_HPHP.GetX()[i])
      print gr_VH_HPHP.GetY()[i]

    gr_VH_HPHP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_HPHP.SetLineStyle(2)
    gr_VH_HPHP.SetLineWidth(2)
    gr_VH_HPHP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_HPHP.SetMarkerStyle(26)
    gr_VH_HPHP.GetYaxis().SetTitle("a.u.")
    gr_VH_HPHP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VH_HPHP.GetYaxis().SetTitleOffset(1.3)
    gr_VH_HPHP.GetYaxis().SetNdivisions(4,5,0)
    gr_VH_HPHP.GetXaxis().SetNdivisions(3,5,0)
    gr_VH_HPHP.SetMinimum(0.)
    gr_VH_HPHP.SetMaximum(0.225)
    gr_VH_HPHP.GetXaxis().SetTitleSize(0.055)
    gr_VH_HPHP.GetYaxis().SetTitleSize(0.055)
    gr_VH_HPHP.GetYaxis().SetLabelSize(0.05)
    gr_VH_HPHP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VH_HPHP.GetFunction("func")
    gr_VH_HPHP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VH_HPHP.Draw("PL")

 
    r_file_VH_HPLP = ROOT.TFile(directoryVH+"JJ_"+signal+"_"+str(options.period)+"_VH_HPLP_yield.root","READ")
    gr_VH_HPLP = r_file_VH_HPLP.Get("yield")
    print " get number of points ", gr_VH_HPLP.GetN()
    for i in range(gr_VH_HPLP.GetN()) :
      print gr_VH_HPLP.GetY()[i]
      gr_VH_HPLP.GetY()[i] *= 1000
      VH_HPLP.append(gr_VH_HPLP.GetY()[i])
      print gr_VH_HPLP.GetY()[i]

    gr_VH_HPLP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_HPLP.SetLineStyle(3)
    gr_VH_HPLP.SetLineWidth(2)
    gr_VH_HPLP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_HPLP.SetMarkerStyle(21)
    gr_VH_HPLP.GetYaxis().SetTitle("a.u.")
    gr_VH_HPLP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VH_HPLP.GetYaxis().SetTitleOffset(1.3)
    gr_VH_HPLP.GetYaxis().SetNdivisions(4,5,0)
    gr_VH_HPLP.GetXaxis().SetNdivisions(3,5,0)
    gr_VH_HPLP.SetMinimum(0.)
    gr_VH_HPLP.SetMaximum(0.225)
    gr_VH_HPLP.GetXaxis().SetTitleSize(0.055)
    gr_VH_HPLP.GetYaxis().SetTitleSize(0.055)
    gr_VH_HPLP.GetYaxis().SetLabelSize(0.05)
    gr_VH_HPLP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VH_HPLP.GetFunction("func")
    gr_VH_HPLP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VH_HPLP.Draw("PL")
 

    r_file_VH_LPHP = ROOT.TFile(directoryVH+"JJ_"+signal+"_"+str(options.period)+"_VH_LPHP_yield.root","READ")
    gr_VH_LPHP = r_file_VH_LPHP.Get("yield")
    print " get number of points ", gr_VH_LPHP.GetN()
    for i in range(gr_VH_LPHP.GetN()) :
      print gr_VH_LPHP.GetY()[i]
      gr_VH_LPHP.GetY()[i] *= 1000
      VH_LPHP.append(gr_VH_LPHP.GetY()[i])
      print gr_VH_LPHP.GetY()[i]

    gr_VH_LPHP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_LPHP.SetLineStyle(4)
    gr_VH_LPHP.SetLineWidth(2)
    gr_VH_LPHP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_LPHP.SetMarkerStyle(25)
    gr_VH_LPHP.GetYaxis().SetTitle("a.u.")
    gr_VH_LPHP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VH_LPHP.GetYaxis().SetTitleOffset(1.3)
    gr_VH_LPHP.GetYaxis().SetNdivisions(4,5,0)
    gr_VH_LPHP.GetXaxis().SetNdivisions(3,5,0)
    gr_VH_LPHP.SetMinimum(0.)
    gr_VH_LPHP.SetMaximum(0.225)
    gr_VH_LPHP.GetXaxis().SetTitleSize(0.055)
    gr_VH_LPHP.GetYaxis().SetTitleSize(0.055)
    gr_VH_LPHP.GetYaxis().SetLabelSize(0.05)
    gr_VH_LPHP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VH_LPHP.GetFunction("func")
    gr_VH_LPHP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VH_LPHP.Draw("PL")

    r_file_VH_LPLP = ROOT.TFile(directoryVH+"JJ_"+signal+"_"+str(options.period)+"_VH_LPLP_yield.root","READ")
    gr_VH_LPLP = r_file_VH_LPLP.Get("yield")
    print " get number of points ", gr_VH_LPLP.GetN()
    for i in range(gr_VH_LPLP.GetN()) :
      print gr_VH_LPLP.GetY()[i]
      gr_VH_LPLP.GetY()[i] *= 1000
      VH_LPLP.append(gr_VH_LPLP.GetY()[i])
      print gr_VH_LPLP.GetY()[i]

    gr_VH_LPLP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_LPLP.SetLineStyle(4)
    gr_VH_LPLP.SetLineWidth(2)
    gr_VH_LPLP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_VH_LPLP.SetMarkerStyle(27)
    gr_VH_LPLP.GetYaxis().SetTitle("a.u.")
    gr_VH_LPLP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_VH_LPLP.GetYaxis().SetTitleOffset(1.3)
    gr_VH_LPLP.GetYaxis().SetNdivisions(4,5,0)
    gr_VH_LPLP.GetXaxis().SetNdivisions(3,5,0)
    gr_VH_LPLP.SetMinimum(0.)
    gr_VH_LPLP.SetMaximum(0.225)
    gr_VH_LPLP.GetXaxis().SetTitleSize(0.055)
    gr_VH_LPLP.GetYaxis().SetTitleSize(0.055)
    gr_VH_LPLP.GetYaxis().SetLabelSize(0.05)
    gr_VH_LPLP.GetXaxis().SetLabelSize(0.05)
    ff = gr_VH_LPLP.GetFunction("func")
    gr_VH_LPLP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_VH_LPLP.Draw("PL")

    for i in range(gr_VV_HPHP.GetN()) :
      tot.append( VV_HPHP[i]+VV_HPLP[i]+VH_HPHP[i]+VH_HPLP[i]+VH_LPHP[i]+VH_LPLP[i])
      #tot.append( VV_HPHP[i]+VV_HPLP[i]+VH_HPHP[i]+VH_LPHP[i])
      print tot[i]

    gr_tot = ROOT.TGraph(gr_VV_HPHP.GetN(),Mass,tot)
    gr_tot.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_tot.SetLineStyle(1)
    gr_tot.SetLineWidth(2)
    gr_tot.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_tot.SetMarkerStyle(20)
    gr_tot.Draw("PL")

    leg.AddEntry(gr_tot, "VV+VH tot", "LP")
    leg.AddEntry(gr_VV_HPLP, "VV_HPLP", "LP")
    leg.AddEntry(gr_VV_HPHP, "VV_HPHP", "LP")
    leg.AddEntry(gr_VH_HPLP, "VH_HPLP", "LP")
    leg.AddEntry(gr_VH_LPHP, "VH_LPHP", "LP")
    leg.AddEntry(gr_VH_HPHP, "VH_HPHP", "LP")
    leg.AddEntry(gr_VH_LPLP, "VH_LPLP", "LP")
    leg.Draw("same")

    
    pt2 = ROOT.TPaveText(0.7,0.8,0.8,0.9,"NDC")
    pt2.SetTextFont(42)
    pt2.SetTextSize(0.05)
    pt2.SetTextAlign(12)
    pt2.SetFillColor(0)
    pt2.SetBorderSize(0)
    pt2.SetFillStyle(0)
    pt2.AddText(legend)
    pt2.Draw()


    name = path+"signalYelds_compareTotalVVVH_alsoVHLPLP_%s_%s_%s"  %(options.period,options.name,signal)
    c1.SaveAs(name+".png")
    c1.SaveAs(name+".pdf" )
    c1.SaveAs(name+".C"   )
    c1.SaveAs(name+".root")



def doAllOld(signal,legend,colorindex):

#    directorypaper="results_QCD_pythia_signals_2016_DeepW_VVpaper_HPHP_HPLP/"
    directorypaper="results_2016_VVinclu_deepAK8WDDT/"
#    directoryVV="results_QCD_pythia_signals_2016_tau21DDT_rho_VV_HPHP_HPLP/"
#    directoryVH="results_QCD_pythia_signals_2016_tau21DDT_rho_VH_HPHP_HPLP_LPHP/"
    purities=["VV_HPHP","VV_HPLP"] #,"VH_HPHP","VH_HPLP","VH_LPHP"]
#    purities=["VV_HPHP","VV_HPLP","VH_HPHP","VH_HPLP","VH_LPHP"]


#    files = ["JJ_BulkGZZ_"+str(options.period)+"_"+str(purity1)+"_yield.root","JJ_WprimeWZ_"+str(options.period)+"_"+str(purity1)+"_yield.root","JJ_BulkGWW_"+str(options.period)+"_"+str(purity1)+"_yield.root","JJ_ZprimeWW_"+str(options.period)+"_"+str(purity1)+"_yield.root","JJ_ZprimeZH_"+str(options.period)+"_"+str(purity1)+"_yield.root"]
#    legs = ["G_{bulk} #rightarrow ZZ","W' #rightarrow WZ","G_{bulk} #rightarrow WW","Z'#rightarrow WW","Z'#rightarrow ZH"]
    c1,leg,pt = getCanvasPaper("c1")
    c1.Draw()
    gr=[]

    tot,Mass = array( 'd' ), array( 'd' )
    HPHP=[]
    HPLP=[]
#    tot=[]
#    Mass=[]
    r_file_HPHP = ROOT.TFile(directorypaper+"JJ_"+signal+"_"+str(options.period)+"_VV_HPHP_yield.root","READ")
    gr_HPHP = r_file_HPHP.Get("yield")
    print " get number of points ", gr_HPHP.GetN()
    for i in range(gr_HPHP.GetN()) :
      print gr_HPHP.GetY()[i]
      gr_HPHP.GetY()[i] *= 1000
      HPHP.append( gr_HPHP.GetY()[i])
      Mass.append( gr_HPHP.GetX()[i])
      print gr_HPHP.GetY()[i]

    gr_HPHP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_HPHP.SetLineStyle(2)
    gr_HPHP.SetLineWidth(2)
    gr_HPHP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_HPHP.SetMarkerStyle(22)
    gr_HPHP.GetYaxis().SetTitle("a.u.")
    gr_HPHP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_HPHP.GetYaxis().SetTitleOffset(1.3)
    gr_HPHP.GetYaxis().SetNdivisions(4,5,0)
    gr_HPHP.GetXaxis().SetNdivisions(3,5,0)
    gr_HPHP.SetMinimum(0.)
    gr_HPHP.SetMaximum(0.3)
    gr_HPHP.GetXaxis().SetTitleSize(0.055)
    gr_HPHP.GetYaxis().SetTitleSize(0.055)
    gr_HPHP.GetYaxis().SetLabelSize(0.05)
    gr_HPHP.GetXaxis().SetLabelSize(0.05)
    ff = gr_HPHP.GetFunction("func")
    gr_HPHP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_HPHP.Draw("APL")

    r_file_HPLP = ROOT.TFile(directorypaper+"JJ_"+signal+"_"+str(options.period)+"_VV_HPLP_yield.root","READ")
    gr_HPLP = r_file_HPLP.Get("yield")
    print " get number of points ", gr_HPLP.GetN()
    for i in range(gr_HPLP.GetN()) :
      print gr_HPLP.GetY()[i]
      gr_HPLP.GetY()[i] *= 1000
      HPLP.append(gr_HPLP.GetY()[i])
      print gr_HPLP.GetY()[i]

    gr_HPLP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_HPLP.SetLineStyle(3)
    gr_HPLP.SetLineWidth(2)
    gr_HPLP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_HPLP.SetMarkerStyle(23)
    gr_HPLP.GetYaxis().SetTitle("a.u.")
    gr_HPLP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_HPLP.GetYaxis().SetTitleOffset(1.3)
    gr_HPLP.GetYaxis().SetNdivisions(4,5,0)
    gr_HPLP.GetXaxis().SetNdivisions(3,5,0)
    gr_HPLP.SetMinimum(0.)
    gr_HPLP.SetMaximum(0.225)
    gr_HPLP.GetXaxis().SetTitleSize(0.055)
    gr_HPLP.GetYaxis().SetTitleSize(0.055)
    gr_HPLP.GetYaxis().SetLabelSize(0.05)
    gr_HPLP.GetXaxis().SetLabelSize(0.05)
    ff = gr_HPLP.GetFunction("func")
    gr_HPLP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_HPLP.Draw("PL")

    for i in range(gr_HPHP.GetN()) :
      tot.append( HPHP[i]+HPLP[i])
      print tot[i]

    gr_tot = ROOT.TGraph(gr_HPHP.GetN(),Mass,tot)
    gr_tot.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_tot.SetLineStyle(1)
    gr_tot.SetLineWidth(2)
    gr_tot.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_tot.SetMarkerStyle(20)
    gr_tot.Draw("PL")

    leg.AddEntry(gr_tot, "VV_tot", "LP")
    leg.AddEntry(gr_HPLP, "VV_HPLP", "LP")
    leg.AddEntry(gr_HPHP, "VV_HPHP", "LP")
    leg.Draw("same")

    pt2 = ROOT.TPaveText(0.7,0.8,0.8,0.9,"NDC")
    pt2.SetTextFont(42)
    pt2.SetTextSize(0.05)

    #pt2 = ROOT.TPaveText(0.16,0.62,0.63,0.76,"NDC")
    #pt2.SetTextFont(42)
    #pt2.SetTextSize(0.04)
    pt2.SetTextAlign(12)
    pt2.SetFillColor(0)
    pt2.SetBorderSize(0)
    pt2.SetFillStyle(0)
    pt2.AddText(legend)
    pt2.Draw()


    name = path+"signalYelds_compareTotalVVpaper_%s_%s_%s_%s"  %(options.var,options.period,options.name,signal)
    c1.SaveAs(name+".png")
    c1.SaveAs(name+".pdf" )
    c1.SaveAs(name+".C"   )
    c1.SaveAs(name+".root")

def doAllOldCompare(signal,legend,colorindex):

    directorypaperDeepW="results_QCD_pythia_signals_2016_DeepW_VVpaper_HPHP_HPLP/"
    directorypaper="results_QCD_pythia_signals_2016_tau21DDT_rho_VVpaper_HPHP_HPLP/"
#    directoryVV="results_QCD_pythia_signals_2016_tau21DDT_rho_VV_HPHP_HPLP/"
#    directoryVH="results_QCD_pythia_signals_2016_tau21DDT_rho_VH_HPHP_HPLP_LPHP/"
    purities=["VV_HPHP","VV_HPLP","VH_HPHP","VH_HPLP","VH_LPHP"]


#    files = ["JJ_BulkGZZ_"+str(options.period)+"_"+str(purity1)+"_yield.root","JJ_WprimeWZ_"+str(options.period)+"_"+str(purity1)+"_yield.root","JJ_BulkGWW_"+str(options.period)+"_"+str(purity1)+"_yield.root","JJ_ZprimeWW_"+str(options.period)+"_"+str(purity1)+"_yield.root","JJ_ZprimeZH_"+str(options.period)+"_"+str(purity1)+"_yield.root"]
#    legs = ["G_{bulk} #rightarrow ZZ","W' #rightarrow WZ","G_{bulk} #rightarrow WW","Z'#rightarrow WW","Z'#rightarrow ZH"]
    c1,leg,pt = getCanvasPaper("c1")
    c1.Draw()
    gr=[]

    tot,Mass = array( 'd' ), array( 'd' )
    HPHP=[]
    HPLP=[]
#    tot=[]
#    Mass=[]
    r_file_HPHP = ROOT.TFile(directorypaperDeepW+"JJ_"+signal+"_"+str(options.period)+"_VV_HPLP_yield.root","READ")
    gr_HPHP = r_file_HPHP.Get("yield")
    print " get number of points ", gr_HPHP.GetN()
    for i in range(gr_HPHP.GetN()) :
      print gr_HPHP.GetY()[i]
      gr_HPHP.GetY()[i] *= 1000
      HPHP.append( gr_HPHP.GetY()[i])
      Mass.append( gr_HPHP.GetX()[i])
      print gr_HPHP.GetY()[i]

    gr_HPHP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_HPHP.SetLineStyle(2)
    gr_HPHP.SetLineWidth(2)
    gr_HPHP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_HPHP.SetMarkerStyle(22)
    gr_HPHP.GetYaxis().SetTitle("a.u.")
    gr_HPHP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_HPHP.GetYaxis().SetTitleOffset(1.3)
    gr_HPHP.GetYaxis().SetNdivisions(4,5,0)
    gr_HPHP.GetXaxis().SetNdivisions(3,5,0)
    gr_HPHP.SetMinimum(0.)
    gr_HPHP.SetMaximum(0.225)
    gr_HPHP.GetXaxis().SetTitleSize(0.055)
    gr_HPHP.GetYaxis().SetTitleSize(0.055)
    gr_HPHP.GetYaxis().SetLabelSize(0.05)
    gr_HPHP.GetXaxis().SetLabelSize(0.05)
    ff = gr_HPHP.GetFunction("func")
    gr_HPHP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_HPHP.Draw("APL")

    r_file_HPLP = ROOT.TFile(directorypaper+"JJ_"+signal+"_"+str(options.period)+"_VV_HPLP_yield.root","READ")
    gr_HPLP = r_file_HPLP.Get("yield")
    print " get number of points ", gr_HPLP.GetN()
    for i in range(gr_HPLP.GetN()) :
      print gr_HPLP.GetY()[i]
      gr_HPLP.GetY()[i] *= 1000
      HPLP.append(gr_HPLP.GetY()[i])
      print gr_HPLP.GetY()[i]

    gr_HPLP.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_HPLP.SetLineStyle(3)
    gr_HPLP.SetLineWidth(2)
    gr_HPLP.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_HPLP.SetMarkerStyle(23)
    gr_HPLP.GetYaxis().SetTitle("a.u.")
    gr_HPLP.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_HPLP.GetYaxis().SetTitleOffset(1.3)
    gr_HPLP.GetYaxis().SetNdivisions(4,5,0)
    gr_HPLP.GetXaxis().SetNdivisions(3,5,0)
    gr_HPLP.SetMinimum(0.)
    gr_HPLP.SetMaximum(0.225)
    gr_HPLP.GetXaxis().SetTitleSize(0.055)
    gr_HPLP.GetYaxis().SetTitleSize(0.055)
    gr_HPLP.GetYaxis().SetLabelSize(0.05)
    gr_HPLP.GetXaxis().SetLabelSize(0.05)
    ff = gr_HPLP.GetFunction("func")
    gr_HPLP.Fit(ff)
    ff.SetLineColor(0)
    ff.SetLineWidth(0)

    gr_HPLP.Draw("PL")

    for i in range(gr_HPHP.GetN()) :
      tot.append( HPHP[i]+HPLP[i])
      print tot[i]

    gr_tot = ROOT.TGraph(gr_HPHP.GetN(),Mass,tot)
    gr_tot.SetLineColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_tot.SetLineStyle(1)
    gr_tot.SetLineWidth(2)
    gr_tot.SetMarkerColor(ROOT.TColor.GetColor(colors[colorindex][3]))
    gr_tot.SetMarkerStyle(20)
#    gr_tot.Draw("PL")

 #   leg.AddEntry(gr_tot, "VV_tot", "LP")
    leg.AddEntry(gr_HPLP, "tau21DDT", "LP")
    leg.AddEntry(gr_HPHP, "DeepAK8 WvsQCD", "LP")
    leg.Draw("same")

    pt2 = ROOT.TPaveText(0.7,0.8,0.8,0.9,"NDC")
    pt2.SetTextFont(42)
    pt2.SetTextSize(0.05)

    #pt2 = ROOT.TPaveText(0.16,0.62,0.63,0.76,"NDC")
    #pt2.SetTextFont(42)
    #pt2.SetTextSize(0.04)
    pt2.SetTextAlign(12)
    pt2.SetFillColor(0)
    pt2.SetBorderSize(0)
    pt2.SetFillStyle(0)
    pt2.AddText(legend)
    pt2.Draw()


    name = path+"signalYelds_compareVVpaper_tau21DDT_DeepW_%s_%s_%s_%s"  %(options.var,options.period,options.name,signal)
    c1.SaveAs(name+".png")
    c1.SaveAs(name+".pdf" )
    c1.SaveAs(name+".C"   )
    c1.SaveAs(name+".root")
    
    # sleep(1000)
                
if __name__ == '__main__':
    signals = ["BulkGZZ","WprimeWZ","BulkGWW","ZprimeWW","ZprimeZH","WprimeWH"]
    legs = ["G_{bulk} #rightarrow ZZ","W' #rightarrow WZ","G_{bulk} #rightarrow WW","Z'#rightarrow WW","Z'#rightarrow ZH","W'#rightarrow WH"]
    
    for i in range(len(signals)):
      print i
      print signals[i]
      print legs[i]
      doAll(signals[i],legs[i],i)

