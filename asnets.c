#include <pddl/pddl.h>
#include <pddl/strstream.h>
#include <pheromone/policy_server.h>

pddl_err_t err = PDDL_ERR_INIT;
pddl_asnets_t *asnets = NULL;
const pddl_asnets_ground_task_t *task = NULL;

static char *reqFDRTaskFD(size_t *size, void *data)
{
    char *out = NULL;
    FILE *fout = pddl_strstream(&out, size);

    pddl_fdr_write_config_t write_cfg = PDDL_FDR_WRITE_CONFIG_INIT;
    write_cfg.fout = fout;
    write_cfg.use_fd_fact_names = 1;
    //write_cfg.use_osp_params = 1;
    pddlFDRWrite(&task->fdr, &write_cfg);
    fflush(fout);
    fclose(fout);
    return out;
}

static int reqFDROperator(const int *state, void *data)
{
    return pddlASNetsRunPolicy(asnets, task, state, NULL);
}

int main(int argc, char *argv[])
{
    if (argc != 5){
        fprintf(stderr, "Usage: %s url model.policy domain.pddl problem.pddl\n", argv[0]);
        exit(-1);
    }

    const char *url = argv[1];
    const char *policy_file = argv[2];
    const char *domain_file = argv[3];
    const char *problem_file = argv[4];

    pddlErrInit(&err);
    pddlErrLogEnable(&err, stdout);

    pddl_asnets_config_t cfg;
    pddlASNetsConfigInitFromModel(&cfg, policy_file, &err); 
    pddlASNetsConfigSetDomain(&cfg, domain_file);
    pddlASNetsConfigAddProblem(&cfg, problem_file); 

    asnets = pddlASNetsNew(&cfg, &err);
    if (asnets == NULL){
        pddlErrPrint(&err, 1, stderr);
        return -1;
    }

    if (pddlASNetsLoad(asnets, policy_file, &err) != 0){
        pddlErrPrint(&err, 1, stderr);
        return -1;
    }
    task = pddlASNetsGetGroundTask(asnets, 0);

    int ret = phrmPolicyServer(url, reqFDRTaskFD, reqFDROperator, NULL);
    return ret;
}
