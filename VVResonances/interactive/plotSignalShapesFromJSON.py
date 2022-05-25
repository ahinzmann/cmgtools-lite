#!/bin/env python
import ROOT
import json
import math
import types
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
from time import sleep
import optparse, sys
from  CMGTools.VVResonances.plotting.CMS_lumi import *

# ROOT.gROOT.SetBatch(True)

def getLegend(textsize=0.20,x1=0.345809045,y1=0.6363636,x2=0.9522613,y2=0.9020979):
  legend = ROOT.TLegend(x1,y1,x2,y2)
  legend.SetTextSize(textsize)
  legend.SetLineColor(0)
  legend.SetShadowColor(0)
  legend.SetLineStyle(1)
  legend.SetLineWidth(1)
  legend.SetFillColor(0)
  legend.SetFillStyle(0)
  legend.SetMargin(0.35)
  legend.SetTextFont(42)
  return legend
  
def getCanvasPaper(cname):
 ROOT.gStyle.SetOptStat(0)

 H_ref = 700 
 W_ref = 600 
 W = W_ref
 H  = H_ref
 iPeriod = 0
 # references for T, B, L, R
 if options.var =="mVV":
    T = 0.3*H_ref
    B = 0.35*H_ref 
    L = 0.10*W_ref
    R = 0.10*W_ref #0.07*W_ref
 else:
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
 #legend = getLegend()
 
 
 pt = ROOT.TPaveText(0.1746231,0.6031469,0.5251256,0.7517483,"NDC")
 pt.SetTextFont(42)
 pt.SetTextSize(0.04)
 pt.SetTextAlign(12)
 pt.SetFillColor(0)
 pt.SetBorderSize(0)
 pt.SetFillStyle(0)
 
 
 return canvas, pt

	
def getMVVPdf(w,j,MH,postfix=""):
  getPdf(w,j,MH,postfix,None,True)

def getMJPdf(w,j,MH,postfix="",jH=None):
  getPdf(w,j,MH,postfix,jH,False)

def getPdf(w,j,MH,postfix="",jH=None,isMVV=False):
        var = w.var(options.var)
        pdfName 	= "signal_%d%s" %(MH,postfix)
        variables = []
        ratio        = ROOT.RooRealVar("ratio_%d%s"%(MH,postfix),"ratio_%d%s"%(MH,postfix),0.5)   
        if postfix.find("H")==-1:
            names = ["mean","sigma","alpha","n","alpha2","n2"]
        else: names = ["mean","sigma","alpha","n","alpha2","n2","meanH","sigmaH","alphaH","nH","alpha2H","n2H"]
        if isMVV==True:
          print "mVV shape"
          names = ["MEAN","SIGMA","ALPHA1","N1","ALPHA2","N2"]
        for n in names:
          if n.find("H")==-1 or n.find("ALPHA")!=-1:
            if isinstance(j[n],list) == False: 
              variables.append(ROOT.RooRealVar(n+"_"+str(MH)+postfix,n+"_"+str(MH)+postfix,eval(j[n])))
            else:
              gtmp = ROOT.TGraph()
                       
              for index in range(0,len(j[n])):
                gtmp.SetPoint(index+1,j[n][index][0],j[n][index][1])
              
              tmp = ROOT.TSpline3("tmp_spline",gtmp)
              variables.append(ROOT.RooRealVar(n+"_"+str(MH)+postfix,n+"_"+str(MH)+postfix,tmp.Eval(MH)))
             
          else:
            if isinstance(j[n],list) == False:
              variables.append(ROOT.RooRealVar(n+"_"+str(MH)+postfix,n+"_"+str(MH)+postfix,eval(jH[n])))
            else:
              gtmp = ROOT.TGraph()
                       
              for index in range(0,len(jH[n])):
                gtmp.SetPoint(index+1,jH[n][index][0],jH[n][index][1])
              
              tmp = ROOT.TSpline3("tmp_spline",gtmp)
              variables.append(ROOT.RooRealVar(n+"_"+str(MH)+postfix,n+"_"+str(MH)+postfix,tmp.Eval(MH)))
            variables[-1].setConstant(ROOT.kTRUE)
        if jH==None:
          function = ROOT.RooDoubleCB(pdfName, pdfName, var, variables[0], variables[1], variables[2], variables[3], variables[4], variables[5])  
          getattr(w,'import')(function,ROOT.RooFit.Rename(pdfName))
        else:  
            function1 = ROOT.RooDoubleCB(pdfName+"1", pdfName+"1", var, variables[0], variables[1],variables[2],variables[3],variables[4], variables[5]) 
            function2 = ROOT.RooDoubleCB(pdfName+"2", pdfName+"2", var, variables[6], variables[7], variables[8], variables[9],variables[10], variables[11])
            function =  ROOT.RooAddPdf(pdfName,pdfName,function1,function2,ratio)
            getattr(w,'import')(function,ROOT.RooFit.Rename(pdfName))
            
		
parser = optparse.OptionParser()
parser.add_option("-f","--file",dest="file",default='JJ_BulkGWW_2016_MVV.json',help="input file (JJ_{sig}_2016_MVV.json,JJ_{sig}_2016_MJrandom_VV_HPLP.json)")
parser.add_option("-v","--var",dest="var",help="mVV or mJ",default='mVV')
parser.add_option("-y","--year",dest="year",help="2016 or 2017 or 2018",default='Run2')
parser.add_option("-c","--category",dest="category",help="VV_HPHP or VV_HPLP or VH_HPHP etc",default='VV_HPLP')
parser.add_option("-o","--outdir",dest="outdir",help="output directory",default='../plots/')
parser.add_option("-i","--indir",dest="indir",help="input directory",default='results_Run2/')
parser.add_option("-n","--name",dest="name",help="you may specify an additional label for the output file",default='test')
parser.add_option("-l","--leg",dest="leg",help="mVV or mJ",default='l1')
parser.add_option("-p","--prelim",dest="prelim",help="with label preliminary or not",default=0)

(options,args) = parser.parse_args()

path = options.outdir

purity  = options.category

inFileName = options.file
massPoints = [1200,1400,1600,1800,2000,2500,3000,3500,4000,4500,5000,5500,6000]
postfix = "Jet 1 "
if options.leg == "l2" !=-1: postfix = "Jet 2 "
varName = {'mVV':'Dijet invariant mass [GeV]','mJ':'mass_{%s} [GeV]'%postfix}
varBins = {'mVV':'[40,1000,6500]','mJ':'[80,55,215]'}
#w=ROOT.RooWorkspace("w","w")
#w.factory(options.var+varBins[options.var])
#w.var(options.var).SetTitle(varName[options.var])
colors= []
colors.append(["#000080","#0000CD","#0000FF","#3D59AB","#4169E1","#4876FF","#6495ED","#1E90FF","#63B8FF","#87CEFA","#C6E2FF"]*4)   
colors.append(["#006400","#308014","#228B22","#32CD32","#00CD00","#00EE00","#00FF00","#7CCD7C","#7CFC00","#ADFF2F","#C0FF3E"]*4)   
colors.append(["#CD8500","#CD950C","#EE9A00","#EEAD0E","#FFA500","#FFB90F","#FFC125","#EEC900","#FFD700","#FFEC8B","#FFF68F"]*4) 
colors.append(["#8B2500","#CD3700","#EE4000","#FF4500","#CD4F39","#EE5C42","#EE6A50","#FF7256","#FA8072","#FFA07A","#EEB4B4"]*4)
colors.append(["#EE82EE","#FF00FF","#D02090","#C71585","#B03060 ","#DB7093","#FFB6C1","#FFC0CB"]*4)
colors.append(["#D2B48C","#FFA54F","#EE9A49","#CD853F"]*4)
colors.append(["#241b1b","#3c2929","#450000","#630000","#780000"]*4) #darkest days Color Palette from https://www.color-hex.com/color-palette/105294
colors.append(["#bec1f6","#cfd3ff","#e3e6ff","#f0f3ff"]*4) #periwinkle snowflakes Color Palette from https://www.color-hex.com/color-palette/105538
#colors.append(["#000080","#0000CD","#0000FF","#3D59AB","#4169E1","#4876FF","#6495ED","#1E90FF","#63B8FF","#87CEFA","#C6E2FF"]*3)   



def doSingle():
    w=ROOT.RooWorkspace("w","w")
    w.factory(options.var+varBins[options.var])
    w.var(options.var).SetTitle(varName[options.var])
    with open(inFileName) as jsonFile:
      j = json.load(jsonFile)
    
      c1 = getCanvasPaper("c1")[0]
      c1.Draw()
      leg = ROOT.TLegend(0.8, 0.2, 0.95, 0.8)
      frame = w.var(options.var).frame()   
      
      for i, MH in enumerate(massPoints):  # mind that MH is evaluated below
        if options.var == 'mVV': getMVVPdf(w,j,MH)
        else: 
            if inFileName.find("H")==-1:
                getMJPdf(w,j,MH)
            if inFileName.find("Vjet")!=-1:
                with open(inFileName.replace("Vjet","Hjet")) as jsonFileH:
                    jH = json.load(jsonFileH)
                getMJPdf(j,MH,"H",jH)
            if inFileName.find("Hjet")!=-1:
                with open(inFileName.replace("Hjet","Vjet")) as jsonFileV:
                    jV = json.load(jsonFileV)
                getMJPdf(w,jV,MH,"H",j)
                
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

def doAll(category,jsons,legs):
    w=ROOT.RooWorkspace("w","w")
    w.factory(options.var+varBins[options.var])
    w.var(options.var).SetTitle(varName[options.var])
    #legs = ["G_{bulk} #rightarrow ZZ","W' #rightarrow WZ","G_{bulk} #rightarrow WW","Z'#rightarrow WW","Z' #rightarrow ZH"]
    c1,pt = getCanvasPaper("c1")

    c1.Draw()
    if options.var == 'mVV':
        c1.Divide(1,len(jsons),0.0,0.0)
    leg = []
    frame = []  
    #frame.SetTitle("")
    for ii,f in enumerate(jsons):
        if options.var == 'mVV':
            c1.cd(ii)
            if ii==len(jsons)-1:
                leg.append(getLegend(0.15))
            else:
                leg.append(getLegend())
            frame.append( w.var(options.var).frame() ) 
        else:
            if ii ==0:
                leg.append(getLegend(0.05,0.46))
                frame.append( w.var(options.var).frame() ) 
        if options.var=='mJ':
            frame[-1].SetAxisRange(55,150)
        frame[-1].SetTitle("")
        name = f.split("_")[1]
        if "VBF" in f :  name = name+ f.split("_")[2]
        if f.find("H")!=-1 :
          name = f.split("_")[2]
          if "VBF" in f :  name = name+ f.split("_")[3]
        with open(options.indir+f) as jsonFile:
          j = json.load(jsonFile)
          for i, MH in enumerate(massPoints):  # mind that MH is evaluated below
            if options.var == 'mVV': getMVVPdf(w,j,MH,name)
            else: 
                if f.find("ZH")==-1 and f.find("WH")==-1:
                    print "no H boson in sample "
                    getMJPdf(w,j,MH,name)
                elif f.find("Vjet")!=-1:
                    with open(options.indir+f.replace("Vjet","Hjet")) as jsonFileH:
                        jH = json.load(jsonFileH)
                    getMJPdf(j,MH,name,jH)
                elif f.find("Hjet")!=-1:
                    with open(options.indir+f.replace("Hjet","Vjet")) as jsonFileV:
                        jV = json.load(jsonFileV)
                    getMJPdf(w,jV,MH,name,j)
            w.pdf('signal_%d%s'%(MH,name)).plotOn(frame[-1], ROOT.RooFit.LineColor(ROOT.TColor.GetColor(colors[ii][i])),ROOT.RooFit.Name(str(MH)+name))#,ROOT.RooFit.Range(MH*0.8,1.2*MH))#ROOT.RooFit.Normalization(1, ROOT.RooAbsReal.RelativeExpected),
      
   
    if options.var == 'mVV': 
        for ii,f in enumerate(jsons):
            print len(jsons)
            print ii
            print "json "+str(jsons[len(jsons)-ii-1])
            name = jsons[len(jsons)-ii-1].split("_")[1]
            if "VBF" in jsons[len(jsons)-ii-1]: name=jsons[len(jsons)-ii-1].split("_")[1]+jsons[len(jsons)-ii-1].split("_")[2]
            if jsons[len(jsons)-len(jsons)-ii-1].find("H")!=-1 :
              name = jsons[len(jsons)-len(jsons)-ii-1].split("_")[2]
              if "VBF" in jsons[len(jsons)-ii-1]: name=jsons[len(jsons)-ii-1].split("_")[2]+jsons[len(jsons)-ii-1].split("_")[3]
            leg[len(jsons)-ii-1].AddEntry(frame[len(jsons)-ii-1].findObject(str(2000)+name), legs[len(jsons)-ii-1], "L")
    else:
        for ii,f in enumerate(jsons):
            name = jsons[len(jsons)-ii-1].split("_")[1]
            print name
            print jsons[len(jsons)-ii-1].split("_")[1]+jsons[len(jsons)-ii-1].split("_")[2]
            if "VBF" in jsons[len(jsons)-ii-1]:
              name= jsons[len(jsons)-ii-1].split("_")[1]+jsons[len(jsons)-ii-1].split("_")[2]
            if "H" in jsons[len(jsons)-ii-1]:
              name = jsons[len(jsons)-ii-1].split("_")[2]
              if "VBF" in jsons[len(jsons)-ii-1]: name= jsons[len(jsons)-ii-1].split("_")[2]+jsons[len(jsons)-ii-1].split("_")[3]
            print name
            print jsons[len(jsons)-ii-1]
            leg[-1].AddEntry(frame[0].findObject(str(2000)+name),legs[len(jsons)-ii-1],"L")

    for i in range(1,len(frame)+1):
        c1.cd(i)
        c1.cd(i).SetTickx()
        c1.cd(i).SetTicky()
      
      
        frame[i-1].GetYaxis().SetTitle("a. u.")
        frame[i-1].GetYaxis().SetTitleOffset(1.18)
        frame[i-1].GetXaxis().SetTitleOffset(0.9)
        frame[i-1].GetYaxis().SetNdivisions(6,5,1)
        frame[i-1].GetXaxis().SetNdivisions(6,5,1)
        frame[i-1].SetMaximum(0.17)
        if options.var == 'mVV':
            frame[i-1].SetMaximum(0.45)
            frame[i-1].GetYaxis().SetNdivisions(0,5,0,False)
            frame[i-1].GetYaxis().SetTitleOffset(0.25)
            frame[i-1].GetXaxis().SetTitleSize(0.20)
            frame[i-1].GetYaxis().SetTitleSize(0.20)
            frame[i-1].GetYaxis().SetLabelSize(0.20)
            frame[i-1].GetXaxis().SetLabelSize(0.20)
            #frame[i-1].Draw()
            frame[i-1].GetXaxis().SetTickLength(0.1)
            frame[-1].GetYaxis().SetLabelSize(0.14) 
            frame[-1].GetXaxis().SetLabelSize(0.14)
            frame[-1].GetXaxis().SetTitleSize(0.14)
            frame[-1].GetYaxis().SetTitleSize(0.14)
            frame[-1].GetYaxis().SetTitleOffset(0.35)
            frame[-1].GetXaxis().SetTitleOffset(1.05)
            frame[-1].GetXaxis().SetLabelOffset(0.05)
            frame[-1].GetXaxis().SetTickLength(0.08)
        else:    
            
            frame[i-1].GetXaxis().SetTitleSize(0.06)
            frame[i-1].GetYaxis().SetTitleSize(0.06)
            frame[i-1].GetYaxis().SetLabelSize(0.05)
            frame[i-1].GetXaxis().SetLabelSize(0.05)
                
        frame[i-1].Draw()
        leg[i-1].Draw("same")
    
    
    pt2 = ROOT.TPaveText(0.16,0.62,0.63,0.76,"NDC")
    pt2.SetTextFont(42)
    pt2.SetTextSize(0.04)
    pt2.SetTextAlign(12)
    pt2.SetFillColor(0)
    pt2.SetBorderSize(0)
    pt2.SetFillStyle(0)
    vbfsig=""
    if "VBF" in jsons[0]: vbfsig="VBFsig"
    outname=path+"signalShapes"+vbfsig+"_%s_%s_%s_All_%s_prelim" %(options.var,category,options.year,options.name)

    if options.var == 'mJ': pt2.AddText(category)
    pt2.Draw()
#    if options.var =="mVV": category = "Vall"
    if options.prelim=="1":
        cmslabel_sim_prelim(c1,'sim',11)
        c1.Update()
        c1.SaveAs(outname+".png")
        c1.SaveAs(outname+".pdf")
        c1.SaveAs(outname+".C")
        c1.SaveAs(outname+".root")
    elif options.prelim=="2":
      outname=path+"signalShapes"+vbfsig+"_%s_%s_%s_All_%s_thesis" %(options.var,category,options.year,options.name)
      cmslabel_thesis(c1,'sim',11)
      c1.Update()
      c1.SaveAs(outname+".png")
      c1.SaveAs(outname+".pdf")
      c1.SaveAs(outname+".C")
      c1.SaveAs(outname+".root")
    else:
        cmslabel_sim(c1,'sim',11)
        c1.Update()
        outname=path+"signalShapes"+vbfsig+"_%s_%s_%s_All_%s" %(options.var,category,options.year,options.name)
        c1.SaveAs(outname+".png")
        c1.SaveAs(outname+".pdf")
        c1.SaveAs(outname+".C")
        c1.SaveAs(outname+".root")
    
      
if __name__ == '__main__':

    legs = ["G_{bulk} #rightarrow ZZ","W' #rightarrow WZ","G_{bulk} #rightarrow WW","Z'#rightarrow WW","Z' #rightarrow ZH","W' #rightarrow WH","R #rightarrow WW","R #rightarrow ZZ"]
    signals = ["BulkGZZ","WprimeWZ","BulkGWW","ZprimeWW","ZprimeZHinc","WprimeWHinc","RadionWW","RadionZZ"]
    categories = ["NP"]

    for category in categories:
      jsons=[]
      for s in signals:
        print "################################     signal      "+s+"       #######################"
        if options.var =="mJ":
          if s.find("H")==-1 :
            jsons.append("JJ_"+s+"_Run2_MJrandom_"+category+".json")
          else : jsons.append("JJ_Hjet_"+s+"_Run2_MJrandom_"+category+".json")
        if options.var =="mVV":
          jsons.append("JJ_"+s+"_Run2_MVV.json")

      doAll(category,jsons,legs)


    vbfsignals=[]
    vbftitles= []
    for sig,t in zip(signals,legs):
      vbfsignals.append("VBF_"+sig)
      vbftitles.append("VBF "+t)


    for category in categories:
      jsons=[]
      for s in vbfsignals:
        print "################################     signal      "+s+"       #######################"
        if options.var =="mJ":
          if s.find("H")==-1 :
            jsons.append("JJ_"+s+"_Run2_MJrandom_"+category+".json")
          else : jsons.append("JJ_Hjet_"+s+"_Run2_MJrandom_"+category+".json")
        if options.var =="mVV":
          jsons.append("JJ_"+s+"_Run2_MVV.json")

      doAll(category,jsons,vbftitles)
