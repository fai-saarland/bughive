#include <stdio.h>
#include <bughive/policy_client.h>

int main(int argc, char *argv[])
{
    if (argc != 2){
        fprintf(stderr, "Usage: %s url\n", argv[0]);
        return -1;
    }

    bughive_policy_t *p = bughivePolicyConnect(argv[1]);
    if (p == NULL)
        return -1;

    char *task = bughivePolicyFDRTaskFD(p);
    if (task != NULL){
        fprintf(stdout, "Got:\n%s\n", task);
        free(task);
    }
    bughivePolicyDel(p);
    return 0;
}

