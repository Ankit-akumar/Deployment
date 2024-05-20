#!/bin/bash

username="$1"
password="$2"
hostname="$3"
cluster_name="$4"
namespace_name="$5"

output=$(expect << EOF
spawn ssh "$username@$hostname"
expect "password:"
send "$password\r"
expect "$ "
send "switch_cluster\r"
expect "Enter the cluster name: "
send "$cluster_name\r"
expect "$ "
send "switch_namespace\r"
expect "Enter the namespace: "
send "$namespace_name\r"
expect "$ "
send "kubectl get pods | grep -v Running\r"
expect "$ "
send "ls\r"
expect "$ "
send "kubectl get pods -n kube-system | grep -v Running\r"
expect "$ "
send "ls\r"
expect "$ "
send "uptime\r"
expect "$ "
send "exit\r"
expect eof
EOF
)

storeOutput() {
    start_storing_output=0
    stored_output=""
    while IFS= read -r line; do
        if [[ "$line" == *"$1"* ]]; then
            start_storing_output=1
            continue
        fi
        if [[ "$line" == *"$2"* && $start_storing_output -eq 1 ]]; then
            break
        fi
        if [[ $start_storing_output -eq 1 ]]; then
            stored_output+="$line"$'\n'
        fi
    done <<< "$output"
}

# Getting application pods not in running state
storeOutput "kubectl get pods | grep -v Running" "ls"
echo "$stored_output"
echo -e "app_pods\n$stored_output\nEND_OF_OUTPUT\n" > output_post.txt

# Getting system pods not in running state
storeOutput "kubectl get pods -n kube-system" "ls"
echo "$stored_output"
echo -e "system_pods\n$stored_output\nEND_OF_OUTPUT\n" >> output_post.txt

# Getting average load on the server
storeOutput "uptime" "exit"
stored_output=$(echo "$stored_output" | awk -F 'load average: ' '{print $2}')
echo "$stored_output"
echo -e "load_average\n$stored_output\nEND_OF_OUTPUT\n" >> output_post.txt