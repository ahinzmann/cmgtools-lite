#!bin/bash
for i in $(seq 1 300); do 
    echo toy $i
    if [ ! -f higgsCombine_bfit_toy_jobs_$i.MultiDimFit.mH120.root ]; then
    echo "File not found!"
    fi  
    #COUNT=$(find higgsCombine_bfit_toy_jobs_$i.MultiDimFit.mH120.root  -size +1500c | wc -l)
    #echo count "${COUNT}"
    #if [ "${COUNT}" -lt 300 ]
    #then
	#echo incomplete!
	'''
	for j in ${splits[*]}; do
	    #echo $j
	    l=$((j+1))
	    #echo $l
	    if [ $(find higgsCombine_toy_$i.POINTS.$j.$l.MultiDimFit.mH120.root  -size +1500c  | wc -l) -lt 1 ]
	    then 
		echo this must be resubmitted!
		#combineTool.py  -M  MultiDimFit  results_Run2/workspace_JJ_WprimeWZ_VBF_VVVH_13TeV_Run2_data_afterpreapproval_newShapesFits.root --redefineSignalPOI MH --setParameters r=0 --algo=grid --setParameterRange MH=1250,6050:r=0,200 --points 48 --saveNLL -D higgsCombineTest.GenerateOnly.mH2700.123456.root:toys/toy_$i    --job-mode condor --sub-opts='+JobFlavour="workday"' --task-name mh_globalsignif_toys_test_${i}_points_${j}_${l}  --firstPoint $j --lastPoint $l -n _toy_$i.POINTS.$j.$l  #--split-points 2 --dry-run
		#k=$((j/2))
		#echo $k
	    fi

	done
    fi
done
