#!/usr/bin/env python
############# script to estimate migration uncertainties for the full hadronic VV/VH -> 4q analysis ###############
############# base calculation on measuremnt of sf uncertainties for the W/H-tagging scale factors  ###############

# for the moment there are the same scale factors for W-tagging and H-tagging, for 2018 i put the same as for 2017 for now!
import ROOT
import optparse
import sys,os,time
import json
from array import array
ROOT.gROOT.ProcessLine("struct rootint { Int_t ri;};")
from ROOT import rootint
ROOT.gROOT.ProcessLine("struct rootfloat { Float_t rf;};")
from ROOT import rootfloat
ROOT.gROOT.ProcessLine("struct rootlong { Long_t li;};")
from ROOT import rootlong
sys.path.insert(0, "../interactive/")
import cuts
from rootpy.tree import CharArrayCol
ROOT.gROOT.SetBatch(True)
import tdrstyle
tdrstyle.setTDRStyle()

parser = optparse.OptionParser()
parser.add_option("-y","--year",dest="year",default='2016',help="year of data taking")
parser.add_option("-s","--samples",dest="samples",help="sample to calculate the migration unc.",default='ZprimeToZh')
parser.add_option("-d","--directory",dest="directory",help="directory with signal samples",default="migrationunc/")
parser.add_option("-m","--minMX",dest="minMX",type=float,help="mVV variable",default=1200)
parser.add_option("-M","--maxMX",dest="maxMX",type=float, help="mVV variable",default=8000)
parser.add_option("-c","--categories",dest="categories",help="list of considered categories",default='VH_HPHP,VV_HPHP,VH_LPHP,VH_HPLP,VV_HPLP,VBF_VH_HPHP,VBF_VV_HPHP,VBF_VH_LPHP,VBF_VH_HPLP,VBF_VV_HPLP')
parser.add_option("-t","--tags",dest="tags",help="list of tags",default='H_tag,V_tag,top_tag')
parser.add_option("--isSignal",dest="isSignal",action="store_true", help="is signal?")
parser.add_option("--doPtFit",dest="doPtFit",action="store_true", help="do you want to do pt dependence fit?")
parser.add_option("-o","--output",dest="output",help="Output",default='ZprimeZH')
parser.add_option("--vv",dest="vv",help="make VV only (no VHveto) ?",action='store_true')
parser.add_option("--four",dest="four",help="merge VH HPLP in VV HPLP?",action='store_true')
(options,args) = parser.parse_args()

def getLegend(x1=0.6,y1=0.6363636,x2=0.85,y2=0.9020979):
  legend = ROOT.TLegend(x1,y1,x2,y2)
  legend.SetTextSize(0.08)
  legend.SetLineColor(0)
  legend.SetShadowColor(0)
  legend.SetLineStyle(1)
  legend.SetLineWidth(1)
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


def calculateMigration(tree,uncertainty_var,category):
    print " CAT ",category
    events   = 0
    events_wup = 0
    events_wdown = 0
    # calculate effect of sf uncertainty for one particular category 
    # loop through tree
    for e in tree:
        # apply category cuts to the tree
        if e.category.find(category)==-1: continue
        events += e.genWeight*e.puWeight*e.SF
        # apply weight of uncertainty up/down variation to events with real W or H boson and top mistag correction
        # apply also weight for up/down variation of the SF
        # count overall weighted events in the category
        if uncertainty_var == "V_tag":
            events_wup +=e.genWeight*e.puWeight*e.CMS_eff_vtag_sf_up
        elif uncertainty_var == "H_tag":
            events_wup +=e.genWeight*e.puWeight*e.CMS_eff_htag_sf_up
        elif uncertainty_var == "top_tag":
            events_wup +=e.genWeight*e.puWeight*e.CMS_mistag_top_sf_up
        else:
            print " ATTENTION! unknown uncertainty_var ",uncertainty_var
        if uncertainty_var == "V_tag":
            events_wdown +=e.genWeight*e.puWeight*e.CMS_eff_vtag_sf_down
        elif uncertainty_var == "H_tag":
            events_wdown +=e.genWeight*e.puWeight*e.CMS_eff_htag_sf_down
        elif uncertainty_var == "top_tag":
            events_wdown +=e.genWeight*e.puWeight*e.CMS_mistag_top_sf_down
        else:
            print " ATTENTION! unknown uncertainty_var ",uncertainty_var
    # return list with number of weighted, weighted up and down events in the category given by category cuts
    print " event ",events
    print "up ",events_wup
    print " down ", events_wdown
    return [events, events_wup,events_wdown]


def GetHistsRatio(h1pt,h1nom):
    #ratio:
    h3 = h1pt.Clone("h1nom")
    h3.SetLineColor(1)
    h3.SetMarkerStyle(21)
    h3.SetTitle("")
    h3.SetMinimum(0.8)
    h3.SetMaximum(3.)
    # Set up plot for markers and errors
    h3.Sumw2()
    h3.SetStats(0)
    h3.Divide(h1nom)

    # Adjust y-axis settings
    y = h3.GetYaxis()
    y.SetTitle("ratio hpt/hnom ")
    y.SetNdivisions(505)
    y.SetTitleSize(20)
    y.SetTitleFont(43)
    y.SetTitleOffset(1.55)
    y.SetLabelFont(43)
    y.SetLabelSize(15)

    # Adjust x-axis settings
    x = h3.GetXaxis()
    x.SetTitleSize(20)
    x.SetTitleFont(43)
    x.SetTitle("p_T [GeV]")
    x.SetTitleOffset(4.0)
    x.SetLabelFont(43)
    x.SetLabelSize(15)

    return h3

def fitFunc(h3,func,x1,x2): #[0]*TMath::Log10(x)
  fit1 = ROOT.TF1("fit",func,x1,x2) #"[0]*TMath::Log(x)",x1,x2)
  h3.Fit(fit1,"R")
  return fit1

def calculateSFPT(tree,uncertainty_var,category,name,year,func):
    print " CAT ",category
    # calculate effect of the pt dependence of SF for one particular category
    # loop through tree
    h1nom = ROOT.TH1F("h1nom","h1nom",14,200.,3000.)
    h2nom = ROOT.TH1F("h2nom","h2nom",14,200.,3000.)
    h1pt = ROOT.TH1F("h1pt","h1pt",14,200.,3000.)
    h2pt = ROOT.TH1F("h2pt","h2pt",14,200.,3000.)
    luminosity = ctx.lumi[year]/ctx.lumi["Run2"]
    tmpname = "/tmp/tmp_"+time.strftime("%Y%m%d-%H%M%S")
    outfile = ROOT.TFile(tmpname+'.root','RECREATE')
    cattree = ROOT.TTree()
    if name.find("TT") == -1:
      cattree = tree.CopyTree('strstr(category,\"{cat}\")'.format(cat=category))
    else:
      cattree = tree.CopyTree('strstr(category,\"{cat}\")*'+ctx.cuts[name].format(cat=category))
    print " cattree has entries ? ",cattree.GetEntries()
    cattree.Draw("jj_l1_pt>>h1nom(14,200.,3000)","genWeight*puWeight*SF*{lumi}".format(lumi=str(luminosity)),"goff")
    h1nom = ROOT.gROOT.FindObject('h1nom')
    print " h1nom ",h1nom.GetEntries()
    cattree.Draw("jj_l2_pt>>h2nom(14,200.,3000)","genWeight*puWeight*SF*{lumi}".format(lumi=str(luminosity)),"goff")
    h2nom = ROOT.gROOT.FindObject('h2nom')
    if uncertainty_var == "V_tag":
        cattree.Draw("jj_l1_pt>>h1pt(14,200.,3000)","genWeight*puWeight*Wsfpt*{lumi}".format(lumi=str(luminosity)),"goff")
        h1pt = ROOT.gROOT.FindObject('h1pt')
        cattree.Draw("jj_l2_pt>>h2pt(14,200.,3000)","genWeight*puWeight*Wsfpt*{lumi}".format(lumi=str(luminosity)),"goff")
        h2pt = ROOT.gROOT.FindObject('h2pt')
    elif uncertainty_var == "H_tag":
        cattree.Draw("jj_l1_pt>>h1pt(14,200.,3000)","genWeight*puWeight*Hsfpt*{lumi}".format(lumi=str(luminosity)),"goff")
        h1pt = ROOT.gROOT.FindObject('h1pt')
        cattree.Draw("jj_l2_pt>>h2pt(14,200.,3000)","genWeight*puWeight*Hsfpt*{lumi}".format(lumi=str(luminosity)),"goff")
        h2pt = ROOT.gROOT.FindObject('h2pt')
    else:
        print " ATTENTION! unknown uncertainty_var ",uncertainty_var

    h1nom.Add(h2nom)
    h1pt.Add(h2pt)
    h3 = GetHistsRatio(h1pt,h1nom)
    #fit1 = DrawSFPT(h1nom,h1pt,h3,uncertainty_var,category,name,year,func)
    h1nom.SetDirectory(0)
    h1pt.SetDirectory(0)
    outfile.Close()
    os.system("rm "+tmpname+".root")
    return h1nom,h1pt,h3 #,fit1



def DrawSFPT(h1nom,h1pt,h3,uncertainty_var,category,name,year,func):
    print " CAT ",category
    # plot ratio
    c = ROOT.TCanvas("c", "canvas", 800, 800)
    # Upper histogram plot is pad1
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    pad1.SetBottomMargin(0)  # joins upper and lower plot
    #pad1.SetGridx()
    pad1.Draw()
    # Lower ratio plot is pad2
    c.cd()  # returns to main canvas before defining pad2
    pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
    pad2.SetTopMargin(0)  # joins upper and lower plot
    pad2.SetBottomMargin(0.2)
    #pad2.SetGridx()
    pad2.Draw()
    pad1.cd()
    #h1pt.GetXaxis().SetRangeUser(200.,3000.)
    h1pt.SetTitle("")
    h1pt.GetYaxis().SetRangeUser(0.01,1000000)
    pad2.SetLogy()
    h1pt.Draw("hist")
    h1nom.SetLineColor(1)
    h1pt.SetLineStyle(2)
    h1nom.SetLineWidth(2)
    h1pt.SetLineWidth(2)
    h1nom.Draw("histsame")
    l=getLegend()
    l.AddEntry(h1pt,"pt","l")
    l.AddEntry(h1nom,"nom","l")
    l.Draw()

    # to avoid clipping the bottom zero, redraw a small axis
    h1pt.GetYaxis().SetLabelSize(0.0)
    h1pt.GetYaxis().SetTitle("Events")
    h1nom.GetYaxis().SetLabelSize(0.0)

    axis = ROOT.TGaxis(-5, 20, -5, 220, 20, 220, 510, "")
    axis.SetLabelFont(43)
    axis.SetLabelSize(15)
    axis.Draw()
    pad2.cd()
    h3.Draw("ep")
    fit1 = fitFunc(h3,func,800.,3000.)
    fit1.Draw("same")
    #ROOT.gStyle.SetOptFit(1111)
    label = func+" p0 "+str(fit1.GetParameter(0))
    if func == 'pol1' : label=label+" p1 "+str(fit1.GetParameter(1))
    l2=getLegend(0.2,0.6,0.5,0.9)
    l2.AddEntry(fit1,label,"l")
    l2.Draw()

    c.Update()

    c.SaveAs("ratio_"+uncertainty_var+"_"+category+"_"+name+"_"+year+".pdf")
    return fit1


def printresult(res,cats):
    masses=[]
    for key in res.keys():
        if (key.split('.')[1]).find(cats[0])!=-1:
            masses.append(int(key.split('.')[0]))

    c = 'Sample '
    for cat in cats:
        c+='              '
        c+=cat 
    print c
    for m in sorted(masses):
        tmp =str(m)+'  '
        for cat in cats:
            if res[str(m)+'.'+cat][0]!=0 :
                nom = res[str(m)+'.'+cat][0]
                up = res[str(m)+'.'+cat][1]
                down = res[str(m)+'.'+cat][2]
                tmp+= str(down/float(nom))+' / '+str(up/nom)
            #print up
            #print nom
            tmp+='   '
        print tmp

def printresultbkg(res,cats):
    masses = []
    for key in res.keys():
        if (key.split('.')[1]).find(cats[0])!=-1:
            masses.append(key.split('.')[0])

    c = 'mass '
    for cat in cats:
        c+='              '
        c+=cat
    print c
    for m in sorted(masses):
        tmp =str(m)+'  '
        for cat in cats:
            if res[str(m)+'.'+cat][0]!=0 :
                nom = res[str(m)+'.'+cat][0]
                up = res[str(m)+'.'+cat][1]
                down = res[str(m)+'.'+cat][2]
                tmp+= str(down/float(nom))+' / '+str(up/nom)
            #print up
            #print nom
            tmp+='   '
        print tmp

        
def calcfinalUnc(final,tag,cats):
    data={}
    savekeys=[]
    for k in final.keys():
        if k.find(tag)==-1: continue
        savekeys.append(k)
    masses=[]
    res=final[savekeys[0]]
    for key in res.keys():
        if (key.split('.')[1]).find(cats[0])!=-1:
            masses.append(key.split('.')[0])
    tmplistu = []
    tmplistd = []
    ratiodown ={}
    ratioup ={}
    c = 'Sample '
    for cat in cats:
        c+='              '
        c+=cat 
        tmplistd.append(0.)
        tmplistu.append(0.)
    print c



    print " sorted(masses) ",sorted(masses)
    for m in sorted(masses):
        tmp =str(m)+'  '
        i=0
        for cat in cats:
            if res[str(m)+'.'+cat][0]!=0 :
                nom= res[str(m)+'.'+cat][0]
                upvar = res[str(m)+'.'+cat][1]
                downvar = res[str(m)+'.'+cat][2]
                ratiodown.update({m+"."+cat:float(downvar)/float(nom)})
                ratioup.update({m+"."+cat:float(upvar)/float(nom)})		
                tmp+= str(round(float(ratiodown[m+"."+cat]),2))+' / '+str(round(float(ratioup[m+"."+cat]),2))
                if options.isSignal==True:
                    tmplistu[i]+= ratioup[m+"."+cat]
                    tmplistd[i]+= ratiodown[m+"."+cat]
                i+=1
            else:
              # added when processing diboson samples, low number of events. I was getting nom=zero
              ratiodown.update({m+"."+cat:1.})
              ratioup.update({m+"."+cat:1.})
              tmp+= str(round(float(ratiodown[m+"."+cat]),2))+' / '+str(round(float(ratioup[m+"."+cat]),2))

            tmp+='   '
            
        print tmp
    i=0
    for c in cats:
        if c == "VV_NPHP":c="VV_NPHP_control_region"
        if options.isSignal==True:
            #print " averaging on masses for signal???"
            data[c+'_up']= round(tmplistu[i]/float(len(masses)),2)
            data[c+'_down']= round(tmplistd[i]/float(len(masses)),2)
        else:
            for m in masses:
                data[str(m)+'.'+c+'_up']= round(ratioup[m+'.'+c],2)
                data[str(m)+'.'+c+'_down']= round(ratiodown[m+'.'+c],2)
        i+=1

    return data


if __name__=="__main__":
    # calculate migration uncertainty for all categories
    # up variation of W-Tag HP Sf -> down variation of W-tag LP sf, down variation of anti W-tag HP category
    # do it for all the categories and for W-tag HP up/down, W-tag LP up/down, H-tag HP up/down, H-tag LP up/down
    # and for the combination of: W-tag + H-tag HP up/down and LP up/down
    
    ######### first apply the usual acceptance cuts to the trees ####################
    data ={}
    datapt={}
    years = options.year.split(",")
    directory = options.directory
    categories=options.categories.split(",")
    if options.vv == True: categories=["VV_HPHP","VV_HPLP","VBF_VV_HPHP","VBF_VV_HPLP"]
    if options.four == True: categories=["VH_HPHP","VV_HPHP","VH_LPHP","VV_HPLP","VBF_VH_HPHP","VBF_VV_HPHP","VBF_VH_LPHP","VBF_VV_HPLP"]
    tags=options.tags.split(",")
    sampleTypes = options.samples.split(",")
    total = {}
    totalnom = {}
    totalpt = {}
    contrib =["resT","resW","nonresT","resTnonresT","resWnonresT","resTresW"]
    mappdf = {"resT":"TTJetsTop","resW":"TTJetsW","nonresT":"TTJetsNonRes","resTnonresT":"TTJetsTNonResT","resWnonresT":"TTJetsWNonResT","resTresW":"TTJetsResWResT"}

    dofit = options.doPtFit

    print " Doing migration uncertainties! DID YOU EVALUTE THE SF BEFORE?"
    jsonfilename = {}
    for year in years:
        chain = ROOT.TChain('signalregion')
        print "************     year ",year
        ctx  = cuts.cuts("init_VV_VH.json",year,"random_dijetbins")
        for filename in os.listdir(directory):
            for sampleType in sampleTypes:
                if filename.find(sampleType)!=-1 and filename.find(year)!=-1:
                    if filename.find(".")==-1: continue
                    if filename.find("VBF")!=-1 and sampleType.find("VBF")==-1: continue
                    fnameParts=filename.split('.')
                    fname=fnameParts[0]
                    print "fname ",fname
                    ext=fnameParts[1]
                    if ext.find("root") ==-1: continue
                    if options.isSignal == True:
                        print " is signal !"
                        mass = float(fname.split('_')[-1])
                        if mass <options.minMX or mass > options.maxMX: continue
                        else: sampleType=sampleType+"narrow_"+fname.split('_')[-2]
                    completename=directory+sampleType+"_"+year+".root"
                    FileIn = ROOT.TFile(completename,"READ")
                    chain.Add(completename)
                    print " entries ",chain.GetEntries()
        print " total Entries ",chain.GetEntries()


        final = {}
        finalfit = {}
        finalpt = {}
        finalnom = {}
        splitstr = options.output
        for tag in tags:
            result = {}
            hnom = {}
            hpt = {}
            hratio = {}
            fit = {}
            func = "[0]*TMath::Log(x)"
            par = 1
            if tag == "V_tag":
              func = "pol1"
              par = 2
            #print finaltree.Print()
            for cat in categories:
                print  " ****** "+cat+" *****"
                if splitstr.find("TT") == -1:
                    result[splitstr+'.'+cat] = calculateMigration(chain,tag,cat)
                    if dofit == True:
                      if tag != "top_tag":
                        hnom[splitstr+'.'+cat],hpt[splitstr+'.'+cat],hratio[splitstr+'.'+cat] = calculateSFPT(chain,tag,cat,splitstr,year,func)
                        print " nom ",hnom[splitstr+'.'+cat]
                        print " pt ",hpt[splitstr+'.'+cat]
                else:
                  for con in contrib:
                    tmpname = "tmp_"+time.strftime("%Y%m%d-%H%M%S")
                    outfile = ROOT.TFile(tmpname+'.root','RECREATE')
                    print " %%%%%%%    "+con+"     %%%%%%%%%"
                    ttcomp = chain.CopyTree(ctx.cuts[con])
                    print ttcomp.GetEntries()
                    ttcomp.Write()
                    result[mappdf[con]+'.'+cat] = calculateMigration(ttcomp,tag,cat)
                    if dofit ==True:
                      if tag != "top_tag":
                        hnom[mappdf[con]+'.'+cat],hpt[mappdf[con]+'.'+cat],hratio[mappdf[con]+'.'+cat] = calculateSFPT(ttcomp,tag,cat,con,year,func) 
                        print " cat "+cat+" tag "+tag+" func "+func #+" parameters ",fit[mappdf[con]+'.'+cat].GetParameters()

                    os.system("rm "+tmpname+".root")

            print '###################   '+tag+'    ######################'

            #if splitstr.find("Jets")!=-1 or splitstr.find("TT")!=-1 : printresultbkg(result,categories)
            #else: printresult(result,categories)
            printresultbkg(result,categories)
            final[tag]=result
            finalnom[tag]=hnom
            print " finalnom ",finalnom[tag]
            finalpt[tag]=hpt
            finalfit[tag]=fit
            print "************** FINAL ",final
            print "************** FINAL FIT",finalfit
        total[year]=final
        totalnom[year]=finalnom
        print " totalnom ",totalnom[year]
        print " totalnom V_tag ",totalnom[year]["V_tag"]
        totalpt[year]=finalpt


        print 'CMS_VV_JJ_DeepJet_Htag_eff'
        data[year] = {splitstr+'_'+'CMS_VV_JJ_DeepJet_Htag_eff' : calcfinalUnc(final,'H_tag',categories)}
        print 'CMS_VV_JJ_DeepJet_Vtag_eff'
        data[year].update( {splitstr+'_'+'CMS_VV_JJ_DeepJet_Vtag_eff' : calcfinalUnc(final,'V_tag',categories)})
        print 'CMS_VV_JJ_DeepJet_TOPtag_mistag'
        data[year].update({splitstr+'_'+'CMS_VV_JJ_DeepJet_TOPtag_mistag' : calcfinalUnc(final,'top_tag',categories)})
	print data[year]

        jsonfilename[year] = 'migrationunc_'+splitstr+'_'+year+'.json'
        with open(jsonfilename[year], 'w') as outfile:
            json.dump(data[year], outfile)


    if len(years) == 3 or options.year == "2016,2017" :
        period="Run2"
        if options.year == "2016,2017": period = "1617"
        print "#######################################      Making "+period+" combination by average weighted by lumi      ##############################"
        print " All years uncertainties "
        print " TOTAL ",total
        print " NOM ",totalnom
        print " PT ",totalpt
        splitstr = options.output
        file2write=None
        if dofit ==True:
          file2write = open("SFpt_dependence_"+splitstr+"_"+period+".txt",'w')
        unc_Run2 = {}
        for tag in tags:
            print "tag ",tag
            func="[0]*TMath::Log(x)"
            if tag == "V_tag": func= "pol1"


            unc_Run2[tag]={}
            for cat in categories:
                print "cat ",cat
                n = 0
                u = 0
                d = 0
                if splitstr.find("TT") == -1:
                  Hnom = ROOT.TH1F("Hnom","Hnom",14,200.,3000.)
                  Hpt = ROOT.TH1F("Hpt","Hpt",14,200.,3000.)
                  for year in years:
                    print " year ",year
                    n += total[year][tag][splitstr+'.'+cat][0]*ctx.lumi[year]
                    u += total[year][tag][splitstr+'.'+cat][1]*ctx.lumi[year]
                    d += total[year][tag][splitstr+'.'+cat][2]*ctx.lumi[year]
                    if dofit ==True:
                      if tag != "top_tag":
                        Hnom.Add(totalnom[year][tag][splitstr+'.'+cat])
                        print totalpt[year][tag][splitstr+'.'+cat]
                        Hpt.Add(totalpt[year][tag][splitstr+'.'+cat])
                        print " Hnom ",Hnom.GetEntries()
                        print " Hpt ",Hpt.GetEntries()
                  if dofit ==True:
                    Hratio = GetHistsRatio(Hpt,Hnom)
                    print " Hratio ",Hratio.GetEntries()
                    fitfunc = DrawSFPT(Hnom,Hpt,Hratio,tag,cat,splitstr,period,func)
                    print " cat "+cat+" tag "+tag+" func "+func
                    file2write.write(" cat "+cat+" tag "+tag+" func "+func+" \n")
                    print "N  parameters ",fitfunc.GetNpar()
                    file2write.write("N  parameters "+str(fitfunc.GetNpar())+" \n")
                    for i in range(fitfunc.GetNpar()):
                      print i,fitfunc.GetParameter(i)
                      file2write.write(" p"+str(i)+" "+str(fitfunc.GetParameter(i))+"\n")
                else:
                  for con in contrib:
                    Hnom = ROOT.TH1F("Hnom","Hnom",14,200.,3000.)
                    Hpt =ROOT.TH1F("Hpt","Hpt",14,200.,3000.)
                    for year in years:
                      n += total[year][tag][mappdf[con]+'.'+cat][0]*ctx.lumi[year]
                      u += total[year][tag][mappdf[con]+'.'+cat][1]*ctx.lumi[year]
                      d += total[year][tag][mappdf[con]+'.'+cat][2]*ctx.lumi[year]
                      if dofit ==True:
                        if tag != "top_tag":
                          Hnom.Add(totalnom[year][tag][mappdf[con]+'.'+cat])
                          Hpt.Add(totalpt[year][tag][mappdf[con]+'.'+cat])
                    if dofit ==True:
                      if tag != "top_tag":
                        print " Hnom ",Hnom.GetEntries()
                        print " Hpt ",Hpt.GetEntries()
                        Hratio = GetHistsRatio(Hpt,Hnom)
                        fitfunc = DrawSFPT(Hnom,Hpt,Hratio,tag,cat,mappdf[con],period,func)
                        file2write.write(" cat "+cat+" tag "+tag+" func "+func+" \n")
                        print "N  parameters ",fitfunc.GetNpar()
                        file2write.write("N  parameters "+str(fitfunc.GetNpar())+" \n")
                        for i in range(par):
                          print i,fitfunc.GetParameter(i)
                          file2write.write(" p"+str(i)+" "+str(fitfunc.GetParameter(i))+"\n")

                if  unc_Run2[tag] == None:
                    if splitstr.find("TT") == -1:
                        unc_Run2[tag] = {splitstr+'.'+cat : [n,u,d] }
                    else:
                        for con in contrib:
                            unc_Run2[tag] = {mappdf[con]+'.'+cat : [n,u,d] }
                else:
                    if splitstr.find("TT") == -1:
                        unc_Run2[tag].update( {splitstr+'.'+cat : [n,u,d] })
                    else:
                        for con in contrib:
                            unc_Run2[tag].update( {mappdf[con]+'.'+cat : [n,u,d] })

        print " unc ",period
        print unc_Run2
        if dofit ==True:
          file2write.close()
        print 'CMS_VV_JJ_DeepJet_Htag_eff'
        data[period] = {splitstr+'_'+'CMS_VV_JJ_DeepJet_Htag_eff' : calcfinalUnc(unc_Run2,'H_tag',categories)}
        print 'CMS_VV_JJ_DeepJet_Vtag_eff'
        data[period].update( {splitstr+'_'+'CMS_VV_JJ_DeepJet_Vtag_eff' : calcfinalUnc(unc_Run2,'V_tag',categories)})
        print 'CMS_VV_JJ_DeepJet_TOPtag_mistag'
        data[period].update({splitstr+'_'+'CMS_VV_JJ_DeepJet_TOPtag_mistag' : calcfinalUnc(unc_Run2,'top_tag',categories)})

        jsonfilename[period] = 'migrationunc_'+splitstr+'_'+period+'.json'
        with open(jsonfilename[period], 'w') as outfile:
            json.dump(data[period], outfile)


 
