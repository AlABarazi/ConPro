import pandas as pd

def read_csv(filename="init_tasks_comma.csv"):
    """
    read csv file
    :return:
    """
    df = pd.read_csv(filename, header=0)
    return df

def filter_cols(df, filter_key="KEY"):
    cols = df.columns
    filtered_cols = [header for header in df.columns if filter_key in header]
    return filtered_cols

def read_task(df, cols, agent, task_name="dry_wall1"):
    df = df.set_index('task_name')
    agent["tasks"] = {key:{} for key in cols}
    agent["zone"] = df.loc[task_name, "zone"]
    #print (agent)
    # todo: add dependancy for phases
    for phase in cols:
        agent["tasks"][phase]["amount"] = df.loc[task_name, phase]
        agent["tasks"][phase]["start_date"] = df.loc[task_name, "start_date"]
        agent["tasks"][phase]["end_date"] = df.loc[task_name, "end_date"]
        # agent[phase]["u/manhour"] = df.loc[task_name, phase]
        # agent["{}_amount".format(phase)] = df.loc[task_name, phase]
        # agent["{}_start_date".format(phase)] = df.loc[task_name, "start_date"]
        # agent["{}_end_date".format(phase)] = df.loc[task_name, "end_date"]
        # agent["{}_u/manhour".format(phase)] = df.loc[task_name, "end_date"]

    return agent
def main():
    df = read_csv(filename="init_tasks_comma.csv")
    cols = filter_cols(df)
    # print (cols)
    read_task(df, cols)

if __name__ == "__main__":
    main()
