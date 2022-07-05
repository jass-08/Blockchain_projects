Good Morning/Evening,

The blockchain peer works fine, I have also implemented the bonus for flooding where it sends flood to all the peers in the list 
if its not empty line 146. I have heavily commented the implemetation .  

1) STATS REPLY AND WAIT FOR IT
To get the STATS from peers, I sent the STATS request in a loop to all the peers at once and wait for thier reply in a while
loop timed to break every 5 secs or until that STAT_REPLY is recieved(Line 172-178). Line 165-192

2) Load balancing
To load balance while getting blocks from the peers, I am assigning each and every height to a random peer in my peer List.
If I don't get a reply I resend it again using random peer Line 205 to 265

3) Validation to verify entire chain
To validate the chain upon recieving blocks; I am making a list when all the blocks are recieved and passing it to the validation funtion
The function validates the chain by going one by one and using hashlib library appropriately and if the hash calculated is equal to the
hash in the block, it is then added to the verified blockchain. Line 76-115

4) CHOOSE the LONGEST CHAIN
To choose the longest chain, I do point number 1) and then when I get back the STATS_REPLY, I make two lists
    1) to store the hash/height combo and the count of votes given by peers         Line 182-187
    2) List of peers that gives the votes to those hash/height combo                Line 188-192
    PS. I could have made one single list but making 2 did my job easier when doing the consesus and validation
    This also helps me to move to ew chain that we chose in consensus and collect blocks 
5) Consensus:
To do the consensus of the most agreed upon hash/hieght combo: I select the max count element out of my statCountList(4.1) and
send the GET_BLOCK messages to all the peers that sent us that combo from my statsReplyList(4.2)

6) Clean up peers that have not sent FLOOD messages (note to students: consider writing where and how you do this in your readme)
To remove the unactive peersm, I am saving the peers latest ping time in my dictionary of peers and checking if that 
time is greater 60 seconds in which case it will delete it. it is in line 148-149 and 290-296

7) Add new block to top of chain on ANNOUNCE
when recieving ANNOUNCE requests, I add that block on top of the heightList and send the entire chain to verify Line 305-312. I felt it
is the safest way

8) Send STATS to all known peers, collect results:
Send all STATS to all peers at once, Line 165-170
wait for result with timeout to trigger doing the consensus, Line 172-179

9) Do consensus when entering network to choose the consensus'd chain
To do the consensus upon entering the network, I have implemented a variable called doConsunsus which does the consensus in first
15 seconds upon joining and then after every 180 secs or if the Consensus message is sent from peers Line

Thank you