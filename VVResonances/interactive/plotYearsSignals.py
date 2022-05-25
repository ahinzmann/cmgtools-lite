#!/bin/env python
import ROOT
import json
import math
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
from time import sleep
import optparse, sys
from collections import defaultdict
from  CMGTools.VVResonances.plotting.CMS_lumi import *
from array import array
   
# ROOT.gROOT.SetBatch(True)

path = "../plots/"

def beautify(h1,color,linestyle=1,markerstyle=8):
    h1.SetLineColor(color)
    h1.SetMarkerColor(color)
    # h1.SetFillColor(color)                                                                                                                                                                                                                  
    h1.SetLineWidth(3)
    h1.SetLineStyle(linestyle)
    h1.SetMarkerStyle(markerstyle)
    h1.SetMarkerSize(1.5)


def getLegend(x1=0.2,y1=0.71,x2=0.45,y2=0.88):
#def getLegend(x1=0.70010112,y1=0.693362,x2=0.90202143,y2=0.829833):
  legend = ROOT.TLegend(x1,y1,x2,y2)
  legend.SetTextSize(0.035)
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
parser = optparse.OptionParser()

parser.add_option("-v","--var",dest="var",help="mVV or mJ",default='mVV')
parser.add_option("-l","--leg",dest="leg",help="l1 or l2",default='l1')
parser.add_option("-p","--period",dest="period",help="2016 or 2017 or 2018",default='2016')
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
massPoints = [1200,1400,1600,1800,2000,2500,3000,3500,4000,4500,5000,5500,6000,6500,7000,7500,8000]
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

colorsyears= {'2016': "#4292c6",'2017': "#41ab5d",'2018':"#ef3b2c", 'Run2': "#17202A"}
markeryears={'2016':8, '2017':25,'2018':22,'Run2':32}

def doYields(signal,legend,years,colorindex):

    purities=["VV_HPHP","VV_HPLP","VH_HPHP","VH_HPLP","VH_LPHP","VBF_VV_HPHP","VBF_VH_HPHP","VBF_VV_HPLP","VBF_VH_HPLP","VBF_VH_LPHP"]
    gr = {}
    for purity in purities:
      print " working on ",purity
      c1,leg,pt = getCanvasPaper("c1")
      c1.Draw()
      data = [] 
      gr[purity]={}
      for year in years : 
        print " getting year ",year
        r_file = ROOT.TFile(options.folder+"/"+"JJ_"+signal+"_"+year+"_"+purity+"_yield.root","READ")
        if gr[purity]==None:
           gr[purity]= {year : r_file.Get("yield")}
        else: gr[purity].update({year : r_file.Get("yield")})

        print " get number of points ", gr[purity][year].GetN()
        for i in range(gr[purity][year].GetN()) :
          print gr[purity][year].GetY()[i]
          gr[purity][year].GetY()[i] *= 1000
          #tot[year].update({purity: gr[purity][year].GetY()[i]})
          #Mass[year].update({gr[purity][year].GetX()[i]})
          print gr[purity][year].GetY()[i]
        

        gr[purity][year].SetLineColor(ROOT.TColor.GetColor(colorsyears[year]))
        gr[purity][year].SetLineStyle(2)
        gr[purity][year].SetLineWidth(2)
        gr[purity][year].SetMarkerColor(ROOT.TColor.GetColor(colorsyears[year]))
        gr[purity][year].SetMarkerStyle(markeryears[year])
        
        ff = gr[purity][year].GetFunction("func")
        gr[purity][year].Fit(ff)
        ff.SetLineColor(0)
        ff.SetLineWidth(0)

        gr[purity][year].GetYaxis().SetTitle("a.u.")
        gr[purity][year].GetXaxis().SetTitle("m_{X} [GeV]")
        gr[purity][year].GetYaxis().SetTitleOffset(1.3)
        gr[purity][year].GetYaxis().SetNdivisions(4,5,0)
        gr[purity][year].GetXaxis().SetNdivisions(3,5,0)
        gr[purity][year].SetMinimum(0.)
        gr[purity][year].SetMaximum(0.3)
        gr[purity][year].GetXaxis().SetLimits(1000.,8500.)
        gr[purity][year].GetXaxis().SetTitleSize(0.055)
        gr[purity][year].GetYaxis().SetTitleSize(0.055)
        gr[purity][year].GetYaxis().SetLabelSize(0.04)
        gr[purity][year].GetXaxis().SetLabelSize(0.04)
        data.append(gr[purity][year])        
        leg.AddEntry(gr[purity][year],year, "LP")

      data[0].Draw("AC")
      for i,(g) in enumerate(data):
        #g.GetXaxis().SetRangeUser(1000.,8500.)
        g.Draw("PLsame")

        #gr[purity][year].Draw("APL")
        #gr[purity][year].Draw("PL")
          
        
      leg.Draw("same")

    
      pt2 = ROOT.TPaveText(0.7,0.87,0.8,0.9,"NDC")
      pt2.SetTextFont(42)
      pt2.SetTextSize(0.04)
      pt2.SetTextAlign(12)
      pt2.SetFillColor(0)
      pt2.SetBorderSize(0)
      pt2.SetFillStyle(0)
      pt2.AddText(legend)
      pt2.Draw()


      pt3 = ROOT.TPaveText(0.7,0.75,0.8,0.87,"NDC")
      pt3.SetTextFont(42)
      pt3.SetTextSize(0.04)
      pt3.SetTextAlign(12)
      pt3.SetFillColor(0)
      pt3.SetBorderSize(0)
      pt3.SetFillStyle(0)
      pt3.AddText(purity)
      pt3.Draw()

      
      name = path+"signalYelds_%s_%s_%s"  %(purity,options.name,signal)
      c1.SaveAs(name+".png")
      c1.SaveAs(name+".pdf" )
      c1.SaveAs(name+".C"   )
      c1.SaveAs(name+".root")



    print " gr ",gr

    flipped = defaultdict(dict)
    for key, val in gr.items():
      for subkey, subval in val.items():
        flipped[subkey][key] = subval

    print "flipped ",flipped


    tot = {}
    Mass = {}
    #tot,Mass = array( 'd' ), array( 'd' )

    ct,legt,ptt = getCanvasPaper("ct")
    ct.Draw()
    datatot = []
    for year in years:
      tot[year],Mass[year] = array( 'd' ), array( 'd' )

      for i in range(flipped[year]['VV_HPHP'].GetN()) :
        tot[year].append( flipped[year]['VV_HPHP'].GetY()[i]+flipped[year]['VV_HPLP'].GetY()[i]+flipped[year]['VH_HPHP'].GetY()[i]+flipped[year]['VH_LPHP'].GetY()[i]+flipped[year]['VH_HPLP'].GetY()[i])
        Mass[year].append(flipped[year]['VV_HPHP'].GetX()[i] )

          #tot.append( VV_HPHP[i]+VV_HPLP[i]+VH_HPHP[i]+VH_HPLP[i]+VH_LPHP[i])
          #tot.append( VV_HPHP[i]+VV_HPLP[i]+VH_HPHP[i]+VH_LPHP[i])
      print tot[year]

      gr_tot = ROOT.TGraph(gr['VV_HPHP'][year].GetN(),Mass[year],tot[year])
      gr_tot.SetLineColor(ROOT.TColor.GetColor(colorsyears[year]))
      gr_tot.SetLineStyle(1)
      gr_tot.SetLineWidth(2)
      gr_tot.SetMarkerColor(ROOT.TColor.GetColor(colorsyears[year]))
      gr_tot.SetMarkerStyle(markeryears[year])
      gr_tot.SetMinimum(0.)
      gr_tot.SetMaximum(0.3)
      gr_tot.GetXaxis().SetLimits(1000.,8500.)
      gr_tot.SetTitle("") 
      datatot.append(gr_tot)

      
      legt.AddEntry(gr_tot,year, "LP")
    datatot[0].Draw("AC")
    for i,(g) in enumerate(datatot):
      g.Draw("PLsame")


    legt.Draw("same")

    
    pt3 = ROOT.TPaveText(0.7,0.8,0.8,0.9,"NDC")
    pt3.SetTextFont(42)
    pt3.SetTextSize(0.05)
    pt3.SetTextAlign(12)
    pt3.SetFillColor(0)
    pt3.SetBorderSize(0)
    pt3.SetFillStyle(0)
    pt3.AddText(legend)
    pt3.Draw()


    name = path+"signalYelds_compareTotalVVVH_%s_%s"  %(options.name,signal)
    ct.SaveAs(name+".png")
    ct.SaveAs(name+".pdf" )
    ct.SaveAs(name+".C"   )
    ct.SaveAs(name+".root")



def doMVV(signal,titles,years):

    vars = ["MEAN","SIGMA","ALPHA1","ALPHA2","N1","N2"]
    ROOT.gStyle.SetOptFit(0)

    files=[]
    for year in years :
      print " getting year ",year
      files.append(ROOT.TFile("results_"+year+"/debug_JJ_"+signal+"_"+year+"_MVV.json.root","READ"))

    for var in vars:
      fits=[]
      datas=[]

      c,l,pt = getCanvasPaper("c")
      l2 = getLegend(0.7788945,0.1783217,0.9974874,0.2482517)
      ROOT.gStyle.SetOptStat(0)
      ROOT.gStyle.SetOptTitle(0)

      for i,f in enumerate(files):
        g = f.Get(var)
        fun = f.Get(var+"_func")
        beautify(fun ,rt.TColor.GetColor(colorsyears[years[i]]),2,markeryears[years[i]])
        beautify(g ,rt.TColor.GetColor(colorsyears[years[i]]),2,markeryears[years[i]])
        #fun.SetLineColor(0)
        #fun.SetLineWidth(0)

        datas.append(g)
        fits.append(fun)
        l.AddEntry(fun,years[i],"LP")
        
        datas[0].GetXaxis().SetTitle("M_{X} [GeV]")
        datas[0].GetYaxis().SetTitle(var+" [GeV]")
        datas[0].GetYaxis().SetNdivisions(4,5,0)
        datas[0].GetXaxis().SetNdivisions(9,2,0)
        datas[0].GetYaxis().SetTitleOffset(0.97)
        datas[0].GetYaxis().SetMaxDigits(2)
        datas[0].GetXaxis().SetTitleOffset(0.94)
        datas[0].GetXaxis().SetLimits(1126, 8500.)
        datas[0].GetYaxis().SetRangeUser(-2., 3.)
        if var.find("ALPHA1")!=-1: datas[0].GetYaxis().SetRangeUser(0., 4.)
        if var.find("ALPHA2")!=-1: datas[0].GetYaxis().SetRangeUser(0., 20.)
        if var.find("SIGMA")!=-1:  datas[0].GetYaxis().SetRangeUser(0., 400.)
        if var.find("MEAN")!=-1:   datas[0].GetYaxis().SetRangeUser(700., 8000)
        if var.find("N1")!=-1:     datas[0].GetYaxis().SetRangeUser(0., 150.)
        if var.find("N2")!=-1:     datas[0].GetYaxis().SetRangeUser(-10., 150.)
        datas[0].Draw("CA")
        print datas[0].Eval(1200.)
        c.Update()
      for i,gg in enumerate(fits):
        gg.Draw("Lsame")
        datas[i].Draw("Psame")
      l.SetNColumns(len(years)/2)
      l.Draw("same")

      pt2 = ROOT.TPaveText(0.7,0.87,0.8,0.9,"NDC")
      pt2.SetTextFont(42)
      pt2.SetTextSize(0.04)
      pt2.SetTextAlign(12)
      pt2.SetFillColor(0)
      pt2.SetBorderSize(0)
      pt2.SetFillStyle(0)
      pt2.AddText(titles)
      pt2.Draw()



      #cmslabel_sim_prelim(c,'sim',11)
      c.Update()
      name = path+"Signal_mVV_allyears_"+var+"_"+signal+"_"+options.name
      c.SaveAs(name+".png")
      c.SaveAs(name+".pdf")
      c.SaveAs(name+".C")
      


def doJetMass(leg,signal,titles,years):
    print signal
    ROOT.gStyle.SetOptFit(0)

    files=[]
    filesHjet=[]

    for i,year in enumerate(years):
        files.append(ROOT.TFile("results_"+year+"/debug_JJ_"+signal+"_"+year+"_MJ"+leg+"_NP.json.root","READ"))
        filesHjet.append(None)
        if files[-1].IsZombie()==1:
            files[-1] =(ROOT.TFile("results_"+year+"/debug_JJ_Vjet_"+signal+"_"+year+"_MJ"+leg+"_NP.json.root","READ"))
            filesHjet[-1] =(ROOT.TFile("results_"+year+"/debug_JJ_Hjet_"+signal+"_"+year+"_MJ"+leg+"_NP.json.root","READ"))
            

    vars = ["mean","sigma","alpha","n","alpha2","n2"]
    for var in vars:

       fits =[]
       fitsHjet=[]
       datas=[]
       datasHjet=[]

       c,l,pt = getCanvasPaper("c")

       ROOT.gStyle.SetOptStat(0)
       ROOT.gStyle.SetOptTitle(0)
       #title = "Jet mass width "
       #if var == "mean": title="Jet mass mean"
       for i,(f,fH) in enumerate(zip(files,filesHjet)):
           print fH
           print f

           if fH ==None:
                gH = f.Get(var)
                funH = f.Get(var+"_func")
           else:
                print fH.GetName()
                gH = fH.Get(var+"H")
                funH = fH.Get(var+"H_func")
           g = f.Get(var)
           fun = f.Get(var+"_func")

           beautify(fun  ,rt.TColor.GetColor(colorsyears[years[i]]),2,markeryears[years[i]])
           beautify(funH ,rt.TColor.GetColor(colorsyears[years[i]]),1,markeryears[years[i]])
           beautify(g ,rt.TColor.GetColor(colorsyears[years[i]]),2,markeryears[years[i]])
           beautify(gH ,rt.TColor.GetColor(colorsyears[years[i]]),1,markeryears[years[i]])
           datas.append(g)
           datasHjet.append(gH)
           fits.append(fun)
           fitsHjet.append(funH)
           l.AddEntry(funH,years[i],"LP")
       print datasHjet

       datas[0].GetXaxis().SetTitle("m_{X} [GeV]")
       datas[0].GetYaxis().SetTitle(var)
       datas[0].GetYaxis().SetNdivisions(4,5,0)
       datas[0].GetXaxis().SetNdivisions(5,5,0)
       datas[0].GetYaxis().SetTitleOffset(1.05)
       datas[0].GetXaxis().SetTitleOffset(0.9)
       datas[0].GetXaxis().SetRangeUser(1126, 5500.)
       datas[0].GetXaxis().SetLabelSize(0.04)
       datas[0].GetXaxis().SetTitleSize(0.06)
       datas[0].GetYaxis().SetLabelSize(0.04)
       datas[0].GetYaxis().SetTitleSize(0.06)
       if var == "mean": datas[0].GetYaxis().SetRangeUser(75,150);
       if var == "sigma": datas[0].GetYaxis().SetRangeUser(5,20.);
       if var == "alpha": datas[0].GetYaxis().SetRangeUser(0,5); datas[0].GetYaxis().SetTitle("alpha")
       if var == "n": datas[0].GetYaxis().SetRangeUser(0,250); datas[0].GetYaxis().SetTitle("n")
       if var == "alpha2": datas[0].GetYaxis().SetRangeUser(0,5); datas[0].GetYaxis().SetTitle("alpha2")
       if var == "n2": datas[0].GetYaxis().SetRangeUser(0,20); datas[0].GetYaxis().SetTitle("n2")
       datas[0].Draw("AP")
       for i,(g,gH) in enumerate(zip(datas,datasHjet)):
           g.Draw("Psame")
           gH.Draw("Psame")
           fits[i].Draw("Csame")
           fitsHjet[i].Draw("Csame")
       datas[0].GetXaxis().SetLimits(1126, 8500.)
       l.Draw("same")
       pt2 = ROOT.TPaveText(0.7,0.87,0.8,0.9,"NDC")
       pt2.SetTextFont(42)
       pt2.SetTextSize(0.04)
       pt2.SetTextAlign(12)
       pt2.SetFillColor(0)
       pt2.SetBorderSize(0)
       pt2.SetFillStyle(0)
       pt2.AddText(titles)
       pt2.Draw()




       #cmslabel_sim_prelim(c,'sim',11)

       c.Update()
       name = path+"Signal_mjet_Allyears_"+signal+"_"+var+"_"+options.name
       c.SaveAs(name+".png")
       c.SaveAs(name+".pdf")
       c.SaveAs(name+".C")

                
if __name__ == '__main__':

    signals = ["BulkGZZ","WprimeWZ","BulkGWW","ZprimeWW","ZprimeZH","WprimeWH","ZprimeZHinc","WprimeWHinc"]
    legs = ["G_{bulk} #rightarrow ZZ","W' #rightarrow WZ","G_{bulk} #rightarrow WW","Z'#rightarrow WW","Z'#rightarrow ZHbb","W'#rightarrow WHbb","Z'#rightarrow ZHinc","W'#rightarrow WHinc"]
    years = ["2016","2017","2018","Run2"]
    for i in range(len(signals)):
      print i
      print signals[i]
      print legs[i]
      doYields(signals[i],legs[i],years,i)
      doMVV(signals[i],legs[i],years)
      doJetMass("random",signals[i],legs[i],years)
  
