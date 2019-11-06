
CC = gcc
CFLAGS1 = -Wall -g -c
CFLAGS2 = -g

helloworld:	helloworld.c
	${CC} ${CFLAGS1} -o helloworld helloworld.c

clean:
	rm *.o output
