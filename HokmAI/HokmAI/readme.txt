you need to create a client to communicate with the AI's server

every meesage should start with tow-digit number (01, 02, 03, ......, 10, 11, 12, ......, 50, 51, ....., 98 , 99)  which represent an agreed code, then "-" and in the end "!"

to send the strong symbol you should send the code 01 then "-" and then the symbol name and then "!"
example 1: the strong symbol is 'clubs' so you have to send: "01-clubs!"
example 2: the strong symbol is 'hearts' so you have to send: "01-hearts!"

symbols are: [hearts, diamonds, clubs, spades]


to send our cards you have to start with the code 02 and then "-" and then capital of the first letter of the symbol and the number
you have to send all of the cards at once

example: 02-H2-D14-S12-D3-C8! 	this means you sent 2 of hearts, ace of diamonds, 12 of spades, 3 of diamonds, 8 of clubs. (you must send 13 cards at once)

pay attention: ace is 14 and no 1. cards values starts with 2.


to make a player do a turn you should start the mwssage with "03-" then the number which represent the player. then "-" and then capital letter of the symbol
of the card and number of the card. and then "!"
note: we are player 1. the player who is right to us is player 2. the player in front of us is player 3. the player in our left is player 4.

example 1: we played 3 of diamonds so you should send: "03-1-D3!"
example 2: the player in the right played ace of hearts to you should send: "03-2-H14!"
example 3: the player in front us played 2 of clubs so you should send: '03-3-C2!"
example 4: the player in the left played 12 of spades so you should send '03-4-S12!"

int the end of turn you should send "04-" then 0 if we won and 1 if not and then "!"

example 1: now its the end of the turn and our team won so you send: "04-0!"
example 2: now its the end of the turn and our team did not win so you send: "04-1!"
