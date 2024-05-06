#!bin/bash

username="gor"
password="JEZ3*pj_!?nVm4="
server="10.32.11.243"
server_knode1="10.32.11.241"
server_knode2="10.32.11.242"

checkBotsTasks() {
    get_postgres_pods="kubectl get pods | awk '/postgres/ && !/manager/ && !/postgres12/ {print \$1}'"
    command="echo '$password' | sudo -S $get_postgres_pods"
    postgres_pods=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command")

    postgres_pod=$(echo "$postgres_pods" | grep -v 'slave')
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

checkBotsTasks