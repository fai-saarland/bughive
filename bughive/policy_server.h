/***
 * Copyright (c)2023 Daniel Fiser <danfis@danfis.cz>. All rights reserved.
 * This file is part of bughive licensed under 3-clause BSD License (see file
 * LICENSE, or https://opensource.org/licenses/BSD-3-Clause)
 */

#ifndef __BUGHIVE_POLICY_SERVER_H__
#define __BUGHIVE_POLICY_SERVER_H__

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

/** Forward declaration */
typedef struct bughive_policy_server bughive_policy_server_t;

typedef char *(*bughive_policy_req_fdr_fd)(void *userdata);
typedef int (*bughive_policy_req_fdr_operator)(const int *state,
                                               void *userdata);

/**
 * Creates a server object with the associated methods.
 */
bughive_policy_server_t *
bughivePolicyServerNew(const char *url,
                       bughive_policy_req_fdr_fd req_fdr_fd,
                       bughive_policy_req_fdr_operator req_fdr_op,
                       void *userdata);

/**
 * Deletes allocated memory.
 */
void bughivePolicyServerDel(bughive_policy_server_t *s);

/**
 * Runs the server and blocks as long as the server is running
 */
int bughivePolicyServerRun(bughive_policy_server_t *s);

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* __BUGHIVE_POLICY_SERVER_H__ */
