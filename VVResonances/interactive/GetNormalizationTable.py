#!/usr/bin/env python                                                                                                                                                                   
import ROOT
from array import array
import argparse
import os, sys, re, optparse,pickle,shutil,json, copy
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.v5.TFormula.SetMaxima(10000) #otherwise we get an error that the TFormula called by the TTree draw has too many operators when running on the CR
from  CMGTools.VVResonances.plotting.CMS_lumi import *
#sys.path.insert(0, "../interactive/")
import cuts

parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="outname",default='')
parser.add_option("-i","--inputdir",dest="inputdir",help="directory where the input files are stored",default="results_Run2")
parser.add_option("-p","--period",dest="period",help="2016 or 2017 or 2016,2017,2018",default="2016,2017,2018")
parser.add_option("-c","--categories",dest="categories",help="VV_HPHP etc",default="VH_HPHP,VV_HPHP,VH_LPHP,VH_HPLP,VV_HPLP")
parser.add_option("-v","--vbf",dest="vbf",help="make vbf?",action='store_true')

(options,args) = parser.parse_args()

def loadJson(inputdir,category,filename,period):
    jsonname=inputdir+"/"+filename+"_"+period+"_"+category+".json" 
    with open(jsonname) as jsonFile:
        print " opened json file ",jsonname
        j = json.load(jsonFile)
    print j
    return j


def tablePreambole(txtfile,caption):
    txtfile.write("\\begin{table}[b]\n")
    txtfile.write("\\topcaption{%s yield and background yields extracted from the background-only fit together with post-fit uncertainties.}\n" %caption)
    txtfile.write("\centering\n")
    txtfile.write("\\begin{tabular}{lcccccc}\n")
    txtfile.write("\hline\n")
    txtfile.write("Background & Data & Total  & QCD &\\ttbar{} & \PW{}+jets & \PZ{}+jets \\\\ \n")
    txtfile.write("\hline\n")

def tableClosing(txtfile,caption):
    txtfile.write("\hline\n")
    txtfile.write("\end{tabular}\n")
    txtfile.write("\label{tab:ObsEvents}\n")
    txtfile.write("\end{table}\n")


def simpleTablePreambole(txtfile,caption):
    txtfile.write("\\begin{table}[b]\n")
    txtfile.write("\centering\n")
    txtfile.write("\\begin{tabular}{lccccccccccccc}\n")
    txtfile.write("\hline\n")
    txtfile.write("Background & Data & Total  & QCD & W+jets & Z+jets & ttbar & 2resT & 2resW & nonresT & resTnonresT & resWnonresT & resTresW \\\\ \n")
    txtfile.write("\hline\n")


if __name__ == "__main__":
    contrib =["resT","resW","nonresT","resTnonresT","resWnonresT","resTresW"]
    mappdf = {"resT":"TTJetsTop","resW":"TTJetsW","nonresT":"TTJetsNonRes","resTnonresT":"TTJetsTNonResT","resWnonresT":"TTJetsWNonResT","resTresW":"TTJetsResWResT"}
    bkg = ["nonRes","TTJets","Wjets","Zjets"]
    eventstype=["Expected","Observed"]
    if options.period.find(",")!=-1 and len(options.period.split(",")) == 3: 
        year = "Run2"
    elif options.period.find(",")!=-1 and len(options.period.split(",")) == 2:
        year = "1617"
    else: year = options.period


    category = options.categories.split(",")
    print category

    events = {}
    for evt in eventstype:
        print " processing ",evt
        events[evt] = {}
        text_file = open(evt+"_"+year+options.output+".txt", "w")
        simpletext_file = open(evt+"simple_"+year+options.output+".txt", "w")
        tablePreambole(text_file,evt)
        simpleTablePreambole(simpletext_file,evt)
        production = ["gg/DY"]
        if options.vbf == True:
            production = ["VBF","gg/DY"]

        exp = {}
        unc = {}
        for prod in production:
            print " production ",prod
            for c in category:
                print " cat ",c
                if prod == "VBF": c = "VBF_"+c
                exp[c] = loadJson(options.inputdir,c,evt,year)
                if evt == "Observed":
                    unc[c] = loadJson(options.inputdir,c,"Uncertainty",year)
                print " non res ",exp[c]["nonRes"]
                totalTT=0
                totalTTunc=0
                for con in contrib:
                    if evt == "Expected":
                        totalTT=totalTT+int(round(exp[c][mappdf[con]]))
                    else:
                        totalTT=totalTT+int(round(exp[c][con]))
                        print " con ",con,"unc[c][con]",unc[c][con]
                        totalTTunc=totalTTunc+int(round(unc[c][con]))       #+int(round(unc[c][con]*unc[c][con]))
                        print "partial TT unc",totalTTunc
                exp[c]["TTJets"]=totalTT
                if evt == "Observed": 
                    unc[c]["TTJets"]=totalTTunc     #ROOT.TMath.Sqrt(totalTTunc)
                    print "total TTunc",unc[c]["TTJets"]
                total = 0
                totalunc=0
                for b in bkg:
                    total=total+int(round(exp[c][b]))
                    if evt == "Observed":
                        totalunc=totalunc+int(round(unc[c][b]*unc[c][b]))
                totalunc=ROOT.TMath.Sqrt(totalunc)
                if prod == "VBF":
                    if evt == "Expected":
                        text_file.write(" %s %s %s & %.0f & %.0f & %.0f & %.0f & %.0f & %.0f  \\\\ \n"%(c.split("_")[1],c.split("_")[2],c.split("_")[0],exp[c]["data"],total,exp[c]["nonRes"],totalTT,exp[c]["Wjets"],exp[c]["Zjets"]))
                    else:
                        text_file.write(" %s %s %s & %.0f $\pm$ %0.f & %.0f $\pm$ %0.f & %.0f $\pm$ %0.f & %.0f $\pm$ %0.f & %.0f $\pm$ %0.f & %.0f $\pm$ %0.f \\\\ \n"%(c.split("_")[1],c.split("_")[2],c.split("_")[0],exp[c]["data"],unc[c]["data"],total,totalunc,exp[c]["nonRes"],unc[c]["nonRes"],totalTT,unc[c]["TTJets"],exp[c]["Wjets"],unc[c]["Wjets"],exp[c]["Zjets"],unc[c]["Zjets"]))
                    if evt == "Expected":
                        simpletext_file.write(" %s %s %s & %.0f & %.0f & %.0f & %.0f & %.0f & %.0f &%.0f & %.0f & %.0f & %.0f & %.0f & %.0f  \\\\ \n"%(c.split("_")[1],c.split("_")[2],c.split("_")[0],exp[c]["data"],total,exp[c]["nonRes"],exp[c]["Wjets"],exp[c]["Zjets"],totalTT,exp[c]["TTJetsTop"],exp[c]["TTJetsW"],exp[c]["TTJetsNonRes"],exp[c]["TTJetsTNonResT"],exp[c]["TTJetsWNonResT"],exp[c]["TTJetsResWResT"]))
                    else:
                        simpletext_file.write(" %s %s %s & %.0f & %.0f & %.0f & %.0f & %.0f &%.0f & %.0f & %.0f & %.0f & %.0f & %.0f & %.0f \\\\ \n"%(c.split("_")[1],c.split("_")[2],c.split("_")[0],exp[c]["data"],total,exp[c]["nonRes"],exp[c]["Wjets"],exp[c]["Zjets"],totalTT,exp[c]["resT"],exp[c]["resW"],exp[c]["nonresT"],exp[c]["resTnonresT"],exp[c]["resWnonresT"],exp[c]["resTresW"]))

                else:
                    if evt == "Expected":
                        text_file.write(" %s %s %s & %.0f & %.0f & %.0f & %.0f & %.0f & %.0f \\\\ \n"%(c.split("_")[0],c.split("_")[1],"DY/gg",exp[c]["data"],total,exp[c]["nonRes"],totalTT,exp[c]["Wjets"],exp[c]["Zjets"]))
                    else:
                        text_file.write(" %s %s %s & %.0f $\pm$ %0.f & %.0f $\pm$ %0.f & %.0f $\pm$ %0.f & %.0f $\pm$ %0.f & %.0f $\pm$ %0.f & %.0f $\pm$ %0.f \\\\ \n"%(c.split("_")[0],c.split("_")[1],"DY/gg",exp[c]["data"],unc[c]["data"],total,totalunc,exp[c]["nonRes"],unc[c]["nonRes"],totalTT,unc[c]["TTJets"],exp[c]["Wjets"],unc[c]["Wjets"],exp[c]["Zjets"],unc[c]["Zjets"]))
                    if evt == "Expected":
                        simpletext_file.write(" %s %s %s & %.0f & %.0f & %.0f & %.0f & %.0f &%.0f & %.0f & %.0f & %.0f & %.0f & %.0f & %.0f \\\\ \n"%(c.split("_")[0],c.split("_")[1],"DY/gg",exp[c]["data"],total,exp[c]["nonRes"],exp[c]["Wjets"],exp[c]["Zjets"],totalTT,exp[c]["TTJetsTop"],exp[c]["TTJetsW"],exp[c]["TTJetsNonRes"],exp[c]["TTJetsTNonResT"],exp[c]["TTJetsWNonResT"],exp[c]["TTJetsResWResT"]))
                    else:
                        simpletext_file.write(" %s %s %s & %.0f & %.0f & %.0f & %.0f & %.0f &%.0f & %.0f & %.0f & %.0f & %.0f & %.0f & %.0f \\\\ \n"%(c.split("_")[0],c.split("_")[1],"DY/gg",exp[c]["data"],total,exp[c]["nonRes"],exp[c]["Wjets"],exp[c]["Zjets"],totalTT,exp[c]["resT"],exp[c]["resW"],exp[c]["nonresT"],exp[c]["resTnonresT"],exp[c]["resWnonresT"],exp[c]["resTresW"]))

            simpletext_file.write("\hline\n")
            #text_file.write("\hline\n")


        tableClosing(text_file,evt)
        text_file.close()
        tableClosing(simpletext_file,evt)
        simpletext_file.close()

