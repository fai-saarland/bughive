/***
 * Copyright (c)2023 Daniel Fiser <danfis@danfis.cz>. All rights reserved.
 * This file is part of bughive licensed under 3-clause BSD License (see file
 * LICENSE, or https://opensource.org/licenses/BSD-3-Clause)
 */

#include "bughive/policy_server.h"
#include "bughive/common.h"
#include "msg/policy_reader.h"
#include "msg/policy_builder.h"
#include "msg/policy_verifier.h"

#include <stdio.h>
#include <nanomsg/nn.h>
#include <nanomsg/reqrep.h>

#define ns(x) FLATBUFFERS_WRAP_NAMESPACE(bughive_policy, x)
#define nsfdr(x) FLATBUFFERS_WRAP_NAMESPACE(bughive_fdr, x)
#define reqtype(X) ns(RequestType_REQ_##X)

static void *resFDRTaskFD(int sock,
                          flatcc_builder_t *builder,
                          bughive_policy_req_fdr_task_fd req_fdr_fd,
                          void *userdata,
                          size_t *bufsize)
{
    size_t size;
    char *task = req_fdr_fd(&size, userdata);
    if (task == NULL)
        return NULL;

    flatcc_builder_reset(builder);
    ns(ResponseFDRTaskFD_start_as_root(builder));

    ns(ResponseFDRTaskFD_response_start(builder));
    bughive_Response_status_add(builder, bughive_Status_OK);
    ns(ResponseFDRTaskFD_response_end(builder));

    ns(ResponseFDRTaskFD_task_create(builder, task, size));
    ns(ResponseFDRTaskFD_end_as_root(builder));

    free(task);
    return flatcc_builder_get_direct_buffer(builder, bufsize);
}

static void *resFDROperator(int sock,
                            flatcc_builder_t *builder,
                            bughive_policy_req_fdr_operator req_fn,
                            ns(Request_table_t) req,
                            void *userdata,
                            size_t *bufsize)
{
    if (!ns(Request_state_is_present(req))){
        fprintf(stderr, "Error: Invalid request. Missing .state member.\n");
        return NULL;
    }

    nsfdr(State_table_t) _state = ns(Request_state_get(req));
    flatbuffers_int32_vec_t state = nsfdr(State_val_get(_state));

    int op_id = -1;
    if (sizeof(int) == 4){
    }else{
        int size = flatbuffers_int32_vec_len(state);
        int fdrstate[size];
        for (int i = 0; i < size; ++i)
            fdrstate[i] = flatbuffers_int32_vec_at(state, i);

        op_id = req_fn(fdrstate, userdata);
    }

    flatcc_builder_reset(builder);
    ns(ResponseFDROperator_start_as_root(builder));

    ns(ResponseFDROperator_response_start(builder));
    bughive_Response_status_add(builder, bughive_Status_OK);
    ns(ResponseFDROperator_response_end(builder));

    ns(ResponseFDROperator_operator_add(builder, op_id));
    ns(ResponseFDROperator_end_as_root(builder));
    return flatcc_builder_get_direct_buffer(builder, bufsize);
}

int bughivePolicyServer(const char *url,
                        bughive_policy_req_fdr_task_fd req_fdr_fd,
                        bughive_policy_req_fdr_operator req_fdr_op,
                        void *userdata)
{
    int sock, eid;
    if ((sock = nn_socket(AF_SP, NN_REP)) < 0){
        fprintf(stderr, "Error: Could not create a socket: %s\n",
                nn_strerror(nn_errno()));
        return -1;
    }

    if ((eid = nn_bind(sock, url)) < 0){
        fprintf(stderr, "Error: Could not bind socket to url %s: %s\n",
                url, nn_strerror(nn_errno()));
        return -1;
    }

    flatcc_builder_t builder;
    flatcc_builder_init(&builder);
    char *buf = (char *)malloc(BUGHIVE_BUF_MAX_SIZE);
    while (1){
        int buflen = 0;
        // nn_recv(s->sock, &buf, NN_MSG, 0)
        if ((buflen = nn_recv(sock, buf, BUGHIVE_BUF_MAX_SIZE, 0)) < 0){
            fprintf(stderr, "Error: nn_recv: %s\n",
                    nn_strerror(nn_errno()));
            // TODO: Ignore errors for now
            continue;
        }
        ns(Request_table_t) req;
        req = ns(Request_as_root(buf));
        if (req == NULL){
            fprintf(stderr, "Error: Incorrectly formed received message (size: %d)\n",
                    buflen);
            return -1;
        }

        void *sendbuf = NULL;
        size_t sendsize = 0;
        switch (ns(Request_request(req))){
            case reqtype(FDR_TASK_FD):
                fprintf(stdout, "Got FDR_TASK_FD request\n");
                fflush(stdout);

                sendbuf = resFDRTaskFD(sock, &builder, req_fdr_fd, userdata,
                                       &sendsize);
                break;

            case reqtype(FDR_STATE_OPERATOR):
                fprintf(stdout, "Got FDR_STATE_OPERATOR request\n");
                fflush(stdout);

                sendbuf = resFDROperator(sock, &builder, req_fdr_op, req,
                                         userdata, &sendsize);
                break;

            default:
                fprintf(stderr, "Error: Unkown request %d\n",
                        (int)ns(Request_request(req)));
                continue;
        }

        if (sendbuf != NULL){
            if (nn_send(sock, sendbuf, sendsize, 0) < 0){
                fprintf(stderr, "Error: Cannot send a message: %s\n",
                        nn_strerror(nn_errno()));
                return -1;
            }
        }
    }
    free(buf);
    flatcc_builder_clear(&builder);

    return 0;
}
