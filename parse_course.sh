#!/bin/bash

rm -rf course/
tar -xf $1

echo
echo $2" = CourseData("

cd course/sequential/
echo -e "\tsequential_ids=("
for f in *; do
    echo -e "\t\t'"`basename $f .xml`"',"
done
echo -e "\t),"

cd ../problem/
echo -e "\tcapa_problems={"
for f in *; do
    found_problem=0
    num_choices=0
    counter=2
    if grep --quiet multiplechoiceresponse $f; then
        echo -e "\t\t'"`basename $f .xml`"': {"
        echo -e "\t\t\t'inputs': {"
        cat $f |
        while read -r line || [[ -n "$line" ]]; do
            if [ $found_problem -eq 0 ]; then
                if [[ "$line" =~ ^\<choicegroup* ]]; then
                    found_problem=1
                fi
            elif [[ "$line" =~ ^\<\/choicegroup* ]]; then
                echo -en "\t\t\t\t'_"$counter"_1': ["
                for i in `seq 0 $num_choices`; do
                    echo -n "'choice_"$i"', "
                done
                echo "],"

                found_problem=0
                num_choices=0
                ((counter++))
            else
                ((num_choices++))
            fi  
        done
        echo -e "\t\t\t},"
        echo -e "\t\t},"
    fi
done
echo -e "\t}"
echo ")"
cd ../../
rm -rf course/
