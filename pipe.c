/* How to use pipes for redirection */

#include <stdio.h>
#include <unistd.h>

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
	
	/*	Child will get 0, and parent will get the child process's pid
	*/
	child_pid = fork ();

	if (child_pid == 0) {
		/* 	Child process. Close the write end of the pipe 
		*/
		close(pipefd[1]);
		
		/* 	Use dup2 syscall which runs close(0) and dup atomically.
			pipefd[0], the read end of the pipe gets assigned file
			descriptor 0, which is the stdin	
		*/
		dup2(0, pipefd[0]);	

	} else {

		/*	Parent process. Close the read end of the pipe
		*/
		close(pipefd[0]);

		/*	Use dup2 syscall which runs close(1) and dup atomically.
			pipefd[1], the write end of the pipe gets assigned file
			descriptor 1, which is the stdout
		*/
		dup2(1, pipefd[1]);		

		/* Writing to stdout pipes the data to child process
		*/ 
		printf("Hello from parent\n");
		printf("child pid = %d\n", child_pid);
	}
	
	return 0;
}
