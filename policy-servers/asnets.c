#include <pddl/pddl.h>
#include <pddl/strstream.h>
#include <pheromone/policy_server.h>

pddl_err_t err = PDDL_ERR_INIT;
pddl_asnets_t *asnets = NULL;
pddl_asnets_ground_task_t task;

static char *reqFDRTaskFD(size_t *size, void *data)
{
    char *out = NULL;
    FILE *fout = pddl_strstream(&out, size);

    pddl_fdr_write_config_t write_cfg = PDDL_FDR_WRITE_CONFIG_INIT;
    write_cfg.fout = fout;
    write_cfg.use_fd_fact_names = 1;
    pddlFDRWrite(&task.fdr, &write_cfg);
    fflush(fout);
    fclose(fout);
    return out;
}

static int reqFDROperator(const int *state, void *data)
{
    return pddlASNetsRunPolicy(asnets, &task, state, NULL, NULL);
}

static int reqFDROperatorsProb(const int *state,
                               int *op_size,
                               int **op_ids,
                               float **op_probs,
                               void *userdata)
{
    pddl_asnets_policy_distribution_t op_dist;
    pddlASNetsPolicyDistributionInit(&op_dist);
    int st = pddlASNetsPolicyDistribution(asnets, &task, state, NULL, &op_dist);
    if (st == 0){
        *op_size = op_dist.op_size;
        *op_ids = (int *)malloc(sizeof(int) * *op_size);
        *op_probs = (float *)malloc(sizeof(float) * *op_size);
        memcpy(*op_ids, op_dist.op_id, sizeof(int) * *op_size);
        memcpy(*op_probs, op_dist.prob, sizeof(float) * *op_size);
    }
    pddlASNetsPolicyDistributionFree(&op_dist);
    return st;
}

int main(int argc, char *argv[])
{
    if (argc != 5){
        fprintf(stderr, "Usage: %s URL model.policy domain.pddl problem.pddl\n", argv[0]);
        fprintf(stderr, "\n");
        fprintf(stderr, "See https://grpc.github.io/grpc/cpp/md_doc_naming.html"
                        " for how to specify URL.\n");
        exit(-1);
    }

    const char *url = argv[1];
    const char *policy_file = argv[2];
    const char *domain_file = argv[3];
    const char *problem_file = argv[4];

    pddlErrInit(&err);
    pddlErrLogEnable(&err, stdout);

    asnets = pddlASNetsNewLoad(policy_file, domain_file, &err);
    if (asnets == NULL){
        pddlErrPrint(&err, 1, stderr);
        return -1;
    }

    const pddl_asnets_config_t *cfg = pddlASNetsGetConfig(asnets);
    const pddl_asnets_lifted_task_t *lt = pddlASNetsGetLiftedTask(asnets);
    if (pddlASNetsGroundTaskInit(&task, lt, domain_file, problem_file,
                                 cfg, &err) != 0){
        pddlASNetsDel(asnets);
        pddlErrPrint(&err, 1, stderr);
        return -1;
    }

    return phrmPolicyServer(url, reqFDRTaskFD, reqFDROperator,
                            reqFDROperatorsProb, NULL);
}
