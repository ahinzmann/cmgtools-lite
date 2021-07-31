#bin/bash!

period=Run2
inputdir=results_Run2/
wsdir=results_Run2/
extralabel=afterpreapproval_newShapesFits_10000
c=$1
ws=VBF_VVVH
name=_${extralabel} 
signal=BulkGWW

outputdir=postfit_data_SR_VorH_bonly_${extralabel}_${period}/
mkdir ${outputdir}
echo "############## make postfit for ##############"
label=postfit_data_SR_VorH_bonly_${extralabel}_${period}_${c}
echo $label

python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${wsdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M 3000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --doFit -x 65,105 -y 110,140 --proj z --both | tee ${label}.log

  

