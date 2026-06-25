"""
The read module contains methods that can be used to read in- and output
files. The methods can be used stand-alone but are also available from the
Model object. All the methods return the data as Pandas DataFrames.

Examples
--------
>>> import phydrus as ps
>>> ps.read.read_obs_node()

or

>>> ml.read_obs_node()

"""

from pandas import read_csv, DataFrame, to_numeric, concat

from .decorators import check_file_path


def read_profile(path="PROFILE.OUT"):
    """
    Method to read the PROFILE.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the profile out file. default is "PROFILE.OUT".

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the profile data

    """
    data = _read_file(path=path, start="depth", idx_col="n")
    return data


def read_run_inf(path="RUN_INF.OUT", usecols=None):
    """
    Method to read the RUN_INF.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the run_inf out file. default is "RUN_INF.OUT".
    usecols: list of str optional
        List with the names of the columns to import. Default is all columns.

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the run_inf data

    """
    data = _read_file(path=path, start="TLevel", idx_col="TLevel",
                      usecols=usecols)
    return data


@check_file_path
def read_i_check(path="I_CHECK.OUT"):
    """
    Method to read the I_CHECK.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the I_Check out file. default is "I_Check.OUT".

    Returns
    -------
    data: dict
        Dictionary with the node as a key and a Pandas DataFrame as a value.

    """
    names = ["theta", "h", "log_h", "C", "K", "log_K", "S", "Kv"]

    end = []
    start = 0

    with open(path) as file:
        # Find the starting line
        for i, line in enumerate(file.readlines()):
            if "theta" in line:
                start = i
            elif "end" in line and start > 0:
                end.append(i)

        data = {}

        for i, e in enumerate(end):
            file.seek(0)  # Go back to start of file

            # Read data into a Pandas DataFrame
            nrows = e - start - 2
            data[i] = read_csv(file, skiprows=start + 1, nrows=nrows,
                               skipinitialspace=True, delim_whitespace=True,
                               names=names, dtype=float)
            start = e
        return data


def read_tlevel(path="T_LEVEL.OUT", usecols=None):
    """
    Method to read the T_LEVEL.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the t_level out file. default is "T_LEVEL.OUT".
    usecols: list of str optional
        List with the names of the columns to import. By default
        only the real fluxes are imported and not the cumulative
        fluxes. Options are: "rTop", "rRoot", "vTop", "vRoot", "vBot",
        "sum(rTop)", "sum(rRoot)", "sum(vTop)", "sum(vRoot)", "sum(vBot)",
        "hTop", "hRoot", "hBot", "RunOff", "sum(RunOff)", "Volume",
        "sum(Infil)", "sum(Evap)", "TLevel", "Cum(WTrans)", "SnowLayer".

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the t_level data

    """
    data = _read_file(path=path, start="rTop", idx_col="Time",
                      remove_first_row=True, usecols=usecols)
    data = data.set_index(to_numeric(data.index, errors='coerce'))
    return data


def read_alevel(path="A_LEVEL.OUT", usecols=None):
    """
    Method to read the A_LEVEL.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the t_level out file. default is "A_LEVEL.OUT".
    usecols: list of str optional
        List with the names of the columns to import.

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the a_level data

    """
    data = _read_file(path=path, start="Time", idx_col="Time",
                      remove_first_row=True, usecols=usecols)
    return data


def read_solute(path="SOLUTE1.OUT"):
    """
    Method to read the SOLUTE.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the solute out file. default is "SOLUTE1.OUT".

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the a_level data

    """
    data = _read_file(path=path, start="Time", idx_col="Time",
                      remove_first_row=True)
    return data


@check_file_path
def _read_file(path, start, end="end", usecols=None, idx_col=None,
               remove_first_row=False):
    """
    Internal method to read Hydrus output files.

    Parameters
    ----------
    path: str
        String with the filepath.
    start: str
        String that determines the start of the data to be imported.
    end: str, optional
        String that determines the end of the data to be imported.
    usecols: list, optional
        List with the names of the columns to import. Default is all columns.
    idx_col: str, optional
        String with the name used for the index column.
    remove_first_row: bool, optional
        Remove the first row if True. Default is False.

    Returns
    -------
    data: pandas.DataFrame
        Pandas DataFrame with the imported data.

    """
    with open(path) as file:
        # Find the starting line
        for i, line in enumerate(file.readlines()):
            if start in line:
                s = i
            elif end in line:
                e = i
                break
        file.seek(0)  # Go back to start of file

        # Read data into a Pandas DataFrame
        data = read_csv(file, skiprows=s, nrows=e - s - 2, usecols=usecols,
                        index_col=idx_col, skipinitialspace=True,
                        delim_whitespace=True)

        if remove_first_row:
            data = data.drop(index=data.index[0]).apply(to_numeric,
                                                        errors="ignore")
        else:
            data = data.apply(to_numeric, errors="ignore")

    return data


@check_file_path
def read_obs_node(path="OBS_NODE.OUT", nodes=None, conc=False, co2=False,cols=None):
    """
    Method to read the OBS_NODE.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the OBS_NODE out file. default is
        "OBS_NODE.OUT".
    nodes: list of ints, optional
        nodes to imoport
    conc: boolean, optional
    cols: list of strs, optional
        List of strings with the columns to read.

    Returns
    -------
    data: dict
        Dictionary with the node as a key and a Pandas.DataFrame as a value.

    """
    data = {}
    with open(path) as file:
        # Find the starting times to read the information
        for i, line in enumerate(file.readlines()):
            if "time" in line:
                start = i
            elif "end" in line:
                end = i
                break

    df1 = read_csv(path, skiprows=start, index_col=0, nrows=end - start - 1,
                   skipinitialspace=True, delim_whitespace=True, engine="c")
    if cols is None:
        cols = ["h", "theta", "Temp"]
    if conc:
        cols.append("Conc")
    if co2:
        cols.append("CO2")

    for i, node in enumerate(nodes):
        if i > 0:
            usecols = [f"{c}.{i}" for c in cols]
        else:
            usecols = cols

        df = df1.loc[:, usecols]
        df.columns = cols
        data[node] = df

    return data


@check_file_path
def read_nod_inf(path="NOD_INF.OUT", times=None):
    """
    Method to read the NOD_INF.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the NOD_INF out file. default is "NOD_INF.OUT".
    times: int, optional
        Create a DataFrame with nodal values of the pressure head, the water
        content, the solution and sorbed concentrations, and temperature,
        etc, at the time "times". default is None.

    Returns
    -------
    data: dict
        Dictionary with the time as a key and a Pandas DataFrame as a value.

    """
    use_times = []
    start = []
    end = []

    with open(path) as file:
        # Find the starting times to read the information
        for i, line in enumerate(file.readlines()):
            if "Time" in line and "Date" not in line:
                time = line.replace(" ", "").split(":")[1].replace("\n", "")
                use_times.append(float(time))
            elif "Node" in line:
                start.append(i)
            elif "end" in line:
                end.append(i)
        if times is None:
            times = use_times
        # Read the data into a Pandas DataFrame
        data = {}
        for s, e, time in zip(start, end, use_times):
            if time in times:
                file.seek(0)  # Go back to start of file
                df = read_csv(file, skiprows=s,
                                      skipinitialspace=True,
                                      delim_whitespace=True,
                                      usecols=[i for i in range(0,9,1)],
                                      nrows=e - s - 2)
                df = df.drop([0])
                df = df.apply(to_numeric)
                # data[time] = pd.read_csv(file, skiprows=s,
                #                       skipinitialspace=True,
                #                       delim_whitespace=True,
                #                       usecols=[i for i in range(0,9,1)],
                #                       nrows=e - s - 2)
                # data[time] = data[time].drop([0])
                # data[time] = data[time].apply(pd.to_numeric)
                file.seek(0)  # Go back to start of file
                df_co2 = read_csv(file, skiprows=s,
                                      skipinitialspace=True,
                                      delim_whitespace=True,
                                      usecols=[i for i in range(10,14,1)],
                                      nrows=e - s - 2)
                df_co2.rename({'CO2': 'Temp', 'CO2.1': 'CO2', 'Prod': 'CO2_prod'}, axis=1, inplace=True)
                df_co2 = df_co2.drop([0])
                df_co2 = df_co2.apply(to_numeric)
                df = concat([df, df_co2], axis=1)
                data[time] = df
    if len(data) == 1:
        return next(iter(data.values()))
    else:
        return data


@check_file_path
def read_balance(path="BALANCE.OUT", usecols=None):
    """
    Method to read the BALANCE.OUT output file.

    Parameters
    ----------
    path: str, optional
        String with the name of the run_inf out file. default is "BALANCE.OUT".
    usecols: list of str optional
        List with the names of the columns to import. By default:
        ['Area','W-volume','In-flow','h Mean','Top Flux', 'Bot Flux',
        'WatBalT','WatBalR'].

    Returns
    -------
    data: pandas.DataFrame
        Pandas with the balance data

    """
    if usecols is None:
        usecols = ["Length", "W-volume", "In-flow", "h Mean", "Top Flux",
                   "Bot Flux", "WatBalT", "WatBalR"]
    # print('read_balance')

    lines = open(path).readlines()
    use_times = []
    start = []
    end = [16]
    for i, line in enumerate(lines):
        for x in usecols:
            if x in line:
                line1 = x
                line2 = line.replace("\n", "").split(" ")[-1]
                line3 = line.replace("  ", " ").split(" ")[-2]
                lines[i] = [line1, line2, line3]
                # print(lines[i])

        if "Time" in line and "Date" not in line:
            time = float(
                line.replace(" ", "").split("]")[1].replace("\n", ""))
            use_times.append(time)
        if "Length" in line:
            start.append(i)
        if "WatBalR" in line:
            end.append(i + 1)
        if "Sub-region" in line:
            subreg = line.replace("  ", " ").replace("\n", "").split(" ")[-1]

    # print(start, end, use_times)
    data = {}
    for s, e, time in zip(start, end, use_times):
        df = DataFrame(lines[s:e]).set_index(0).T
        # print(s, e, time)
        # print(lines[s:e])
        index = {}
        for x in range(int(subreg) + 1):
            index[x + 1] = x
            df = df.rename(index=index)
        data[time] = df
    # for t in use_times:
    #     print(data[t])
    return data


def read_co2_inf(path="CO2_INF.OUT", usecols=None):
    """
    Method to read the CO2_INF.OUT output file.

    Parameters
    ----------
    """
    data = _read_file(path=path, start="Time", idx_col="Time",
                      remove_first_row=True, usecols=usecols)
    return data