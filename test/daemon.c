#include <sys/types.h>

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

extern char **environ;

int
main(argc, argv)
char *argv[];
{
	FILE *f;
	if (daemon(0, 0)) {
		fprintf(stderr, "daemon: %s\n", strerror(errno));
		return 1;
	}

	execve(argv[1], &argv[1], environ);

	if (f = fopen("/tmp/daemon.log", "a")) {
		fprintf(f, "%s: %s\n", argv[1], strerror(errno));
		fclose(f);
	}

	return 1;
}
