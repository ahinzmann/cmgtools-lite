#!/bin/env python                                                                                                                                                                                                                                                               
import ROOT
import json
import math
from time import sleep
import optparse, sys

parser = optparse.OptionParser()


parser.add_option("-c","--category",dest="category",help="VV_HPHP or VV_HPLP or VH_HPHP etc",default='VV_HPLP')
parser.add_option("-i","--indir",dest="indir",help="input directory",default='')
parser.add_option("-o","--outdir",dest="outdir",help="output directory",default='')
parser.add_option("-b","--binning",dest="binning",help="rebinning factor",type="int",default=1)
parser.add_option("-p","--period",dest="period",help="period e.g 2016 or Run2",default="2016")
parser.add_option("-w","--wtd",dest="wtd",help="What to do? pseudodata and/or shapes",default="shapes")

(options,args) = parser.parse_args()

purity = options.category
rebin  = options.binning
period = options.period


if options.wtd.find("pseudo")!= -1 :
    print "####        rebinning pseudo data "
    pseudo = "JJ_"+str(period)+"_PDALL_"+str(purity)+".root"

    r_file = ROOT.TFile(str(options.indir)+pseudo,"READ")
    data = r_file.Get("data")
    nonRes = r_file.Get("nonRes")

    print data.GetXaxis().GetNbins()

    data.RebinX(rebin)

    print data.GetXaxis().GetNbins()

    data.RebinY(rebin)

    nonRes.RebinX(rebin)
    nonRes.RebinY(rebin)


    r_file_out = ROOT.TFile(str(options.outdir)+pseudo,"RECREATE")
    data.Write()
    nonRes.Write("nonRes")

if options.wtd.find("dib")!= -1 :
    print "####        rebinning pseudo data "
    pseudo1 = "JJ_"+str(period)+"_PDWZ_"+str(purity)+".root"
    pseudo2 = "JJ_"+str(period)+"_PDZZ_"+str(purity)+".root"

    r_file1 = ROOT.TFile(str(options.indir)+pseudo1,"READ")
    data = r_file1.Get("data")
    r_file2 = ROOT.TFile(str(options.indir)+pseudo2,"READ")
    data2 = r_file2.Get("data")


    data.Add(data2)

    print data.GetXaxis().GetNbins()

    data.RebinX(rebin)

    print data.GetXaxis().GetNbins()

    data.RebinY(rebin)


    r_file_out = ROOT.TFile(str(options.outdir)+pseudo1.replace("WZ","DIB"),"RECREATE")
    data.Write()

if options.wtd.find("tt")!= -1 :
    print "####        rebinning ttbar pseudo data "
    pseudo = "JJ_"+str(period)+"_PDTT_"+str(purity)+".root"

    r_file = ROOT.TFile(str(options.indir)+pseudo,"READ")
    data = r_file.Get("data")
    print data.GetXaxis().GetNbins()

    data.RebinX(rebin)

    print data.GetXaxis().GetNbins()
    
    data.RebinY(rebin)

    r_file_out = ROOT.TFile(str(options.outdir)+pseudo,"RECREATE")
    data.Write()

if options.wtd.find("data")!= -1 :
    print "####        rebinning  data "
    pseudo = "JJ_"+str(period)+"_data_"+str(purity)+".root"
    if period == "Run2" or period == "1617": pseudo = "JJ_"+str(purity)+".root"

    r_file = ROOT.TFile(str(options.indir)+pseudo,"READ")
    data = r_file.Get("data")
    print data.GetXaxis().GetNbins()

    data.RebinX(rebin)

    print data.GetXaxis().GetNbins()
    
    data.RebinY(rebin)

    r_file_out = ROOT.TFile(str(options.outdir)+pseudo,"RECREATE")
    data.Write("data")


if options.wtd.find("norm")!= -1 :
    print "####        rebinning norm pythia"
    pseudo = "JJ_"+str(period)+"_nonRes_"+str(purity)+".root"

    r_file = ROOT.TFile(str(options.indir)+pseudo,"READ")
    nonRes = r_file.Get("nonRes")


    nonRes.RebinX(rebin)
    nonRes.RebinY(rebin)


    r_file_out = ROOT.TFile(str(options.outdir)+pseudo,"RECREATE")
    nonRes.Write("nonRes")

    print "####        rebinning norm herwig"
    pseudo = "JJ_"+str(period)+"_nonRes_"+str(purity)+"_altshapeUp.root"

    r_file = ROOT.TFile(str(options.indir)+pseudo,"READ")
    nonRes = r_file.Get("nonRes")


    nonRes.RebinX(rebin)
    nonRes.RebinY(rebin)


    r_file_out = ROOT.TFile(str(options.outdir)+pseudo,"RECREATE")
    nonRes.Write("nonRes")

    print "####        rebinning norm mad"
    pseudo = "JJ_"+str(period)+"_nonRes_"+str(purity)+"_altshape2.root"

    r_file = ROOT.TFile(str(options.indir)+pseudo,"READ")
    nonRes = r_file.Get("nonRes")


    nonRes.RebinX(rebin)
    nonRes.RebinY(rebin)


    r_file_out = ROOT.TFile(str(options.outdir)+pseudo,"RECREATE")
    nonRes.Write("nonRes")


if options.wtd.find("shapes")!=-1  and 'VBF' not in purity:
    print "####        rebinning template shapes "

    generators = ["pythia","madgraph","herwig"]
    for gen in generators:
        print "gen"
        templ = "save_new_shapes_"+str(period)+"_"+gen+"_"+str(purity)+"_3D.root"
        f_templ = ROOT.TFile(str(options.indir)+templ,"READ")
        fout_templ = ROOT.TFile(str(options.outdir)+templ,"RECREATE")
        for key in f_templ.GetListOfKeys():
            print key.GetName()
            kname = key.GetName()
            hist = f_templ.Get(kname)
            #print hist.GetEntries()
            #print hist.GetXaxis().GetNbins()
            hist.RebinX(rebin)
            hist.RebinY(rebin)
            #print hist.GetXaxis().GetNbins()
            hist.Write()

