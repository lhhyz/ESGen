# !/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 Reference Prediction ScoreSaveFile" >&2
    exit 1
fi

REF=$1
PRED=$2
FILE=$3


filePath=${FILE}
if [ ! -f "$filePath" ];then
touch $filePath
echo "score.txt创建完成"
else
echo "score.txt已经存在"
fi


echo "$(date)" >> ${FILE}

echo "Bleu-B-Norm:" >> ${FILE}
python ./Metrics/Bleu-B-Norm.py ${REF} < ${PRED} >> ${FILE};
echo "Rouge:" >> ${FILE}
python ./Metrics/Rouge.py --ref_path ${REF} --gen_path ${PRED} >> ${FILE};
echo "Meteor:" >> ${FILE}
python ./Metrics/Meteor.py --ref_path ${REF} --gen_path ${PRED} >> ${FILE};
echo "Bleu-Penalty:" >> ${FILE}
python ./Metrics/Bleu-Penalty.py ${REF} < ${PRED} >> ${FILE};
echo "BLUE:" >> ${FILE}
nlg-eval --hypothesis=${PRED}  --references=${REF}>> ${FILE}



echo "评分完成"
echo " " >> ${FILE}
echo " " >> ${FILE}