#!/usr/bin/env python

import ROOT
from array import array
import os, sys, re, optparse,pickle,shutil,json
from CMGTools.VVResonances.plotting.VarTools import returnString
ROOT.gROOT.SetBatch(True)


parser = optparse.OptionParser()
parser.add_option("-g","--graphs",dest="graphs",default='',help="Comma   separated graphs and functions to fit  like MEAN:pol3,SIGMA:pol2")
parser.add_option("-o","--output",dest="output",help="Output JSON",default='')
parser.add_option("-m","--min",dest="min",type=float, help="minimum x",default=0)
parser.add_option("-M","--max",dest="max",type=float, help="maximum x",default=0)


(options,args) = parser.parse_args()
#define output dictionary


rootFile=ROOT.TFile(args[0])


graphStr= options.graphs.split(',')
parameterization={}



ff=ROOT.TFile("debug_"+options.output+".root","RECREATE")
ff.cd()
print " graphStr ",graphStr
for string in graphStr:
    comps =string.split(':')
    graph=rootFile.Get(comps[0])
    if comps[0].find("corr")==-1:
        if comps[1].find("pol")!=-1:
            func=ROOT.TF1(comps[0]+"_func",comps[1],0,13000)
            #func=ROOT.TF1(comps[0]+"_func","[0]-[1]*x" ,0,13000)
        elif  comps[1]=="llog":
            func=ROOT.TF1(comps[0]+"_func","[0]+[1]*log(x)",1,13000)
            func.SetParameters(1,1)
        elif  comps[1].find("laur")!=-1:
            order=int(comps[1].split("laur")[1])
            st='0'
            for i in range(0,order):
                st=st+"+["+str(i)+"]"+"/x^"+str(i)
            print 'Laurent String',st    
            func=ROOT.TF1(comps[0]+"_func",st,1,13000)
            for i in range(0,order):
                func.SetParameter(i,0)
        elif comps[1]=="sqrt":
            func = ROOT.TF1(comps[0]+"_func","[0]+[1]*sqrt(x)",1,13000)
            st= "work in progress"
        elif comps[1]=="1/sqrt":
            func = ROOT.TF1(comps[0]+"_func","[0]+[1]/sqrt(x)",1,13000)
            st = "work in progress"
        elif comps[1]=="spline":
            print "fit spline"
            func = ROOT.TSpline3(comps[0],graph)
            
    else:
        func = ROOT.TF2(comps[0]+"_func","[0] + [1]*x +[2] *y +[3]*x*y",55,215,55,215) # +[3]*x*y
        if comps[0].find("sigma")!=-1:
            func = ROOT.TF2(comps[0]+"_func","[0] + [1]*x +[2] *y ",55,215,55,215) # +[3]*x*y
    print "function ",func    
    if comps[0].find("corr")!=-1:
        graph.Fit(func,"","")
        graph.Fit(func,"","")
        graph.Fit(func,"","")
    elif comps[0].find("gorr")!=-1:
        print 'fit function '+func.GetName()
        graph.Fit(func,"","",55,215)
        graph.Fit(func,"","",55,215)
        graph.Fit(func,"","",55,215)
    elif comps[1]=="spline":
        print "Spline used, no need to fit it"
    else:
        print comps[1]
        print 'fit function '+func.GetName()
        graph.Fit(func,"","",options.min,options.max)
        graph.Fit(func,"","",options.min,options.max)
        graph.Fit(func,"","",options.min,options.max)
    parameterization[comps[0]]=returnString(func,comps[1])

    c = ROOT.TCanvas()
    c.SetRightMargin(0.2)
    if comps[0].find("corr")!=-1:
        signal="W' #rightarrow "
        decay = "WH "
        if  options.output.find("Zprime")!=-1: 
            signal="Z' #rightarrow "
            decay="ZH "
        if  options.output.find("WZ")!=-1: decay="WZ "
        if options.output.find("VBF")!=-1: 
            signal = " VBF "+signal
        else: 
            signal = "     "+signal
        signal = signal+decay
        graph.SetTitle("Simulation        "+signal+"           (13 TeV)")
        variable = "mean"
        graph.GetZaxis().SetTitle("#frac{mean_{bin}}{mean_{inclusive}}")
        graph.SetMinimum(0.94)
        graph.SetMaximum(1.04)

        if comps[0].find("sigma")!=-1: 
            variable = "sigma"
            graph.GetZaxis().SetTitle("#frac{sigma_{bin}}{sigma_{inclusive}}")
            graph.SetMinimum(0.95)
            graph.SetMaximum(1.07)
            if options.output.find("VBF")!=-1: 
                graph.SetMaximum(1.7) 
                graph.SetMinimum(0.9)
    
        graph.GetXaxis().SetTitle("m_{jet1} [GeV]")
        graph.GetYaxis().SetTitle("m_{jet2} [GeV]")
        graph.GetZaxis().SetTitleOffset(1.5)

        graph.Draw("COLZ")
    else:
        graph.Draw()
    func.SetLineColor(ROOT.kRed)
    func.Draw("lcsame")
    name="debug_"+options.output+"_"+comps[0]
    name=name.replace(".","_")
    c.SaveAs(name+".png")
    c.SaveAs(name+".pdf")
    c.SaveAs(name+".C")
    graph.Write(comps[0])
    func.Write(comps[0]+"_func")
ff.Close()
f=open(options.output,"w")
json.dump(parameterization,f)
f.close()


