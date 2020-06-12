import json
import gzip
import os

callbk_counter = 0
file_num = 0

def log_threshold(num_workers, num_envs_per_worker, num_iters, num_agents):
    """
    num_workers
    num_envs_per_worker
    num_iters

    num_eps = num_workers * num_envs_per_worker * num_iters

    num_agents
    """
    num_eps = num_workers * num_envs_per_worker * num_iters
    print("num_eps", num_eps)

    if num_iters % num_envs_per_worker == 0:
        return (num_iters * num_agents) - num_agents
    else:
        return num_iters * num_agents

def create_dir(path):
    try:
        os.mkdir(path)
    except OSError:
        print ("Folder creation failed or folder already exists: %s" % path)
    else:
        print ("Folder created: %s" % path)

def log_json(agt_id, eps_id, sample_obj, write_dir):
    """
    Output as training data as json files.
    """

    global file_num
    file_name = str(file_num) + '_' + str(agt_id) + '_' + str(eps_id)
    tmp_dict = {}
    tmp_dict["eps"] = {}
    for i,r in enumerate(sample_obj.rows()): # each row is a step dictionary
        tmp_dict["eps"][str(i)] = {}
        for k,v in r.items():
            tmp_dict["eps"][str(i)][k] = str(v)

        with open(write_dir + file_name + '.dat', 'w') as outfile:
            json.dump(tmp_dict, outfile, indent=3) # write to file in json format:
    file_num = file_num + 1

def _load_json(agent_ID, max_step, obs_store, act_store, infos_store, data):
    """
    Load 1 json file (1 episode) to memory for 1 agent
    """
    key_obs = 'agt' + '_' + agent_ID + '_obs_list'
    key_act = 'agt' + '_' + agent_ID + '_act_list'
    key_infos = 'agt' + '_' + agent_ID + '_infos_list'
    for i in range(max_step):
        obs_store[key_obs].append(data["eps"][str(i)]["obs"])
        act_store[key_act].append(data["eps"][str(i)]["actions"])
        infos_store[key_infos].append(data["eps"][str(i)]["infos"])

        #print("{}, obs_store = {}".format(key_obs, obs_store[key_obs][i]))
        #print("{}, act_store = {}".format(key_act, act_store[key_act][i]))
        #if i == 1:
        #    break

def load_json(write_dir, max_step, obs_store, act_store, infos_store):
    """
    Load all json files to memory.
    """
    for file_name in os.listdir(write_dir):
        print(file_name)
        if file_name.endswith('.dat'):
            with open(os.path.join(write_dir, file_name)) as json_file:
                data = json.load(json_file)
                split_words = file_name.split('_')
                #print("split_words", split_words)
                agent_ID = split_words[1]

                _load_json(agent_ID, max_step, obs_store, act_store, infos_store, data)

def log_eps(write_eps_dir, file_name, store):
    """
    Log episode data from trainer callback.
    """
    with open(write_eps_dir + file_name + '.dat', 'w') as outfile:
        json.dump(store, outfile, indent=3) # write to file in json format:

def load_eps(write_eps_dir, file_name, store):
    """
    Load episode data to memory storage.
    """
    for f in os.listdir(write_eps_dir):
        #print(file_name)
        if f == file_name:
            with open(os.path.join(write_eps_dir, f)) as json_file:
                store = json.load(json_file)
                #print(store)
                return store

def log_json_gzip(agt_id, eps_id, sample_obj, write_dir):
    """
    Output as training data as json files.
    """

    global file_num
    file_name = str(file_num) + '_' + str(agt_id) + '_' + str(eps_id)
    tmp_dict = {}
    tmp_dict["eps"] = {}
    for i,r in enumerate(sample_obj.rows()): # each row is a step dictionary
        tmp_dict["eps"][str(i)] = {}
        for k,v in r.items():
            tmp_dict["eps"][str(i)][k] = str(v)

        #with open(write_dir + file_name + '.dat', 'w') as outfile:
        #    json.dump(tmp_dict, outfile, indent=3) # write to file in json format:

        with gzip.GzipFile(write_dir + file_name + '.gzip', 'w') as fout:
            fout.write(json.dumps(tmp_dict).encode('utf-8'))

    file_num = file_num + 1

def load_json_gzip(write_dir, max_step, obs_store, act_store, infos_store):
    """
    Load all json files to memory.
    """
    for file_name in os.listdir(write_dir):
        print(file_name)
        if file_name.endswith('.gzip'):

            #with open(os.path.join(write_dir, file_name)) as json_file:
            #    data = json.load(json_file)

            with gzip.GzipFile(write_dir + file_name, 'r') as fin:
                data = json.loads(fin.read().decode('utf-8'))

                split_words = file_name.split('_')
                #print("split_words", split_words)
                agent_ID = split_words[1]

                _load_json(agent_ID, max_step, obs_store, act_store, infos_store, data)