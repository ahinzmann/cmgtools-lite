#bin/bash!

period=Run2
inputdir=results_Run2/

#extralabel=afterpreapproval_newShapesFits
extralabel=afterpreapproval_newShapesFits_10000000
c=$1
ws=VBF_VVVH

name=_${extralabel} 

#signal=VBF_RadionZZ
#mass=2000

signal=VBF_WprimeWZ
mass=1500



outputdir=prefit_data_SR_${signal}${mass}_${extralabel}_${period}_VplusH/
mkdir ${outputdir}
echo "############## make postfit for ##############"
label=prefit_data_blindSR_${signal}${mass}_${extralabel}_${period}_VplusH_${c}
echo $label
python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${inputdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M ${mass}  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --signalScaleF 0 -s  -x 65,140 -y 65,140 --proj z| tee ${label}.log

