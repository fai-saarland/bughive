/***
 * Copyright (c)2023 Daniel Fiser <danfis@danfis.cz>. All rights reserved.
 * This file is part of bughive licensed under 3-clause BSD License (see file
 * LICENSE, or https://opensource.org/licenses/BSD-3-Clause)
 */

#ifndef __BUGHIVE_POLICY_CLIENT_H__
#define __BUGHIVE_POLICY_CLIENT_H__

#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

/** Forward declaration */
typedef struct bughive_policy bughive_policy_t;

/**
 * Create a connection to the policy server.
 */
bughive_policy_t *bughivePolicyConnect(const char *url);

/**
 * Disconnects and deletes allocated memory.
 */
void bughivePolicyDel(bughive_policy_t *p);

/**
 * Retrieves policy's FDR planning task encoded in Fast Downward's format.
 */
char *bughivePolicyFDRTaskFD(bughive_policy_t *p);

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* __BUGHIVE_POLICY_CLIENT_H__ */
