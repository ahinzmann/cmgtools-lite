#bin/bash!

period=Run2
inputdir=results_Run2/
extralabel=afterpreapproval_newShapesFits_100000
c=$1
ws=VBF_VVVH

name=_${extralabel} 
signal=BulkGWW

outputdir=postfit_data_SR_${signal}_${extralabel}_${period}_VplusH/
mkdir ${outputdir}
echo "############## make postfit for ##############"
label=postfit_data_SR_${signal}_${extralabel}_${period}_VplusH_${c}
echo $label

python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${inputdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M 2000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --doFit -x 65,140 -y 65,140 --proj z| tee ${label}.log
  

