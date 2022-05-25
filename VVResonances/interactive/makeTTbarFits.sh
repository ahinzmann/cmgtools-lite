#!bin/bash

## make pseudodata for ttbar only
#    python makeInputs.py -p 2016 --run "pseudoTT" 

#make the ws for ttbar only -> for the purpose of doing a ttbar only fit to get the true yields for the different ttbar contributions for the final fit 
# the workspaces need to be made with ttbar pseudodata from the ttbar-MC sample

period=Run2
c=$1
extralabel=""
dir=results_${period}/
wsdir=results_${period}/
signal=WprimeWZ

#outputdir=prefit_ttbar_${extralabel}_${period}/
#mkdir ${outputdir}
#echo "############## make prefit for ##############"
#label=prefit_ttbar_${extralabel}_${period}_${c}
#echo $label
#python runFitPlots_vjets_signal_bigcombo_splitRes.py -n results_${period}/workspace_JJ_BulkGWW_${c}_13TeV_${period}_ttbar.root  -i  results_${period}/JJ_${period}_nonRes_${c}.root -M 2000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --pseudo | tee ${label}.log


outputdir=postfit_ttbar_${extralabel}_${period}/
mkdir ${outputdir}

echo "############## make postfit for ##############"
label=postfit_ttbar_${name}_${period}_${c}
echo $label

python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${wsdir}/workspace_JJ_${signal}_${c}_13TeV_${period}_ttbar${extralabel}.root  -i  ${dir}/JJ_${period}_nonRes_${c}.root -M 2000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --doFit --pseudo | tee ${label}.log

## the fit produces json output files -> these are then included in the makeCard script to extract the yields if NOT pseudodata=ttbar
