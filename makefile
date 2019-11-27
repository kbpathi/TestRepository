
CC = gcc
CFLAGS1 = -Wall -g -c
CFLAGS2 = -o

helloworld:	helloworld.c
	${CC} ${CFLAGS2} helloworld helloworld.c

clean:
	rm *.o output
