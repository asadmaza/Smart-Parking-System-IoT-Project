#!/bin/bash
 
# server's IP address
SERVER_IP="3.106.140.164"
 
# use ping check the server is available
while ! ping -c 1 -W 1 $SERVER_IP > /dev/null
do
    echo "Waiting for $SERVER_IP to be reachable..."
    sleep 5
done
 
# when server available, excute the frp command 
 
/home/asadRPI/Group3-CITS5506-2023/'6. Camera'/frp_0.51.3_linux_arm64/frpc -c /home/asadRPI/Group3-CITS5506-2023/'6. Camera'/frp_0.51.3_linux_arm64/frpc.ini