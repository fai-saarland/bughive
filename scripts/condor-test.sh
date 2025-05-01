#!/usr/bin/env bash

if [ $# -ne 0 ] 
then
    echo "condor-test.sh expects no arguments" > /dev/stderr
    exit 1
fi

script_dir=$(realpath "$(dirname "$0")")
test_script="${script_dir}/condor-test.py"
policy_path=$(realpath "$(cat)")
policy_dir=$(dirname "$policy_path")
policy_filename=$(basename -- "$policy_path")
policy_name="${policy_filename%.*}"

cd "$policy_dir" || (echo "fatal: cannot cd into directory of policy file" > /dev/stderr 1 && exit 1)
mkdir "testdata-$policy_name" || exit 1
cd "testdata-$policy_name" || exit 1
ln -s "$policy_path" "$policy_filename"

cp "$test_script" .
./condor-test.py 1 2 3 4 2> test.err 1> test.out

if [ -e results.toml ]
then
	secs=$SECONDS
	echo "Testing finished in $secs seconds" >> test.out
	echo "testing_time = $secs" >> results.toml
else
  echo "No testing results file generated" > /dev/stderr
  exit 1
fi

if [ -s test.err ]; then
  echo "There was output to test.err:" > /dev/stderr
  cat test.err > /dev/stderr
	exit 1
else
	rm test.err
	cat results.toml
fi

