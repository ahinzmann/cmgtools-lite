import os,sys,optparse,time
import ROOT as rt
import tdrstyle
tdrstyle.setTDRStyle()
import CMGTools.VVResonances.plotting.CMS_lumi as CMS_lumi
rt.gStyle.SetOptStat(0)
rt.gStyle.SetOptTitle(0)
rt.gROOT.SetBatch(True)
from time import sleep

# Run from command line with
#python Projections3DHisto.py --mc ${normdir}/JJ_${period}_nonRes_${catOut}${labels[$i]}.root,nonRes -k save_new_shapes_${period}_${samples[$i]}_${catOut}_3D.root,histo -o control-plots-${period}-${catOut}-${samples[$i]} --period "${period}" -l ${nicelabels[$i]}

def get_canvas(cname):

 #change the CMS_lumi variables (see CMS_lumi.py)
 CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
 CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
 CMS_lumi.writeExtraText = 1
 CMS_lumi.extraText = "Simulation"
 CMS_lumi.lumi_sqrtS = "13 TeV ("+options.period+")" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)

 iPos = 11
 if( iPos==0 ): CMS_lumi.relPosX = 0.12

 H_ref = 600
 W_ref = 800
 W = W_ref
 H  = H_ref

 iPeriod = 0

 # references for T, B, L, R
 T = 0.08*H_ref
 B = 0.12*H_ref
 L = 0.12*W_ref
 R = 0.04*W_ref

 canvas = rt.TCanvas(cname,cname,50,50,W,H)
 canvas.SetFillColor(0)
 canvas.SetBorderMode(0)
 canvas.SetFrameFillStyle(0)
 canvas.SetFrameBorderMode(0)
 canvas.SetLeftMargin( L/W )
 canvas.SetRightMargin( R/W )
 canvas.SetTopMargin( T/H )
 canvas.SetBottomMargin( B/H )
 canvas.SetTickx(0)
 canvas.SetTicky(0)

 return canvas


def get_canvas_forRatio(cname):

 #change the CMS_lumi variables (see CMS_lumi.py)
 CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
 CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
 CMS_lumi.writeExtraText = 1
 CMS_lumi.extraText = "Simulation"
 CMS_lumi.lumi_sqrtS = "13 TeV ("+options.period+")" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)

 iPos = 10
 CMS_lumi.relPosX = 0.12

 H_ref = 600 
 W_ref = 600 
 W = W_ref
 H  = H_ref

 iPeriod = 0

 # references for T, B, L, R
 T = 0.07*H_ref
 B = 0.12*H_ref 
 L = 0.15*W_ref
 R = 0.05*W_ref

 canvas = rt.TCanvas(cname,cname,W,H)
 canvas.SetFillColor(0)
 canvas.SetBorderMode(0)
 canvas.SetFrameFillStyle(0)
 canvas.SetFrameBorderMode(0)
 canvas.SetFrameBorderSize(0)
 canvas.SetFrameLineWidth(0)
 canvas.SetLeftMargin( L/W )
 canvas.SetRightMargin( R/W )
 canvas.SetTopMargin( T/H )
 canvas.SetBottomMargin( B/H )
 canvas.SetTickx(0)
 canvas.SetTicky(0)
 
 return canvas

parser = optparse.OptionParser()
parser.add_option("--mc","--mc",dest="mc",help="File with mc events and histo name (separated by comma)",default='JJ_nonRes_HPHP_nominal.root,nonRes')
parser.add_option("-k","--kernel",dest="kernel",help="File with kernel and histo name (separated by comma)",default='JJ_nonRes_3D_HPHP.root,histo')
parser.add_option("-o","--outdir",dest="outdir",help="Output directory for plots",default='control-plots')
parser.add_option("-l","--label",dest="label",help="MC type label (Pythia8, Herwig, Madgraph, Powheg)",default='Pythia8')
parser.add_option("-p","--period",dest="period",help="year or Run2",default='Run2')
parser.add_option("--prelim",dest="prelim",help="which CMS labels?",default='prelim')
(options,args) = parser.parse_args()

prelim = options.prelim

#void Projections3DHisto(std::string dataFile, std::string hdataName, std::string fitFile, std::string hfitName, std::string outDirName){

os.system('rm -rf %s'%options.outdir)
os.system('mkdir %s'%options.outdir)

kfile,kname = options.kernel.split(',')
print "kfile "+str(kfile)
fin = rt.TFile.Open(kfile,"READ")
print "kname "+str(kname)
hin = fin.Get(kname)
hin.Scale(1./hin.Integral())

MCfile,MCname = options.mc.split(',')
finMC = rt.TFile.Open(MCfile,"READ")
hinMC = finMC.Get(MCname)
hinMC.Scale(1./hinMC.Integral())

binsx = hin.GetNbinsX()
xmin = hin.GetXaxis().GetXmin()
xmax = hin.GetXaxis().GetXmax()
print "xmin",xmin,"xmax",xmax,"binsx",binsx

binsy = hin.GetNbinsY()
ymin = hin.GetYaxis().GetXmin()
ymax = hin.GetYaxis().GetXmax()
print "ymin",ymin,"ymax",ymax,"binsy",binsy

binsz = hin.GetNbinsZ()
zmin = hin.GetZaxis().GetXmin()
zmax = hin.GetZaxis().GetXmax()
print "zmin",zmin,"zmax",zmax,"binsz",binsz

hx = []
hy = []
hz = []
hxMC = []
hyMC = []
hzMC = []

pullsx = []
pullsy = []
pullsz = []

zbinMin = [1,1,hin.GetZaxis().FindBin(1530)+1,hin.GetZaxis().FindBin(2546)+1]
zbinMax = [binsz,hin.GetZaxis().FindBin(1530),hin.GetZaxis().FindBin(2546),binsz]
colors = [1,99,9,8,94,6]

scale = [1.,0.8,3.0,30.]

for i in range(4):

 print "Plotting mJ projections",zbinMin[i],zbinMax[i]
 pname = "px_%i"%i
 hx.append( hin.ProjectionX(pname,1,binsy,zbinMin[i],zbinMax[i],"e") )
 pname = "py_%i"%i
 hy.append( hin.ProjectionY(pname,1,binsx,zbinMin[i],zbinMax[i],"e") )
 pname = "px_MC%i"%i
 hxMC.append( hinMC.ProjectionX(pname,1,binsy,zbinMin[i],zbinMax[i],"e") )
 pname = "pyMC_%i"%i
 hyMC.append( hinMC.ProjectionY(pname,1,binsx,zbinMin[i],zbinMax[i],"e") )

 pname = "pullsx_%i"%i
 pullsx.append( rt.TH1F(pname,pname,40,-10,10) )
 pname = "pullsy_%i"%i
 pullsy.append( rt.TH1F(pname,pname,40,-10,10) )
        
fx = open(options.outdir+"/cx_chi2.txt","w")
fy = open(options.outdir+"/cy_chi2.txt","w")
fx.write("minx maxx chi2/ndof\n")
fy.write("minx maxx chi2/ndof\n")
for i in range(4):
 for b in range(1,binsx+1):
  if hxMC[i].GetBinContent(b) != 0: pullsx[i].Fill( (hxMC[i].GetBinContent(b)-hx[i].GetBinContent(b))/hxMC[i].GetBinError(b) )
  if hyMC[i].GetBinContent(b) != 0: pullsy[i].Fill( (hyMC[i].GetBinContent(b)-hy[i].GetBinContent(b))/hyMC[i].GetBinError(b) )

 fx.write("%f %f %f\n"%(hxMC[i].GetBinCenter(zbinMin[i]),hxMC[i].GetBinCenter(zbinMax[i]),hx[i].Chi2Test(hxMC[i],"CHI2/NDF")))
 fy.write("%f %f %f\n"%(hyMC[i].GetBinCenter(zbinMin[i]),hyMC[i].GetBinCenter(zbinMax[i]),hy[i].Chi2Test(hyMC[i],"CHI2/NDF")))


fx.close()
fy.close()
for i in range(4):

 hx[i].Scale(scale[i])
 hy[i].Scale(scale[i])
 hxMC[i].Scale(scale[i])
 hyMC[i].Scale(scale[i])
 print " rebinning!"
 hx[i].Rebin(2)
 hy[i].Rebin(2)
 hxMC[i].Rebin(2)
 hyMC[i].Rebin(2)

 hx[i].SetLineColor(colors[i])
 hx[i].SetMarkerColor(colors[i])
 hy[i].SetLineColor(colors[i])
 hy[i].SetMarkerColor(colors[i])
 hxMC[i].SetLineColor(colors[i])
 hxMC[i].SetMarkerColor(colors[i])
 hxMC[i].SetMarkerStyle(20+i)
 hxMC[i].SetMarkerSize(0.8)
 hyMC[i].SetLineColor(colors[i])
 hyMC[i].SetMarkerColor(colors[i]) 
 hyMC[i].SetMarkerStyle(20+i)
 hyMC[i].SetMarkerSize(0.8)
 
 pullsx[i].SetLineColor(colors[i])
 pullsx[i].SetLineWidth(2)
 pullsx[i].SetMarkerSize(0)
 pullsy[i].SetLineColor(colors[i])
 pullsy[i].SetLineWidth(2)
 pullsy[i].SetMarkerSize(0)
  
hx[0].SetMinimum(0)
hx[0].SetMaximum(0.06)
hy[0].SetMinimum(0)
hy[0].SetMaximum(0.06)
#leg = rt.TLegend(0.6,0.6,0.85,0.8)
leg = rt.TLegend(0.51,0.60,0.76,0.85)
leg.SetBorderSize(0)
leg.SetTextSize(0.035)
leg.AddEntry(hxMC[0],"Simulation (%s)"%options.label,"LP")
leg.AddEntry(hx[0],"Template","L")
for i in range(1,4):
 leg.AddEntry(hxMC[i],"%.1f < m_{jj} < %.1f TeV"%( hin.GetZaxis().GetBinLowEdge(zbinMin[i])/1000.,hin.GetZaxis().GetBinUpEdge(zbinMax[i])/1000.),"LP" )
 
# ------------------------------------------------------- X
cx = get_canvas_forRatio("cx")
cx.cd()

# Upper histogram plot is pad1
pad1 = rt.TPad("pad1", "pad1", 0, 0.31, 1, 1.0)
pad1.SetBottomMargin(0)  # joins upper and lower plot
pad1.SetRightMargin(0.05)
pad1.SetLeftMargin(0.15)
pad1.SetTopMargin(0.1)
pad1.Draw()

# Lower ratio plot is pad2
cx.cd()  # returns to main canvas before defining pad2
pad2 = rt.TPad("pad2", "pad2", 0, 0.00, 1, 0.3)
pad2.SetTopMargin(0)  # joins upper and lower plot
pad2.SetBottomMargin(0.25)
pad2.SetRightMargin(0.05)
pad2.SetLeftMargin(0.15)
pad2.Draw()

pad1.cd()

for i in range(4):
 hx[i].Draw("HISTsame")
 hxMC[i].Draw("PEsame")
hx[0].GetXaxis().SetTitle("m_{jet1} (proj. x) [GeV]")
hx[0].GetYaxis().SetTitle("a.u.")
leg.Draw()


if prelim.find("prelim")!=-1:
 CMS_lumi.cmslabel_sim_prelim(cx,'sim',11)
elif prelim.find("thesis")!=-1:
 CMS_lumi.cmslabel_thesis(cx,'sim',0)
else:
 CMS_lumi.cmslabel_sim(cx,'sim',11)


pad2.cd()


hxMC_r = []
for i in range(4):
 h = hxMC[i].Clone("hx_%i"%i)
 for b in range(1,binsx+1):
  hx[i].SetBinError(b,0.)

 h.Divide(hx[i])
 hxMC_r.append( h )

 hxMC_r[i].Draw("epsame")
hxMC_r[0].GetXaxis().SetTitleSize(0.11)
hxMC_r[0].GetXaxis().SetLabelSize(0.11)
hxMC_r[0].GetYaxis().SetTitleSize(0.11)
hxMC_r[0].GetYaxis().SetTitleOffset(0.5)
hxMC_r[0].GetYaxis().SetLabelSize(0.11)
hxMC_r[0].GetYaxis().SetRangeUser(0.,2.)
hxMC_r[0].GetYaxis().SetNdivisions(5)
hxMC_r[0].GetXaxis().SetTitle("m_{jet1} (proj. x) [GeV]")
hxMC_r[0].GetYaxis().SetTitle("#frac{Simulation}{Template}")

linea =  rt.TLine(xmin,1.,xmax,1.);
linea.SetLineColor(17);
linea.SetLineWidth(2);
linea.SetLineStyle(2);
linea.Draw("same");

cx.cd()
cx.Update()
cx.RedrawAxis()
frame = cx.GetFrame()
frame.Draw()
cx.SaveAs(options.outdir+"/cx.png","pdf")
cx.SaveAs(options.outdir+"/cx.pdf","pdf")
cx.SaveAs(options.outdir+"/cx.C")

# ------------------------------------------------------- Y 
cy = get_canvas_forRatio("cy")
cy.cd()

# Upper histogram plot is pad1
pad1y = rt.TPad("pad1", "pad1", 0, 0.31, 1, 1.0)
pad1y.SetBottomMargin(0)  # joins upper and lower plot
pad1y.SetRightMargin(0.05)
pad1y.SetLeftMargin(0.15)
pad1y.SetTopMargin(0.1)
pad1y.Draw()

# Lower ratio plot is pad2
cy.cd()  # returns to main canvas before defining pad2
pad2y = rt.TPad("pad2", "pad2", 0, 0.00, 1, 0.3)
pad2y.SetTopMargin(0)  # joins upper and lower plot
pad2y.SetBottomMargin(0.25)
pad2y.SetRightMargin(0.05)
pad2y.SetLeftMargin(0.15)
pad2y.Draw()
pad1y.cd()
hy[0].GetXaxis().SetTitle("m_{jet2} (proj. y) [GeV]")
hy[0].GetYaxis().SetTitle("a.u.")
hy[0].GetXaxis().SetTitleSize(hx[0].GetXaxis().GetTitleSize())
hy[0].GetXaxis().SetTitleOffset(hx[0].GetXaxis().GetTitleOffset())
for i in range(4): 
 hy[i].Draw("HISTsame")
 hyMC[i].Draw("PEsame")
leg.Draw()

if prelim.find("prelim")!=-1:
 CMS_lumi.cmslabel_sim_prelim(cy,'sim',11)
elif prelim.find("thesis")!=-1:
 CMS_lumi.cmslabel_thesis(cy,'sim',0)
else:
 CMS_lumi.cmslabel_sim(cy,'sim',11)
pad2y.cd()
hyMC_r = []
for i in range(4):
 h = hyMC[i].Clone("hy_%i"%i)
 for b in range(1,binsx+1):
  hy[i].SetBinError(b,0.)

 h.Divide(hy[i])
 hyMC_r.append( h )

 hyMC_r[i].Draw("epsame")
hyMC_r[0].GetXaxis().SetTitleSize(0.11)
hyMC_r[0].GetXaxis().SetLabelSize(0.11)
hyMC_r[0].GetYaxis().SetTitleSize(0.11)
hyMC_r[0].GetYaxis().SetTitleOffset(0.5)
hyMC_r[0].GetYaxis().SetLabelSize(0.11)
hyMC_r[0].GetYaxis().SetRangeUser(0.,2.)
hyMC_r[0].GetYaxis().SetNdivisions(5)
hyMC_r[0].GetXaxis().SetTitle("m_{jet2} (proj. y) [GeV]")
hyMC_r[0].GetYaxis().SetTitle("#frac{Simulation}{Template}")

linea.Draw("same");

cy.cd()
cy.Update()
cy.RedrawAxis()
frame = cy.GetFrame()
frame.Draw()
cy.SaveAs(options.outdir+"/cy.png","pdf")
cy.SaveAs(options.outdir+"/cy.pdf","pdf")
cy.SaveAs(options.outdir+"/cy.C")

labelsXY = ['All m_{jj} bins']
for i in range(1,4): labelsXY.append( "%.1f < m_{jj} < %.1f TeV"%( hin.GetZaxis().GetBinLowEdge(zbinMin[i])/1000.,hin.GetZaxis().GetBinUpEdge(zbinMax[i])/1000.) )

for i in range(4):

 pt = rt.TPaveText(0.1436782,0.7690678,0.4224138,0.8644068,"brNDC")
 pt.SetTextFont(42)
 pt.SetTextSize(0.042)
 pt.SetTextAlign(22)
 pt.SetFillColor(0)
 pt.SetBorderSize(1)
 pt.SetFillStyle(0)
 pt.SetLineWidth(2)
 pt.AddText(labelsXY[i])
  
 cname = "cpullsx_%i"%i
 cpullsx = get_canvas(cname)
 cpullsx.cd() 
 pullsx[i].Draw("PE")

 f = rt.TF1("func","gaus(0)",-10,10)
 f.SetParameter(0,10)
 f.SetParError(0,5)
 f.SetParameter(1,0)
 f.SetParError(1,0.5)
 f.SetParameter(2,4)
 f.SetParError(2,2)
 pullsx[i].Fit("func")
 
 pt.Draw()

 cpullsx.SaveAs(options.outdir+"/"+cpullsx.GetName()+".png","pdf")
 cpullsx.SaveAs(options.outdir+"/"+cpullsx.GetName()+".pdf","pdf")
 cpullsx.SaveAs(options.outdir+"/"+cpullsx.GetName()+".C")

for i in range(4):

 pt = rt.TPaveText(0.1436782,0.7690678,0.4224138,0.8644068,"brNDC")
 pt.SetTextFont(42)
 pt.SetTextSize(0.042)
 pt.SetTextAlign(22)
 pt.SetFillColor(0)
 pt.SetBorderSize(1)
 pt.SetFillStyle(0)
 pt.SetLineWidth(2)
 pt.AddText(labelsXY[i])
  
 cname = "cpullsy_%i"%i
 cpullsy = get_canvas(cname)
 cpullsy.cd() 
 pullsy[i].Draw("PE")

 f = rt.TF1("func","gaus(0)",-10,10)
 f.SetParameter(0,10)
 f.SetParError(0,5)
 f.SetParameter(1,0)
 f.SetParError(1,0.5)
 f.SetParameter(2,4)
 f.SetParError(2,2)
 pullsy[i].Fit("func")
 
 pt.Draw()

 cpullsy.SaveAs(options.outdir+"/"+cpullsy.GetName()+".png","pdf")
 cpullsy.SaveAs(options.outdir+"/"+cpullsy.GetName()+".pdf","pdf")
 cpullsy.SaveAs(options.outdir+"/"+cpullsy.GetName()+".C")

#------------------------------------------ Z
#default slices
xbinMin = [1,hin.GetXaxis().FindBin(55),hin.GetXaxis().FindBin(73)+1,hin.GetXaxis().FindBin(103)+1,hin.GetXaxis().FindBin(167)+1]
xbinMax = [binsx,hin.GetXaxis().FindBin(73),hin.GetXaxis().FindBin(103),hin.GetXaxis().FindBin(167),binsx]

scalez = [1.,1.,0.1,0.01,0.001,0.0001]

count = 0
counttot = 0
for i in range(5):

 print "Plotting mJJ projections",xbinMin[i],xbinMax[i]
 pname = "pz_%i"%i
 hz.append( hin.ProjectionZ(pname,xbinMin[i],xbinMax[i],xbinMin[i],xbinMax[i]) )
 pname = "pzMC_%i"%i
 hzMC.append( hinMC.ProjectionZ(pname,xbinMin[i],xbinMax[i],xbinMin[i],xbinMax[i]) )

 pname = "pullsz_%i"%i
 pullsz.append( rt.TH1F(pname,pname,40,-10,10) )

# add one more projection
print "Plotting mJJ projections",xbinMin[i],xbinMax[i]
pname = "pz_5"
h1 = hin.ProjectionZ(pname,hin.GetXaxis().FindBin(73)+1,hin.GetXaxis().FindBin(103)+1,hin.GetXaxis().FindBin(103)+1,hin.GetXaxis().FindBin(167)+1)
h2 = hin.ProjectionZ(pname,hin.GetXaxis().FindBin(103)+1,hin.GetXaxis().FindBin(167)+1,hin.GetXaxis().FindBin(73)+1,hin.GetXaxis().FindBin(103)+1)
h1.Add(h2)
hz.append(h1) 
pname = "pzMC_5"
h1 = hinMC.ProjectionZ(pname,hinMC.GetXaxis().FindBin(73)+1,hinMC.GetXaxis().FindBin(103)+1,hinMC.GetXaxis().FindBin(103)+1,hinMC.GetXaxis().FindBin(167)+1)
h2 = hinMC.ProjectionZ(pname,hinMC.GetXaxis().FindBin(103)+1,hinMC.GetXaxis().FindBin(167)+1,hinMC.GetXaxis().FindBin(73)+1,hinMC.GetXaxis().FindBin(103)+1)
h1.Add(h2)
hzMC.append(h1) 
pullsz.append( rt.TH1F(pname,pname,40,-10,10) )


fz = open(options.outdir+"/cz_chi2.txt","w")
   
for i in range(6):
 print " pulls and chi2"
 hzMC[i].Sumw2()
 ratio = hzMC[i].Clone()
 ratio.Divide(hz[i])

 f = rt.TF1("f","[0]",0.,7600.);
 f.SetParameter(0,1)
 chi2 = ratio.Chisquare(f)
 chi2/= ratio.GetNbinsX()

 if i != 5:
  for b in range(1,binsx+1):
   if hzMC[i].GetBinContent(b) != 0:
    pullsz[i].Fill( (hzMC[i].GetBinContent(b)-hz[i].GetBinContent(b))/hzMC[i].GetBinError(b) )

  fz.write("%f %f %f\n"%(hin.GetXaxis().GetBinCenter(xbinMin[i]),hin.GetXaxis().GetBinCenter(xbinMax[i]),chi2)) #hz[i].Chi2Test(hzMC[i]))) #,"CHI2/NDF")))
 else:
  fz.write("V Ht %f\n"%(chi2)) #hz[i].Chi2Test(hzMC[i]))) #,"CHI2/NDF")))

fz.close()



for i in range(6):
 
 hz[i].Scale(scalez[i])
 hzMC[i].Scale(scalez[i])

 hz[i].SetLineColor(colors[i])
 hz[i].SetMarkerColor(colors[i])
 hzMC[i].SetLineColor(colors[i])
 hzMC[i].SetMarkerColor(colors[i])
 hzMC[i].SetMarkerStyle(20+i)
 hzMC[i].SetMarkerSize(0.8)

 pullsz[i].SetLineColor(colors[i])
 pullsz[i].SetLineWidth(2)
 pullsz[i].SetMarkerSize(0)


#leg2 = rt.TLegend(0.6,0.6,0.85,0.85)
leg2 = rt.TLegend(0.51,0.6,0.76,0.89)
leg2.SetBorderSize(0)
leg2.SetTextSize(0.035)
leg2.AddEntry(hzMC[0],"Simulation (%s)"%options.label,"LP")
leg2.AddEntry(hz[0],"Template","L")
for i in range(1,5):
 leg2.AddEntry(hzMC[i],"%i < m_{jet} < %i GeV"%(  hin.GetXaxis().GetBinLowEdge(xbinMin[i]),hin.GetXaxis().GetBinUpEdge(xbinMax[i])),"LP" )

leg2.AddEntry(hzMC[5],"75 <m_{jet1/2} < 105 GeV,","LP")
leg2.AddEntry(hzMC[5]," 105 < m_{jet2/1} < 169 GeV","")

cz = get_canvas_forRatio("cz")
cz.cd()
# Upper histogram plot is pad1
pad1z = rt.TPad("pad1", "pad1", 0, 0.31, 1, 1.0)
pad1z.SetBottomMargin(0)  # joins upper and lower plot
pad1z.SetRightMargin(0.05)
pad1z.SetLeftMargin(0.15)
pad1z.SetTopMargin(0.09)
pad1z.Draw()

# Lower ratio plot is pad2
cz.cd()  # returns to main canvas before defining pad2
pad2z = rt.TPad("pad2", "pad2", 0, 0.00, 1, 0.3)
pad2z.SetTopMargin(0)  # joins upper and lower plot
pad2z.SetBottomMargin(0.25)
pad2z.SetRightMargin(0.05)
pad2z.SetLeftMargin(0.15)
pad2z.Draw()
pad1z.cd()
pad1z.SetLogy()

hz[0].SetMinimum(1E-11)
hz[0].SetMaximum(50.0)
hz[0].SetMaximum(100.)
for i in range(6):
 hz[i].Draw("HISTsame")
 hzMC[i].Draw("PEsame")
hz[0].GetXaxis().SetTitle("m_{jj} (proj. z) [GeV]")
hz[0].GetYaxis().SetTitle("a.u.")
leg2.Draw()

if prelim.find("prelim")!=-1:
 CMS_lumi.cmslabel_sim_prelim(cz,'sim',11)
elif prelim.find("thesis")!=-1:
 CMS_lumi.cmslabel_thesis(cz,'sim',0)
else:
 CMS_lumi.cmslabel_sim(cz,'sim',11)

pad2z.cd()
hzMC_r = []
for i in range(6):
 h = hzMC[i].Clone("hz_%i"%i)
 for b in range(1,binsx+1):
  hz[i].SetBinError(b,0.)

 h.Divide(hz[i])
 hzMC_r.append( h )

 hzMC_r[i].Draw("epsame")
hzMC_r[0].GetXaxis().SetTitleSize(0.11)
hzMC_r[0].GetXaxis().SetLabelSize(0.11)
hzMC_r[0].GetYaxis().SetTitleSize(0.11)
hzMC_r[0].GetYaxis().SetTitleOffset(0.5)
hzMC_r[0].GetYaxis().SetLabelSize(0.11)
hzMC_r[0].GetYaxis().SetRangeUser(0.,2.)
hzMC_r[0].GetYaxis().SetNdivisions(5)
hzMC_r[0].GetXaxis().SetTitle("m_{jj} (proj. z) [GeV]")
hzMC_r[0].GetYaxis().SetTitle("#frac{Simulation}{Template}")

lineaz =  rt.TLine(zmin,1.,zmax,1.);
lineaz.SetLineColor(17);
lineaz.SetLineWidth(2);
lineaz.SetLineStyle(2);
lineaz.Draw("same");


cz.cd()
cz.Update()
cz.RedrawAxis()
frame = cz.GetFrame()
frame.Draw()
cz.SaveAs(options.outdir+"/cz.png","pdf")
cz.SaveAs(options.outdir+"/cz.pdf","pdf")
cz.SaveAs(options.outdir+"/cz.C")

labelsZ = ["All m_{jet} bins"]
for i in range(1,5):
 labelsZ.append("%i < m_{jet} < %i GeV"%(hin.GetXaxis().GetBinLowEdge(xbinMin[i]),hin.GetXaxis().GetBinUpEdge(xbinMax[i])))

labelsZ.append("75 <m_{jet1/2} < 105 GeV, 105 < m_{jet2/1} < 169 GeV")
for i in range(6):

 pt = rt.TPaveText(0.1436782,0.7690678,0.4224138,0.8644068,"brNDC")
 pt.SetTextFont(42)
 pt.SetTextSize(0.042)
 pt.SetTextAlign(22)
 pt.SetFillColor(0)
 pt.SetBorderSize(1)
 pt.SetFillStyle(0)
 pt.SetLineWidth(2)
 pt.AddText(labelsZ[i])
 

 
 cname = "cpullsz_%i"%i
 cpullsz = get_canvas(cname)
 cpullsz.cd() 
 pullsz[i].Draw("PE")

 f = rt.TF1("func","gaus(0)",-10,10)
 f.SetParameter(0,10)
 f.SetParError(0,5)
 f.SetParameter(1,0)
 f.SetParError(1,0.5)
 f.SetParameter(2,4)
 f.SetParError(2,2)
 pullsz[i].Fit("func")
 
 pt.Draw()

 cpullsz.SaveAs(options.outdir+"/"+cpullsz.GetName()+".png","pdf")
 cpullsz.SaveAs(options.outdir+"/"+cpullsz.GetName()+".pdf","pdf")
 cpullsz.SaveAs(options.outdir+"/"+cpullsz.GetName()+".C")


#xbinMin = [hin.GetXaxis().FindBin(173)+1]
#xbinMax = [binsx]


hin_PTUp = fin.Get("histo_PTUp")
hin_PTUp.Scale(1./hin_PTUp.Integral())
hin_PTDown = fin.Get("histo_PTDown")
hin_PTDown.Scale(1./hin_PTDown.Integral())
hin_OPTUp = fin.Get("histo_OPTUp")
hin_OPTUp.Scale(1./hin_OPTUp.Integral())
hin_OPTDown = fin.Get("histo_OPTDown")
hin_OPTDown.Scale(1./hin_OPTDown.Integral())
hin_altshapeUp = fin.Get("histo_altshapeUp")
hin_altshapeUp.Scale(1./hin_altshapeUp.Integral())
hin_altshapeDown = fin.Get("histo_altshapeDown")
hin_altshapeDown.Scale(1./hin_altshapeDown.Integral())
hin_altshape2Up = fin.Get("histo_altshape2Up")
hin_altshape2Up.Scale(1./hin_altshape2Up.Integral())
hin_altshape2Down = fin.Get("histo_altshape2Down")
hin_altshape2Down.Scale(1./hin_altshape2Down.Integral())
#hin_altshape3Up = fin.Get("histo_altshape3Up")
#hin_altshape3Up.Scale(1./hin_altshape3Up.Integral())
#hin_altshape3Down = fin.Get("histo_altshape3Down")
#hin_altshape3Down.Scale(1./hin_altshape3Down.Integral())
hin_TurnOnUp = fin.histo_TurnOnUp
hin_TurnOnUp.Scale(1./hin_TurnOnUp.Integral())
hin_TurnOnDown = fin.histo_TurnOnDown
hin_TurnOnDown.Scale(1./hin_TurnOnDown.Integral())
'''
hin_PT3Up = fin.Get("histo_PT3Up")
hin_PT3Up.Scale(1./hin_PT3Up.Integral())
hin_PT3Down = fin.Get("histo_PT3Down")
hin_PT3Down.Scale(1./hin_PT3Down.Integral())
hin_OPT3Up = fin.Get("histo_OPT3Up")
hin_OPT3Up.Scale(1./hin_OPT3Up.Integral())
hin_OPT3Down = fin.Get("histo_OPT3Down")
hin_OPT3Down.Scale(1./hin_OPT3Down.Integral())

hin_PT4Up = fin.Get("histo_PT4Up")
hin_PT4Up.Scale(1./hin_PT4Up.Integral())
hin_PT4Down = fin.Get("histo_PT4Down")
hin_PT4Down.Scale(1./hin_PT4Down.Integral())
hin_OPT4Up = fin.Get("histo_OPT4Up")
hin_OPT4Up.Scale(1./hin_OPT4Up.Integral())
hin_OPT4Down = fin.Get("histo_OPT4Down")
hin_OPT4Down.Scale(1./hin_OPT4Down.Integral())
'''

hz_PTUp = hin_PTUp.ProjectionZ("pz_PTUp",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_PTUp.SetLineColor(rt.kMagenta)
hz_PTUp.Scale(1./hz_PTUp.Integral())
hz_PTDown = hin_PTDown.ProjectionZ("pz_PTDown",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_PTDown.SetLineColor(rt.kMagenta)
hz_PTDown.Scale(1./hz_PTDown.Integral())
hz_OPTUp = hin_OPTUp.ProjectionZ("pz_OPTUp",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_OPTUp.SetLineColor(210)
hz_OPTUp.Scale(1./hz_OPTUp.Integral())
hz_OPTDown = hin_OPTDown.ProjectionZ("pz_OPTDown",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_OPTDown.SetLineColor(210)
hz_OPTDown.Scale(1./hz_OPTDown.Integral())
hz_altshapeUp = hin_altshapeUp.ProjectionZ("pz_altshapeUp",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_altshapeUp.SetLineColor(rt.kBlue)
hz_altshapeUp.Scale(1./hz_altshapeUp.Integral())
hz_altshapeDown = hin_altshapeDown.ProjectionZ("pz_altshapeDown",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_altshapeDown.SetLineColor(rt.kBlue)
hz_altshapeDown.Scale(1./hz_altshapeDown.Integral())
hz_altshape2Up = hin_altshape2Up.ProjectionZ("pz_altshape2Up",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_altshape2Up.SetLineColor(rt.kRed)
hz_altshape2Up.Scale(1./hz_altshape2Up.Integral())
hz_altshape2Down = hin_altshape2Down.ProjectionZ("pz_altshape2Down",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_altshape2Down.SetLineColor(rt.kRed)
hz_altshape2Down.Scale(1./hz_altshape2Down.Integral())
#hz_altshape3Up = hin_altshape3Up.ProjectionZ("pz_altshape3Up",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
#hz_altshape3Up.SetLineColor(rt.kOrange+1)
#hz_altshape3Down = hin_altshape3Down.ProjectionZ("pz_altshape3Down",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
#hz_altshape3Down.SetLineColor(rt.kOrange+1)
hz_TurnOnUp = hin_TurnOnUp.ProjectionZ("pz_TurnOnUp",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_TurnOnUp.SetLineColor(rt.kViolet-6)
hz_TurnOnUp.Scale(1./hz_TurnOnUp.Integral())
hz_TurnOnDown = hin_TurnOnDown.ProjectionZ("pz_TurnOnDown",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_TurnOnDown.SetLineColor(rt.kViolet-6)
hz_TurnOnDown.Scale(1./hz_TurnOnDown.Integral())
'''
hz_OPT3Up = hin_OPT3Up.ProjectionZ("pz_OPT3Up",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_OPT3Up.SetLineColor(rt.kViolet-6)
hz_OPT3Up.Scale(1./hz_OPT3Up.Integral())
hz_OPT3Down = hin_OPT3Down.ProjectionZ("pz_OPT3Down",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_OPT3Down.SetLineColor(rt.kViolet-6)
hz_OPT3Down.Scale(1./hz_OPT3Down.Integral())

hz_PT3Up = hin_PT3Up.ProjectionZ("pz_PT3Up",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_PT3Up.SetLineColor(rt.kViolet-1)
hz_PT3Up.Scale(1./hz_PT3Up.Integral())
hz_PT3Down = hin_PT3Down.ProjectionZ("pz_PT3Down",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_PT3Down.SetLineColor(rt.kViolet-1)
hz_PT3Down.Scale(1./hz_PT3Down.Integral())

hz_OPT4Up = hin_OPT4Up.ProjectionZ("pz_OPT4Up",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_OPT4Up.SetLineColor(rt.kViolet-7)
hz_OPT4Up.Scale(1./hz_OPT4Up.Integral())
hz_OPT4Down = hin_OPT4Down.ProjectionZ("pz_OPT4Down",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_OPT4Down.SetLineColor(rt.kViolet-7)
hz_OPT4Down.Scale(1./hz_OPT4Down.Integral())

hz_PT4Up = hin_PT4Up.ProjectionZ("pz_PT4Up",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_PT4Up.SetLineColor(rt.kViolet-2)
hz_PT4Up.Scale(1./hz_PT4Up.Integral())
hz_PT4Down = hin_PT4Down.ProjectionZ("pz_PT4Down",xbinMin[0],xbinMax[0],xbinMin[0],xbinMax[0])
hz_PT4Down.SetLineColor(rt.kViolet-2)
hz_PT4Down.Scale(1./hz_PT4Down.Integral())
'''
hzMC[0].Scale(1./hzMC[0].Integral())
hz[0].Scale(1./hz[0].Integral())

#leg3 = rt.TLegend(0.6,0.55,0.95,0.8)
leg3 = rt.TLegend(0.53,0.55,0.78,0.89)
leg3.SetBorderSize(0)
leg3.SetTextSize(0.035)
if prelim.find("thesis")==-1: leg3.AddEntry(hzMC[0],"Simulation (%s)"%(options.label),"LP")
leg3.AddEntry(hz[0],"Template","L")

leg3.AddEntry(hz_PTUp,"#propto m_{jj} up/down","L")
leg3.AddEntry(hz_OPTUp,"#propto 1/m_{jj} up/down","L")
leg3.AddEntry(hz_altshapeUp,"HERWIG up/down","L")
leg3.AddEntry(hz_altshape2Up,"MADGRAPH+PYTHIA up/down","L")
#leg3.AddEntry(hz_altshape3Up,"POWHEG up/down","L")
leg3.AddEntry(hz_TurnOnUp,"m_{jj} turn-on up/down","L")
'''
leg3.AddEntry(hz_OPT3Up,"OPT3","L")
leg3.AddEntry(hz_PT3Up," PT3","L")
leg3.AddEntry(hz_OPT4Up,"OPT4","L")
leg3.AddEntry(hz_PT4Up," PT4","L")
'''
czSyst = get_canvas("czSyst")
czSyst.cd()
czSyst.SetLogy()

#hz[4].SetLineColor(rt.kBlack)
#hz[4].Scale(1./0.001)
hz[0].SetMinimum(1E-011)
hz[0].SetMaximum(100.0)
hz[0].GetXaxis().SetTitleSize(0.05)
hz[0].GetXaxis().SetLabelSize(0.05)
hz[0].GetYaxis().SetTitleSize(0.05)
hz[0].GetYaxis().SetTitleOffset(1.2)
hz[0].GetYaxis().SetLabelSize(0.05)
hz[0].Draw("HIST")
hz_PTUp.Draw("HISTsame")
hz_PTDown.Draw("HISTsame") 
hz_OPTUp.Draw("HISTsame")
hz_OPTDown.Draw("HISTsame")
hz_altshapeUp.Draw("HISTsame")
hz_altshapeDown.Draw("HISTsame")
hz_altshape2Up.Draw("HISTsame")
hz_altshape2Down.Draw("HISTsame")
#hz_altshape3Up.Draw("HISTsame")
#hz_altshape3Down.Draw("HISTsame")
#hzMC[4].SetLineColor(rt.kBlack)
#hzMC[4].SetMarkerColor(rt.kBlack)
#hzMC[4].Scale(1./0.001)
hz_TurnOnUp.Draw("HISTsame")
hz_TurnOnDown.Draw("HISTsame")
'''
hz_OPT3Up.Draw("HISTsame")
hz_OPT3Down.Draw("HISTsame")
hz_PT3Up.Draw("HISTsame")
hz_PT3Down.Draw("HISTsame")
hz_OPT4Up.Draw("HISTsame")
hz_OPT4Down.Draw("HISTsame")
hz_PT4Up.Draw("HISTsame")
hz_PT4Down.Draw("HISTsame")
'''
if prelim.find("thesis")==-1:hzMC[0].Draw("same")
leg3.Draw()

#CMS_lumi.CMS_lumi(czSyst, 0, 11)
if prelim.find("prelim")!=-1:
 CMS_lumi.cmslabel_sim_prelim(czSyst,'sim',11)
elif prelim.find("thesis")!=-1:
 CMS_lumi.cmslabel_thesis(czSyst,'sim',0)
else:
 CMS_lumi.cmslabel_sim(czSyst,'sim',11)
czSyst.cd()
czSyst.Update()
czSyst.RedrawAxis()
frame = czSyst.GetFrame()
frame.Draw()
czSyst.SaveAs(options.outdir+"/czSyst.png","pdf")
czSyst.SaveAs(options.outdir+"/czSyst.pdf","pdf")
# sleep(10000)
hx_PTUp = hin_PTUp.ProjectionX("px_PTUp",1,binsy,zbinMin[0],zbinMax[0])
hx_PTUp.SetLineColor(rt.kMagenta)
hx_PTUp.Scale(1./hx_PTUp.Integral())
hx_PTUp.Rebin(2)
hx_PTDown = hin_PTDown.ProjectionX("px_PTDown",1,binsy,zbinMin[0],zbinMax[0])
hx_PTDown.SetLineColor(rt.kMagenta)
hx_PTDown.Scale(1./hx_PTDown.Integral())
hx_PTDown.Rebin(2)
hx_OPTUp = hin_OPTUp.ProjectionX("px_OPTUp",1,binsy,zbinMin[0],zbinMax[0])
hx_OPTUp.SetLineColor(210)
hx_OPTUp.Scale(1./hx_OPTUp.Integral())
hx_OPTUp.Rebin(2)
hx_OPTDown = hin_OPTDown.ProjectionX("px_OPTDown",1,binsy,zbinMin[0],zbinMax[0])
hx_OPTDown.SetLineColor(210)
hx_OPTDown.Scale(1./hx_OPTDown.Integral())
hx_OPTDown.Rebin(2)
hx_altshapeUp = hin_altshapeUp.ProjectionX("px_altshapeUp",1,binsy,zbinMin[0],zbinMax[0])
hx_altshapeUp.SetLineColor(rt.kBlue)
hx_altshapeUp.Scale(1./hx_altshapeUp.Integral())
hx_altshapeUp.Rebin(2)
hx_altshapeDown = hin_altshapeDown.ProjectionX("px_altshapeDown",1,binsy,zbinMin[0],zbinMax[0])
hx_altshapeDown.SetLineColor(rt.kBlue)
hx_altshapeDown.Scale(1./hx_altshapeDown.Integral())
hx_altshapeDown.Rebin(2)
hx_altshape2Up = hin_altshape2Up.ProjectionX("px_altshape2Up",1,binsy,zbinMin[0],zbinMax[0])
hx_altshape2Up.SetLineColor(rt.kRed)
hx_altshape2Up.Scale(1./hx_altshape2Up.Integral())
hx_altshape2Up.Rebin(2)
hx_altshape2Down = hin_altshape2Down.ProjectionX("px_altshape2Down",1,binsy,zbinMin[0],zbinMax[0])
hx_altshape2Down.SetLineColor(rt.kRed)
hx_altshape2Down.Scale(1./hx_altshape2Down.Integral())
hx_altshape2Down.Rebin(2)
#hx_altshape3Up = hin_altshape3Up.ProjectionX("px_altshape3Up",1,binsy,zbinMin[0],zbinMax[0])
#hx_altshape3Up.SetLineColor(rt.kOrange+1)
#hx_altshape3Down = hin_altshape3Down.ProjectionX("px_altshape3Down",1,binsy,zbinMin[0],zbinMax[0])
#hx_altshape3Down.SetLineColor(rt.kOrange+1)
hx_TurnOnUp = hin_TurnOnUp.ProjectionX("px_TurnOnUp",1,binsy,zbinMin[0],zbinMax[0])
hx_TurnOnUp.SetLineColor(rt.kViolet-6)
hx_TurnOnUp.Scale(1./hx_TurnOnUp.Integral())
hx_TurnOnUp.Rebin(2)
hx_TurnOnDown = hin_TurnOnDown.ProjectionX("px_TurnOnDown",1,binsy,zbinMin[0],zbinMax[0])
hx_TurnOnDown.SetLineColor(rt.kViolet-6)
hx_TurnOnDown.Scale(1./hx_TurnOnDown.Integral())
hx_TurnOnDown.Rebin(2)
'''
hx_OPT3Up = hin_OPT3Up.ProjectionX("px_OPT3Up",1,binsy,zbinMin[0],zbinMax[0])
hx_OPT3Up.SetLineColor(rt.kViolet-6)
hx_OPT3Up.Scale(1./hx_OPT3Up.Integral())
hx_OPT3Down = hin_OPT3Down.ProjectionX("px_OPT3Down",1,binsy,zbinMin[0],zbinMax[0])
hx_OPT3Down.SetLineColor(rt.kViolet-6)
hx_OPT3Down.Scale(1./hx_OPT3Down.Integral())


hx_PT3Up = hin_PT3Up.ProjectionX("px_PT3Up",1,binsy,zbinMin[0],zbinMax[0])
hx_PT3Up.SetLineColor(rt.kViolet-1)
hx_PT3Up.Scale(1./hx_PT3Up.Integral())
hx_PT3Down = hin_PT3Down.ProjectionX("px_PT3Down",1,binsy,zbinMin[0],zbinMax[0])
hx_PT3Down.SetLineColor(rt.kViolet-1)
hx_PT3Down.Scale(1./hx_PT3Down.Integral())

hx_OPT4Up = hin_OPT4Up.ProjectionX("px_OPT4Up",1,binsy,zbinMin[0],zbinMax[0])
hx_OPT4Up.SetLineColor(rt.kViolet-7)
hx_OPT4Up.Scale(1./hx_OPT4Up.Integral())
hx_OPT4Down = hin_OPT4Down.ProjectionX("px_OPT4Down",1,binsy,zbinMin[0],zbinMax[0])
hx_OPT4Down.SetLineColor(rt.kViolet-7)
hx_OPT4Down.Scale(1./hx_OPT4Down.Integral())

hx_PT4Up = hin_PT4Up.ProjectionX("px_PT4Up",1,binsy,zbinMin[0],zbinMax[0])
hx_PT4Up.SetLineColor(rt.kViolet-2)
hx_PT4Up.Scale(1./hx_PT4Up.Integral())
hx_PT4Down = hin_PT4Down.ProjectionX("px_PT4Down",1,binsy,zbinMin[0],zbinMax[0])
hx_PT4Down.SetLineColor(rt.kViolet-2)
hx_PT4Down.Scale(1./hx_PT4Down.Integral())
'''

hxMC[0].Scale(1./hxMC[0].Integral())
hx[0].Scale(1./hx[0].Integral())
#leg3 = rt.TLegend(0.6,0.55,0.95,0.8)
leg3 = rt.TLegend(0.53,0.55,0.78,0.89)
leg3.SetBorderSize(0)
leg3.SetTextSize(0.035)
if prelim.find("thesis")==-1: leg3.AddEntry(hxMC[0],"Simulation (%s)"%(options.label),"LP")
leg3.AddEntry(hx[0],"Template","L")
leg3.AddEntry(hx_PTUp,"#propto m_{jj} up/down","L")
leg3.AddEntry(hx_OPTUp,"#propto 1/m_{jj} up/down","L")
leg3.AddEntry(hx_altshapeUp,"HERWIG up/down","L")
leg3.AddEntry(hx_altshape2Up,"MADGRAPH+PYTHIA up/down","L")
#leg3.AddEntry(hx_altshape3Up,"POWHEG up/down","L")
leg3.AddEntry(hx_TurnOnUp,"m_{jj} turn-on up/down","L")
'''
leg3.AddEntry(hx_OPT3Up,"OPT3","L")
leg3.AddEntry(hx_PT3Up,"PT3","L")
leg3.AddEntry(hx_OPT4Up,"OPT4","L")
leg3.AddEntry(hx_PT4Up,"PT4","L")
'''
cxSyst = get_canvas("cxSyst")
cxSyst.cd()

hx[0].SetMinimum(0)
hx[0].SetMaximum(0.08)
hx[0].GetXaxis().SetTitleSize(0.05)
hx[0].GetXaxis().SetLabelSize(0.05)
hx[0].GetYaxis().SetTitleSize(0.05)
hx[0].GetYaxis().SetTitleOffset(1.2)
hx[0].GetYaxis().SetLabelSize(0.05)


hx[0].Draw("HIST")
hx_PTUp.Draw("HISTsame")
hx_PTDown.Draw("HISTsame") 
hx_OPTUp.Draw("HISTsame")
hx_OPTDown.Draw("HISTsame")
hx_altshapeUp.Draw("HISTsame")
hx_altshapeDown.Draw("HISTsame")
hx_altshape2Up.Draw("HISTsame")
hx_altshape2Down.Draw("HISTsame")
#hx_altshape3Up.Draw("HISTsame")
#hx_altshape3Down.Draw("HISTsame")
hx_TurnOnUp.Draw("HISTsame")
hx_TurnOnDown.Draw("HISTsame")
'''
hx_OPT3Up.Draw("HISTsame")
hx_OPT3Down.Draw("HISTsame")

hx_PT3Up.Draw("HISTsame")
hx_PT3Down.Draw("HISTsame")

hx_OPT4Up.Draw("HISTsame")
hx_OPT4Down.Draw("HISTsame")
hx_PT4Up.Draw("HISTsame")
hx_PT4Down.Draw("HISTsame")
'''
if prelim.find("thesis")==-1:hxMC[0].Draw("same")
leg3.Draw()

if prelim.find("prelim")!=-1:
 CMS_lumi.cmslabel_sim_prelim(cxSyst,'sim',11)
elif prelim.find("thesis")!=-1:
 CMS_lumi.cmslabel_thesis(cxSyst,'sim',0)
else:
 CMS_lumi.cmslabel_sim(cxSyst,'sim',11)
cxSyst.cd()
cxSyst.Update()
cxSyst.RedrawAxis()
frame = cxSyst.GetFrame()
frame.Draw()
cxSyst.SaveAs(options.outdir+"/cxSyst.png","pdf")
cxSyst.SaveAs(options.outdir+"/cxSyst.pdf","pdf")


hy_PTUp = hin_PTUp.ProjectionY("py_PTUp",1,binsy,zbinMin[0],zbinMax[0])
hy_PTUp.SetLineColor(rt.kMagenta)
hy_PTUp.Scale(1./hy_PTUp.Integral())
hy_PTUp.Rebin(2)
hy_PTDown = hin_PTDown.ProjectionY("py_PTDown",1,binsy,zbinMin[0],zbinMax[0])
hy_PTDown.SetLineColor(rt.kMagenta)
hy_PTDown.Scale(1./hy_PTDown.Integral())
hy_PTDown.Rebin(2)
hy_OPTUp = hin_OPTUp.ProjectionY("py_OPTUp",1,binsy,zbinMin[0],zbinMax[0])
hy_OPTUp.SetLineColor(210)
hy_OPTUp.Scale(1./hy_OPTUp.Integral())
hy_OPTUp.Rebin(2)
hy_OPTDown = hin_OPTDown.ProjectionY("py_OPTDown",1,binsy,zbinMin[0],zbinMax[0])
hy_OPTDown.SetLineColor(210)
hy_OPTDown.Scale(1./hy_OPTDown.Integral())
hy_OPTDown.Rebin(2)
hy_altshapeUp = hin_altshapeUp.ProjectionY("py_altshapeUp",1,binsy,zbinMin[0],zbinMax[0])
hy_altshapeUp.SetLineColor(rt.kBlue)
hy_altshapeUp.Scale(1./hy_altshapeUp.Integral())
hy_altshapeUp.Rebin(2)
hy_altshapeDown = hin_altshapeDown.ProjectionY("py_altshapeDown",1,binsy,zbinMin[0],zbinMax[0])
hy_altshapeDown.SetLineColor(rt.kBlue)
hy_altshapeDown.Scale(1./hy_altshapeDown.Integral())
hy_altshapeDown.Rebin(2)
hy_altshape2Up = hin_altshape2Up.ProjectionY("py_altshape2Up",1,binsy,zbinMin[0],zbinMax[0])
hy_altshape2Up.SetLineColor(rt.kRed)
hy_altshape2Up.Scale(1./hy_altshape2Up.Integral())
hy_altshape2Up.Rebin(2)
hy_altshape2Down = hin_altshape2Down.ProjectionY("py_altshape2Down",1,binsy,zbinMin[0],zbinMax[0])
hy_altshape2Down.SetLineColor(rt.kRed)
hy_altshape2Down.Scale(1./hy_altshape2Down.Integral())
hy_altshape2Down.Rebin(2)
#hy_altshape3Up = hin_altshape3Up.ProjectionY("py_altshape3Up",1,binsy,zbinMin[0],zbinMax[0])
#hy_altshape3Up.SetLineColor(rt.kOrange+1)
#hy_altshape3Down = hin_altshape3Down.ProjectionY("py_altshape3Down",1,binsy,zbinMin[0],zbinMax[0])
#hy_altshape3Down.SetLineColor(rt.kOrange+1)
hy_TurnOnUp = hin_TurnOnUp.ProjectionY("py_TurnOnUp",xbinMin[0],xbinMax[0],zbinMin[0],zbinMax[0])
hy_TurnOnUp.SetLineColor(rt.kViolet-6)
hy_TurnOnUp.Scale(1./hy_TurnOnUp.Integral())
hy_TurnOnUp.Rebin(2)
hy_TurnOnDown = hin_TurnOnDown.ProjectionY("py_TurnOnDown",xbinMin[0],xbinMax[0],zbinMin[0],zbinMax[0])
hy_TurnOnDown.SetLineColor(rt.kViolet-6)
hy_TurnOnDown.Scale(1./hy_TurnOnDown.Integral())
hy_TurnOnDown.Rebin(2)
'''
hy_OPT3Up = hin_OPT3Up.ProjectionY("py_OPT3Up",xbinMin[0],xbinMax[0],zbinMin[0],zbinMax[0])
hy_OPT3Up.SetLineColor(rt.kViolet-6)
hy_OPT3Up.Scale(1./hy_OPT3Up.Integral())
hy_OPT3Down = hin_OPT3Down.ProjectionY("py_OPT3Down",xbinMin[0],xbinMax[0],zbinMin[0],zbinMax[0])
hy_OPT3Down.SetLineColor(rt.kViolet-6)
hy_OPT3Down.Scale(1./hy_OPT3Down.Integral())
'''
hyMC[0].Scale(1./hyMC[0].Integral())
hy[0].Scale(1./hy[0].Integral())
#leg3 = rt.TLegend(0.6,0.55,0.95,0.8)
leg3 = rt.TLegend(0.53,0.50,0.78,0.84)
leg3.SetBorderSize(0)
leg3.SetTextSize(0.035)
if prelim.find("thesis")==-1: leg3.AddEntry(hyMC[0],"Simulation (%s)"%(options.label),"LP")
leg3.AddEntry(hy[0],"Template","L")
leg3.AddEntry(hy_PTUp,"#propto m_{jj} up/down","L")
leg3.AddEntry(hy_OPTUp,"#propto 1/m_{jj} up/down","L")
leg3.AddEntry(hy_altshapeUp,"HERWIG up/down","L")
leg3.AddEntry(hy_altshape2Up,"MADGRAPH+PYTHIA up/down","L")
#leg3.AddEntry(hy_altshape3Up,"POWHEG up/down","L")
leg3.AddEntry(hy_TurnOnUp,"m_{jj} turn on up/down","L")



cySyst = get_canvas("cySyst")
cySyst.cd()

hy[0].SetMinimum(0)
hy[0].SetMaximum(0.08)

hy[0].GetXaxis().SetTitleSize(0.05)
hy[0].GetXaxis().SetLabelSize(0.05)
hy[0].GetYaxis().SetTitleSize(0.05)
hy[0].GetYaxis().SetTitleOffset(1.2)
hy[0].GetYaxis().SetLabelSize(0.05)
hy[0].Draw("HIST")
hy_PTUp.Draw("HISTsame")
hy_PTDown.Draw("HISTsame") 
hy_OPTUp.Draw("HISTsame")
hy_OPTDown.Draw("HISTsame")
hy_altshapeUp.Draw("HISTsame")
hy_altshapeDown.Draw("HISTsame")
hy_altshape2Up.Draw("HISTsame")
hy_altshape2Down.Draw("HISTsame")
#hy_altshape3Up.Draw("HISTsame")
#hy_altshape3Down.Draw("HISTsame")
hy_TurnOnUp.Draw("HISTsame")
hy_TurnOnDown.Draw("HISTsame")
if prelim.find("thesis")==-1:hyMC[0].Draw("same")

leg3.Draw()

if prelim.find("prelim")!=-1:
 CMS_lumi.cmslabel_sim_prelim(cySyst,'sim',11)
elif prelim.find("thesis")!=-1:
 CMS_lumi.cmslabel_thesis(cySyst,'sim',0)
else:
 CMS_lumi.cmslabel_sim(cySyst,'sim',11)

cySyst.cd()
cySyst.Update()
cySyst.RedrawAxis()
frame = cySyst.GetFrame()
frame.Draw()
cySyst.SaveAs(options.outdir+"/cySyst.png","pdf")
cySyst.SaveAs(options.outdir+"/cySyst.pdf","pdf")



'''
TCanvas* cxz = new TCanvas("cxz","cxz")
cxz.cd()
TH2F* hxz = (TH2F*)hin.Project3D("zx")
hxz.Draw("COLZ")

cxz.SaveAs(TString(outDirName)+TString("/")+TString("cxz.png"),"pdf")

TCanvas* cyz = new TCanvas("cyz","cyz")
cyz.cd()
TH2F* hyz = (TH2F*)hin.Project3D("zy")
hyz.Draw("COLZ")

cyz.SaveAs(TString(outDirName)+TString("/")+TString("cyz.png"),"pdf")

}

'''
