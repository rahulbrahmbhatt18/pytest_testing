import os
import fnmatch
import pandas as pd
import shutil
import numpy as np
from datetime import datetime


####################
# DEFINE FUNCTIONS #
####################

# Example usage
# data_dict = {'date': [20210817, 20210818], 'time': [123456, 789012]}
# df = pd.DataFrame(data_dict)
# result = combine_date_time_num(df)
# print(result)

def combine_date_time_num(data, comb_name="datetime", date_name="date", time_name="time", remove_sep=True):
    if date_name not in data.columns or time_name not in data.columns:
        print("Warning: date/time extraction failed")
        return data

    date = data[date_name].astype(str)
    datey = date.str[0:4]
    datem = date.str[4:6]
    dated = date.str[6:8]

    time = data[time_name].astype(str)
    timeh = time.str[0:2]
    timem = time.str[2:4]
    times = time.str[4:6]

    data[comb_name] = datey + "-" + datem + "-" + dated + "T" + timeh + ":" + timem + ":" + times

    if remove_sep:
        data = data.drop(columns=[date_name, time_name])

    return data


def safe_extract(s, x):
    try:
        return s[x]
    except Exception as e:
        print(f"Error processing {s} at index {x}: {e}")
        return None  # or some default value, or just skip it with `return`


# Example usage
#fns = ['file1.ext', 'file2.ext']
#result = parse_scored_filenames(fns)
#print(result)

def parse_scored_filenames(fns):
    fn_ext = [os.path.basename(fn) for fn in fns]
    fn = [os.path.splitext(f)[0] for f in fn_ext]
    fn = [f.replace('cat', 'dog') for f in fn]

    setz = [f.split('_') for f in fn]

    type = [safe_extract(s, 0) for s in setz]
    id1 = [safe_extract(s, 1) for s in setz]
    id2 = [safe_extract(s, 2) for s in setz]
    task = [safe_extract(s, 3) for s in setz]
    task = [s if len(s) <= 3 else "" for s in task]  # empty elements when there is no task (e.g, dog files)
    date = [safe_extract(s, -2) for s in setz]
    time = [safe_extract(s, -1) for s in setz]

    df = pd.DataFrame({'id1': id1, 'id2': id2, 'tasknum': task, 'date': date, 'time': time, 'type': type})
    df = combine_date_time_num(df, 'datetime', 'date', 'time', remove_sep=False)

    df['filename'] = fn_ext
    return df


# Example usage
# path = "/path/to/your/files"
# patterns = ["*.json", "scor*"]
# excludes = [] #["*error*"]
# result = list_files_multipattern(path, patterns, excludes)
# print(result)


def list_files_multipattern(path, patterns=None, excludes=None, search_type='basename', full_names=True):
    if patterns is None:
        patterns = ['*']
    if excludes is None:
        excludes = []

    def st(x):
        if search_type == 'basename':
            return os.path.basename(x)
        elif search_type == 'dirname':
            return os.path.dirname(x)
        else:
            return x

    # List files recursively based on matching all patterns
    ll = [os.path.join(dp, f) for dp, _, filenames in os.walk(path) for f in filenames if
          all(fnmatch.fnmatch(f, pattern) for pattern in patterns)]

    # Exclude files based on the exclusion patterns
    for exclude_pattern in excludes:
        ll = [f for f in ll if not fnmatch.fnmatch(st(f), exclude_pattern)]

    # Filter files based on the remaining inclusion patterns
    for pattern in patterns[1:]:
        ll = [f for f in ll if fnmatch.fnmatch(st(f), pattern)]

    # Return full path names or base names based on the full_names flag
    if full_names:
        return ll
    else:
        return [os.path.basename(f) for f in ll]


# Usage example
# s3_dir = "/path/to/your/s3/files"
# result_dir = "/path/to/your/result/files"
# target_dir = "/path/to/your/target/dir"
# subject_list = ["subject1", "subject2"]
# output = qc_s3_download_create_formatted(s3_dir, result_dir, target_dir, subject_list, verbose=True)
# print(output)

def qc_s3_download_create_formatted(s3_dir, result_dir=None,
                                            target_dir=None,
                                            subject_list=None,
                                            skip_copy=False,
                                            verbose=False):
    # Function list_files_multipattern is assumed to be defined as in the previous example
    # Function parse_scored_filenames is assumed to be defined
    # Additional helper functions like get_usrid_from_specdirname, get_sesid_from_specdirname
    # are assumed to be defined somewhere in the code.

    def simple_date():
        return datetime.now().strftime('%Y%m%d')

    ll1 = list_files_multipattern(s3_dir, patterns=["scorin*", "*.json"])
    print(f"Found {len(ll1)} 'scored' files")

    if result_dir is None:
        ll2 = list_files_multipattern(s3_dir, patterns=["result*", "*.json"])
    else:
        ll2 = list_files_multipattern(result_dir, patterns=["result*", "*.json"])

    dat_dirs = ["cognition-scores", "cognition-uploads"]
    file_sep = os.sep
    datedir = simple_date()
    tempd = target_dir or os.tempdir
    loc_dir = os.path.join(tempd, datedir)
    out_dir = os.path.join(loc_dir, "output")

    os.makedirs(loc_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    for lli, su in zip([ll1, ll2], dat_dirs):
        bbb = parse_scored_filenames([os.path.basename(f) for f in lli])
        if len(bbb) < 1:
            continue
        all_id = ["{}_{}".format(row['id1'], row['id2']) for _, row in bbb.iterrows()]

        if subject_list is not None:
            sub_sel = [id in subject_list for id in all_id]

            if sum(sub_sel) < 1:
                print("subject_list filter option failed to find xxxx_xxxx format, trying for user ids")
                user_ids = get_usrid_from_specdirname(all_id)
                sub_sel = [user_id in subject_list for user_id in user_ids]

            if sum(sub_sel) < 1:
                print("subject_list filter option failed to find user ids, trying for session ids")
                session_ids = get_sesid_from_specdirname(all_id)
                sub_sel = [session_id in subject_list for session_id in session_ids]

            if sum(sub_sel) < 1:
                raise Exception("no matches found from any list for subject_list filter, removed all subjects")

            all_id = [id for id, sel in zip(all_id, sub_sel) if sel]
            ll = [l for l, sel in zip(ll, sub_sel) if sel]


        sub_dirs = list(set(all_id))
        in_situ = [os.path.join(loc_dir, su, sub) for sub in sub_dirs]

        if not all(os.path.exists(p) for p in in_situ):
            di = os.path.dirname(in_situ[0])
            os.makedirs(di, exist_ok=True)
            for p in in_situ:
                os.makedirs(p, exist_ok=True)

        for j, sub_dir in enumerate(sub_dirs):
            if not os.path.exists(in_situ[j]):
                os.makedirs(in_situ[j])
            id_sel = [aid == sub_dir for aid in all_id]
            selected_files = [f for f, sel in zip(lli, id_sel) if sel]
            if not skip_copy:
                if verbose:
                    print("copying", ', '.join([os.path.basename(f) for f in selected_files]))
                for f in selected_files:
                    shutil.copy(f, os.path.join(in_situ[j], os.path.basename(f)))

    return {'loc_dir': loc_dir, 'dat_dirs': dat_dirs, 'out_dir': out_dir}


# Example usage
# fn = 'your_data_file.csv'
# output = study_export_to_id_list(fn, check_files_exist=True, as_table=True)
# print(output)

def study_export_to_id_list(fn, check_files_exist=False, as_table=False, exclude_missing=True,
                            add_field=None, scores_loc="~/scores/"):
    SES_CNT = "user_session_cnt"
    SES_SET = "user_session_str"
    USER_ID = "user_id"
    SES_ID = "session_id"
    SUB_ID = "subject_id"

    # Read the CSV file into a pandas DataFrame
    meta = pd.read_csv(fn)

    # If check_files_exist option is enabled
    if check_files_exist:
        allf = os.listdir(os.path.expanduser(scores_loc))
    print("test")
    if all(c in meta.columns for c in [SES_CNT, SES_SET]):
        # Newer exports
        if all(meta[SES_CNT].notna()):
            # Newer exports with only 1 session per subject
            pass  # Placeholder: not sure what to do in this case based on the R code
        else:
            # Newer exports with multiple sessions for at least 1 subject
            maxn = meta[SES_CNT].max()
            ss = meta[SES_SET].str.split(",", expand=False)
            # Reverse order and pad with NAs
            ss = [list(reversed(s)) + [np.nan] * (maxn - len(s)) for s in ss]

            sesn = []
            for j in range(maxn):
                sesidz = [s[j] for s in ss]
                nxt_set = pd.Series(
                    [f"{uid}_{sid}" if pd.notna(sid) else np.nan for uid, sid in zip(meta[USER_ID], sesidz)])

                if check_files_exist and nxt_set.dropna().isin(allf).any():
                    print("WARNING! ", ", ".join(nxt_set[~nxt_set.isin(allf)]), " not found in score jsons directory")

                sesn.append(nxt_set)

            if as_table:
                out = pd.DataFrame.from_items(zip([f"visit_{i + 1}" for i in range(maxn)], sesn))
                if SUB_ID in meta.columns:
                    out[SUB_ID] = meta[SUB_ID]

                if add_field is not None:
                    if add_field in meta.columns:
                        out[add_field] = meta[add_field]
                    else:
                        raise ValueError(
                            f"add_field ({add_field}) must be a column of the dataset, e.g., {', '.join(meta.columns)}")

                return out

            else:
                if exclude_missing:
                    sesn = [s.dropna() for s in sesn]
                return sesn
    else:
        raise ValueError("unsupported version of spectra portal export file")

    # Simple case of 1 session per subject
    nxt_set = meta[USER_ID] + "_" + meta[SES_ID]

    if check_files_exist and nxt_set.dropna().isin(allf).any():
        print("WARNING! ", ", ".join(nxt_set[~nxt_set.isin(allf)]), " not found in score jsons directory")

    return nxt_set


# Example usage
# x = ["user1_session1", "user2_session2", "user3_session3"]
# print(get_sesid_from_specdirname(x))  # Output: ['session1', 'session2', 'session3']
# print(get_usrid_from_specdirname(x))  # Output: ['user1', 'user2', 'user3']


def get_sesid_from_specdirname(x):
    """
    Extract the session ID from a string, where the string is assumed to be
    in the format: "<user_id>_<session_id>".

    Parameters:
    x (list of str): List of strings, each in the format: "<user_id>_<session_id>"

    Returns:
    list of str: The extracted session IDs
    """
    return [item.split("_")[1] for item in x]

def get_usrid_from_specdirname(x):
    """
    Extract the user ID from a string, where the string is assumed to be
    in the format: "<user_id>_<session_id>".

    Parameters:
    x (list of str): List of strings, each in the format: "<user_id>_<session_id>"

    Returns:
    list of str: The extracted user IDs
    """
    return [item.split("_")[0] for item in x]

# end function definitions
##############################################################################
