#!bin/bash

username="$1"
password="$2"
server="$3"
server_knode1="$4"
server_knode2="$5"

## Optimize further
checkApplicationPods() {
    app_pods="kubectl get pods | grep -vE 'Running'"
    command="echo '$password' | sudo -S $app_pods"
    not_running_app_pods=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command" 2>&1)
    echo -e "app_pods\n$not_running_app_pods\nEND_OF_OUTPUT\n" > output_post.txt
    echo -e "$not_running_app_pods"
}

checkSystemPods() {
    system_pods="kubectl get pods -n kube-system | grep -vE 'Running'"
    command="echo '$password' | sudo -S $system_pods"
    not_running_system_pods=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command" 2>&1)
    echo -e "system_pods\n$not_running_system_pods\nEND_OF_OUTPUT\n" >> output_post.txt
    echo -e "$not_running_system_pods"
}

checkPostgresPromoted() {
    get_postgres_promoted="kubectl get pods | grep 'postgres-promoted'"
    command="echo '$password' | sudo -S $get_postgres_promoted"
    postgres_promoted_status=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command" 2>&1)

    # if [ $? -ne 0 ]; then
    #     echo -e "Error occured"
    #     echo -e "postgres_promoted\n$postgres_promoted_status\nEND_OF_OUTPUT\n" >> output_post.txt
    # fi
        
    postgres_promoted_status=$(echo "$postgres_promoted_status" | tr -d '[:space:]')
    if [ ${#postgres_promoted_status} -eq 0 ]; then
        echo -e "postgres_promoted\nPostgres is not Promoted\nEND_OF_OUTPUT\n" >> output_post.txt
    else
        echo -e "postgres_promoted\nPostgres is Promoted!!\nEND_OF_OUTPUT\n" >> output_post.txt
    fi
}

## Base file size shd be same even if 0 rows in slave
checkPostgresReplication() {
    get_postgres_pods="kubectl get pods | awk '/postgres/ && !/manager/ && !/postgres12/ {print \$1}'"
    command="echo '$password' | sudo -S $get_postgres_pods"
    postgres_pods=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command" 2>&1)
    echo -e "Postgres pods"
    echo -e "$postgres_pods"

    if [ $? -ne 0 ]; then
        echo -e "postgres_replication\n$postgres_pods\nEND_OF_OUTPUT\n" >> output_post.txt
        return
    fi

    postgres_pod=$(echo "$postgres_pods" | grep -v 'slave')
    postgres_slave_pod=$(echo "$postgres_pods" | grep 'slave')

    get_replication_state_postgres="kubectl exec -it $postgres_pod bash -- su - postgres -c 'psql -c \"SELECT state FROM pg_stat_replication;\"'"
    command="echo '$password' | sudo -S $get_replication_state_postgres"
    replication_state_postgres=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command" 2>&1)
    echo -e "replication_state_postgres"
    echo -e "\n$replication_state_postgres\n"

    if [ $? -ne 0 ]; then
        echo -e "postgres_replication\n$replication_state_postgres\nEND_OF_OUTPUT\n" >> output_post.txt
        return
    fi

    if ! grep -q "streaming" <<< "$replication_state_postgres"; then
        echo -e "postgres_replication\nPostgres Replication is not working\nEND_OF_OUTPUT\n" >> output_post.txt
        return
    fi

    get_replication_state_postgres_slave="kubectl exec -it $postgres_slave_pod bash -- su - postgres -c 'psql -c \"SELECT state FROM pg_stat_replication;\"'"
    command="echo '$password' | sudo -S $get_replication_state_postgres_slave"
    replication_state_postgres_slave=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command" 2>&1)
    echo -e "\n$replication_state_postgres_slave\n"

    if [ $? -ne 0 ]; then
        echo -e "postgres_replication\n$replication_state_postgres_slave\nEND_OF_OUTPUT\n" >> output_post.txt
        return
    fi

    if ! grep -q "streaming" <<< "$replication_state_postgres_slave"; then
        get_base_file_size="ls -ld /opt/data/postgres/base | cut -d' ' -f5"
        command="echo '$password' | sudo -S $get_base_file_size"
        base_file_size_knode1=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server_knode1" "$command" 2>&1)
        echo -e "\n$base_file_size_knode1\n"

        if [ $? -ne 0 ]; then
            echo -e "postgres_replication\nError while getting base file size from knode1 - $base_file_size_knode1\nEND_OF_OUTPUT\n" >> output_post.txt
            return
        fi

        base_file_size_knode2=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server_knode2" "$command" 2>&1)
        echo -e "\n$base_file_size_knode2\n"

        if [ $? -ne 0 ]; then
            echo -e "postgres_replication\nError while getting base file size from knode2 - $base_file_size_knode2\nEND_OF_OUTPUT\n" >> output_post.txt
            return
        fi

        base_file_size_knode1="$(echo -e "${base_file_size_knode1}" | tr -d '[:space:]')"
        base_file_size_knode2="$(echo -e "${base_file_size_knode2}" | tr -d '[:space:]')"

        if [ "$base_file_size_knode1" = "$base_file_size_knode2" ]; then
            echo -e "postgres_replication\nPostgres Replication is working\nEND_OF_OUTPUT\n" >> output_post.txt
        else
            echo -e "postgres_replication\nPostgres Replication is not working\nEND_OF_OUTPUT\n" >> output_post.txt
        fi
    else
        echo -e "postgres_replication\nPostgres Replication is working\nEND_OF_OUTPUT\n" >> output_post.txt
    fi
}

checkLoadAverage() {
    command="uptime"
    load_average_server=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$1" "$command" 2>&1)
    if [ $? -ne 0 ]; then
        return
    fi

    load_average_server=$(echo "$load_average_server" | awk -F 'load average: ' '{print $2}')

    flag=0
    for number in $(echo "$load_average_server" | tr ',' ' '); do
        if (( $(echo "$number > 2" | bc -l) )); then
            echo -e "\nAverage load on server is high - $1 - $load_average_server\n"
            flag=1
            break
        fi
    done

    if [ "$flag" -eq 0 ]; then
        echo -e "\nAverage load on server is stable - $1 - $load_average_server"
    fi
}

## When to renew
checkCertificateExpiry() {
    get_residual_time="kubeadm certs check-expiration | grep 'admin.conf'" 
    command="echo '$password' | sudo -S $get_residual_time"
    residual_time=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$command" 2>&1)
    if [ $? -ne 0 ]; then
        echo -e "certificate_expiry\n$residual_time\nEND_OF_OUTPUT\n" >> output_post.txt
    else
        residual_time=$(echo $residual_time | awk '{print $(NF-1)}')
        echo -e "certificate_expiry\n$residual_time\nEND_OF_OUTPUT\n" >> output_post.txt
    fi
}

checkNfs() {
    get_mounted_status="df -h | grep 'knode1:/mnt'"
    mounted_status=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server" "$get_mounted_status" 2>&1)
    if [ $? -ne 0 ]; then
        echo -e "nfs_status\n$mounted_status\nEND_OF_OUTPUT\n" >> output_post.txt
        return
    fi
    mounted_status=$(echo "$mounted_status" | tr -d '[:space:]')
    if [ -z "$mounted_status" ]; then
        echo -e "nfs_status\nNFS is not mounted on Kmaster\n" >> output_post.txt
    else 
        echo -e "nfs_status\nNFS is mounted on Kmaster\n" >> output_post.txt
    fi


    get_service_status="service nfs-server status | grep 'Active: active'"
    command="echo '$password' | sudo -S $get_service_status"
    service_status=$(sshpass -p "$password" ssh -o StrictHostKeyChecking=no "$username"@"$server_knode1" "$command" 2>&1)
    if [ $? -ne 0 ]; then
        echo -e "nfs_status\n$service_status\nEND_OF_OUTPUT\n" >> output_post.txt
        return
    fi
    service_status=$(echo "$service_status" | tr -d '[:space:]')
    if [ -z "$service_status" ]; then
        echo -e "nfs_status\nNFS is not running\nEND_OF_OUTPUT\n" >> output_post.txt
    else 
        echo -e "nfs_status\nNFS is running\nEND_OF_OUTPUT\n" >> output_post.txt
    fi
}

# Gets a list of application pods that are not in running state
checkApplicationPods

# Gets a list of system pods that are not in running state
checkSystemPods

# Check if postgres promoted
checkPostgresPromoted

# Check if postgres replication is working
checkPostgresReplication

# Check load average on all nodes
checkLoadAverage "$server"
kmaster_load_average="$load_average_server"
echo -e "load_kmaster\n$kmaster_load_average\nEND_OF_OUTPUT\n" >> output_post.txt

checkLoadAverage "$server_knode1"
knode1_load_average="$load_average_server"
echo -e "load_knode1\n$knode1_load_average\nEND_OF_OUTPUT\n" >> output_post.txt

checkLoadAverage "$server_knode2"
knode2_load_average="$load_average_server"
echo -e "load_knode2\n$knode2_load_average\nEND_OF_OUTPUT\n" >> output_post.txt

# Check k8s certificate expiry
checkCertificateExpiry

# Check NFS is mounted and running
checkNfs