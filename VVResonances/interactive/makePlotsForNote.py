from CMGTools.VVResonances.plotting.RooPlotter import *
from CMGTools.VVResonances.plotting.tdrstyle import *
#setTDRStyle()
from  CMGTools.VVResonances.plotting.CMS_lumi import *

#from start16 import *
directory='plots16'
lumi='12900'
period='2016'


def makePileup():
    canvas,h1,h2,legend,pt=compare(WJets_quark,data,"nVert","lnujj_LV_mass>0","lnujj_LV_mass>0",60,0,60,'number of vertices','','Simulation','Data')
    cmslabel_prelim(canvas,period,12)
    canvas.SaveAs(directory+"/nVert.pdf")
    canvas.SaveAs(directory+"/nVert.png")
    canvas.SaveAs(directory+"/nVert.root")
    



def makeSignalMVVParamPlot(datacard,pdf,var='MLNuJ'):
    ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
    F=ROOT.TFile(datacard)
    w=F.Get('w')
    frame=w.var(var).frame()
    for mass in [800,1200,1600,2000,2400,2800,3200,3600,4000]:
        w.var("MH").setVal(mass)
        w.pdf(pdf).plotOn(frame)
       

    frame.GetXaxis().SetTitle("M_{VV} (GeV)")
    frame.GetYaxis().SetTitle("a.u")
    frame.GetYaxis().SetTitleOffset(1.35)
    frame.SetTitle('')
    canvas=ROOT.TCanvas("c")
    canvas.cd()
    frame.Draw()
    cmslabel_sim(canvas,period,12)
    canvas.Update()
    canvas.SaveAs(directory+"/MVVParam.png")
    canvas.SaveAs(directory+"/MVVParam.pdf")
    canvas.SaveAs(directory+"/MVVParam.root")


def getMJJParams(filename,newname):
    F=ROOT.TFile(filename)
    canvas=F.Get('c')
    canvas.SetRightMargin(0.04)
    cmslabel_sim(canvas,period,12)
    canvas.Update()
    canvas.SaveAs(directory+"/"+newname+".png")
    canvas.SaveAs(directory+"/"+newname+".pdf")
    canvas.SaveAs(directory+"/"+newname+".root")


def makeShapeUncertaintiesMJJ(filename,sample,tag,syst):
    #MJJ
    f=ROOT.TFile(filename)
    hN = f.Get("histo").ProjectionY("nominal")
    hU = f.Get("histo_"+syst+"_"+sample+"_"+tag+"Up").ProjectionY("up")
    hD = f.Get("histo_"+syst+"_"+sample+"_"+tag+"Down").ProjectionY("down")
    hN.SetLineColor(ROOT.kBlack)
    hN.SetLineStyle(1)
    hN.SetLineWidth(2)
    hU.SetLineColor(ROOT.kBlack)
    hU.SetLineStyle(3)
    hU.SetLineWidth(2)

    hD.SetLineColor(ROOT.kBlack)
    hD.SetLineStyle(4)
    hD.SetLineWidth(2)

    c=ROOT.TCanvas("c")
    c.cd()
    frame=c.DrawFrame(40,0,160,0.07)
    frame.GetXaxis().SetTitle("M_{J} (GeV)")
    frame.GetYaxis().SetTitle("a.u")
    hN.Draw("HIST,SAME")
    hU.Draw("HIST,SAME")
    hD.Draw("HIST,SAME")
    cmslabel_sim(c,period,12)

#    cmslabel_sim(canvas,period,12)
    c.Update()
    c.SaveAs(directory+"/"+sample+"_"+syst+tag+".png")
    c.SaveAs(directory+"/"+sample+"_"+syst+tag+".root")
    c.SaveAs(directory+"/"+sample+"_"+syst+tag+".pdf")


def makeShapeUncertaintiesMVV(filename,sample,tag,syst):
    #MJJ
    f=ROOT.TFile(filename)
    hN = f.Get("histo").ProjectionX("nominal")
    hU = f.Get("histo_"+syst+"_"+sample+"_"+tag+"Up").ProjectionX("up")
    hD = f.Get("histo_"+syst+"_"+sample+"_"+tag+"Down").ProjectionX("down")
    hN.SetLineColor(ROOT.kBlack)
    hN.SetLineStyle(1)
    hN.SetLineWidth(2)
    hU.SetLineColor(ROOT.kBlack)
    hU.SetLineStyle(3)
    hU.SetLineWidth(2)

    hD.SetLineColor(ROOT.kBlack)
    hD.SetLineStyle(4)
    hD.SetLineWidth(2)

    c=ROOT.TCanvas("c")
    c.cd()
    frame=c.DrawFrame(600,0,4800,0.07)
    frame.GetXaxis().SetTitle("M_{VV} (GeV)")
    frame.GetYaxis().SetTitle("a.u")
    hN.Draw("HIST,SAME")
    hU.Draw("HIST,SAME")
    hD.Draw("HIST,SAME")
    cmslabel_sim(c,period,12)

#    cmslabel_sim(canvas,period,12)
    c.Update()
    c.SaveAs(directory+"/"+sample+"_"+syst+tag+".png")
    c.SaveAs(directory+"/"+sample+"_"+syst+tag+".root")
    c.SaveAs(directory+"/"+sample+"_"+syst+tag+".pdf")


def makeShapeUncertainties2D(filename,sample,syst):
    #MJJ
    f=ROOT.TFile(filename)
    hN = f.Get("histo")
    hU = f.Get("histo_"+syst+"Up")
    hD = f.Get("histo_"+syst+"Down")
    hU.Divide(hN)
    hD.Divide(hN)


    c=ROOT.TCanvas("c")
    c.cd()
    hU.Draw("COL")
    c.SaveAs(directory+"/"+sample+"_"+syst+"Up.root")
    c.SaveAs(directory+"/"+sample+"_"+syst+"Up.pdf")
    c.SaveAs(directory+"/"+sample+"_"+syst+"Up.jpg")

    c=ROOT.TCanvas("c")
    c.cd()
    hD.Draw("COL")
    c.SaveAs(directory+"/"+sample+"_"+syst+"Down.root")
    c.SaveAs(directory+"/"+sample+"_"+syst+"Down.pdf")
    c.SaveAs(directory+"/"+sample+"_"+syst+"Down.jpg")


def makeShapeUncertaintiesProj2D(filename,sample,syst):
    #MJJ
    f=ROOT.TFile(filename)
    hN = f.Get("histo")
    hU = f.Get("histo_"+syst+"Up")
    hD = f.Get("histo_"+syst+"Down")

    
    c=ROOT.TCanvas("c")
    c.cd()
    hN.ProjectionX("a").DrawNormalized("HIST")
    hN.GetYaxis().SetRangeUser(1e-5,1000)
    hU.ProjectionX("b").DrawNormalized("HIST,SAME")
    hD.ProjectionX("c").DrawNormalized("HIST,SAME")
    c.SetLogy()
    c.SaveAs(directory+"/"+sample+"_"+syst+"ProjX.root")
    c.SaveAs(directory+"/"+sample+"_"+syst+"ProjX.pdf")
    c.SaveAs(directory+"/"+sample+"_"+syst+"ProjX.jpg")

    c2=ROOT.TCanvas("c2")
    c2.cd()
    hN.ProjectionY("e").DrawNormalized("HIST")
    hN.GetYaxis().SetRangeUser(0,1)
    hU.ProjectionY("f").DrawNormalized("HIST,SAME")
    hD.ProjectionY("g").DrawNormalized("HIST,SAME")
    c2.SaveAs(directory+"/"+sample+"_"+syst+"ProjY.root")
    c2.SaveAs(directory+"/"+sample+"_"+syst+"ProjY.pdf")
    c2.SaveAs(directory+"/"+sample+"_"+syst+"ProjY.jpg")


    


def makeTemplates2D(filename,sample,tag):
    #MJJ
    f=ROOT.TFile(filename)
    hN = f.Get("histo")
    c=ROOT.TCanvas("c")
    c.cd()
    hN.Draw("COL")
    hN.GetXaxis().SetTitle("M_{VV} (GeV)")
    hN.GetYaxis().SetTitle("m_{j} (GeV)")
    c.SetLogz()
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    c.Update()
    
    c.SaveAs(directory+"/"+sample+"_"+tag+".root")
    c.SaveAs(directory+"/"+sample+"_"+tag+".pdf")
    c.SaveAs(directory+"/"+sample+"_"+tag+".jpg")



    
def makeTemplates1D(filename,sample,tag):
    #MJJ
    f=ROOT.TFile(filename)
    hN = f.Get("histo")
    c=ROOT.TCanvas("c")
    c.cd()
    hN.Draw("HIST")
    hN.GetXaxis().SetTitle("M_{VV} (GeV)")
    c.SetLogy()
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    c.Update()
    c.SaveAs(directory+"/"+sample+"_"+tag+".root")
    c.SaveAs(directory+"/"+sample+"_"+tag+".pdf")
    
    
    


def makeSignalMJJParam(fileW,fileZ,purity='HP'):
    FW=ROOT.TFile(fileW)
    FZ=ROOT.TFile(fileZ)


    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(800,70,4500,100)
    frame.GetXaxis().SetTitle("M_{X} (GeV)")
    frame.GetYaxis().SetTitle("#mu (GeV)")

    g1=FW.Get("mean")
    g1.SetName("mean1")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    func1=FW.Get("mean_func")
    func1.SetLineColor(ROOT.kRed)
    func1.Draw("lsame")


    g2=FZ.Get("mean")
    g2.SetName("mean2")
    g2.SetMarkerColor(ROOT.kBlue)
    g2.SetMarkerStyle(21)
    g2.SetMarkerSize(0.8)
    g2.SetLineColor(ROOT.kBlue)
    g2.Draw("Psame")
    func2=FZ.Get("mean_func")
    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("lsame")

    l=ROOT.TLegend(0.6,0.7,0.9,0.8)
    l.AddEntry(g1,"X #rightarrow WW","p")
    l.AddEntry(g2,"X #rightarrow WZ","p")

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"MJJParam_mean.png")
    c.SaveAs(directory+"/"+purity+"MJJParam_mean.pdf")
    c.SaveAs(directory+"/"+purity+"MJJParam_mean.root")

    


    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(800,0,4500,18)
    frame.GetXaxis().SetTitle("M_{X} (GeV)")
    frame.GetYaxis().SetTitle("#sigma (GeV)")

    g1=FW.Get("sigma")
    g1.SetName("sigma1")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    func1=FW.Get("sigma_func")
    func1.SetLineColor(ROOT.kRed)
    func1.Draw("lsame")

    g2=FZ.Get("sigma")
    g2.SetName("sigma2")
    g2.SetMarkerColor(ROOT.kBlue)
    g2.SetMarkerStyle(21)
    g2.SetMarkerSize(0.8)
    g2.SetLineColor(ROOT.kBlue)
    g2.Draw("Psame")
    func2=FZ.Get("sigma_func")
    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("lsame")


    l=ROOT.TLegend(0.6,0.7,0.9,0.8)
    l.AddEntry(g1,"X #rightarrow WW","p")
    l.AddEntry(g2,"X #rightarrow WZ","p")

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"MJJParam_sigma.png")
    c.SaveAs(directory+"/"+purity+"MJJParam_sigma.pdf")
    c.SaveAs(directory+"/"+purity+"MJJParam_sigma.root")




    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(800,0,4500,3)
    frame.GetXaxis().SetTitle("M_{X} (GeV)")
    frame.GetYaxis().SetTitle("#alpha")

    g1=FW.Get("alpha")
    g1.SetName("alpha1")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    func1=FW.Get("alpha_func")
    func1.SetLineColor(ROOT.kRed)
    func1.Draw("lsame")

    g2=FZ.Get("alpha")
    g2.SetName("alpha2")
    g2.SetMarkerColor(ROOT.kBlue)
    g2.SetMarkerStyle(21)
    g2.SetMarkerSize(0.8)
    g2.SetLineColor(ROOT.kBlue)
    g2.Draw("Psame")
    func2=FZ.Get("alpha_func")
    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("lsame")


    l=ROOT.TLegend(0.6,0.7,0.9,0.8)
    l.AddEntry(g1,"X #rightarrow WW","p")
    l.AddEntry(g2,"X #rightarrow WZ","p")

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"MJJParam_alpha.png")
    c.SaveAs(directory+"/"+purity+"MJJParam_alpha.pdf")
    c.SaveAs(directory+"/"+purity+"MJJParam_alpha.root")



    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(800,0,4500,3)
    frame.GetXaxis().SetTitle("M_{X} (GeV)")
    frame.GetYaxis().SetTitle("#alpha2")

    g1=FW.Get("alpha2")
    g1.SetName("alpha1")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    func1=FW.Get("alpha2_func")
    func1.SetLineColor(ROOT.kRed)
    func1.Draw("lsame")

    g2=FZ.Get("alpha2")
    g2.SetName("alpha2")
    g2.SetMarkerColor(ROOT.kBlue)
    g2.SetMarkerStyle(21)
    g2.SetMarkerSize(0.8)
    g2.SetLineColor(ROOT.kBlue)
    g2.Draw("Psame")
    func2=FZ.Get("alpha2_func")
    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("lsame")


    l=ROOT.TLegend(0.4,0.8,0.7,0.9)
    l.AddEntry(g1,"X #rightarrow WW","p")
    l.AddEntry(g2,"X #rightarrow WZ","p")

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"MJJParam_alpha2.png")
    c.SaveAs(directory+"/"+purity+"MJJParam_alpha2.pdf")
    c.SaveAs(directory+"/"+purity+"MJJParam_alpha2.root")

    if purity=="HP":
        return

    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(800,-0.1,4500,0.05)
    frame.GetXaxis().SetTitle("M_{X} (GeV)")
    frame.GetYaxis().SetTitle("slope")

    g1=FW.Get("slope")
    g1.SetName("slope")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    func1=FW.Get("slope_func")
    func1.SetLineColor(ROOT.kRed)
    func1.Draw("lsame")

    g2=FZ.Get("slope")
    g2.SetName("slope2")
    g2.SetMarkerColor(ROOT.kBlue)
    g2.SetMarkerStyle(21)
    g2.SetMarkerSize(0.8)
    g2.SetLineColor(ROOT.kBlue)
    g2.Draw("Psame")
    func2=FZ.Get("slope_func")
    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("lsame")


    l=ROOT.TLegend(0.6,0.7,0.9,0.8)
    l.AddEntry(g1,"X #rightarrow WW","p")
    l.AddEntry(g2,"X #rightarrow WZ","p")

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"MJJParam_slope.png")
    c.SaveAs(directory+"/"+purity+"MJJParam_slope.pdf")
    c.SaveAs(directory+"/"+purity+"MJJParam_slope.root")


    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(800,0,4500,1.5)
    frame.GetXaxis().SetTitle("M_{X} (GeV)")
    frame.GetYaxis().SetTitle("f")

    g1=FW.Get("f")
    g1.SetName("f")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    func1=FW.Get("f_func")
    func1.SetLineColor(ROOT.kRed)
    func1.Draw("lsame")

    g2=FZ.Get("f")
    g2.SetName("f2")
    g2.SetMarkerColor(ROOT.kBlue)
    g2.SetMarkerStyle(21)
    g2.SetMarkerSize(0.8)
    g2.SetLineColor(ROOT.kBlue)
    g2.Draw("Psame")
    func2=FZ.Get("f_func")
    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("lsame")


    l=ROOT.TLegend(0.6,0.7,0.9,0.8)
    l.AddEntry(g1,"X #rightarrow WW","p")
    l.AddEntry(g2,"X #rightarrow WZ","p")

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"MJJParam_f.png")
    c.SaveAs(directory+"/"+purity+"MJJParam_f.pdf")
    c.SaveAs(directory+"/"+purity+"MJJParam_f.root")





def makeSignalMVVParam(fileW,fileZ,purity='mu'):
    FW=ROOT.TFile(fileW)
    FZ=ROOT.TFile(fileZ)


    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(700,700,4500,4500)
    frame.GetXaxis().SetTitle("M_{X} (GeV)")
    frame.GetYaxis().SetTitle("#mu (GeV)")

    g1=FW.Get("MEAN")
    g1.SetName("mean1")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    func1=FW.Get("MEAN_func")
    func1.SetLineColor(ROOT.kRed)
    func1.Draw("lsame")


    g2=FZ.Get("MEAN")
    g2.SetName("mean2")
    g2.SetMarkerColor(ROOT.kBlue)
    g2.SetMarkerStyle(21)
    g2.SetMarkerSize(0.8)
    g2.SetLineColor(ROOT.kBlue)
    g2.Draw("Psame")
    func2=FZ.Get("MEAN_func")
    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("lsame")

    l=ROOT.TLegend(0.6,0.7,0.9,0.8)
    l.AddEntry(g1,"X #rightarrow WW","p")
    l.AddEntry(g2,"X #rightarrow WZ","p")

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"MVVParam_mean.png")
    c.SaveAs(directory+"/"+purity+"MVVParam_mean.pdf")
    c.SaveAs(directory+"/"+purity+"MVVParam_mean.root")

    

    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(700,0,4500,400)
    frame.GetXaxis().SetTitle("M_{X} (GeV)")
    frame.GetYaxis().SetTitle("#sigma (GeV)")

    g1=FW.Get("SIGMA")
    g1.SetName("sigma1")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    func1=FW.Get("SIGMA_func")
    func1.SetLineColor(ROOT.kRed)
    func1.Draw("lsame")

    g2=FZ.Get("SIGMA")
    g2.SetName("sigma2")
    g2.SetMarkerColor(ROOT.kBlue)
    g2.SetMarkerStyle(21)
    g2.SetMarkerSize(0.8)
    g2.SetLineColor(ROOT.kBlue)
    g2.Draw("Psame")
    func2=FZ.Get("SIGMA_func")
    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("lsame")


    l=ROOT.TLegend(0.6,0.7,0.9,0.8)
    l.AddEntry(g1,"X #rightarrow WW","p")
    l.AddEntry(g2,"X #rightarrow WZ","p")

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"MVVParam_SIGMA.png")
    c.SaveAs(directory+"/"+purity+"MVVParam_SIGMA.pdf")
    c.SaveAs(directory+"/"+purity+"MVVParam_sigma.root")




    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(700,0,4500,3)
    frame.GetXaxis().SetTitle("M_{X} (GeV)")
    frame.GetYaxis().SetTitle("#alpha")

    g1=FW.Get("ALPHA1")
    g1.SetName("alpha1")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    func1=FW.Get("ALPHA1_func")
    func1.SetLineColor(ROOT.kRed)
    func1.Draw("lsame")

    g2=FZ.Get("ALPHA1")
    g2.SetName("alpha2")
    g2.SetMarkerColor(ROOT.kBlue)
    g2.SetMarkerStyle(21)
    g2.SetMarkerSize(0.8)
    g2.SetLineColor(ROOT.kBlue)
    g2.Draw("Psame")
    func2=FZ.Get("ALPHA1_func")
    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("lsame")


    l=ROOT.TLegend(0.6,0.7,0.9,0.8)
    l.AddEntry(g1,"X #rightarrow WW","p")
    l.AddEntry(g2,"X #rightarrow WZ","p")

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"MVVParam_alpha.png")
    c.SaveAs(directory+"/"+purity+"MVVParam_alpha.pdf")
    c.SaveAs(directory+"/"+purity+"MVVParam_alpha.root")



    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(800,0,4500,3)
    frame.GetXaxis().SetTitle("M_{X} (GeV)")
    frame.GetYaxis().SetTitle("#alpha2")

    g1=FW.Get("ALPHA2")
    g1.SetName("alpha1")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    func1=FW.Get("ALPHA2_func")
    func1.SetLineColor(ROOT.kRed)
    func1.Draw("lsame")

    g2=FZ.Get("ALPHA2")
    g2.SetName("alpha2")
    g2.SetMarkerColor(ROOT.kBlue)
    g2.SetMarkerStyle(21)
    g2.SetMarkerSize(0.8)
    g2.SetLineColor(ROOT.kBlue)
    g2.Draw("Psame")
    func2=FZ.Get("ALPHA2_func")
    func2.SetLineColor(ROOT.kBlue)
    func2.Draw("lsame")


    l=ROOT.TLegend(0.4,0.8,0.7,0.9)
    l.AddEntry(g1,"X #rightarrow WW","p")
    l.AddEntry(g2,"X #rightarrow WZ","p")

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"MVVParam_alpha2.png")
    c.SaveAs(directory+"/"+purity+"MVVParam_alpha2.pdf")
    c.SaveAs(directory+"/"+purity+"MVVParam_alpha2.root")

    if purity=="HP":
        return





def makeTopMJJParam(fileW,purity='HP'):
    FW=ROOT.TFile(fileW)
    ROOT.gStyle.SetOptFit(0)

    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(600,60,3500,120)
    frame.GetXaxis().SetTitle("M_{VV} (GeV)")
    frame.GetYaxis().SetTitle("#mu (GeV)")

    g1=FW.Get("mean")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")

    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"topMJJParam_mean.pdf")
    c.SaveAs(directory+"/"+purity+"topMJJParam_mean.root")



    c=ROOT.TCanvas("c")
    frame=c.DrawFrame(600,0,3500,40)
    frame.GetXaxis().SetTitle("M_{VV} (GeV)")
    frame.GetYaxis().SetTitle("#sigma (GeV)")

    g1=FW.Get("sigma")
    g1.SetMarkerColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.8)
    g1.SetLineColor(ROOT.kRed)
    g1.Draw("Psame")
    cmslabel_sim(c,period,11)
    c.SaveAs(directory+"/"+purity+"topMJJParam_sigma.pdf")
    c.SaveAs(directory+"/"+purity+"topMJJParam_sigma.root")



def makeBackgroundMVVParamPlot(datacard,pdf,var='MLNuJ',nametag='Wjets'):
    ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
    F=ROOT.TFile(datacard)
    w=F.Get('w')
    frame=w.var(var).frame()
    masses={40:ROOT.kRed, 60:ROOT.kBlue, 80:ROOT.kMagenta, 100:ROOT.kOrange, 120:ROOT.kTeal, 140: ROOT.kBlack}

    l=ROOT.TLegend(0.6,0.4,0.8,0.9)
    for mass,color in sorted(masses.iteritems()):
        w.var("MJ").setVal(mass)
        w.pdf(pdf).plotOn(frame,ROOT.RooFit.LineColor(color),ROOT.RooFit.Name("curve_"+str(mass)))
        curve=frame.getCurve("curve_"+str(mass))
        l.AddEntry(curve,"M_{J} = "+str(mass)+" GeV","l")
      

    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)

    frame.GetXaxis().SetTitle("M_{VV} (GeV)")
    frame.GetYaxis().SetTitle("a.u")
    frame.GetYaxis().SetTitleOffset(1.35)
    canvas=ROOT.TCanvas("c")
    canvas.cd()    
    frame.Draw()
    cmslabel_sim(canvas,period,11)
    canvas.Update()
    l.Draw()
    canvas.SaveAs(directory+"/"+nametag+"MVVParam.png")
    canvas.SaveAs(directory+"/"+nametag+"MVVParam.pdf")
    canvas.SaveAs(directory+"/"+nametag+"MVVParam.root")
    


def makeGOF(filename,val):
    f=ROOT.TFile(filename)
    t=f.Get("limit")
    c=ROOT.TCanvas("c","c")
    c.cd()
    t.Draw("limit>>h")
    h=ROOT.gDirectory.Get("h")
    h.SetLineWidth(2)
    h.SetLineColor(ROOT.kBlack)
    h.SetFillColor(ROOT.kOrange+1)
    h.Draw()
    l=ROOT.TArrow(val,0.8*h.GetMaximum(),val,0)
    l.Draw()
    h.GetXaxis().SetTitle("G.O.F. estimator")
    h.GetYaxis().SetTitle("toys")
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    c.Update()
    c.SaveAs("GOF.root")
    




def makeTopVsVJetsMJJ(filename):
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    f=ROOT.TFile(filename)
    nominal=f.Get("histo")
    topUp=f.Get("histo_TOPUp")
    topDown=f.Get("histo_TOPDown")

    scaleUp=f.Get("histo_ScaleUp")
    scaleDown=f.Get("histo_ScaleDown")
    c=ROOT.TCanvas("c")
    c.cd()
    nominal.SetLineWidth(2)
    topUp.SetLineWidth(2)
    topUp.SetLineColor(ROOT.kRed)
    topDown.SetLineWidth(2)
    topDown.SetLineColor(ROOT.kRed)

    scaleUp.SetLineWidth(2)
    scaleUp.SetLineColor(ROOT.kMagenta)
    scaleDown.SetLineWidth(2)
    scaleDown.SetLineColor(ROOT.kMagenta)

    scaleDown.DrawNormalized("HIST")
    scaleDown.GetXaxis().SetTitle("m_{J} (GeV)")
    scaleDown.GetYaxis().SetTitle("a.u")
    c.Update()
    nominal.DrawNormalized("HIST,SAME")
    topUp.DrawNormalized("HIST,SAME")
    topDown.DrawNormalized("HIST,SAME")
    scaleUp.DrawNormalized("HIST,SAME")
    c.Update()
    l=ROOT.TLegend(0.6,0.7,0.9,0.8)
    l.AddEntry(nominal,"nominal","l")
    l.AddEntry(topUp,"top non res */ 2","l")
    l.AddEntry(scaleUp,"scale #pm 3 #sigma","l")
    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    c.SaveAs("plots16/topVSVJets_MJJ.root")



def makeTopVsVJetsMVV(filename):
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    f=ROOT.TFile(filename)
    nominal=f.Get("histo").ProjectionX("nominal")
    topUp=f.Get("histo_TOPUp").ProjectionX("tUp")
    topDown=f.Get("histo_TOPDown").ProjectionX("tDown")

    scaleUp=f.Get("histo_ScaleUp").ProjectionX("scUp")
    scaleDown=f.Get("histo_ScaleDown").ProjectionX("scDown")
    c=ROOT.TCanvas("c")
    c.cd()
    nominal.SetLineWidth(2)
    topUp.SetLineWidth(2)
    topUp.SetLineColor(ROOT.kRed)
    topDown.SetLineWidth(2)
    topDown.SetLineColor(ROOT.kRed)

    scaleUp.SetLineWidth(2)
    scaleUp.SetLineColor(ROOT.kMagenta)
    scaleDown.SetLineWidth(2)
    scaleDown.SetLineColor(ROOT.kMagenta)

    scaleDown.DrawNormalized("HIST")
    scaleDown.GetXaxis().SetTitle("m_{J} (GeV)")
    scaleDown.GetYaxis().SetTitle("a.u")
    c.Update()
    nominal.DrawNormalized("HIST,SAME")
    topUp.DrawNormalized("HIST,SAME")
    topDown.DrawNormalized("HIST,SAME")
    scaleUp.DrawNormalized("HIST,SAME")
    c.Update()
    l=ROOT.TLegend(0.6,0.7,0.9,0.8)
    l.AddEntry(nominal,"nominal","l")
    l.AddEntry(topUp,"top non res */ 2","l")
    l.AddEntry(scaleUp,"scale #pm 3 #sigma","l")
    l.SetBorderSize(0)
    l.SetFillColor(ROOT.kWhite)
    l.Draw()

    c.SaveAs("plots16/topVSVJets_MVV.root")
    


def makePostFit(card,MH,slices,bkgOnly=True,cut=''):
    ROOT.gSystem.Load('libHiggsAnalysisCombinedLimit')
    plotter=RooPlotter(card)    
    plotter.fix("MH",MH)
    if bkgOnly:
        plotter.fix("r",0.0)
    else:
        plotter.addContribution("XWW",True,"X #rightarrow WW",3,1,ROOT.kOrange+10,0,ROOT.kWhite)
    plotter.prefit()


    plotter.addContribution("topRes",False," t#bar{t} (W)",2,1,ROOT.kBlack,1001,ROOT.kTeal-1)
    plotter.addContribution("WW",False,"SM WW",2,1,ROOT.kBlack,1001,ROOT.kOrange)
    plotter.addContribution("WZ",False,"SM WZ",2,1,ROOT.kBlack,1001,ROOT.kOrange+10)
    plotter.addContribution("Wjets",False,"V+jets",2,1,ROOT.kBlack-3,1001,ROOT.kAzure-9,"_opt")
    plotter.addContribution("topNonRes",False,"t#bar{t} (other)",2,1,ROOT.kBlack,1001,ROOT.kSpring-5,"_opt")

    for s in slices:
        if s.find('nob')!=-1:
            blind=1
        else:
            blind=0
        plotter.drawStack("MJ","M_{j} (GeV)",s,cut,blind)
        cmslabel_prelim(plotter.canvas,period,11)
        plotter.canvas.SaveAs(directory+"/MJ_"+s+".png")
        plotter.canvas.SaveAs(directory+"/MJ_"+s+".pdf")
        plotter.canvas.SaveAs(directory+"/MJ_"+s+".root")
        plotter.drawStack("MLNuJ","M_{VV} (GeV)",s,cut,blind,1)
        cmslabel_prelim(plotter.canvas,period,11)
        plotter.canvas.SaveAs(directory+"/MVV_"+s+".png")
        plotter.canvas.SaveAs(directory+"/MVV_"+s+".pdf")
        plotter.canvas.SaveAs(directory+"/MVV_"+s+".root")


def compare2D_shapex(contrib,tag, bini,binj):
    f1=ROOT.TFile("LNuJJ_"+contrib+"_COND2D_"+tag+".root")
    f2=ROOT.TFile("LNuJJ_"+tag+".root")
    kernel=f1.Get("histo")
    mc=f2.Get(contrib)

    c=ROOT.TCanvas("c")
    c.cd()
    kernel.ProjectionX("aaa",bini,binj).DrawNormalized()
    mc.ProjectionX("bb",bini,binj).DrawNormalized("SAME")
    c.Update()



def compare1D(contrib,tag, var="MVV"):
    f1=ROOT.TFile("LNuJJ_"+contrib+"_"+var+"_"+tag+".root")
    f2=ROOT.TFile("LNuJJ_"+tag+".root")
    kernel=f1.Get("histo")
    mc=f2.Get(contrib)

    c=ROOT.TCanvas("c")
    c.cd()
    kernel.DrawNormalized("HIST")
    if var=="MVV":
        mc.ProjectionX("qq").DrawNormalized("SAME")
        c.SetLogy()    
    if var=="MJ":
        mc.ProjectionY("qq").DrawNormalized("SAME")

    c.Update()





def makeKernelScaleResolution(filename,histoname):
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    f=ROOT.TFile(filename)
    histo=f.Get(histoname)
    name=""
    if "scalex" in histoname:
        histo.GetYaxis().SetTitle("M_{VV} scale")
        name="background_scale_MVV.root"
    if "scaley" in histoname:
        histo.GetYaxis().SetTitle("m_{j} scale")
        name="background_scale_MJJ.root"

    if "resx" in histoname:
        histo.GetYaxis().SetTitle("M_{VV} resolution")
        name="background_resolution_MVV.root"

    if "resy" in histoname:
        histo.GetYaxis().SetTitle("m_{j} resolution")
        name="background_resolution_MJJ.root"

    histo.GetXaxis().SetTitle("gen jet p_{T} (GeV)")
    histo.SetLineWidth(2)
    c=ROOT.TCanvas("c")
    histo.Draw()
    cmslabel_sim(c,period,12)
    c.SaveAs(directory+"/"+name)
    c.SaveAs(directory+"/"+name.replace(".root",".pdf"))
    




#makeTrigger()
#makePileup()
#makeLeptonPlots()
#makeJetMass('pruned',1)
#makeTau21()
#makeWLPlots()
#makeVVPlots(1)

#makeSignalMVVParamPlot("LNUJJ_2016/combined.root","XWW_MVV_b_mu_HP_13TeV")

#getMJJParams('LNUJJ_2016/debugLNuJJ_MJJ_Wjets_HP.root','Wjets_MJJ_HP')
#getMJJParams('LNUJJ_2016/debugLNuJJ_MJJ_Wjets_LP.root','Wjets_MJJ_LP')

#makeSignalMJJParam('debug_LNuJJ_XWW_MJJ_HP.json.root','debug_LNuJJ_XWZ_MJJ_HP.json.root','HP')
#makeSignalMJJParam('debug_LNuJJ_XWW_MJJ_LP.json.root','debug_LNuJJ_XWZ_MJJ_LP.json.root','LP')

#makeSignalMVVParam('debug_LNuJJ_XWW_MVV_mu.json.root','debug_LNuJJ_XWZ_MVV_mu.json.root','HP')
#makeSignalMVVParam('debug_LNuJJ_XWW_MVV_e.json.root','debug_LNuJJ_XWZ_MVV_e.json.root','LP')


#makeTopMJJParam("LNUJJ_2016/LNuJJ_MJJ_topRes_HP.root",'HP')
#makeTopMJJParam("LNUJJ_2016/LNuJJ_MJJ_topRes_LP.root",'LP')


#makeBackgroundMVVParamPlot("LNUJJ_2016/combinedSlow.root","Wjets_MVV_nob_mu_HP_13TeV",'MLNuJ','Wjets_mu_')
#makeBackgroundMVVParamPlot("LNUJJ_2016/combinedSlow.root","Wjets_MVV_nob_e_HP_13TeV",'MLNuJ','Wjets_e_')
#makePostFit("LNUJJ_2016/combined.root",2000,['nob_mu_HP_13TeV','nob_mu_LP_13TeV','nob_e_HP_13TeV','nob_e_LP_13TeV','b_mu_HP_13TeV','b_mu_LP_13TeV','b_e_HP_13TeV','b_e_LP_13TeV'],1)



#makeShapeUncertaintiesMJJ("LNUJJ_2016/LNuJJ_MVVHist_Wjets_mu_HP.root","Wjets","HP","slopeSystMJJ")
#makeShapeUncertaintiesMJJ("LNUJJ_2016/LNuJJ_MVVHist_Wjets_mu_HP.root","Wjets","HP","meanSystMJJ")
#makeShapeUncertaintiesMJJ("LNUJJ_2016/LNuJJ_MVVHist_Wjets_mu_HP.root","Wjets","HP","widthSystMJJ")

#makeShapeUncertaintiesMJJ("LNUJJ_2016/LNuJJ_MVVHist_Wjets_mu_LP.root","Wjets","LP","slopeSystMJJ")
#makeShapeUncertaintiesMJJ("LNUJJ_2016/LNuJJ_MVVHist_Wjets_mu_LP.root","Wjets","LP","meanSystMJJ")
#makeShapeUncertaintiesMJJ("LNUJJ_2016/LNuJJ_MVVHist_Wjets_mu_LP.root","Wjets","LP","widthSystMJJ")


#makeShapeUncertaintiesMVV("LNUJJ_2016/LNuJJ_MVVHist_Wjets_mu_HP.root","Wjets","mu","slopeSyst")
#makeShapeUncertaintiesMVV("LNUJJ_2016/LNuJJ_MVVHist_Wjets_mu_HP.root","Wjets","mu","meanSyst0")
#makeShapeUncertaintiesMVV("LNUJJ_2016/LNuJJ_MVVHist_Wjets_mu_HP.root","Wjets","mu","widthSyst")


for c in ['nob','vbf']:
    if c=='vbf':
        pur=['NP']
    else:
        pur=['HP','LP']
    for p in pur:
        for l in ['mu','e']:
#            makeTemplates2D("LNuJJ_nonRes_2D_"+l+"_"+p+"_"+c+".root","template_nonRes",l+"_"+p+"_"+c)
#            makeTemplates1D("LNuJJ_resW_MVV_"+l+"_"+p+"_"+c+".root","template_resW",l+"_"+p+"_"+c)
            makeShapeUncertaintiesProj2D("LNuJJ_nonRes_2D_"+l+"_"+p+"_"+c+".root","systs_nonRes_"+l+"_"+p+"_"+c,"ScaleX")
            makeShapeUncertaintiesProj2D("LNuJJ_nonRes_2D_"+l+"_"+p+"_"+c+".root","systs_nonRes_"+l+"_"+p+"_"+c,"ScaleY")
            makeShapeUncertaintiesProj2D("LNuJJ_nonRes_2D_"+l+"_"+p+"_"+c+".root","systs_nonRes_"+l+"_"+p+"_"+c,"PTX")
            makeShapeUncertaintiesProj2D("LNuJJ_nonRes_2D_"+l+"_"+p+"_"+c+".root","systs_nonRes_"+l+"_"+p+"_"+c,"PTY")
            continue;



#makeTopMJJParam('LNuJJ_MJJ_resW_HP.root','HP')
#makeTopMJJParam('LNuJJ_MJJ_resW_LP.root','LP')
#makeTopMJJParam('LNuJJ_MJJ_resW_NP.root','NP')
            
#makeGOF("GOFToys.root",9534.22)



#makeTopVsVJetsMJJ("LNuJJ_nonRes_MJJ_mu_HP_nob.root")
#makeTopVsVJetsMVV("LNuJJ_nonRes_COND2D_mu_HP_nob.root")


#makeKernelScaleResolution("LNuJJ_nonRes_detectorResponse.root","scalexHisto")
#makeKernelScaleResolution("LNuJJ_nonRes_detectorResponse.root","scaleyHisto")

#makeKernelScaleResolution("LNuJJ_nonRes_detectorResponse.root","resxHisto")
#makeKernelScaleResolution("LNuJJ_nonRes_detectorResponse.root","resyHisto")
