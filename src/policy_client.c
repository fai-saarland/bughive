/***
 * Copyright (c)2023 Daniel Fiser <danfis@danfis.cz>. All rights reserved.
 * This file is part of bughive licensed under 3-clause BSD License (see file
 * LICENSE, or https://opensource.org/licenses/BSD-3-Clause)
 */

#include "bughive/policy_client.h"
#include "bughive/common.h"
#include "msg/policy_reader.h"
#include "msg/policy_builder.h"
//#include "msg/policy_verifier.h"

#include <stdio.h>
#include <assert.h>
#include <nanomsg/nn.h>
#include <nanomsg/reqrep.h>

#undef ns
#define ns(x) FLATBUFFERS_WRAP_NAMESPACE(bughive_policy, x)
#define reqtype(X) ns(RequestType_REQ_##X)

struct bughive_policy {
    int sock;
    int eid;
    void *recv_buf;
    flatcc_builder_t builder;
};

bughive_policy_t *bughivePolicyConnect(const char *url)
{
    bughive_policy_t *p;
    p = (bughive_policy_t *)calloc(1, sizeof(bughive_policy_t));

    if ((p->sock = nn_socket(AF_SP, NN_REQ)) < 0){
        fprintf(stderr, "Error: Could not create a socket: %s\n",
                nn_strerror(nn_errno()));
        return NULL;
    }

    if ((p->eid = nn_connect(p->sock, url)) < 0){
        fprintf(stderr, "Error: Cannot connect to %s: %s\n",
                url, nn_strerror(nn_errno()));
        return NULL;
    }

    p->recv_buf = malloc(BUGHIVE_BUF_MAX_SIZE);
    flatcc_builder_init(&p->builder);

    return p;
}

void bughivePolicyDel(bughive_policy_t *p)
{
    int ret;
    if ((ret = nn_shutdown(p->sock, p->eid)) < 0)
        fprintf(stderr, "Error: shutting down: %s\n", nn_strerror(nn_errno()));

    flatcc_builder_clear(&p->builder);
    if (p->recv_buf != NULL)
        free(p->recv_buf);
    free(p);
}

char *bughivePolicyFDRTaskFD(bughive_policy_t *p)
{
    flatcc_builder_reset(&p->builder);
    ns(Request_start_as_root(&p->builder));
    ns(Request_request_add(&p->builder, reqtype(FDR_TASK_FD)));
    ns(Request_end_as_root(&p->builder));

    size_t sendsize;
    void *sendbuf = flatcc_builder_get_direct_buffer(&p->builder, &sendsize);
    if (nn_send(p->sock, sendbuf, sendsize, 0) < 0){
        fprintf(stderr, "Error: Cannot send a message: %s\n",
                nn_strerror(nn_errno()));
        return NULL;
    }

    int buflen;
    if ((buflen = nn_recv(p->sock, p->recv_buf, BUGHIVE_BUF_MAX_SIZE, 0)) < 0){
        fprintf(stderr, "Error: Cannot receive a message: %s\n",
                nn_strerror(nn_errno()));
        return NULL;
    }

    ns(ResponseFDRTaskFD_table_t) res;
    res = ns(ResponseFDRTaskFD_as_root(p->recv_buf));
    if (res == NULL){
        fprintf(stderr, "Error: Incorrectly formed received message (size: %d)\n",
                buflen);
        return NULL;
    }

    bughive_Response_table_t status = ns(ResponseFDRTaskFD_response(res));
    assert(bughive_Response_status(status) == bughive_Status_OK);
    assert(!bughive_Response_errmsg_is_present(status));

    flatbuffers_string_t task = ns(ResponseFDRTaskFD_task_get(res));
    int outsize = flatbuffers_string_len(task);
    char *out = (char *)malloc(sizeof(char) * (outsize + 1));
    strcpy(out, task);
    return out;
}
