import os
import pytest
import pandas as pd
import tempfile
from source.reformatFunctions import (combine_date_time_num, safe_extract, parse_scored_filenames,
                                      list_files_multipattern, qc_s3_download_create_formatted,
                                      study_export_to_id_list, get_sesid_from_specdirname, get_usrid_from_specdirname)


@pytest.fixture
def sample_data():
    return pd.DataFrame({'date': [20210817, 20210818], 'time': [123456, 789012]})


def test_combine_date_time_num(sample_data, capsys):
    # Test with valid input data
    result = combine_date_time_num(sample_data)
    assert 'datetime' in result.columns
    assert result['datetime'].iloc[0] == '2021-08-17T12:34:56'

    # Test with missing date or time columns
    combine_date_time_num(pd.DataFrame({'date': [20210817]}))
    combine_date_time_num(pd.DataFrame({'time': [123456]}))
    captured = capsys.readouterr()
    assert "Warning: date/time extraction failed" in captured.out

    # Test with invalid input data types
    with pytest.raises(AttributeError):
        combine_date_time_num(None)
    with pytest.raises(AttributeError):
        combine_date_time_num("invalid_data")


def test_safe_extract():
    # Test with valid inputs
    assert safe_extract([1, 2, 3], 1) == 2

    # Test with invalid inputs
    assert safe_extract([1, 2, 3], 5) is None


def test_parse_scored_filenames():
    # Test with valid filenames
    filenames = ['file1_cat_123_456_task.json', 'file2_dog_789_012.json']
    result = parse_scored_filenames(filenames)
    assert 'id1' in result.columns

    # Check the transformed values after parsing the filenames
    assert result['id1'].iloc[0] == 'dog'
    assert result['type'].iloc[0] == 'file1'
    assert result['id1'].iloc[1] == 'dog'
    assert result['type'].iloc[1] == 'file2'

    # Test with empty filename list
    assert parse_scored_filenames([]).empty


@pytest.fixture
def tmpdir(tmpdir):
    # Create temporary files
    files = ['file1.json', 'file2.txt', 'file3.json']
    for file in files:
        tmpdir.join(file).write('data')
    return tmpdir


def test_list_files_multipattern(tmpdir):
    # Test with valid patterns
    result = list_files_multipattern(tmpdir, patterns=['*.json'])
    assert len(result) == 2
    assert '/file1.json' in result[0] or '/file1.json' in result[1]
    assert '/file3.json' in result[0] or '/file3.json' in result[1]

    # Test with exclusion patterns
    result = list_files_multipattern(tmpdir, patterns=['*'], excludes=['*.txt'])
    assert len(result) == 2
    assert '/file1.json' in result[0] or '/file1.json' in result[1]
    assert '/file3.json' in result[0] or '/file3.json' in result[1]

    # Test with search type 'dirname'
    result = list_files_multipattern(tmpdir, patterns=['*'], search_type='dirname')
    assert len(result) == 3
    assert '/file1.json' in result[0] or '/file1.json' in result[1] or '/file1.json' in result[2]
    assert '/file2.txt' in result[0] or '/file2.txt' in result[1] or '/file2.txt' in result[2]
    assert '/file3.json' in result[0] or '/file3.json' in result[1] or '/file3.json' in result[2]


def test_qc_s3_download_create_formatted():
    # Create temporary directories
    with tempfile.TemporaryDirectory() as s3_dir:
        with tempfile.TemporaryDirectory() as result_dir:
            with tempfile.TemporaryDirectory() as target_dir:
                # Mock data
                subject_list = ['subject1', 'subject2']

                # Test with valid inputs
                result = qc_s3_download_create_formatted(s3_dir, result_dir, target_dir, subject_list)
                assert os.path.exists(result['loc_dir'])
                assert os.path.exists(result['out_dir'])

                # Test with empty subject list
                result = qc_s3_download_create_formatted(s3_dir, result_dir, target_dir)
                assert os.path.exists(result['loc_dir'])
                assert os.path.exists(result['out_dir'])

                # Test with non-existing directories
                with pytest.raises(Exception):
                    qc_s3_download_create_formatted('/non/existing/dir', subject_list=subject_list)


def test_study_export_to_id_list(tmpdir):
    # Create a temporary CSV file
    csv_file = tmpdir.join('test.csv')
    csv_file.write('user_id,session_id\nuser1,session1\nuser2,session2')

    # Test with valid CSV file
    with pytest.raises(ValueError):
        result = study_export_to_id_list(str(csv_file), check_files_exist=False)
        assert result[0] == 'user1_session1'
        assert result[1] == 'user2_session2'


def test_get_sesid_from_specdirname():
    # Test with valid input
    assert get_sesid_from_specdirname(['user1_session1', 'user2_session2']) == ['session1', 'session2']

    # Test with invalid input
    with pytest.raises(IndexError):
        get_sesid_from_specdirname(['user1', 'user2'])


def test_get_usrid_from_specdirname():
    # Test with valid input
    input_strings = ["user123_session456", "user789_session987"]
    expected_output = ["user123", "user789"]
    assert get_usrid_from_specdirname(input_strings) == expected_output

    # Test with invalid input
    invalid_input = ["user123", "invalid_format", "user_session", "user_with_multiple_underscores_session"]
    expected_output = ["user123", "invalid", "user", "user"]
    assert get_usrid_from_specdirname(invalid_input) == expected_output
