#!bin/bash

username="$1"
password="$2"
server="$3"
server_knode1="$4"
server_knode2="$5"

getPostgresPod() {
    get_postgres_pods="kubectl get pods | awk '/postgres/ && !/manager/ && !/postgres12/ {print \$1}'"
    command="echo '$password' | sudo -S $get_postgres_pods"
    postgres_pods=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command")

    postgres_pod=$(echo "$postgres_pods" | grep -v 'slave')
    echo "$postgres_pod"
}

getBotsTasks() {
    getPostgresPod
    echo "$postgres_pod"

    get_bot_tasks="kubectl exec -it $postgres_pod bash -- su - postgres -c 'psql -d bfspilot -c \"select bot_id, task_type from bots;\"'"
    command="echo '$password' | sudo -S $get_bot_tasks"
    bot_tasks=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command")
    echo "$bot_tasks"

    echo -e "bot_tasks\n" >output_pre.txt
    is_task=0
    while IFS= read -r line; do
        if [[ $line =~ [[:digit:]] ]]; then
            bot_id=$(echo "$line" | awk '{print $1}')
            task_type=$(echo "$line" | awk '{print $3}')
            if [[ ! -z "$task_type" ]]; then
                is_task=1
                echo -e "Bot ID: $bot_id, Task Type: $task_type\n" >> output_pre.txt
            fi
        fi
    done <<< "$bot_tasks"
    if [ "$is_task" -eq 0 ]; then
        echo -e "No tasks present on bots.\nEND_OF_OUTPUT\n" >> output_pre.txt
    else
        echo -e "END_OF_OUTPUT\n" >> output_pre.txt
    fi
}

getInductStatus() {
    getPostgresPod
    echo "$postgres_pod"

    get_induct_status="kubectl exec -it $postgres_pod bash -- su - postgres -c 'psql -d bfspilot -c \"select induct_id, status from inducts;\"'"
    command="echo '$password' | sudo -S $get_induct_status"
    induct_status=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command")
    echo "$induct_status"

    echo -e "induct_status\n" >>output_pre.txt

    IFS=$'\n' read -r -d '' -a lines <<< "$induct_status"

    converted_strings=()
    for ((i=2; i<${#lines[@]}-1; i++)); do
        IFS='|' read -r -a fields <<< "${lines[$i]}"
        induct_id=$(echo "${fields[0]}" | tr -d '[:space:]')
        status=$(echo "${fields[1]}" | tr -d '[:space:]')
        converted_string="Induct ID : $induct_id, Status : $status"
        converted_strings+=("$converted_string\n")
    done

    output_string=$(printf "%s\n" "${converted_strings[@]}")

    echo "$output_string"
    echo -e "$output_string\nEND_OF_OUTPUT\n" >>output_pre.txt
}

get_ws_status() {
    getPostgresPod
    echo "$postgres_pod"

    get_ws_status="kubectl exec -it $postgres_pod bash -- su - postgres -c 'psql -d bfspilot -c \"select wait_station_id, status from wait_stations;\"'"
    command="echo '$password' | sudo -S $get_ws_status"
    ws_status=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command")
    echo "$ws_status"

    echo -e "ws_status\n" >>output_pre.txt

    IFS=$'\n' read -r -d '' -a lines <<< "$induct_status"

    converted_strings=()
    for ((i=2; i<${#lines[@]}-1; i++)); do
        IFS='|' read -r -a fields <<< "${lines[$i]}"
        induct_id=$(echo "${fields[0]}" | tr -d '[:space:]')
        status=$(echo "${fields[1]}" | tr -d '[:space:]')
        converted_string="Wait Station ID : $induct_id, Status : $status"
        converted_strings+=("$converted_string\n")
    done

    output_string=$(printf "%s\n" "${converted_strings[@]}")

    echo "$output_string"
    echo -e "$output_string\nEND_OF_OUTPUT\n" >>output_pre.txt
}


getBotsTasks
getInductStatus
get_ws_status