all: daemon

#CC=clang

CFLAGS=-Wall -g -O2 -Wno-parentheses

daemon: daemon.o
	$(CC) -o $@ $^

daemon.o:

clean:
	rm -f daemon.o daemon
