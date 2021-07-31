from ROOT import TFile, TCanvas, TPaveText, TLegend, gDirectory, TH1F,gROOT,gStyle, TLatex,TF1,TGraph
import sys,copy
import tdrstyle
tdrstyle.setTDRStyle()
from  CMGTools.VVResonances.plotting.CMS_lumi import *
from collections import defaultdict
from array import array
from time import sleep
gROOT.SetBatch(True)
# infile = sys.argv[1]
# f = TFile(infile,"READ")

path = sys.argv[1]
cols = [46,30]
colors = ["#4292c6","#41ab5d","#ef3b2c","#ffd300","#D02090","#fdae61","#abd9e9","#492a60","#780000"]
#mstyle = [8,24,22,26,32]
#linestyle=[1,2,1,2,3]
markerstyle = [21,8,23,4,25,32,22,26]
linestyle = [1,2,3,4,5,6,7,8,9,1,2]
mstyle = [8,4]

def beautify(h1,color,linestyle=1,markerstyle=8):
    h1.SetLineColor(color)
    h1.SetMarkerColor(color)
    # h1.SetFillColor(color)
    h1.SetLineWidth(3)
    h1.SetLineStyle(linestyle)
    h1.SetMarkerStyle(markerstyle)
    
def getLegend(x1=0.5809045,y1=0.6363636,x2=0.9522613,y2=0.9020979):
  legend = TLegend(x1,y1,x2,y2)
  legend.SetTextSize(0.04)
  legend.SetLineColor(0)
  legend.SetShadowColor(0)
  legend.SetLineStyle(1)
  legend.SetLineWidth(0)
  legend.SetFillColor(0)
  legend.SetFillStyle(0)
  legend.SetMargin(0.35)
  legend.SetTextFont(42)
  return legend

def getPavetext():
  addInfo = TPaveText(0.3010112,0.2066292,0.4202143,0.3523546,"NDC")
  addInfo.SetFillColor(0)
  addInfo.SetLineColor(0)
  addInfo.SetFillStyle(0)
  addInfo.SetBorderSize(0)
  addInfo.SetTextFont(42)
  addInfo.SetTextSize(0.040)
  addInfo.SetTextAlign(12)
  return addInfo
    
    
def getCanvas(w=800,h=600):
   
 H_ref = 600 
 W_ref = 600 
 W = W_ref
 H  = H_ref

 iPeriod = 0

 # references for T, B, L, R
 T = 0.08*H_ref
 B = 0.12*H_ref 
 L = 0.15*W_ref
 R = 0.04*W_ref
 cname = "c"
 canvas = TCanvas(cname,cname,50,50,W,H)
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
 
 return canvas
    

def doSignalEff(directory,signals,titles,categories,ymaxrange=[0.3,0.5,0.05,0.05,0.05,0.05,0.5,0.5,0.05,0.05,0.05,0.05]):
  ky=-1
  gr = {}
  for category in categories:
    ky+=1
    gStyle.SetOptFit(0)
    fitsHP=[]
    fitstmpHP=[]
    datasHP=[]
    signalcolor={}
    signalline={}
    signalmarker={}
    gr[category]={}
    c = getCanvas()
    l = getLegend()#0.7788945,0.723362,0.9974874,0.879833)
    l2 = getLegend(0.17,0.5783217,0.4974874,0.7482517)
    gStyle.SetOptStat(0)
    gStyle.SetOptTitle(0)
    
    filesHP=[]
  
    for i,s in enumerate(signals):
        filesHP.append(TFile(directory+"JJ_"+s+"_Run2_"+category+"_yield.root","READ"))
        print 'open file '+directory+"JJ_"+s+"_Run2_"+category+"_yield.root"
    
    for i,fHP in enumerate(filesHP):
        gHPHP = fHP.Get("yield")
        print gHPHP
        if gr[category]==None:
           gr[category]= {signals[i] : gHPHP}
        else: gr[category].update({signals[i] : gHPHP})

        #### rescale graphs to remove cross section from yield ####
        for k in range(0,gHPHP.GetN()): gHPHP.GetY()[k] *= 1000.
        
        if gHPHP.GetFunction("func")!=None:
            print "polinomial function"
            gHPHP.GetFunction("func").SetBit(rt.TF1.kNotDraw)
            ftmpHPHP = gHPHP.GetFunction("func")
            fHPHP = TF1("funcHP"+str(i),str(ftmpHPHP.GetExpFormula()).replace("func","")+"*1000.",ftmpHPHP.GetXmin(),ftmpHPHP.GetXmax())
            for o in range(0,ftmpHPHP.GetNpar()): 
                fHPHP.SetParameter(o,ftmpHPHP.GetParameter(o))
        else: fHPHP = gHPHP
        signalcolor[signals[i]] = rt.TColor.GetColor(colors[i])
        signalline[signals[i]] = linestyle[i]
        signalmarker[signals[i]] = markerstyle[i]
        #beautify(fHPHP ,rt.TColor.GetColor(colors[i]),linestyle[i],markerstyle[i])
        #beautify(gHPHP ,rt.TColor.GetColor(colors[i]),linestyle[i],markerstyle[i])
        beautify(fHPHP ,rt.TColor.GetColor(colors[i]),1,markerstyle[i])
        beautify(gHPHP ,rt.TColor.GetColor(colors[i]),1,markerstyle[i])
        datasHP.append(gHPHP)
        fitsHP.append(fHPHP)
        l.AddEntry(fHPHP,titles[i],"LP")
    fitsHP[0].Draw("C")
    l2.AddEntry(fitsHP[0],category,"")
    fitsHP[0].GetXaxis().SetTitle("m_{X} [GeV]")
    fitsHP[0].GetYaxis().SetTitle("Signal efficiency")
    fitsHP[0].GetYaxis().SetNdivisions(4,5,0)
    fitsHP[0].GetXaxis().SetNdivisions(5,5,0)
    fitsHP[0].GetYaxis().SetTitleOffset(1.15)
    fitsHP[0].GetXaxis().SetTitleOffset(0.9)
    fitsHP[0].GetXaxis().SetRangeUser(1246, 6050.)
    fitsHP[0].GetYaxis().SetRangeUser(0.0,0.3)
    if "VBF" in category: fitsHP[0].GetYaxis().SetRangeUser(0.0,0.1)
    #fitsHP[0].GetYaxis().SetRangeUser(0.0, ymaxrange[ky])
    #fitsHP[0].Draw("AC")
    c.Update()
    for i,(gHP) in enumerate(datasHP): 
        gHP.Draw("Psame")
        fitsHP[i].Draw("Csame") #"Csame")
    c.Update()
    l.Draw("same")
    l2.Draw("same")
    if prelim.find("prelim")!=-1:
         cmslabel_sim_prelim(c,'sim',11)
    elif prelim.find("thesis")!=-1:
        cmslabel_thesis(c,'sim',11)
    else:
         cmslabel_sim(c,'sim',11)
    
    
    c.Update()
    vbfsig=""
    if "VBF" in signals[0]: vbfsig="VBFsig"
    outname=path+"signalEff"+vbfsig+prelim+"_"+category
    c.SaveAs(outname+".png")
    c.SaveAs(outname+".pdf")
    c.SaveAs(outname+".C")
    print ky
    print ymaxrange[ky]

  print " total signal eff!!! "

  flipped = defaultdict(dict)
  for key, val in gr.items():
    for subkey, subval in val.items():
        print " key ",key
        print " subkey ",subkey
        flipped[subkey][key] = subval

  print "flipped ",flipped


  tot = {}
  Mass = {}

  ct = getCanvas()
  legt = getLegend(0.5,0.55,0.9522613,0.9020979)
  ptt = getPavetext()
  ct.Draw()
  i=0
  datatot = []
  for s,l in zip(signals,titles):
    tot[s],Mass[s] = array( 'd' ), array( 'd' )
    print " flipped "+s+" ",flipped[s]
    for i in range(flipped[s][categories[0]].GetN()) :
        totsum = 0
        for c in categories: totsum += flipped[s][c].GetY()[i]

        tot[s].append( totsum )
        Mass[s].append(flipped[s][categories[0]].GetX()[i] )

    print tot[s]

    gr_tot = TGraph(gr['VH_HPHP'][s].GetN(),Mass[s],tot[s])
    gr_tot.SetLineColor(signalcolor[s])
    gr_tot.SetLineStyle(1)
    gr_tot.SetLineWidth(2)
    gr_tot.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_tot.GetYaxis().SetTitle("Signal efficiency")
    gr_tot.GetYaxis().SetNdivisions(4,5,0)
    gr_tot.GetXaxis().SetNdivisions(5,5,0)

    gr_tot.SetMarkerColor(signalcolor[s])
    gr_tot.SetMarkerStyle(signalmarker[s])
    gr_tot.SetMinimum(0.)
    gr_tot.SetMaximum(0.5)
    gr_tot.GetXaxis().SetLimits(1000.,6000.)
    gr_tot.SetTitle("")
    datatot.append(gr_tot)

    legt.AddEntry(gr_tot,l, "LP")
    i=i+1
    datatot[0].Draw("AC")
    for i,(g) in enumerate(datatot):
        g.Draw("PLsame")


  legt.Draw("same")
  if prelim.find("prelim")!=-1:
      cmslabel_sim_prelim(ct,'sim',11)
  elif prelim.find("thesis")!=-1:
      cmslabel_thesis(ct,'sim',11)
  else:
      cmslabel_sim(ct,'sim',11)
 
  name = path+"signalEff%s_TotalVVVH_%s"  %(vbfsig,prelim)
  ct.SaveAs(name+".png")
  ct.SaveAs(name+".pdf" )
  ct.SaveAs(name+".C"   )
  ct.SaveAs(name+".root")

  tot_ggDY = {}
  ct = getCanvas()
  legt = getLegend(0.35,0.55,0.9522613,0.9020979)
  ptt = getPavetext()
  ct.Draw()
  i=0
  datatot_ggDY = []
  for s,l in zip(signals,titles):
    tot_ggDY[s] = array( 'd' )
    for i in range(flipped[s][categories[0]].GetN()) :
        totsum = 0
        ggdysum = 0
        for c in categories:
            totsum += flipped[s][c].GetY()[i]
            if "VBF" not in c: ggdysum += flipped[s][c].GetY()[i]
        tot_ggDY[s].append( ggdysum/totsum )
        Mass[s].append(flipped[s][categories[0]].GetX()[i] )

    print tot_ggDY[s]

    gr_tot_ggDY = TGraph(gr['VH_HPHP'][s].GetN(),Mass[s],tot_ggDY[s])
    gr_tot_ggDY.SetLineColor(signalcolor[s])
    gr_tot_ggDY.SetLineStyle(1)
    gr_tot_ggDY.SetLineWidth(2)
    gr_tot_ggDY.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_tot_ggDY.GetYaxis().SetTitle("% of total signal efficiency")
    gr_tot_ggDY.GetYaxis().SetNdivisions(4,5,0)
    gr_tot_ggDY.GetXaxis().SetNdivisions(5,5,0)

    gr_tot_ggDY.SetMarkerColor(signalcolor[s])
    gr_tot_ggDY.SetMarkerStyle(signalmarker[s])
    gr_tot_ggDY.SetMinimum(0.5)
    gr_tot_ggDY.SetMaximum(1.5)
    gr_tot_ggDY.GetXaxis().SetLimits(1000.,6000.)
    gr_tot_ggDY.SetTitle("")
    datatot_ggDY.append(gr_tot_ggDY)

    legt.AddEntry(gr_tot_ggDY,l+" ggDY", "LP")
    i=i+1
    datatot_ggDY[0].Draw("AC")
    for i,(g) in enumerate(datatot_ggDY):
        g.Draw("PLsame")


  legt.Draw("same")
 
  name = path+"signalEff%s_ggDYvsTotalVVVH_%s"  %(vbfsig,prelim)
  ct.SaveAs(name+".png")
  ct.SaveAs(name+".pdf" )
  ct.SaveAs(name+".C"   )
  ct.SaveAs(name+".root")


  tot_VBF = {}
  ct = getCanvas()
  legt = getLegend(0.4,0.6363636,0.9522613,0.9020979)
  ptt = getPavetext()
  ct.Draw()
  i=0
  datatot_VBF = []
  for s,l in zip(signals,titles):
    tot_VBF[s] = array( 'd' )
    for i in range(flipped[s][categories[0]].GetN()) :
        totsum = 0
        ggdysum = 0
        for c in categories:
            totsum += flipped[s][c].GetY()[i]
            if "VBF" in c: ggdysum += flipped[s][c].GetY()[i]
        tot_VBF[s].append( ggdysum/totsum )
        Mass[s].append(flipped[s][categories[0]].GetX()[i] )

    print tot_VBF[s]

    gr_tot_VBF = TGraph(gr['VH_HPHP'][s].GetN(),Mass[s],tot_VBF[s])
    gr_tot_VBF.SetLineColor(signalcolor[s])
    gr_tot_VBF.SetLineStyle(1)
    gr_tot_VBF.SetLineWidth(2)
    gr_tot_VBF.GetXaxis().SetTitle("m_{X} [GeV]")
    gr_tot_VBF.GetYaxis().SetTitle("% of total signal efficiency")
    gr_tot_VBF.GetYaxis().SetNdivisions(4,5,0)
    gr_tot_VBF.GetXaxis().SetNdivisions(5,5,0)

    gr_tot_VBF.SetMarkerColor(signalcolor[s])
    gr_tot_VBF.SetMarkerStyle(signalmarker[s])
    gr_tot_VBF.SetMinimum(0.)
    gr_tot_VBF.SetMaximum(0.5)
    gr_tot_VBF.GetXaxis().SetLimits(1000.,6000.)
    gr_tot_VBF.SetTitle("")
    datatot_VBF.append(gr_tot_VBF)

    legt.AddEntry(gr_tot_VBF,l+" VBF", "LP")
    i=i+1
    datatot_VBF[0].Draw("AC")
    for i,(g) in enumerate(datatot_VBF):
        g.Draw("PLsame")


  legt.Draw("same")
 
  name = path+"signalEff%s_VBFvsTotalVVVH_%s"  %(vbfsig,prelim)
  ct.SaveAs(name+".png")
  ct.SaveAs(name+".pdf" )
  ct.SaveAs(name+".C"   )
  ct.SaveAs(name+".root")

  for cat in categories:
      tot_cat = {}
      ct = getCanvas()
      legt = getLegend(0.3,0.6363636,0.9522613,0.9020979)
      ptt = getPavetext()
      ct.Draw()
      i=0
      datatot_cat = []
      for s,l in zip(signals,titles):
          tot_cat[s] = array( 'd' )
          for i in range(flipped[s][categories[0]].GetN()) :
              totsum = 0
              ggdysum = 0
              for c in categories:
                  totsum += flipped[s][c].GetY()[i]
                  if cat == c: 
                      ggdysum += flipped[s][c].GetY()[i]
              tot_cat[s].append( ggdysum/totsum )
              Mass[s].append(flipped[s][categories[0]].GetX()[i] )

          print tot_cat[s]

          gr_tot_cat = TGraph(gr['VH_HPHP'][s].GetN(),Mass[s],tot_cat[s])
          gr_tot_cat.SetLineColor(signalcolor[s])
          gr_tot_cat.SetLineStyle(1)
          gr_tot_cat.SetLineWidth(2)
          gr_tot_cat.GetXaxis().SetTitle("m_{X} [GeV]")
          gr_tot_cat.GetYaxis().SetTitle("% of total signal efficiency")
          gr_tot_cat.GetYaxis().SetNdivisions(4,5,0)
          gr_tot_cat.GetXaxis().SetNdivisions(5,5,0)

          gr_tot_cat.SetMarkerColor(signalcolor[s])
          gr_tot_cat.SetMarkerStyle(signalmarker[s])
          gr_tot_cat.SetMinimum(0.)
          gr_tot_cat.SetMaximum(0.5)
          if cat == "VH_HPHP": gr_tot_cat.SetMaximum(1.)
          if "VBF" in cat: gr_tot_cat.SetMaximum(0.4)
          gr_tot_cat.GetXaxis().SetLimits(1000.,6000.)
          gr_tot_cat.SetTitle("")
          datatot_cat.append(gr_tot_cat)

          legt.AddEntry(gr_tot_cat,l+" "+cat, "LP")
          i=i+1
          datatot_cat[0].Draw("AC")
          for i,(g) in enumerate(datatot_cat):
              g.Draw("PLsame")
              
              
      legt.Draw("same")
 
      name = path+"signalEff%s_%svsTotalVVVH_%s"  %(vbfsig,cat,prelim)
      ct.SaveAs(name+".png")
      ct.SaveAs(name+".pdf" )
      ct.SaveAs(name+".C"   )
      ct.SaveAs(name+".root")




def doJetMass(leg,signals,titles,categories):
    print signals
    gStyle.SetOptFit(0)
 
    files=[]
    filesHjet=[]
    fHLP=0
    fHHP=0
    for i,s in enumerate(signals):
        if len(categories)==1:
            if categories[0].find("NP")!=-1:
                files.append(TFile(path+"debug_JJ_"+s+"_"+categories[0].split("_")[0]+"_MJ"+leg+"_"+categories[0].split("_")[1]+".json.root","READ"))
                filesHjet.append(None)
            else:
                files.append(TFile(path+"debug_JJ_"+s+"_"+categories[0].split("_")[0]+"_MJ"+leg+"_"+categories[0].split("_")[1]+"_"+categories[0].split("_")[2]+".json.root","READ"))
            if files[-1].IsZombie()==1:
                if categories[0].find("NP")!=-1:
                    files[-1] =(TFile(path+"debug_JJ_Vjet_"+s+"_"+categories[0].split("_")[0]+"_MJ"+leg+"_"+categories[0].split("_")[1]+".json.root","READ"))
                    filesHjet[-1] =(TFile(path+"debug_JJ_Hjet_"+s+"_"+categories[0].split("_")[0]+"_MJ"+leg+"_"+categories[0].split("_")[1]+".json.root","READ"))
                else:
                    files[-1] =(TFile(path+"debug_JJ_Vjet_"+s+"_"+categories[0].split("_")[0]+"_MJ"+leg+"_"+categories[0].split("_")[1]+"_"+categories[0].split("_")[2]+".json.root","READ"))
                    filesHjet[-1] = (TFile(path+"debug_JJ_Hjet_"+s+"_"+categories[0].split("_")[0]+"_MJ"+leg+"_"+categories[0].split("_")[1]+"_"+categories[0].split("_")[2]+".json.root","READ"))
        if len(categories)> 1:    
            for categ in categories:
                files.append(TFile(path+"debug_JJ_"+s+"_"+categ.split("_")[0]+"_MJ"+leg+"_"+categ.split("_")[1]+"_"+categ.split("_")[2]+".json.root","READ"))
    
    vars = ["mean","sigma","alpha","n","alpha2","n2"]
    for var in vars:
           
       fits =[]
       fitsHjet=[]
       datas=[]
       datasHjet=[]
        
       c = getCanvas()
       l = getLegend()#0.7788945,0.723362,0.9974874,0.879833)
       l2 = getLegend(0.17,0.5783217,0.4974874,0.7482517)
       l3 = getLegend(0.18,0.5783217,0.6974874,0.2482517)
       gStyle.SetOptStat(0)
       gStyle.SetOptTitle(0)
       title = "Jet mass width "
       if var == "mean": title="Jet mass mean"
                        
       for i,(fHP,fLP) in enumerate(zip(files,filesHjet)):
           print fHP 
           print fLP 
           
           if fLP ==None:
                gHPLP = fHP.Get(var)
                fHPLP = fHP.Get(var+"_func")
           else: 
                print fLP.GetName()
                gHPLP = fLP.Get(var+"H")
                fHPLP = fLP.Get(var+"H_func")

           gHPHP = fHP.Get(var)
           fHPHP = fHP.Get(var+"_func")

           
           beautify(fHPLP ,rt.TColor.GetColor(colors[i]),2,markerstyle[i])
           beautify(fHPHP ,rt.TColor.GetColor(colors[i]),1,markerstyle[i])
           beautify(gHPLP ,rt.TColor.GetColor(colors[i]),2,markerstyle[i])
           beautify(gHPHP ,rt.TColor.GetColor(colors[i]),1,markerstyle[i])
           datas.append(gHPHP)
           datasHjet.append(gHPLP)
           fits.append(fHPHP)
           fitsHjet.append(fHPLP)
           l.AddEntry(fHPHP,titles[i],"LP")
       print datasHjet 
       if len(categories) > 1: l2.AddEntry(datas[0],categories[0],"LP") 
       if len(categories)>1: l2.AddEntry(datasHjet[0],categories[1],"LP")    
       datas[0].GetXaxis().SetTitle("m_{X} [GeV]")
       datas[0].GetYaxis().SetTitle(title+" [GeV]")
       datas[0].GetYaxis().SetNdivisions(4,5,0)
       datas[0].GetXaxis().SetNdivisions(5,5,0)
       datas[0].GetYaxis().SetTitleOffset(1.05)
       datas[0].GetXaxis().SetTitleOffset(0.9)
       datas[0].GetXaxis().SetRangeUser(1126, 6050.)
       datas[0].GetXaxis().SetLabelSize(0.05)
       datas[0].GetXaxis().SetTitleSize(0.06)
       datas[0].GetYaxis().SetLabelSize(0.05)
       datas[0].GetYaxis().SetTitleSize(0.06)
       if var == "mean": datas[0].GetYaxis().SetRangeUser(75,150);  
       if var == "sigma": datas[0].GetYaxis().SetRangeUser(5,20.);
       if var == "alpha": datas[0].GetYaxis().SetRangeUser(0,5); datas[0].GetYaxis().SetTitle("alpha")
       if var == "n": datas[0].GetYaxis().SetRangeUser(0,250); datas[0].GetYaxis().SetTitle("n")
       if var == "alpha2": datas[0].GetYaxis().SetRangeUser(0,5); datas[0].GetYaxis().SetTitle("alpha2")
       if var == "n2": datas[0].GetYaxis().SetRangeUser(0,20); datas[0].GetYaxis().SetTitle("n2")
       datas[0].Draw("AP")
       for i,(gHP,gLP) in enumerate(zip(datas,datasHjet)): 
           gLP.Draw("Psame")
           gHP.Draw("Psame")
           fits[i].Draw("Csame")
           fitsHjet[i].Draw("Csame")
       datas[0].GetXaxis().SetRangeUser(1126, 6050.)
       l.Draw("same")
       l2.Draw("same")
       if prelim.find("prelim")!=-1:
           cmslabel_sim_prelim(c,'sim',11)
       elif prelim.find("thesis")!=-1:
           cmslabel_thesis(c,'sim',11)
       else:
           cmslabel_sim(c,'sim',11)
       pt = getPavetext()
       c.Update()
       vbfsig = ""
       if "VBF" in signals[0]: vbfsig = "VBFsig"
       outname=path+"Signal"+vbfsig+"_mjet%s_"%categories[0].replace("HPHP","")+var+prelim
       c.SaveAs(outname+".png")
       c.SaveAs(outname+".pdf")
       c.SaveAs(outname+".C")
    
    
    

    
    
    
    
def doYield():
    FHPLP = TFile("JJ_"+sys.argv[2]+"_HPLP_yield.root","READ")
    FHPHP = TFile("JJ_"+sys.argv[2]+"_HPHP_yield.root","READ")
    
    vars = ["yield"]
    for var in vars:
        c = getCanvas()
        l = getLegend()
        gStyle.SetOptStat(0)
        gStyle.SetOptTitle(0)
        
        
        gHPLP = FHPLP.Get(var)
        gHPHP = FHPHP.Get(var)
        fHPLP = gHPLP.GetFunction("func")
        fHPHP = gHPHP.GetFunction("func")
        
        beautify(gHPLP ,1,1,8)
        beautify(gHPHP ,1,1,4)
        beautify(fHPLP ,46,1,8)
        beautify(fHPHP ,30,1,4)
        
        l.AddEntry(fHPLP,"HPLP","LP")
        l.AddEntry(fHPHP,"HPHP","LP")
        
        gHPLP.GetXaxis().SetTitle("M_{X} (GeV)")
        gHPLP.GetYaxis().SetTitle(var)
        gHPLP.GetYaxis().SetNdivisions(9,1,0)
        gHPLP.GetYaxis().SetTitleOffset(1.7)
        gHPLP.GetXaxis().SetRangeUser(1126., 5500.)
        gHPLP.GetYaxis().SetRangeUser(0.0, 0.00025)
            
        gHPLP.Draw("APE")
        gHPHP.Draw("samePE")
        # fHPLP.Draw("sameL")
    #   fHPHP.Draw("sameL")
        model = "G_{bulk} #rightarrow WW"
        if sys.argv[2].find("ZZ")!=-1:
            model = "G_{bulk} #rightarrow ZZ"
        if sys.argv[2].find("WZ")!=-1:
            model = "W' #rightarrow WZ"
        if sys.argv[2].find("Zprime")!=-1:
            model = "Z' #rightarrow WW"
        text = TLatex()
        text.DrawLatex(3500,0.00020,model)
        l.Draw("same")
        cmslabel_sim(c,'2016',11)
        c.Update()
        #sleep(112600)
        c.SaveAs(path+"signalFit/"+sys.argv[2]+"_Yield_"+var+"_fit.png")
        
def doMVV(signals,titles,year):

#    variab = ["MEAN","SIGMA","ALPHA1","ALPHA2","N1","N2"]
#    for var in variab:
#        print "var ",var

    vars = ["MEAN","SIGMA","ALPHA1","ALPHA2","N1","N2"]
    gStyle.SetOptFit(0)
    filesHP=[]
    # filesLP=[]
    
    for i,s in enumerate(signals):
        # filesLP.append(TFile("debug_JJ_"+s+"_MVV_jer.json.root","READ"))
        if TFile(path+"debug_JJ_"+s+"_"+year+"_MVV.json.root","READ").IsZombie() ==1:
            filesHP.append(TFile(path+"debug_JJ_j1"+s+"_"+year+"_MVV.json.root","READ"))
        else:
            filesHP.append(TFile(path+"debug_JJ_"+s+"_"+year+"_MVV.json.root","READ"))
    
    for var in vars:
        fitsHP=[]
        fitsLP=[]
        datasHP=[]
        datasLP=[]
        
        c = getCanvas()
        l = getLegend()
        l2 = getLegend(0.7788945,0.1783217,0.9974874,0.2482517)
        gStyle.SetOptStat(0)
        gStyle.SetOptTitle(0)
        
        for i,fHP in enumerate(filesHP):
                
                # gHPLP = fLP.Get(var)
                gHPHP = fHP.Get(var)

                # fHPLP = fLP.Get(var+"_func")
                fHPHP = fHP.Get(var+"_func")
                fHPHP.SetLineWidth(0)

                ff=  gHPHP.GetFunction(var+"_func")
                ff.SetLineColor(0)
                ff.SetLineWidth(0)

                #gHPHP.GetFunction(var+"_func").SetBit(rt.TF1.kNotDraw)
                
                # beautify(fHPLP ,rt.TColor.GetColor(colors[i]),9,1)
                beautify(fHPHP ,rt.TColor.GetColor(colors[i]),1,markerstyle[i])
                # beautify(gHPLP ,rt.TColor.GetColor(colors[i]),9,1)
                beautify(gHPHP ,rt.TColor.GetColor(colors[i]),1,markerstyle[i])
                datasHP.append(gHPHP)
                # datasLP.append(gHPLP)
                fitsHP.append(fHPHP)
                # fitsLP.append(fHPLP)
                l.AddEntry(fHPHP,titles[i],"LP")
        # l2.AddEntry(datasHP[0],"No JER","L")
 #        l2.AddEntry(datasLP[0],"JER","L")
        datasHP[0].GetXaxis().SetTitle("M_{X} [GeV]")
        datasHP[0].GetYaxis().SetTitle(var+" [GeV]")
        datasHP[0].GetYaxis().SetNdivisions(4,5,0)
        datasHP[0].GetXaxis().SetNdivisions(9,2,0)
        datasHP[0].GetYaxis().SetTitleOffset(0.97)
        datasHP[0].GetYaxis().SetMaxDigits(2)
        datasHP[0].GetXaxis().SetTitleOffset(0.94)
        datasHP[0].GetXaxis().SetRangeUser(1126, 6050.)
        datasHP[0].GetYaxis().SetRangeUser(-2., 3.)
        if var.find("ALPHA1")!=-1: datasHP[0].GetYaxis().SetRangeUser(0., 4.)
        if var.find("ALPHA2")!=-1: datasHP[0].GetYaxis().SetRangeUser(0., 20.)
        if var.find("SIGMA")!=-1:  datasHP[0].GetYaxis().SetRangeUser(0., 400.)
        if var.find("MEAN")!=-1:   datasHP[0].GetYaxis().SetRangeUser(700., 8000)
        if var.find("N1")!=-1:     datasHP[0].GetYaxis().SetRangeUser(0., 15.)
        if var.find("N2")!=-1:     datasHP[0].GetYaxis().SetRangeUser(0., 150.)

        datasHP[0].Draw("PA")
        print datasHP[0].Eval(1200.)
        c.Update()
        for i,gHP in enumerate(fitsHP): 
            # gLP.Draw("Psame")
            gHP.Draw("lsame")
            datasHP[i].Draw("Psame")
            # fitsLP[i].Draw("Csame")
        l.Draw("same")
        # l2.Draw("same")
        if prelim.find("thesis")!=-1:
            cmslabel_thesis(c,'sim',11)
        else:
            cmslabel_sim_prelim(c,'sim',11)
        pt = getPavetext()
        c.Update()
        vbfsig = ""
        if "VBF" in signals[0]: vbfsig = "VBFsig"
        outname=path+"Signal"+vbfsig+"_mVV_"+var+"_"+year+prelim
        c.SaveAs(outname+".png")
        c.SaveAs(outname+".pdf")
        c.SaveAs(outname+".C")
        

def doMJFit():
    FHPLP = TFile("debug_JJ_"+sys.argv[2]+"_MJl1_HPHP.json.root","READ")
    FHPHP = TFile("debug_JJ_"+sys.argv[2]+"_MJl1_HPHP.json.root","READ")
    
    vars = ["mean","sigma"]#,"alpha","n","f","alpha2","n2","slope"]
    #if sys.argv[1].find("Wprime")!=-1:
            #vars = ["meanW","sigmaW","alphaW","f","alphaW2","meanZ","sigmaZ","alphaZ","alphaZ2"]
    for var in vars:
        print "Plotting variable: " ,var
        c = getCanvas()
        l = getLegend()
        gStyle.SetOptStat(0)
        gStyle.SetOptTitle(0)
        
        
        gHPLP = FHPLP.Get(var)
        gHPHP = FHPHP.Get(var)
        fHPLP = FHPLP.Get(var+"_func")
        fHPHP = FHPHP.Get(var+"_func")
        
        beautify(gHPLP ,1,1,8)
        beautify(gHPHP ,1,1,4)
        beautify(fHPLP ,46,1,8)
        beautify(fHPHP ,30,1,4)
        
        l.AddEntry(fHPHP,"HPHP","LP")
        l.AddEntry(fHPLP,"HPLP","LP")
        
        
        gHPLP.GetXaxis().SetTitle("M_{X} (GeV)")
        gHPLP.GetYaxis().SetTitle(var)
        gHPLP.GetYaxis().SetNdivisions(9,1,0)
        gHPLP.GetYaxis().SetTitleOffset(1.7)
        gHPLP.GetXaxis().SetRangeUser(1126., 5500.)
        
                
        if var.find("n2")!=-1: gHPLP.GetYaxis().SetRangeUser(1., 3.)
        if var.find("n")!=-1: gHPLP.GetYaxis().SetRangeUser(1., 3.)
        if var.find("alpha2")!=-1: gHPLP.GetYaxis().SetRangeUser(0.1, 5.1)
        if var.find("alpha")!=-1: gHPLP.GetYaxis().SetRangeUser(0.1, 5.5)
        if var.find("alphaZ2")!=-1: gHPLP.GetYaxis().SetRangeUser(0.1, 10)
        if var.find("alphaZ")!=-1: gHPLP.GetYaxis().SetRangeUser(0.1, 10)
        if var.find("slope")!=-1: gHPLP.GetYaxis().SetRangeUser(-1., 1.)
        if var.find("sigma")!=-1: gHPLP.GetYaxis().SetRangeUser(3.,25.)
        if var.find("mean")!=-1: gHPLP.GetYaxis().SetRangeUser(70., 95.)
        if var.find("meanZ")!=-1: gHPLP.GetYaxis().SetRangeUser(80., 95.)
        if var.find("f")!=-1: gHPLP.GetYaxis().SetRangeUser(-1., 2.)
        gHPLP.Draw("APE")
        gHPHP.Draw("samePE")
        fHPLP.Draw("sameL")
        fHPHP.Draw("sameL")
        l.Draw("same")
        cmslabel_sim(c,'2016',11)
        c.Update()
        c.SaveAs(path+"signalFit/"+sys.argv[2]+"_MJ_"+var+"_fit.png")
        #sleep(10)
        
def doResolution():
    fLP = TFile("JJ_nonRes_detectorResponse_2016.root","READ")
    fHP = TFile("JJ_nonRes_detectorResponse.root","READ")
    hps = []    
    hp_hSx  =fHP.Get("scalexHisto")
    hp_hSy  =fHP.Get("scaleyHisto")
    hp_hRx  =fHP.Get("resxHisto")  
    hp_hRy  =fHP.Get("resyHisto") 
    hp_hSx.GetYaxis().SetTitle("M_{VV} scale" )
    hp_hSy.GetYaxis().SetTitle("M_{jet} scale" )
    hp_hRx.GetYaxis().SetTitle("M_{VV} resolution" )
    hp_hRy.GetYaxis().SetTitle("M_{jet} resolution" )
    hp_hSx.GetYaxis().SetRangeUser(0.9,1.1)
    hp_hSy.GetYaxis().SetRangeUser(0.9,1.1)
    hp_hRx.GetYaxis().SetRangeUser(0.,0.15)
    hp_hRy.GetYaxis().SetRangeUser(0.,0.15)
    
     
    # hp_h2D_x =f.Get("dataX")    
    # hp_h2D_y =f.Get("dataY")    
    hps.append(hp_hSx)
    hps.append(hp_hSy)
    hps.append(hp_hRx)
    hps.append(hp_hRy)
    for h in hps: 
        h.SetLineColor(rt.TColor.GetColor(colors[0]))
        h.SetLineWidth(3)
        h.GetXaxis().SetTitle("Gen p_{T} (GeV)")
        h.GetXaxis().SetNdivisions(9,1,0)
        h.GetYaxis().SetNdivisions(9,1,0)
        h.GetYaxis().SetTitleOffset(1.4)
    
    
    lps =[]
    lp_hSx   =fLP.Get("scalexHisto")
    lp_hSy   =fLP.Get("scaleyHisto")
    lp_hRx   =fLP.Get("resxHisto")
    lp_hRy   =fLP.Get("resyHisto")
    # lp_h2D_x =fLP.Get("dataX")
    # lp_h2D_y =fLP.Get("dataY")
    lps.append(lp_hSx)
    lps.append(lp_hSy)
    lps.append(lp_hRx)
    lps.append(lp_hRy)
    for h in lps:
      h.SetLineColor(rt.TColor.GetColor(colors[1]))
      h.SetLineWidth(3)
      h.GetXaxis().SetTitle("Gen p_{T} (GeV)")
    
    lg = getLegend(0.7788945,0.723362,0.9974874,0.879833)
  # lg.AddEntry(hp_hSx,"m_{VV} scale","L")
  # lg.AddEntry(lp_hSx,"HPLP","L")
    lg.AddEntry(hp_hSx,"2017","L")
    lg.AddEntry(lp_hSx,"2016","L")
    
    pt = getPavetext()
    # pt.AddText("WP #tau_{21}^{DDT} = 0.57")
    
    
    for hp,lp in zip(hps,lps):
        c = getCanvas()
        hp.GetXaxis().SetRangeUser(200.,2600.)
        hp.Draw("HIST")
        lp.Draw("HISTsame")
        lg.Draw('same')
        pt.Draw("same")
        c.Update()
        c.SaveAs(path+"detectorresolution_"+hp.GetName()+".png")
        
    dataY_lp = fLP.Get('dataY')
    dataY_lp.SetName('dataY_lp')
    plotY_lp = TH1F('plotYlp','mJJ projection',dataY_lp.GetNbinsY(),dataY_lp.GetYaxis().GetXmin(),dataY_lp.GetYaxis().GetXmax())
    
    dataY_hp = fHP.Get('dataY')
    dataY_hp.SetName('dataY_hp')
    plotY_hp = TH1F('plotYhp','mJJ projection',dataY_hp.GetNbinsY(),dataY_hp.GetYaxis().GetXmin(),dataY_hp.GetYaxis().GetXmax())
    
    for bx in range(dataY_hp.GetNbinsX()):
      for by in range(dataY_hp.GetNbinsY()):
        plotY_hp.Fill(dataY_hp.GetYaxis().GetBinCenter(by),dataY_hp.GetBinContent(bx,by))
        plotY_lp.Fill(dataY_lp.GetYaxis().GetBinCenter(by),dataY_lp.GetBinContent(bx,by))
    plotY_hp.SetLineColor(rt.TColor.GetColor(colors[0])) 
    plotY_lp.SetLineColor(rt.TColor.GetColor(colors[1]))
    plotY_hp.SetLineWidth(3)
    plotY_lp.SetLineWidth(3)
    c = getCanvas()
    
    plotY_hp.GetXaxis().SetTitle("M_{jet}^{reco}/M_{jet}^{gen}")
    plotY_hp.GetYaxis().SetTitle("A.U")
    plotY_hp.GetXaxis().SetNdivisions(9,1,0)
    plotY_hp.GetYaxis().SetNdivisions(9,1,0)
    plotY_hp.GetYaxis().SetTitleOffset(0.94)
    plotY_hp.GetXaxis().SetTitleOffset(0.97)
    plotY_hp.GetYaxis().SetRangeUser(0.,plotY_hp.GetMaximum()*1.8)
    plotY_hp.DrawNormalized('HIST')
    plotY_lp.DrawNormalized('HISTSAME')
    lg.Draw("same")
    cmslabel_sim(c,'2016',11)
    c.Update()
    c.SaveAs(path+"detectorresolution_mjet.png")
    
    dataX_lp = fLP.Get('dataX')
    dataX_lp.SetName('dataX_lp')
    plotX_lp = TH1F('plotXlp','mJJ projection',dataX_lp.GetNbinsY(),dataX_lp.GetYaxis().GetXmin(),dataX_lp.GetYaxis().GetXmax())
    
    dataX_hp = fHP.Get('dataX')
    dataX_hp.SetName('dataX_hp')
    plotX_hp = TH1F('plotXhp','mVV projection',dataX_hp.GetNbinsY(),dataX_hp.GetYaxis().GetXmin(),dataX_hp.GetYaxis().GetXmax())
    
    for bx in range(dataX_hp.GetNbinsX()):
     for by in range(dataX_hp.GetNbinsY()):
      plotX_hp.Fill(dataX_hp.GetYaxis().GetBinCenter(by),dataX_hp.GetBinContent(bx,by))
      plotX_lp.Fill(dataX_lp.GetYaxis().GetBinCenter(by),dataX_lp.GetBinContent(bx,by))
    
    plotX_hp.SetLineColor(rt.TColor.GetColor(colors[0])) 
    plotX_lp.SetLineColor(rt.TColor.GetColor(colors[1]))
    plotX_hp.SetLineWidth(3)
    plotX_lp.SetLineWidth(3)
    c = getCanvas()
    
    plotX_hp.GetXaxis().SetTitle("M_{VV}^{reco}/M_{VV}^{gen}")
    plotX_hp.GetYaxis().SetTitle("A.U")
    plotX_hp.GetXaxis().SetNdivisions(4,5,0)
    plotX_hp.GetYaxis().SetNdivisions(4,5,0)
    plotX_hp.GetYaxis().SetTitleOffset(0.94)
    plotX_hp.GetXaxis().SetTitleOffset(0.97)
    plotX_hp.GetYaxis().SetRangeUser(0.,plotX_lp.GetMaximum()*1.8)
    plotX_hp.DrawNormalized('HIST')
    plotX_lp.DrawNormalized('HISTSAME')
    lg.Draw("same")
    cmslabel_sim(c,'2016',11)
    c.Update()
    c.SaveAs(path+"detectorresolution_mvv.png")
    
    fLP.Close()
    fHP.Close() 
    
def doKernelMVV():
    files = []
    fLP = TFile("JJ_nonRes_MVV_HPHP.root","READ")
    fHP = TFile("JJ_nonRes_MVV_HPHP.root","READ")
    files.append(fLP)
    files.append(fHP)
    cols = [46,30]
    mstyle = [8,4]
    c = getCanvas()
    c.SetLogy()
    l = getLegend(0.60010112,0.723362,0.90202143,0.879833)
    hists = []
    for i,f in enumerate(files):
        hsts = []
        fromKernel = f.Get("histo_nominal")
        fromSim    = f.Get("mvv_nominal")
        beautify(fromKernel,cols[i],1,mstyle[i])
        beautify(fromSim   ,cols[i],1,mstyle[i])
        l.AddEntry(fromKernel,"%s,From Kernel    "%(f.GetName().replace(".root","").split("_")[3]),"L")
        l.AddEntry(fromSim   ,"%s,From Simulation"%(f.GetName().replace(".root","").split("_")[3]),"PE")
        
        hsts.append(fromSim)
        hsts.append(fromKernel)
        hists.append(hsts)
    hists[0][0].GetXaxis().SetTitle("M_{jj} (GeV)")
    hists[0][0].GetYaxis().SetTitle("A.U")
    hists[0][0].GetYaxis().SetNdivisions(9,1,0)
    hists[0][0].GetYaxis().SetTitleOffset(1.5)  
    hists[0][0].GetXaxis().SetRangeUser(1126   , 6808)
    hists[0][0].DrawNormalized("histPE")
    for h in hists:
        h[0].DrawNormalized("samehistPE")
        h[1].DrawNormalized("sameLhist")
        
    l.Draw("same")
    c.SaveAs(path+"1Dkernel.png")

def compKernelMVV():
    purities=['HPHP','HPLP']
    
    for p in purities:
        hists = []
        files = []
        fNominal = TFile("JJ_nonRes_MVV_"+p+".root","READ")
        fCombined = TFile("JJ_nonRes_MVV_"+p+"_NP.root","READ")
        files.append(fNominal)
        files.append(fCombined)
        
        
        hists = []
        l = getLegend(0.60010112,0.723362,0.90202143,0.879833)
        cols = [46,30]
        for i,f in enumerate(files):
            hsts = []
    
            fromKernel = f.Get("histo_nominal")
            fromSim    = f.Get("mvv_nominal")

            beautify(fromKernel,cols[i])
            beautify(fromSim   ,cols[i])
            if i == 1:
                l.AddEntry(fromKernel,"Combined, Kernel    ","L")
                l.AddEntry(fromSim   ,"Combined, Simulation","PE")
            elif i == 0:
                l.AddEntry(fromKernel,"%s res., Kernel    "%p,"L")
                l.AddEntry(fromSim   ,"%s res., Simulation"%p,"PE")
                    
            hsts.append(fromSim)
            hsts.append(fromKernel)
            hists.append(hsts)
        c = getCanvas()
        c.SetLogy()
        
        hists[0][0].GetXaxis().SetTitle("M_{jj} (GeV)")
        hists[0][0].GetYaxis().SetTitle("A.U")
        hists[0][0].GetYaxis().SetNdivisions(9,1,0)
        hists[0][0].GetYaxis().SetTitleOffset(1.5)  
        hists[0][0].GetXaxis().SetRangeUser(1126.   , 4900)
        hists[0][0].Draw("histPE")
        for h in hists:
            h[0].Draw("samehistPE")
            h[1].Draw("sameLhist")
        
        l.Draw("same")
        c.SaveAs(path+"compare_1Dkernel"+p+".png")

def doKernel2D():
    files = []
    fLP = TFile("JJ_nonRes_COND2D_HPHP_l1.root","READ")
    fHP = TFile("JJ_nonRes_COND2D_HPHP_l2.root","READ")
    histnames = ["mjet_mvv_nominal","histo_nominal"]
    files.append(fLP)
    files.append(fHP)
    cols = [46,30]
    c = getCanvas()
    c.SetLogy()
    l = getLegend(0.60010112,0.723362,0.90202143,0.879833)
    hists = []
    for i,f in enumerate(files):
        hsts = []
    
        fromKernel  = f.Get(histnames[i])
        fromSim     = f.Get(histnames[i])
        fromKernelY = fromKernel.ProjectionX()
        fromSimY    = fromSim.ProjectionX()
        fromKernelY .SetName("kernel"+f.GetName().replace(".root","").split("_")[3])
        fromSimY    .SetName("sim"+f.GetName().replace(".root","").split("_")[3])

        beautify(fromKernelY,cols[i])
        beautify(fromSimY   ,cols[i])
        l.AddEntry(fromKernelY,"%s,From Kernel    "%(f.GetName().replace(".root","").split("_")[3]),"L")
        l.AddEntry(fromSimY   ,"%s,From Simulation"%(f.GetName().replace(".root","").split("_")[3]),"PE")
        
        hsts.append(fromSimY)
        hsts.append(fromKernelY)
        hists.append(hsts)

    hists[0][0].GetXaxis().SetTitle("M_{jet} (GeV)")
    hists[0][0].GetYaxis().SetTitle("A.U")
    hists[0][0].GetYaxis().SetNdivisions(9,1,0)
    hists[0][0].GetYaxis().SetTitleOffset(1.5)  
    # hists[0][0].GetXaxis().SetRangeUser(1126.   , 5200)
    hists[0][0].DrawNormalized("histPE")
    for h in hists:
        h[0].DrawNormalized("samehistPE")
        h[1].DrawNormalized("sameLhist")
    
    l.Draw("same")
    c.SaveAs(path+"2Dkernel_Mjet.png")      
    
    c = getCanvas()
    c.SetLogy()
    l = getLegend(0.60010112,0.723362,0.90202143,0.879833)
    hists = []
    for i,f in enumerate(files):
        hsts = []
    
        fromKernel  = f.Get("histo_nominal")
        fromSim     = f.Get("mjet_mvv_nominal")
        fromKernelY = fromKernel.ProjectionY()
        fromSimY    = fromSim.ProjectionY()
        fromKernelY .SetName("kernel"+f.GetName().replace(".root","").split("_")[3])
        fromSimY    .SetName("sim"+f.GetName().replace(".root","").split("_")[3])

        beautify(fromKernelY,cols[i])
        beautify(fromSimY   ,cols[i])
        l.AddEntry(fromKernelY,"%s,From Kernel    "%(f.GetName().replace(".root","").split("_")[3]),"L")
        l.AddEntry(fromSimY   ,"%s,From Simulation"%(f.GetName().replace(".root","").split("_")[3]),"PE")
        
        hsts.append(fromSimY)
        hsts.append(fromKernelY)
        hists.append(hsts)
    hists[0][0].GetXaxis().SetTitle("M_{jj} (GeV)")
    hists[0][0].GetYaxis().SetTitle("A.U")
    hists[0][0].GetYaxis().SetNdivisions(9,1,0)
    hists[0][0].GetYaxis().SetTitleOffset(1.5)  
    # hists[0][0].GetXaxis().SetRangeUser(1126.   , 5200)
    hists[0][0].DrawNormalized("histPE")

    for h in hists:
        # h[0].DrawNormalized("samehistPE")
        h[1].DrawNormalized("sameLhist")
    
    # l.Draw("same")
    c.SaveAs(path+"2Dkernel_Mjj.png")

def compSignalMVV():
    
    masses = [1200,1400,1600,1800,2000,2500,3000,3500,4000,4500]
    
    
    files = []
    fHP  = TFile("massHISTOS_JJ_"+sys.argv[2]+"_MVV.root","READ")
    fLP = TFile("massHISTOS_JJ_"+sys.argv[2]+"_MVV_jer.root","READ")
    files.append(fHP)
    files.append(fLP)
    
    
    histsHP = []
    histsLP = []
    l = getLegend(0.80010112,0.723362,0.90202143,0.879833)
    cols = [46,30]
    for m in masses:
        print "Working on masspoint " ,m
        hHP = fHP.Get("%i"%m)
        hLP = fLP.Get("%i"%m)
        hHP.SetName(hHP.GetName()+"HP")
        hLP.SetName(hLP.GetName()+"LP")
        hHP.SetLineColor(cols[0])
        hLP.SetLineColor(cols[1])
        hHP.SetLineWidth(2)
        hLP.SetLineWidth(2)
        hHP.SetFillColor(0)
        hLP.SetFillColor(0)
        if m == masses[0]:
            l.AddEntry(hHP   ,"No JER","L")
            l.AddEntry(hLP   ,"JER","L")
                
        histsHP.append(hHP)
        histsLP.append(hLP)
    
    print " ", len(histsHP) 
    print " ", len(histsLP)
    c = getCanvas()
    
    histsHP[0].GetXaxis().SetTitle("M_{jj} (GeV)")
    histsHP[0].GetYaxis().SetTitle("A.U")
    histsHP[0].GetYaxis().SetNdivisions(9,1,0)
    histsHP[0].GetYaxis().SetTitleOffset(1.5)
    histsHP[0].GetXaxis().SetRangeUser(1126,5500)
    histsHP[0].GetXaxis().SetLimits(1126,5500);
    # histsHP[0].GetYaxis().SetRangeUser(0,0.4)
    # histsHP[0].GetYaxis().SetLimits(0.,0.4);
    histsHP[0].Draw("hist")
    for hp,lp in zip(histsHP,histsLP):
        hp.Draw("hist same")
        lp.Draw("hist same")
    l.Draw("same")
    c.Update()
    c.SaveAs(path+"compareJER_MVV.png")
    
    
  
        
if __name__ == '__main__':
  prelim = "prelim"
  signals = ["ZprimeWW","BulkGWW","WprimeWZ","BulkGZZ","ZprimeZHinc","WprimeWHinc","RadionWW","RadionZZ"]
  titles =  ["Z' #rightarrow WW","G_{B}#rightarrow WW","W' #rightarrow WZ","G_{B}#rightarrow ZZ","Z' #rightarrow ZH","W' #rightarrow WH","R #rightarrow WW","R #rightarrow ZZ"]
  categories = ["Run2_NP"]
  doJetMass("random",signals,titles,categories)
  doMVV(signals,titles,"Run2")
  vbfsignals=[]
  vbftitles= []
  for sig,t in zip(signals,titles):
      vbfsignals.append("VBF_"+sig)
      vbftitles.append("VBF "+t)
  doJetMass("random",vbfsignals,vbftitles,categories)
  doMVV(vbfsignals,vbftitles,"Run2")


  categories = ["VH_HPHP","VV_HPHP","VH_LPHP","VH_HPLP","VV_HPLP","VBF_VH_HPHP","VBF_VV_HPHP","VBF_VH_LPHP","VBF_VH_HPLP","VBF_VV_HPLP"]
  doSignalEff(sys.argv[1],signals,titles,categories,[0.3,0.06,0.2,0.05,0.03,0.03,0.03,0.03,0.03,0.03])
  vbfsignals=[]
  vbftitles= []
  for sig,t in zip(signals,titles):
      vbfsignals.append("VBF_"+sig)
      vbftitles.append("VBF "+t)

  doSignalEff(sys.argv[1],vbfsignals,vbftitles,categories,[0.3,0.06,0.2,0.05,0.03,0.03,0.03,0.03,0.03,0.03])
