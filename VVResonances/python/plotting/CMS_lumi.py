import ROOT as rt

class CMSPlotLabel:
    def __init__(self,text='CMS',extraText='Preliminary',lumiPeriods={'2015':{'lumi':'2.6 fb^{-1}','energy':'13 TeV'},'2016':{'lumi':'36 fb^{-1}','energy':'13 TeV'},'2017':{'lumi':'(2017) 42 fb^{-1}','energy':'13 TeV'},'2018':{'lumi':'60 fb^{-1} ','energy':'(13 TeV)'},'ALL':{'lumi':'138 fb^{-1} ','energy':'(13 TeV)'},'sim17':{'lumi':'(2017)','energy':'13 TeV'},'sim16':{'lumi':'(2016)','energy':'13 TeV'},'sim':{'lumi':'','energy':'13 TeV'}}):
        self.cmsText=text
        self.cmsTextFont=61
        self.extraText=extraText
        self.extraTextFont=52
        self.lumiTextSize=0.6
        self.lumiTextOffset=0.2
        self.cmsTextSize=0.6
        self.cmsTextOffset=0.1
        
        self.relPosX    = 0.045
        self.relPosY    = 0.035
        self.relExtraDY = 1.2

        self.extraOverCmsTextSize  = 0.76
        self.periods=lumiPeriods
        self.drawLogo=False

        if extraText!='':
            self.writeExtraText=1
        else:
            self.writeExtraText=0

    def __call__(self,pad,iPeriod,iPosX):    
        outOfFrame    = False
        if(iPosX/10==0 ): outOfFrame = True

        alignY_=3
        alignX_=2
        if( iPosX/10==0 ): alignX_=1
        if( iPosX==0    ): alignY_=1
        if( iPosX/10==1 ): alignX_=1
        if( iPosX/10==2 ): alignX_=2
        if( iPosX/10==3 ): alignX_=3
        align_ = 10*alignX_ + alignY_

        H = pad.GetWh()
        W = pad.GetWw()
        l = pad.GetLeftMargin()
        t = pad.GetTopMargin()
        r = pad.GetRightMargin()
        b = pad.GetBottomMargin()
        e = 0.025

        pad.cd()
        
        lumiText = self.periods[iPeriod]['lumi']+""+self.periods[iPeriod]['energy']+""
        #if self.extraText=='Simulation':
        #    lumiText=''


        latex = rt.TLatex()
        latex.SetNDC()
        latex.SetTextAngle(0)
        latex.SetTextColor(rt.kBlack)    
    
        extraTextSize = self.extraOverCmsTextSize*self.cmsTextSize
    
        latex.SetTextFont(42)
        latex.SetTextAlign(31) 
        latex.SetTextSize(self.lumiTextSize*t)    

        latex.DrawLatex(1-r,1-t+self.lumiTextOffset*t,lumiText)

        if( outOfFrame ):
            latex.SetTextFont(self.cmsTextFont)
            latex.SetTextAlign(11) 
            latex.SetTextSize(self.cmsTextSize*t)    
            latex.DrawLatex(l,1-t+self.lumiTextOffset*t,self.cmsText)
  
        pad.cd()

        posX_ = 0
        if( iPosX%10<=1 ):
            posX_ =   l + self.relPosX*(1-l-r)
        elif( iPosX%10==2 ):
            posX_ =  l + 0.5*(1-l-r)
        elif( iPosX%10==3 ):
            posX_ =  1-r - self.relPosX*(1-l-r)

        posY_ = 1-t - self.relPosY*(1-t-b)

        if( not outOfFrame ):
            if( self.drawLogo ):
                posX_ =   l + 0.045*(1-l-r)*W/H
                posY_ = 1-t - 0.045*(1-t-b)
                xl_0 = posX_
                yl_0 = posY_ - 0.15
                xl_1 = posX_ + 0.15*H/W
                yl_1 = posY_
                CMS_logo = rt.TASImage("CMS-BW-label.png")
                pad_logo =  rt.TPad("logo","logo", xl_0, yl_0, xl_1, yl_1 )
                pad_logo.Draw()
                pad_logo.cd()
                CMS_logo.Draw("X")
                pad_logo.Modified()
                pad.cd()          
            else:
                latex.SetTextFont(self.cmsTextFont)
                latex.SetTextSize(self.cmsTextSize*t)
                latex.SetTextAlign(align_)
                latex.DrawLatex(posX_, posY_, self.cmsText)
                if( self.writeExtraText ) :
                    latex.SetTextFont(self.extraTextFont)
                    latex.SetTextAlign(align_)
                    latex.SetTextSize(extraTextSize*t)
                    latex.DrawLatex(posX_, posY_- self.relExtraDY*self.cmsTextSize*t, self.extraText)
        elif( self.writeExtraText ):
            if( iPosX==0):
                posX_ =   l +  self.relPosX*(1-l-r)
                posY_ =   1-t+self.lumiTextOffset*t

            latex.SetTextFont(self.extraTextFont)
            latex.SetTextSize(extraTextSize*t)
            latex.SetTextAlign(align_)
            latex.DrawLatex(posX_, posY_, self.extraText)      

        pad.Update()


cmslabel_prelim=CMSPlotLabel("CMS","Preliminary")
cmslabel_int=CMSPlotLabel("CMS","Internal")
cmslabel_sim=CMSPlotLabel("CMS","Simulation")
cmslabel_thesis=CMSPlotLabel("","Simulation",{'sim':{'lumi':'','energy':'13 TeV'}})
cmslabel_empty=CMSPlotLabel("",'')
cmslabel_sim_prelim=CMSPlotLabel("CMS","Simulation Preliminary")
cmslabel_final=CMSPlotLabel("CMS")



