/***
 * Copyright (c)2023 Daniel Fiser <danfis@danfis.cz>. All rights reserved.
 * This file is part of bughive licensed under 3-clause BSD License (see file
 * LICENSE, or https://opensource.org/licenses/BSD-3-Clause)
 */

#ifndef __BUGHIVE_COMMON_H__
#define __BUGHIVE_COMMON_H__

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

/**
 * Maximum size of a buffer used server and client to send and receive
 * messages, i.e., it has to be large enough to keep the largest possible
 * message.
 */
#define BUGHIVE_BUF_MAX_SIZE (1024 * 1024 * 10)

/**
 * Maximum size of the string enconding url
 */
#define BUGHIVE_URL_MAX_SIZE 256

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* __BUGHIVE_COMMON_H__ */
