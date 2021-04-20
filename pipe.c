/* How to use pipes for redirection */

#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <string.h>

int main() {

	/* 	Store the child pid in parent process */
	pid_t child_pid;

	/* 	Shared file descriptors between parent and child process
		pipefd[0] refers to the read end of the pipe
		pipefd[1] refers to the write end of the pipe
		
		NOTE: 	Date written to the write end of the pipe is buffered
				by the kernel until it is read from the read end of
				the pipe (from the man page)
	*/
	int pipefd[2];
#define READ_PIPE_END	pipefd[0]
#define WRITE_PIPE_END	pipefd[1]

	pipe(pipefd);
	
	/*	Child will get 0, and parent will get the child process's pid
	*/
	child_pid = fork ();

	if (child_pid == 0) {
		printf("Child process pid: %d\n", getpid());
		/* 	Child process. Close the write end of the pipe 
		*/
		close(WRITE_PIPE_END);
		
		/* 	Use dup2 syscall which runs close(0) and dup atomically.
			pipefd[0], the read end of the pipe gets assigned file
			descriptor 0, which is the stdin	
		*/
		dup2(READ_PIPE_END, STDIN_FILENO);

		/* 	EITHER READ FROM STDIN OR RUN A PROGRAM IN EXEC WHICH WILL
			IMPLICITLY READ FROM STDIN
		*/
		char out;
		while ((out = getchar()) != '\0') {
			/* perform some function on char
			 * to confirm that child printed
			 * this out
			 */
			putchar(out+2);						
		}
		printf("\n");

	} else {

		/*	Parent process. Close the read end of the pipe
		*/
		close(READ_PIPE_END);

		/*	Use dup2 syscall which runs close(1) and dup atomically.
			pipefd[1], the write end of the pipe gets assigned file
			descriptor 1, which is the stdout
		*/
		dup2(WRITE_PIPE_END, STDOUT_FILENO);

		/*	WRITE DATA TO PRINTF OR STDOUT THAT YOU WANT TO PROCESS IN
			CHILD PROCESS. TEST BUFFERING. EOF?
			PRINTF IS BUFFERED
		*/
		char *in = "Some random string from parent";
		write(STDOUT_FILENO, in, strlen(in)+1);
	}
	
	
	return 0;
}
