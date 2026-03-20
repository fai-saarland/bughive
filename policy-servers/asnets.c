#include <pddl/pddl.h>
#include <pddl/strstream.h>
#include <pheromone/policy_server.h>
#include <stdlib.h>

pddl_err_t err = PDDL_ERR_INIT;
pddl_asnets_model_t **models = NULL;
pddl_asnets_ground_task_t task;
int num_policies = 0;

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

static int reqFDROperator(const int *state, int model_index, void *data)
{
    return pddlASNetsRunPolicy(models[model_index], &task, state, NULL, NULL);
}

static int reqFDROperatorsProb(const int *state,
                               int model_index,
                               int *op_size,
                               int **op_ids,
                               float **op_probs,
                               void *userdata)
{
    pddl_asnets_policy_distribution_t op_dist;
    pddlASNetsPolicyDistributionInit(&op_dist);
    int st = pddlASNetsPolicyDistribution(models[model_index], &task, state, NULL, &op_dist);
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

static int reqNumPolicies(void *data)
{
    return num_policies;
}

void print_usage(const char* name) {
    fprintf(stderr, "Usage: %s URL domain.pddl problem.pddl model.policy [additional_model.policy...] [options: -v,--verbose | -g,--enable-gpu | -b,--enable-autobatching]\n", name);
    fprintf(stderr, "\n");
    fprintf(stderr, "See https://grpc.github.io/grpc/cpp/md_doc_naming.html for how to specify URL.\n");
}

int main(int argc, char *argv[])
{
    // handle options first, leave argc and argv[] as if no options where given
    asnets_gpu_enabled = 0;
    for (int i = 0; i < argc;) {
        if (argv[i][0] == '-') {
            if(strcmp(argv[i], "--verbose") == 0 || strcmp(argv[i], "-v") == 0) {
                asnets_verbosity = 1;
            }
            else if(strcmp(argv[i], "--enable-gpu") == 0 || strcmp(argv[i], "-g") == 0) {
                asnets_gpu_enabled = 1;
            }
            else if(strcmp(argv[i], "--enable-autobatching") == 0 || strcmp(argv[i], "-b") == 0) {
                asnets_autobatching_enabled = 1;
            }
            else {
                fprintf(stderr, "Unknown option %s\n", argv[i]);
                print_usage(argv[0]);
                exit(-1);
            }
            argc -= 1;
            for (int j=i; j<argc; ++j) {
                argv[j] = argv[j+1];
            }
        } else {
            ++i;
        }
    }
    if (argc < 5){
        print_usage(argv[0]);
        exit(-1);
    }

    const char *url = argv[1];
    const char *domain_file = argv[2];
    const char *problem_file = argv[3];
    num_policies = argc - 4;
    models = calloc(num_policies, sizeof(pddl_asnets_model_t *));
    const char **policy_files = calloc(num_policies, sizeof(char *));
    for (int i = 0; i < num_policies; ++i) {
        policy_files[i] = argv[i + 4];
    }

    pddlErrInit(&err);
    pddlErrLogEnable(&err, stdout);
    
    // load first model and task
    pddl_asnets_t *asnets = pddlASNetsNewLoad(policy_files[0], domain_file, &err);
    if (asnets == NULL){
        pddlErrPrint(&err, 1, stderr);
        return -1;
    }
    const pddl_asnets_config_t *cfg = pddlASNetsGetConfig(asnets);
    const pddl_asnets_lifted_task_t *lt = pddlASNetsGetLiftedTask(asnets);
    if (pddlASNetsGroundTaskInit(&task, lt, domain_file, problem_file, cfg, &err) != 0){
        pddlASNetsDel(asnets);
        pddlErrPrint(&err, 1, stderr);
        return -1;
    }
    models[0] = pddlASNetsGetModel(asnets);
    for (int i=1; i<num_policies; ++i){
        models[i] = pddlASNetsLoadAdditionalModel(asnets, policy_files[i], domain_file, &err);
        if (models[i] == NULL){
        pddlErrPrint(&err, 1, stderr);
        return -1;
    }
    }

    return phrmPolicyServer(url, reqFDRTaskFD, reqFDROperator, reqFDROperatorsProb, reqNumPolicies, NULL);
}
