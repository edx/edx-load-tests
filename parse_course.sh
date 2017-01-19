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
    found_multiple_choice=0
    num_choices=0
    counter=2
    if grep --quiet -E "multiplechoiceresponse|stringresponse" $f; then
        echo -e "\t\t'"`basename $f .xml`"': {"
        echo -e "\t\t\t'inputs': {"
        cat $f |
        while read -r line || [[ -n "$line" ]]; do
            if [ $found_multiple_choice -eq 0 ]; then
                if [[ "$line" =~ ^\<choicegroup* ]]; then
                    found_multiple_choice=1
                fi
                string_rex="\<stringresponse answer=\"(.*)\" type=.*\>"
                if [[ $line =~ $string_rex ]]; then
                    echo -e "\t\t\t\t'_"$counter"_1': ('"${BASH_REMATCH[1]}"', ),"
                    ((counter++))
                fi
            else
                if [[ "$line" =~ ^\<\/choicegroup* ]]; then
                    echo -en "\t\t\t\t'_"$counter"_1': ["
                    for i in `seq 0 $num_choices`; do
                        echo -n "'choice_"$i"', "
                    done
                    echo "],"

                    found_multiple_choice=0
                    num_choices=0
                    ((counter++))
                else
                    ((num_choices++))
                fi
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
