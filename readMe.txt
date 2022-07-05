Good Morning/Evening

The assignment runs fine until the bonus part of delete button.
I have also talked to you about using a local cookie at the 
client side as I was not getting the cookie from my web server.

So my web server sets and deletes the cookies finely, However it just does not send
it to my front end.

=========================================================
Answer to the Bonus question #2 is:

What could possibly go wrong with multiple threads accessing, 
changing, deleting the same piece of data? We should be using 
layering to abstract out the persistence layer, in case you would 
like to change to a more reliable database… like a 2PC database…?

Since multiple threads have no communication between each other, hence
when multiple users make commits at the same time, it may cause imformation
leaks and the same database may not save several changes.

For example if user1 and User2 are on multiple threads at the same time;
now; Lets say user1 delets a public item x and user 2 tries to access it at the same time
This situation will create problems into our DB as our user2 is trying to access null object.

Whereas, in 2PC database, blocking and unblocking prevents our database from getting into these kind
of situation. 

However, I was not able to compplete this bonus due to lack of time.


Thanks :)))