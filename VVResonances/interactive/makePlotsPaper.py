import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, re, optparse,pickle,shutil,json
import time
from array import array
import math
import CMS_lumi
import numpy as np
from tools import PostFitTools
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gROOT.ProcessLine(".x tdrstyle.cc");


#python makePlotsPaper.py -i DIR_WITH_BG_POSTFITS -p "z" -n "PullsPaper" 
# for the dir names where signal prefits should be stored look below, or change accordingly

# NB: Before running this plotting script, one should run and store in different directories both prefit with signal (needed for signal) and posfits bg only!
# first plot:
# run b only on 65-105 for both jets - only ggF/DY categories
# for signal use: makeDataPreFitsBGZZ.sh & run for BGWW also!
# second plot:
# run b only fit on 65-105 & 110-140 with the option (--both)  of adding distributions: makeDataFitsVorH.sh 
# and for signal prefit use makeDataFitsVorHsignal.sh (two options inside)
# third plot:
# run on VBF categories only, use makeDataFitsVH.sh for b only fit 
# and makeDataFitsVHsignal.sh for signals prefit

parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output folder name",default='')
parser.add_option("-n","--name",dest="name",help="ouptut name",default='PullsPaper')
parser.add_option("-i","--input",dest="input",help="Input directory",default='postfits_Zprojections_paper/')
parser.add_option("-I","--secondinput",dest="secondinput",help="Input directory of the second file",default='postfit_data_blindSR__Run2/')
parser.add_option("-x","--xrange",dest="xrange",help="set range for x bins in projection",default="0,-1")
parser.add_option("-y","--yrange",dest="yrange",help="set range for y bins in projection",default="0,-1")
parser.add_option("-z","--zrange",dest="zrange",help="set range for z bins in projection",default="0,-1")
parser.add_option("-p","--projection",dest="projection",help="choose which projection should be done",default="z")
parser.add_option("-d","--data",dest="data",action="store_true",help="make also postfit plots",default=True)
parser.add_option("-l","--label",dest="label",help="add extra label such as pythia or herwig",default="")
parser.add_option("--log",dest="log",help="write fit result to log file",default="fit_results.log")
parser.add_option("--blind",dest="blind",action="store_true",help="Use to blind data in control region",default=False)
parser.add_option("--pdfz",dest="pdfz",help="name of pdfs lie PTZUp etc",default="")
parser.add_option("--pdfx",dest="pdfx",help="name of pdfs lie PTXUp etc",default="")
parser.add_option("--pdfy",dest="pdfy",help="name of pdfs lie PTYUp etc",default="")
parser.add_option("-t","--addTop",dest="addTop",action="store_true",help="Fit top",default=False)
parser.add_option("-M","--mass",dest="signalMass",type=float,help="signal mass",default=1560.)
parser.add_option("--signalScaleF",dest="signalScaleF",type=float,help="scale factor to apply to signal when drawing so its still visible!",default=500.)
parser.add_option("--prelim",dest="prelim",help="add preliminary label",default="Preliminary")
parser.add_option("--channel",dest="channel",help="which category to use? ",default="VV_HPHP")
parser.add_option("--slopes",dest="slopes",action="store_true",help="save ttbar slopes",default=False)
parser.add_option("--pseudo",dest="pseudo",action="store_true",help="write pseudodata in legend",default=False)

(options,args) = parser.parse_args()
ROOT.gStyle.SetOptStat(0)
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)

def addPullPlot(hdata,hpostfit,nBins,error_band):
    #print "make pull plots: (data-fit)/sigma_data"                                                                                                                                  
    N = hdata.GetNbinsX()
    gpost = ROOT.TGraphErrors(0)
    gt = ROOT.TH1F("gt","gt",len(nBins)-1,nBins)
    for i in range(1,N+1):
        m = hdata.GetXaxis().GetBinCenter(i)
        #ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/hdata.GetBinErrorUp(i)                                                                                      
        if hpostfit.GetBinContent(i) <= hdata.GetBinContent(i):
            if error_band !=0: ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ ROOT.TMath.Abs(hdata.GetBinErrorUp(i))
            else: ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ hdata.GetBinErrorUp(i)
        else:
            if error_band!=0: ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ ROOT.TMath.Sqrt(ROOT.TMath.Abs( pow(hdata.GetBinErrorUp(i),2) - pow(error_band.GetErrorYlow(i-1),2) ))
            else: ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ hdata.GetBinErrorUp(i)
            gpost.SetPoint(i-1,m,ypostfit)
            gt.SetBinContent(i,ypostfit)
            #print "bin",i,"x",m,"data",hdata.GetBinContent(i),"post fit",hpostfit.GetBinContent(i),"err data",hdata.GetBinErrorUp(i),"err fit",error_band.GetBinError(i),"pull postfit",ypostfit                                                                                                                                                                               
            #print "bin",i,"x",m,"data",hdata.GetBinContent(i),"post fit",hpostfit.GetBinContent(i),"err data",hdata.GetBinErrorUp(i),"err fit",error_band.GetErrorYhigh(i-1),"pull postfit",ypostfit                                                                                                                                                                           

    gpost.SetLineColor(colors[1])
    gpost.SetMarkerColor(colors[1])
    gpost.SetFillColor(ROOT.kGray+3)
    gpost.SetMarkerSize(1)
    gpost.SetMarkerStyle(20)
    gt.SetFillColor(ROOT.kGray+3)
    gt.SetLineColor(ROOT.kGray+3)
    gt.SetTitle("")
    #gt.SetMinimum(0.5);                                                                                                                                                             
    #gt.SetMaximum(1.5);                                                                                                                                                             
    gt.SetMinimum(-3.5);
    #gt.SetMaximum(3.5);                                                                                                                                                             
    gt.SetDirectory(0);
    gt.SetStats(0);
    gt.SetLineStyle(0);
    gt.SetMarkerStyle(20);
    gt.GetXaxis().SetTitle(hpostfit.GetXaxis().GetTitle());
    gt.GetXaxis().SetLabelFont(42);
    gt.GetXaxis().SetLabelOffset(0.02);
    gt.GetXaxis().SetLabelSize(0.17);
    gt.GetXaxis().SetTitleSize(0.15);
    gt.GetXaxis().SetTitleOffset(1.2);
    gt.GetXaxis().SetTitleFont(42);
    gt.GetYaxis().SetTitle("#frac{Data-fit}{#sigma}");
    gt.GetYaxis().CenterTitle(True);
    gt.GetYaxis().SetNdivisions(205);
    gt.GetYaxis().SetLabelFont(42);
    gt.GetYaxis().SetLabelOffset(0.007);
    gt.GetYaxis().SetLabelSize(0.15);
    gt.GetYaxis().SetTitleSize(0.15);
    gt.GetYaxis().SetTitleOffset(0.4);
    gt.GetYaxis().SetTitleFont(42);
    gt.GetXaxis().SetNdivisions(505)
    #gpre.SetHistogram(gt);                                                                                                                                                          
    #gpost.SetHistogram(gt);                                                                                                                                                         
    return [gt]

def get_canvas(cname):
    
    #change the CMS_lumi variables (see CMS_lumi.py)                                                                                                                                 
    CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
    CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
    period = "Run2"
    if options.name.find("2017")!=-1: period = "2017"
    if options.name.find("2018")!=-1: period = "2018"
    if options.name.find("16+17")!=-1: period = "16+17"
    if options.name.find("2016")!=-1: period = "2016"
    if period =="2016":  CMS_lumi.lumi_13TeV = "36 fb^{-1}"
    if period =="2017":  CMS_lumi.lumi_13TeV = "43 fb^{-1}"
    if period =="2018":  CMS_lumi.lumi_13TeV = "60 fb^{-1}"
    if period =="16+17":  CMS_lumi.lumi_13TeV = "78 fb^{-1}"
    if period =="Run2":  CMS_lumi.lumi_13TeV = "138 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.lumi_sqrtS = "13 TeV (Run2)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
    CMS_lumi.extraText = options.prelim




    H_ref = 600
    W_ref = 600
    W = W_ref
    H  = H_ref
    
    iPeriod = 0
    
    # references for T, B, L, R                                                                                                                                                      
    T = 0.08*H_ref
    B = 0.12*H_ref
    L = 0.15*W_ref #0.12
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
    
    return canvas

def get_pad(name,ymin=0.3,ymax=1.):
    
    #change the CMS_lumi variables (see CMS_lumi.py)                                                                                                                                 
    CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
    CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
    period = "Run2"
    if options.name.find("2017")!=-1: period = "2017"
    if options.name.find("2018")!=-1: period = "2018"
    if options.name.find("16+17")!=-1: period = "16+17"
    if options.name.find("2016")!=-1: period = "2016"
    if period =="2016":  CMS_lumi.lumi_13TeV = "36 fb^{-1}"
    if period =="2017":  CMS_lumi.lumi_13TeV = "43 fb^{-1}"
    if period =="2018":  CMS_lumi.lumi_13TeV = "60 fb^{-1}"
    if period =="16+17":  CMS_lumi.lumi_13TeV = "78 fb^{-1}"
    if period =="Run2":  CMS_lumi.lumi_13TeV = "138 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.lumi_sqrtS = "13 TeV (Run2)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
    CMS_lumi.extraText = options.prelim
    
    CMS_lumi.lumiText = "(13 TeV)"
    iPos = 0
    CMS_lumi.relPosX=0.05
    if( iPos==0 ): CMS_lumi.relPosX = 0.014

    H_ref = 600
    W_ref = 600
    W = W_ref
    H  = H_ref
    
    iPeriod = 0
    iPeriod = 4
    
    pad = ROOT.TPad(name, name, 0, ymin, 1, ymax)
    pad.SetFillColor(0)
    pad.SetBorderMode(0)
    pad.SetFrameFillStyle(0)
    pad.SetFrameBorderMode(0)
    pad.SetTickx()
    pad.SetTicky()

    pad.SetBottomMargin(0.01)
    pad.SetTopMargin(0.1)

    return pad


def PrepareSignal(hist,scaling=1.):
    print hist.Integral()
    hist.Scale(1./scaling)
    print hist.Integral()
    return hist

def GetHist(infile,histname,scale=True):
    print " file opened "
    hist = infile.Get(histname)
    print " hist ",hist
    if histname != "syst_band" and histname !="syst_unc":
        hist.SetDirectory(0)
        if scale == True: hist = fromGeVtoTeV(hist)
    else:
        if scale == True: hist = fromGeVtoTeVGraph(hist)
    return hist


def fromGeVtoTeV(hist,scale=1000.):
    xaxis =  hist.GetXaxis()
    xbins = []
    xbins = xaxis.GetXbins()
    for i in range(xbins.GetSize()):
        xbins[i] = xbins[i]/scale
    xaxis.Set((xbins.GetSize() - 1), xbins.GetArray())
    return hist

def fromGeVtoTeVGraph(graph,scale=1000.):
    N =  graph.GetN()
    syst_band_scaled = ROOT.TGraphAsymmErrors()
    syst_band_scaled.Copy(graph)
    for i in range(N):
        X = ROOT.Double()
        Y = ROOT.Double()
        graph.GetPoint(i,X,Y)
        syst_band_scaled.SetPoint(i,X/scale,0)
        Y = graph.GetErrorYhigh(i)
        X = graph.GetErrorXhigh(i)
        syst_band_scaled.SetPointEYhigh(i,Y)
        syst_band_scaled.SetPointEXhigh(i,X/scale)
        Y = graph.GetErrorYlow(i)
        X = graph.GetErrorXlow(i)
        syst_band_scaled.SetPointEYlow(i,Y) 
        syst_band_scaled.SetPointEXlow(i,X/scale)


    return syst_band_scaled


def MakeSignalPulls(S,data,scaling=1.):
    final = ROOT.TH1F()
    S.Copy(final)
    for i in range(1,S.GetNbinsX()+1):
        lastbin =1.
        if data.GetBinContent(i) != 0:
            lastbin=data.GetBinContent(i)
        s = S.GetBinContent(i)
        err_data = ROOT.TMath.Sqrt(lastbin)
        pull = s / err_data
        final.SetBinContent(i,pull*scaling)
        #final.SetBinContent(i,s*scaling)

    return final

def Plot(categories,histos,axis,signal1=None,signal2=None):
    print histos
    extra1 = ''
    extra2 = ''
    htitle = ''
    xtitle = ''
    ymin = 0
    ymax = 0
    xrange = options.xrange
    yrange = options.yrange
    zrange = options.zrange
    if options.xrange == '0,-1': xrange = '55,215'
    if options.yrange == '0,-1': yrange = '55,215'
    if options.zrange == '0,-1': zrange = '1.246,7.6' #5500'                                                                                                                    
    xlow = xrange.split(',')[0]
    xhigh = xrange.split(',')[1]
    ylow = yrange.split(',')[0]
    yhigh = yrange.split(',')[1]
    if options.blind == True:
        if len(xrange.split(',')) == 4:
            xlow2 = xrange.split(',')[2]
            xhigh2 = xrange.split(',')[3]
        if len(yrange.split(',')) == 4:
            ylow2 = yrange.split(',')[2]
            yhigh2 = yrange.split(',')[3]

    if axis=='z':
        print "make Z projection"
        htitle = "Z-Proj. x : "+options.xrange+" y : "+options.yrange
        hhtitle = options.channel
        xtitle = "Dijet invariant mass [TeV]"
        ymin = 0.2
        ymax = histos[categories[0]]["Data"].GetMaximum()*5000
        extra1 = xrange.split(',')[0]+' < m_{jet1} < '+ xrange.split(',')[1]+' GeV'
        if options.blind == True and len(xrange.split(',')) == 4:
            extra1 = 'Blind '+xhigh+' < m_{jet1} < '+xlow2+' GeV'        #xlow+' < m_{jet1} < '+xhigh+' & '+xlow2+' < m_{jet1} < '+xhigh2+' GeV'                                     
            extra2 = yrange.split(',')[0]+' < m_{jet2} < '+ yrange.split(',')[1]+' GeV'
        if options.blind == True and len(yrange.split(',')) == 4:
            extra2 = 'Blind '+yhigh+' < m_{jet2} < '+ylow2+' GeV'  #extra2 = ylow+' < m_{jet2} < '+yhigh+' & '+ylow2+' < m_{jet2} < '+yhigh2+' GeV'                                  
    elif axis=='x':
        print "make X projection"
        htitle = "X-Proj. y : "+options.yrange+" z : "+options.zrange
        hhtitle = options.channel
        xtitle = " m_{jet1} [GeV]"
        ymin = 0.02
        ymax = histos[categories[0]]["Data"].GetMaximum()*2#max(hdata.GetMaximum()*1.3,maxY*1.3)                                                                              
        extra1 = yrange.split(',')[0]+' < m_{jet2} < '+ yrange.split(',')[1]+' GeV'
        if options.blind == True and len(yrange.split(',')) == 4:
            extra1 = 'Blind '+yhigh+' < m_{jet2} < '+ylow2+' GeV'  #extra1 = ylow+' < m_{jet2} < '+yhigh+' & '+ylow2+' < m_{jet2} < '+yhigh2+' GeV'                                  
            extra2 = zrange.split(',')[0]+' < m_{jj} < '+ zrange.split(',')[1]+' TeV'
    elif axis=='y':
        print "make Y projection"
        htitle = "Y-Proj. x : "+options.xrange+" z : "+options.zrange
        hhtitle = options.channel
        xtitle = " m_{jet2} [GeV]"
        ymin = 0.02
        ymax = histos[categories[0]]["Data"].GetMaximum()*2#max(hdata.GetMaximum()*1.3,maxY*1.3)                                                                                
        extra1 = xrange.split(',')[0]+' < m_{jet1} < '+ xrange.split(',')[1]+' GeV'
        if options.blind == True and len(xrange.split(',')) == 4:
            extra1 = 'Blind '+xhigh+' < m_{jet1} < '+xlow2+' GeV'  #extra1 = xlow+' < m_{jet1} < '+xhigh+' & '+xlow2+' < m_{jet1} < '+xhigh2+' GeV'                                  
            extra2 = zrange.split(',')[0]+' < m_{jj} < '+ zrange.split(',')[1]+' TeV'

    leg = ROOT.TLegend(0.6,0.6,0.88,0.9)
    leg.SetTextSize(0.04)
    c = get_canvas('c')
    #pad1 = get_pad("pad1") #ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)                                                                                                           
    if axis == 'z': c.SetLogy()
    histos[categories[0]]["Data"].SetLineColor(ROOT.kBlack)
    histos[categories[0]]["Data"].SetLineWidth(2)
    histos[categories[0]]["Data"].SetLineStyle(1)
    histos[categories[0]]["Data"].SetMarkerColor(ROOT.kBlack)
    histos[categories[0]]["Data"].SetMarkerStyle(20)
    leg.AddEntry(histos[categories[0]]["Data"],"Background Fit","l")
    leg.AddEntry(histos[categories[0]]["Data"],"Data","ep")

    #pad1.Draw()
    #pad1.cd()
    leg.SetLineColor(0)

    for cat in categories:
        for sample in histos[cat].keys():
            histos[cat][sample].SetMinimum(ymin)
            histos[cat][sample].SetMaximum(ymax)
            histos[cat][sample].SetTitle(hhtitle)
            histos[cat][sample].SetLineColor(colors[cat])
            histos[cat][sample].SetMarkerColor(colors[cat])
            histos[cat][sample].SetMarkerStyle(markers[cat])

            if "Data" in sample :
                histos[cat][sample].SetMarkerSize(0.7)
                histos[cat][sample].Draw("samePE0")
                #leg.AddEntry(histos[cat][sample],"Data "+cat.replace("_"," "),"ep")
            else:
                histos[cat][sample].SetLineWidth(2)
                histos[cat][sample].SetLineStyle(linestyles[cat])
                histos[cat][sample].Draw('HISTsame')

            histos[cat][sample].GetXaxis().SetTitle(xtitle)
            histos[cat][sample].GetYaxis().SetTitleOffset(1.5)
            binwidth = histos[cat][sample].GetXaxis().GetBinWidth(10)
            if axis == "z": binwidth = 100
            histos[cat][sample].GetYaxis().SetTitle("Events / "+str(binwidth)+" GeV")
            histos[cat][sample].GetYaxis().SetTitleSize(0.05)
            histos[cat][sample].GetYaxis().SetLabelSize(0.05)
            histos[cat][sample].GetXaxis().SetTitleSize(0.05)
            histos[cat][sample].GetXaxis().SetLabelSize(0.05)



            '''
            if errors!=None:
            errors[0].SetFillColor(colors[0])
            errors[0].SetFillStyle(3001)
            errors[0].SetLineColor(colors[0])
            errors[0].SetLineWidth(0)
            errors[0].SetMarkerSize(0)
            '''

            #change this scaling in case you don't just want to plot signal! has to match number of generated signal events
            scaling = options.signalScaleF
            eff = 0.1

            if signal1!= None: # and (options.name.find('sigonly')!=-1  and doFit==0):
                print "print do hsignal1 ", signal1.Integral()
                #if signal1.Integral()!=0.:
                #signal1.Scale(scaling/normsig.getVal())
                signal1.SetLineColor(ROOT.kGreen-6)
                signal1.SetLineStyle(1)
                signal1.Draw("HISTsame")
                leg.AddEntry(siganl1,"G_{bulk} (%i TeV) #rightarrow WW (#times %i)"%(options.signalMass/1000.,scaling) ,"F")

            if signal2!= None: # and (options.name.find('sigonly')!=-1  and doFit==0):
                print "print do hsignal2 ", signal2.Integral()
                #if signal2.Integral()!=0.:
                #signal2.Scale(scaling/normsig.getVal())
                signal2.SetLineColor(ROOT.kViolet)
                signal2.SetLineStyle(2)
                signal2.Draw("HISTsame")
                leg.AddEntry(siganl2,"Z' (%i TeV) #rightarrow ZH (#times %i)"%(options.signalMass/1000.,scaling) ,"F")

            '''     
            if errors!=None:
            if axis=="z":
            errors[0].Draw("2same")
            else:
            errors[0].Draw("3same")
            '''

            '''
            if errors!=None:
                leg.AddEntry(errors[0],"#pm 1#sigma unc.","f")
            
            if (options.signalMass%1000.)==0:
                text = "G_{bulk} (%i TeV) #rightarrow WW (#times %i)"%(options.signalMass/1000.,scaling)

            if signalName.find("ZprimeWW")!=-1:
                text = "Z' (%.1f TeV) #rightarrow WW (#times %i)"%(options.signalMass/1000.,scaling)
            if (options.signalMass%1000.)==0:
                text = "Z' (%i TeV) #rightarrow WW (#times %i)"%(options.signalMass/1000.,scaling)

            if signalName.find("ZprimeZH")!=-1:
                text = "Z' (%.1f TeV) #rightarrow ZH (#times %i)"%(options.signalMass/1000.,scaling)
            if (options.signalMass%1000.)==0:
                text = "Z' (%i TeV) #rightarrow ZH (#times %i)"%(options.signalMass/1000.,scaling)

            if signalName.find("WprimeWZ")!=-1:
            text = "W' (%.1f TeV) #rightarrow WZ (#times %i)"%(options.signalMass/1000.,scaling)
            if (options.signalMass%1000.)==0:
                text = "W' (%i TeV) #rightarrow WZ (#times %i)"%(options.signalMass/1000.,scaling)

            if signalName.find("WprimeWH")!=-1:
            text = "W' (%.1f TeV) #rightarrow WH (#times %i)"%(options.signalMass/1000.,scaling)
            if (options.signalMass%1000.)==0:
                text = "W' (%i TeV) #rightarrow WH (#times %i)"%(options.signalMass/1000.,scaling)
            '''
        #still in the category loop
        leg.AddEntry(histos[cat]["BackgroundFit"],cat.replace("_"," "),"epl")

    leg.Draw("same")

    #errors[0].Draw("E2same")                                                                                                                                                        
    print "projection "+extra1+"  "+extra2+" \n"

 
    pt3 = ROOT.TPaveText(0.18,0.55,0.39,0.68,"NDC")
    pt3.SetTextFont(42)
    pt3.SetTextSize(0.04)
    pt3.SetTextAlign(12)
    pt3.SetFillColor(0)
    pt3.SetBorderSize(0)
    pt3.SetFillStyle(0)
    pt3.AddText(extra1)
    pt3.AddText(extra2)
    pt3.Draw()
    
    CMS_lumi.CMS_lumi(c, 4, 10)
    
    #pad1.Modified()
    #pad1.Update()
    #c.Update()
    #c.cd()
    #pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
    #pad2.SetTopMargin(0.01)
    #pad2.SetBottomMargin(0.4)
    #pad2.SetGridy()                                                                                                                                                                 
    #pad2.Draw()
    #pad2.cd()
    
    #for ratio                                                                                                                                                                      
    #graphs = addRatioPlot(hdata,histos[cat][sample],nBins,errors[0])                                                                                                           
    #graphs[1].Draw("AP")                                                                                                                                                           
    #graphs[0].Draw("E3same")                                                                                                                                                       
    #graphs[1].Draw("Psame")                                                                                                                                                        

    #for pulls
    '''
    if errors ==None: errors=[0,0];
    if options.name.find('sigonly')!=-1: graphs = addPullPlot(hdata,hsig,nBins,errors[0])
    else:
    graphs = addPullPlot(hdata,histos[cat][sample],nBins,errors[0])
    # graphs = addRatioPlot(hdata,histos[cat][sample],nBins,errors[0])                                                                                                                         
    graphs[0].Draw("HIST")
    '''
    #pad2.Modified()
    #pad2.Update()
    
    #c.cd()
    c.Update()
    c.Modified()
    c.Update()
    c.cd()
    c.SetSelected(c)
    label = "VVcat"
    if "VH" in categories[0]: label="VHcat"
    elif signal1 != None: label="WithSig"+categpries[0]
    if options.prelim==0:
        outputname= options.output+options.name+label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')
        print "save plot as ", outputname+".pdf"
    else:
        outputname= options.output+options.name+label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+"_prelim"
        print "save plot as ",   outputname+".pdf"
    c.SaveAs(outputname+".png")
    c.SaveAs(outputname+".pdf")
    c.SaveAs(outputname+".C")
    c.SaveAs(outputname+".root")


def SetupLegend(signal,mass,scaling):
    VBFtype = ''
    if 'VBF' in signal: VBFtype='VBF '
    if "WprimeWZ"  in signal:
        titleY =VBFtype+"W' (%i TeV) #rightarrow WZ (#times %i)"%(mass/1000.,scaling)
    if "BulkGWW" in signal:
        titleY =VBFtype+"G_{Bulk} (%i TeV) #rightarrow WW (#times %i)"%(mass/1000.,scaling)
    if "BulkGZZ" in signal:
        titleY =VBFtype+"G_{Bulk} (%i TeV) #rightarrow ZZ (#times %i)"%(mass/1000.,scaling)
    if "RadionWW" in signal:
        titleY =VBFtype+"Rad (%i TeV) #rightarrow WW (#times %i)"%(mass/1000.,scaling)
    if "RadionZZ" in signal:
        titleY =VBFtype+"Rad (%i TeV) #rightarrow ZZ (#times %i)"%(mass/1000.,scaling)
    if "ZprimeWW"  in signal:
        titleY =VBFtype+"Z' (%i TeV) #rightarrow WW (#times %i)"%(mass/1000.,scaling)
    if "ZprimeZH"  in signal:
        titleY =VBFtype+"Z' (%i TeV) #rightarrow ZH (#times %i)"%(mass/1000.,scaling)
    if "WprimeWH"  in signal:
        titleY =VBFtype+"W' (%i TeV) #rightarrow WH (#times %.1f)"%(mass/1000.,scaling)
    return titleY



def PlotPulls(categories,histos,axis,data,signal1=None,signal2=None,scaling1=1,scaling2=1,mass1=2000.,mass2=2000.):
    print histos
    extra1 = ''
    extra2 = ''
    htitle = ''
    xtitle = ''
    ymin = 0
    ymax = 0
    xrange = Xrange
    yrange = Yrange
    zrange = options.zrange
    if Xrange == '0,-1': xrange = '55,215'
    if Yrange == '0,-1': yrange = '55,215'
    if options.zrange == '0,-1': zrange = '1.246,7.600'
    xlow = xrange.split(',')[0]
    xhigh = xrange.split(',')[1]
    ylow = yrange.split(',')[0]
    yhigh = yrange.split(',')[1]
    if options.blind == True:
        if len(xrange.split(',')) == 4:
            xlow2 = xrange.split(',')[2]
            xhigh2 = xrange.split(',')[3]
        if len(yrange.split(',')) == 4:
            ylow2 = yrange.split(',')[2]
            yhigh2 = yrange.split(',')[3]

    if axis=='z':
        print "make Z projection"
        htitle = "Z-Proj. x : "+xrange+" y : "+yrange
        hhtitle = options.channel
        xtitle = "Dijet invariant mass [TeV]"
        ymin = -4
        ymax = 4
        extra1 = xrange.split(',')[0]+' GeV < m_{jet1} < '+ xrange.split(',')[1]+' GeV'
        extra2 = yrange.split(',')[0]+' GeV < m_{jet2} < '+ yrange.split(',')[1]+' GeV'
        if xrange != yrange:
            extra1 = xrange.split(',')[0]+' GeV < m_{jet1/2} < '+ xrange.split(',')[1]+' GeV'
            extra2 = yrange.split(',')[0]+' GeV < m_{jet2/1} < '+ yrange.split(',')[1]+' GeV'

        if options.blind == True and len(xrange.split(',')) == 4:
            extra1 = 'Blind '+xhigh+' < m_{jet1} < '+xlow2+' GeV'        #xlow+' < m_{jet1} < '+xhigh+' & '+xlow2+' < m_{jet1} < '+xhigh2+' GeV'
            extra2 = yrange.split(',')[0]+' < m_{jet2} < '+ yrange.split(',')[1]+' GeV'
        if options.blind == True and len(yrange.split(',')) == 4:
            extra2 = 'Blind '+yhigh+' < m_{jet2} < '+ylow2+' GeV'  #extra2 = ylow+' < m_{jet2} < '+yhigh+' & '+ylow2+' < m_{jet2} < '+yhigh2+' GeV'
    elif axis=='x':
        print "make X projection"
        htitle = "X-Proj. y : "+options.yrange+" z : "+options.zrange
        hhtitle = options.channel
        xtitle = " m_{jet1} [GeV]"
        ymin = 0.02
        ymax = histos[categories[0]]["Data"].GetMaximum()*2#max(hdata.GetMaximum()*1.3,maxY*1.3)
        extra1 = yrange.split(',')[0]+' < m_{jet2} < '+ yrange.split(',')[1]+' GeV'
        if options.blind == True and len(yrange.split(',')) == 4:
            extra1 = 'Blind '+yhigh+' < m_{jet2} < '+ylow2+' GeV'  #extra1 = ylow+' < m_{jet2} < '+yhigh+' & '+ylow2+' < m_{jet2} < '+yhigh2+' GeV'
            extra2 = zrange.split(',')[0]+' < m_{jj} < '+ zrange.split(',')[1]+' GeV'
    elif axis=='y':
        print "make Y projection"
        htitle = "Y-Proj. x : "+options.xrange+" z : "+options.zrange
        hhtitle = options.channel
        xtitle = " m_{jet2} [GeV]"
        ymin = 0.02
        ymax = histos[categories[0]]["Data"].GetMaximum()*2#max(hdata.GetMaximum()*1.3,maxY*1.3)
        extra1 = xrange.split(',')[0]+' < m_{jet1} < '+ xrange.split(',')[1]+' GeV'
        if options.blind == True and len(xrange.split(',')) == 4:
            extra1 = 'Blind '+xhigh+' < m_{jet1} < '+xlow2+' GeV'  #extra1 = xlow+' < m_{jet1} < '+xhigh+' & '+xlow2+' < m_{jet1} < '+xhigh2+' GeV'
            extra2 = zrange.split(',')[0]+' < m_{jj} < '+ zrange.split(',')[1]+' GeV'

    c = get_canvas('c')
    c.SetBottomMargin(0.)

    # Lots of math to have all pulls with the same height of the y-axis, taking into account that the last pad will need be larger to accomodate x-axis labels & title
    cat_usual = len(categories)-1.
    ymin_pad0 = 0.85 #total lenght of the pull parts = cat_usual*usualstep + laststep
    bottom_margin = 0.35
    usualstep = ymin_pad0*(1.-bottom_margin)/(cat_usual-cat_usual*bottom_margin+1.)
    # laststep = usualstep+ bottom_margin*laststep
    laststep = usualstep/(1.-bottom_margin)
    #leg = ROOT.TLegend(0.38,ymin_pad0+0.11,0.99,0.99)
    leg = ROOT.TLegend(0.18,ymin_pad0+0.01,0.45,0.99)
    leg.SetTextSize(0.033)
    #leg.SetNColumns(2)
    leg.SetMargin(0.12)
    leg.SetColumnSeparation(0.05)
    #legsig = ROOT.TLegend(0.48,ymin_pad0+0.001,0.8,ymin_pad0+0.10)
    legsig = ROOT.TLegend(0.45,ymin_pad0+0.05,0.97,0.99)
    legsig.SetTextSize(0.033)

    pad0 =  get_pad("legend",ymin_pad0,1.)
    pad0.SetLeftMargin(0.01)
    pad0.SetRightMargin(0.01)
    pad0.Draw()
    pads ={}
    i=0
    for cat in categories:
        step = usualstep
        ymin_pads = ymin_pad0-step*(i+1)
        if i == len(categories)-1: ymin_pads = ymin_pad0-step*(len(categories)-2)-laststep
        if i ==len(categories)-1: ymin_pads = 0
        pads[cat] = ROOT.TPad(cat,cat,0.01,ymin_pads,1,ymin_pad0-step*i)
        pads[cat].SetFillColor(0)
        pads[cat].SetBorderMode(0)
        pads[cat].SetFrameFillStyle(0)
        pads[cat].SetFrameBorderMode(0)
        pads[cat].SetTickx()
        pads[cat].SetTicky()

        pads[cat].SetBottomMargin(0.01)
        if i == len(categories)-1: pads[cat].SetBottomMargin(bottom_margin)
        pads[cat].SetTopMargin(0.)
        pads[cat].SetLeftMargin(0.1)
        pads[cat].SetRightMargin(0.01)



        pads[cat].Draw()
        i+=1

    pad0.cd()
    histos[categories[0]]["syst_band"].SetLineColor(ROOT.kGray+1)
    histos[categories[0]]["syst_band"].SetFillColor(ROOT.kGray+1)
    histos[categories[0]]["syst_band"].SetLineWidth(2)
    histos[categories[0]]["syst_band"].SetLineStyle(1)

    histos[categories[0]]["syst_band"].GetXaxis().SetRangeUser(1.246,7.600)
    histos[categories[0]]["syst_band"].GetXaxis().SetLimits(1.246,6.00)
    for cat in categories:
        histos[cat]["syst_band"].GetXaxis().SetLimits(1.246,6.00)
    histos[categories[0]]["pulls_stat"].SetMarkerColor(ROOT.kBlack)
    histos[categories[0]]["pulls_stat"].SetMarkerStyle(20)
    histos[categories[0]]["pulls_stat"].SetLineColor(ROOT.kBlack)
    histos[categories[0]]["pulls_stat"].SetLineWidth(2)
    histos[categories[0]]["pulls_stat"].SetLineStyle(1)

    leg.AddEntry(histos[categories[0]]["syst_band"],"\pm \sigma_{syst}/\sigma_{stat}","f")
    leg.AddEntry(histos[categories[0]]["pulls_stat"],"#frac{(Data-Prediction)}{\sigma_{stat}}","ep")
    #leg.AddEntry(histos[categories[0]]["pulls_stat"],"(Data-Prediction)/\sigma_{stat}","ep")
    leg.SetLineColor(0)
    legsig.SetLineColor(0)

    i=0
    leg2 = {}
    line = {}
    h_signal1 = {}
    h_signal2 = {}
    box={}
    for cat in categories:
            print  "cat ",cat
            print " leg ",ymin_pad0-step*(i+1)+0.05, ymin_pad0-step*(i)-0.05
            leg2[cat] = ROOT.TLegend(0.6,0.05,0.88,0.13)
            leg2[cat].SetTextSize(0.25)

            pads[cat].cd()


            histos[cat]["syst_band"].GetXaxis().SetRangeUser(1.246,7.600)
            #histos[cat]["syst_band"].GetXaxis().SetLimits(1.246,7.600)
            histos[cat]["syst_band"].SetMinimum(ymin)
            histos[cat]["syst_band"].SetMaximum(ymax)
            histos[cat]["syst_band"].GetYaxis().SetNdivisions(4)

            histos[cat]["syst_band"].SetTitle(hhtitle)
            #histos[cat][sample].SetLineColor(colors[cat])
            #histos[cat][sample].SetMarkerColor(colors[cat])
            #histos[cat][sample].SetMarkerStyle(markers[cat])
            histos[cat]["syst_band"].SetLineColor(ROOT.kOrange)
            histos[cat]["syst_band"].SetFillColor(ROOT.kOrange)
            histos[cat]["syst_band"].SetLineWidth(2)
            histos[cat]["syst_band"].SetLineStyle(1)
            histos[cat]["pulls_stat"].SetMarkerColor(ROOT.kBlack)
            histos[cat]["pulls_stat"].GetXaxis().SetRangeUser(1.246,7.600)
            histos[cat]["pulls_stat"].SetMarkerStyle(20)
            histos[cat]["pulls_stat"].SetLineColor(ROOT.kBlack)
            histos[cat]["pulls_stat"].SetLineWidth(2)
            histos[cat]["pulls_stat"].SetLineStyle(1)


            histos[cat]["syst_band"].Draw("a2same")
            histos[cat]["pulls_stat"].SetMarkerSize(0.7)
            histos[cat]["pulls_stat"].Draw('sameEP0')

            if "VH_HPHP" in cat:
                pt3 = ROOT.TPaveText(0.55,0.65,0.9,0.8,"NDC")
                pt3.SetTextFont(43)
                pt3.SetTextSize(20)
                pt3.SetTextAlign(12)
                pt3.SetFillColor(0)
                pt3.SetBorderSize(0)
                pt3.SetFillStyle(0)
                pt3.AddText(extra1)
                print " extra1 ",extra1
                #pt3.AddText(extra2)
                pt3.Draw()
                pt32 = ROOT.TPaveText(0.55,0.05,0.9,0.45,"NDC")
                pt32.SetTextFont(43)
                pt32.SetTextSize(20)
                pt32.SetTextAlign(12)
                pt32.SetFillColor(0)
                pt32.SetBorderSize(0)
                pt32.SetFillStyle(0)
                #pt32.AddText(extra1)
                print " extra2 ",extra2
                pt32.AddText(extra2)
                pt32.Draw()



            # boxes are needed to cover the +/- 4 extreme on the y axis that are overlapping in an ugly way and make it crowded
            box[cat] = ROOT.TBox(1.,3.,1.23,4.8)
            box[cat].SetFillColor(0)
            box[cat].Draw("same")

            boxlow = ROOT.TBox(1.,-3.,1.23,-4.8)
            boxlow.SetFillColor(0)
            boxlow.Draw("same")

            histos[cat]["syst_band"].GetXaxis().SetTitle(xtitle)
            histos[cat]["syst_band"].GetYaxis().SetTitleOffset(1.5)
            binwidth = histos[cat]["syst_band"].GetXaxis().GetBinWidth(10)
            if axis == "z": binwidth = 100
            histos[cat]["syst_band"].GetYaxis().SetTitle(cat.replace("VBF_","").replace("_"," "))
            histos[cat]["syst_band"].GetYaxis().SetTitleFont(43)
            histos[cat]["syst_band"].GetYaxis().SetTitleSize(18)
            histos[cat]["syst_band"].GetYaxis().CenterTitle()
            histos[cat]["syst_band"].GetYaxis().SetLabelFont(43)
            histos[cat]["syst_band"].GetYaxis().SetLabelSize(20)
            histos[cat]["syst_band"].GetYaxis().SetTitleOffset(1.4)
            if i == len(categories)-1:
                histos[cat]["syst_band"].GetXaxis().SetTitleFont(43)
                histos[cat]["syst_band"].GetXaxis().SetTitleSize(20)
                histos[cat]["syst_band"].GetXaxis().SetTitleOffset(4.)
                histos[cat]["syst_band"].GetXaxis().SetLabelFont(43)
                histos[cat]["syst_band"].GetXaxis().SetLabelSize(20)

            if signal1!= None:
                h_signal1[cat] = MakeSignalPulls(histos[cat][signal1],histos[cat][data],scaling1)

                print "print do hsignal1 ", h_signal1[cat].Integral()
                h_signal1[cat].GetXaxis().SetRangeUser(1.200,7.700)
                h_signal1[cat].SetLineColor(ROOT.kGreen+1)
                h_signal1[cat].SetLineStyle(1)
                h_signal1[cat].SetLineWidth(2)

                h_signal1[cat].Draw("histsame")

            if signal2!= None:
                h_signal2[cat] = MakeSignalPulls(histos[cat][signal2],histos[cat][data],scaling2)
                print "print do hsignal2 ", h_signal2[cat].Integral()
                h_signal2[cat].SetLineColor(ROOT.kViolet)
                h_signal2[cat].GetXaxis().SetRangeUser(1.200,7.700)
                h_signal2[cat].SetLineStyle(2)
                h_signal2[cat].SetLineWidth(2)

                h_signal2[cat].Draw("HISTsame")

            #still in the category loop
            print " drawing line in cat ",cat
            line[cat] = ROOT.TLine(1.246,0,6.00,0)
            line[cat].SetLineColor(ROOT.kBlack)
            line[cat].SetLineWidth(2)
            line[cat].Draw("same")
            leg2[cat].AddEntry(histos[cat]["syst_band"],cat.replace("_"," "),"")
            #leg2[cat].Draw("same")
            print " done i ",i
            i+=1

    #errors[0].Draw("E2same")
    print "projection "+extra1+"  "+extra2+" \n"

    '''
    pt3 = ROOT.TPaveText(0.18,0.55,0.39,0.68,"NDC")
    pt3.SetTextFont(42)
    pt3.SetTextSize(0.04)
    pt3.SetTextAlign(12)
    pt3.SetFillColor(0)
    pt3.SetBorderSize(0)
    pt3.SetFillStyle(0)
    pt3.AddText(extra1)
    pt3.AddText(extra2)
    pt3.Draw("same")
    '''
    #CMS_lumi.CMS_lumi(c, 4, 10)
    c.Update()
    c.Modified()
    c.Update()
    c.cd()

    CMS_lumi.relPosX = 0.13
    c.SetLeftMargin(0.01)
    c.SetRightMargin(0.01)
    lumiSpecialX = -1.
    lumiSpecialY = -1.
    CMS_lumi.CMS_lumi(c, 4,15,lumiSpecialX,lumiSpecialY)
    CMS_lumi.lumiTextSize=0.45
    CMS_lumi.lumiTextOffset=0.5
    CMS_lumi.cmsTextSize=0.6

    extralabel = ROOT.TText(.06,ymin_pad0+0.03,"Pulls");
    extralabel.SetTextAlign(22);
    extralabel.SetTextFont(43);
    extralabel.SetTextSize(20);
    #extralabel.SetTextAngle(90);
    extralabel.Draw("same");


    leg.Draw("same")
    if signal1 != None: legsig.AddEntry(h_signal1[categories[0]],SetupLegend(signal1,mass1,scaling1),"l") #"G_{bulk} (%i TeV) #rightarrow WW (#times %i)"%(mass1/1000.,scaling1) ,"l")
    if signal2 != None: legsig.AddEntry(h_signal2[categories[0]],SetupLegend(signal2,mass2,scaling2),"l") #"Z' (%i TeV) #rightarrow ZH (#times %i)"%(mass2/1000.,scaling2) ,"l")
    legsig.Draw("same")
    c.SetSelected(c)
    label = "ggDYcat"
    if "VBF" in categories[0]: label="VBFcat"
    if signal1 != None: label+="WithSig"+signal1
    if signal2 != None: label+="WithSig"+signal2
    if options.prelim==0:
        outputname= options.output+options.name+label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')
        print "save plot as ", outputname+".pdf"
    else:
        outputname= options.output+options.name+label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+"_prelim"
        print "save plot as ",   outputname+".pdf"
    c.SaveAs(outputname+".png")
    c.SaveAs(outputname+".pdf")
    c.SaveAs(outputname+".C")
    c.SaveAs(outputname+".root")






colors={"VV_HPHP":1,"VH_HPHP":1,"VBF_VV_HPHP":600,"VBF_VH_HPHP":600,"VV_HPLP":619,"VH_HPLP":619,"VBF_VV_HPLP":616,"VBF_VH_HPLP":616,"VH_LPHP":635,"VBF_VH_LPHP":632}
markers={"VV_HPHP":20,"VH_HPHP":20,"VBF_VV_HPHP":24,"VBF_VH_HPHP":24,"VV_HPLP":21,"VH_HPLP":21,"VBF_VV_HPLP":25,"VBF_VH_HPLP":25,"VH_LPHP":22,"VBF_VH_LPHP":26}
linestyles={"VV_HPHP":1,"VH_HPHP":1,"VBF_VV_HPHP":2,"VBF_VH_HPHP":2,"VV_HPLP":3,"VH_HPLP":3,"VBF_VV_HPLP":4,"VBF_VH_HPLP":4,"VH_LPHP":5,"VBF_VH_LPHP":6}
categories_VV=["VV_HPHP","VBF_VV_HPHP","VV_HPLP","VBF_VV_HPLP"]
categories_VH=["VH_HPHP","VBF_VH_HPHP","VH_HPLP","VBF_VH_HPLP","VH_LPHP","VBF_VH_LPHP"]
categories_VBF=["VBF_VH_HPHP","VBF_VV_HPHP","VBF_VH_LPHP","VBF_VH_HPLP","VBF_VV_HPLP"]
categories_ggDY=["VH_HPHP","VV_HPHP","VH_LPHP","VH_HPLP","VV_HPLP"]
categories_all=["VV_HPHP","VBF_VV_HPHP","VV_HPLP","VBF_VV_HPLP","VH_HPHP","VBF_VH_HPHP","VH_HPLP","VBF_VH_HPLP","VH_LPHP","VBF_VH_LPHP"]
categories_test=["VV_HPHP"]

if __name__ == '__main__':

    for p in options.projection:
        print " doing projection ",p

        if p == "x": 
            htitle = "X-Proj. y : "+options.yrange+" z : "+options.zrange
        elif p == "y":
            htitle = "Y-Proj. x : "+options.xrange+" z : "+options.zrange
        elif p == "z":
            htitle = "Z-Proj. x : "+options.xrange+" y : "+options.yrange
        else:
            print "Error:  unknown proj ",p
            sys.exit()


        data = "Data" #"Simulation"



        # First plot: VV mass window, non VBF signal and categories
        signal1 = "BulkGWW"
        prescaling1 = 10.
        mass1=2000
        signal2 = "BulkGZZ"
        prescaling2 = 10.
        mass2=3000
        pullsnames=[signal1,signal2,"pulls_stat","syst_band",data]
        Xrange="65,105"
        Yrange="65,105"
        htitle = "Z-Proj. x : "+Xrange+" y : "+Yrange

        pulls={}
        for c in categories_ggDY:
        #for c in categories_test:
            pulls[c]={}
            print " getting hists for category ",c

            filename=options.input+"/Histos"+c+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root"
            r_file = ROOT.TFile.Open(filename,"READ")

            filename1="prefit_data_SR_VV_"+signal1+str(mass1)+"/Histos"+c+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root"
            r_file1 = ROOT.TFile.Open(filename1,"READ")

            filename2="prefit_data_SR_VV_"+signal2+str(mass2)+"/Histos"+c+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root"
            r_file2 = ROOT.TFile.Open(filename2,"READ")

            print " filename ",filename
            for histname in pullsnames:
                file_to_use = r_file
                if histname == signal1: file_to_use = r_file1
                if histname == signal2: file_to_use = r_file2
                print
                pulls[c][histname]= GetHist(file_to_use,histname)
                print " pulls[c][histname] ",pulls[c][histname]
                if histname == signal1:
                    pulls[c][signal1] = PrepareSignal(pulls[c][signal1],prescaling1)
                if histname == signal2:
                    pulls[c][signal2] = PrepareSignal(pulls[c][signal2],prescaling2)

            r_file.Close()
        #PlotPulls(categories_test,pulls,p,signal1) 

    
        scaling1 = 10.
        scaling2 = 100.
        PlotPulls(categories_ggDY,pulls,p,data,signal1,signal2,scaling1,scaling2,mass1,mass2)


        print "><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><"

        # second plot: VH + HV mass window, non VBF signal and categories
        signal1 = "WprimeWHinc"
        prescaling1 = 1.
        mass1=2000
        signal2 = "ZprimeZHinc"
        prescaling2 = 1.
        mass2=3000
        pullsnames=[signal1,signal2,"pulls_stat","syst_band",data]

        print " Get VH "
        Xrange="65,105"
        Yrange="110,140"
        htitle = "Z-Proj. x : "+Xrange+" y : "+Yrange

        pulls={}
        for c in categories_ggDY:
        #for c in categories_test:
            pulls[c]={}
            print " getting hists for category ",c

            filename=options.input+"/Histos"+c+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root"
            r_file = ROOT.TFile.Open(filename,"READ")

            filename1="prefit_data_SR_VorH_together_"+signal1+str(mass1)+"/Histos"+c+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root"
            r_file1 = ROOT.TFile.Open(filename1,"READ")

            filename2="prefit_data_SR_VorH_together_"+signal2+str(mass2)+"/Histos"+c+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root"
            r_file2 = ROOT.TFile.Open(filename2,"READ")

            print " filename ",filename
            for histname in pullsnames:
                file_to_use = r_file
                if histname == signal1: file_to_use = r_file1
                if histname == signal2: file_to_use = r_file2
                print
                pulls[c][histname]= GetHist(file_to_use,histname)
                print " pulls[c][histname] ",pulls[c][histname]
                if histname == signal1:
                    pulls[c][signal1] = PrepareSignal(pulls[c][signal1],prescaling1)
                if histname == signal2:
                    pulls[c][signal2] = PrepareSignal(pulls[c][signal2],prescaling2)

            r_file.Close()
        #PlotPulls(categories_test,pulls,p,signal1) 



        scaling1 = 0.2
        scaling2 = 1.
        PlotPulls(categories_ggDY,pulls,p,data,signal1,signal2,scaling1,scaling2,mass1,mass2)


        print "><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><"

        
        # VBF signal and categories
        signal1 = "VBF_RadionZZ"
        prescaling1 = 10.
        mass1=2000
        signal2 = "VBF_WprimeWZ"
        prescaling2 = 10000.
        mass2=1500
        pullsnames=[signal1,signal2,"pulls_stat","syst_band",data]
        Xrange="65,140"
        Yrange="65,140"
        htitle = "Z-Proj. x : "+Xrange+" y : "+Yrange

        pulls={}
        for c in categories_VBF:
        #for c in categories_test:
            pulls[c]={}
            print " getting hists for category ",c

            filename=options.input.replace("BulkGWW",signal1)+"/Histos"+c+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root"
            r_file = ROOT.TFile.Open(filename,"READ")

            filename1="prefit_data_SR_VplusH_"+signal1+str(mass1)+"/Histos"+c+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root"
            r_file1 = ROOT.TFile.Open(filename1,"READ")

            filename2="prefit_data_SR_VplusH_"+signal2+str(mass2)+"/Histos"+c+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root"
            r_file2 = ROOT.TFile.Open(filename2,"READ")

            print " filename ",filename
            for histname in pullsnames:
                file_to_use = r_file
                if histname == signal1: file_to_use = r_file1
                if histname == signal2: file_to_use = r_file2
                print
                pulls[c][histname]= GetHist(file_to_use,histname)
                print " pulls[c][histname] ",pulls[c][histname]
                if histname == signal1:
                    print " signal1 VBF"
                    pulls[c][signal1] = PrepareSignal(pulls[c][signal1],prescaling1)
                if histname == signal2:
                    pulls[c][signal2] = PrepareSignal(pulls[c][signal2],prescaling2)

            r_file.Close()
        scaling1 = 300.
        scaling2 = 300.
        PlotPulls(categories_VBF,pulls,p,data,signal1,signal2,scaling1,scaling2,mass1,mass2)

