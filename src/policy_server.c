/***
 * Copyright (c)2023 Daniel Fiser <danfis@danfis.cz>. All rights reserved.
 * This file is part of bughive licensed under 3-clause BSD License (see file
 * LICENSE, or https://opensource.org/licenses/BSD-3-Clause)
 */

#include "bughive/policy_server.h"
#include "msg/policy_reader.h"

#include <stdio.h>
#include <nanomsg/nn.h>
#include <nanomsg/reqrep.h>

#define BUGHIVE_BUF_MAX_SIZE (1024 * 1024 * 10)
#define BUGHIVE_URL_MAX_SIZE 256

struct bughive_policy_server {
    char url[BUGHIVE_URL_MAX_SIZE];
    int sock;
    int eid;

    bughive_policy_req_fdr_fd req_fdr_fd;
    bughive_policy_req_fdr_operator req_fdr_operator;
    void *userdata;
};

bughive_policy_server_t *
bughivePolicyServerNew(const char *url,
                       bughive_policy_req_fdr_fd req_fdr_fd,
                       bughive_policy_req_fdr_operator req_fdr_op,
                       void *userdata)
{
    if (strlen(url) > BUGHIVE_URL_MAX_SIZE - 1){
        fprintf(stderr, "Error: url too long\n");
        return NULL;
    }

    bughive_policy_server_t *s;
    s = (bughive_policy_server_t *)calloc(1, sizeof(bughive_policy_server_t));

    strcpy(s->url, url);
    s->req_fdr_fd = req_fdr_fd;
    s->req_fdr_operator = req_fdr_op;
    s->userdata = userdata;
    return s;
}

void bughivePolicyServerFree(bughive_policy_server_t *s)
{
    free(s);
}

int bughivePolicyServerRun(bughive_policy_server_t *s)
{
    if ((s->sock = nn_socket(AF_SP, NN_REP)) < 0){
        fprintf(stderr, "Error: Could not create a socket: %s\n",
                nn_strerror(nn_errno()));
        return -1;
    }

    if ((s->eid = nn_bind(s->sock, s->url)) < 0){
        fprintf(stderr, "Error: Could not bind socket to url %s: %s\n",
                s->url, nn_strerror(nn_errno()));
        return -1;
    }

    char *buf = (char *)malloc(BUGHIVE_BUF_MAX_SIZE);
    while (1){
        int buflen = 0;
        // nn_recv(s->sock, &buf, NN_MSG, 0)
        if ((buflen = nn_recv(s->sock, buf, BUGHIVE_BUF_MAX_SIZE, 0)) < 0){
            fprintf(stderr, "Error: nn_recv: %s\n",
                    nn_strerror(nn_errno()));
            // TODO: Ignore errors for now
            continue;
        }

        // TODO: bughive_policy_Request_verify_table()
        // TODO: Deserialize and dispatch to methods

    }
    free(buf);

    return -1;
}
