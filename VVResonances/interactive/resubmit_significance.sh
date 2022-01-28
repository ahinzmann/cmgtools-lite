#!bin/bash
'''
toys=(1 2 3 4 5 6 7 8 9 10 11 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 54 87 88 89 90 95 96 97 98 99)

for i in ${toys[*]}; do
    echo $i 
    combineTool.py  -M  MultiDimFit  results_Run2/workspace_JJ_WprimeWZ_VBF_VVVH_13TeV_Run2_data_afterpreapproval_newShapesFits.root --redefineSignalPOI MH --setParameters r=0 --algo=grid --setParameterRange MH=1250,6050:r=0,200 --points 48 --saveNLL -D higgsCombineTest.GenerateOnly.mH2700.123456.root:toys/toy_$i -n _toy_$i    --job-mode condor --sub-opts='+JobFlavour="workday"' --task-name mh_globalsignif_toys_$i   --split-points 2  ;  

done
'''

splits=(0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 36 38 40 42 44 46 )
#splits=(34 36 38 40 42 44 46 )


for i in $(seq 1 300); do 
#for i in $(seq 281 300); do 
    echo toy $i  
    COUNT=$(find higgsCombine_toy_$i.POINTS.*.MultiDimFit.mH120.root  -size +1500c | wc -l)
    echo count "${COUNT}"
    if [ "${COUNT}" -lt 24 ]
    then
	echo incomplete!
	for j in ${splits[*]}; do
	    #echo $j
	    l=$((j+1))
	    #echo $l
	    if [ $(find higgsCombine_toy_$i.POINTS.$j.$l.MultiDimFit.mH120.root  -size +1500c  | wc -l) -lt 1 ]
	    then 
		echo this must be resubmitted!
		combineTool.py  -M  MultiDimFit  results_Run2/workspace_JJ_WprimeWZ_VBF_VVVH_13TeV_Run2_data_afterpreapproval_newShapesFits.root --redefineSignalPOI MH --setParameters r=0 --algo=grid --setParameterRange MH=1250,6050:r=0,200 --points 48 --saveNLL -D higgsCombineTest.GenerateOnly.mH2700.123456.root:toys/toy_$i    --job-mode condor --sub-opts='+JobFlavour="tomorrow"' --task-name mh_globalsignif_toys_test_${i}_points_${j}_${l}  --firstPoint $j --lastPoint $l -n _toy_$i.POINTS.$j.$l  #--split-points 2 --dry-run
		#k=$((j/2))
		#echo $k
	    fi
	done
    fi
done
