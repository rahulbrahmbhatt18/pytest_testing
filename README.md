## Testing with Pytest 

As a software engineer who has worked with **test-driven development (TDD)**, TDD is the best practice for ensuring code reliability, maintainability, and scalability. By writing tests before writing code, TDD encourages a clear understanding of the desired functionality and promotes modular, well-structured code design. However, there have been some situations where I developed a piece of code first, and then I designed the test cases for the code to make sure that the code never breaks in subsequent changes or updates. While this approach deviates from the strict TDD methodology of writing tests before code, it still prioritizes the importance of comprehensive test coverage to maintain the integrity of the codebase. Hence, let me discuss how I approach testing the code that I developed in most situations. 

In such cases (as in the one provided for this assessment), I typically begin by thoroughly understanding the requirements and expected behavior of the code. 
- **qc_s3_download_create_formatted()**: This is the function that reformatS3.py calls and is responsible for managing the download and organization of files from a remote location, such as Amazon S3. This function ensures that files are downloaded accurately, and are organized efficiently. It sets up local directories, parses file names to extract relevant information, performs the file download, and reports the results of the process by calling the appropriate functions.

Now that I have understood the requirements and the expected behavior of the code, I will design a comprehensive suite of test cases that cover various scenarios, including normal inputs, edge cases, and potential errors. I will ensure that each test case is focused, independent, and verifies a specific aspect of the code's functionality. Once the test cases are in place, I will execute them against the code, carefully observing the results and debugging any issues that arise. Since this codebase is not very complex and is relatively small, I would prefer to use the bottom-up approach of testing for testing the individual functions. This approach allows for thorough testing of each function in isolation, ensuring that they behave as expected before integrating them into larger components or systems. By focusing on testing small units of code first, I can catch and address any issues early in the development process, leading to a more robust and reliable software solution. Additionally, the bottom-up approach facilitates easier debugging and troubleshooting, as it enables me to isolate and pinpoint the root cause of any defects. Hence, beginning with **combine_date_time_num()**, following the **bottom-up approach**:

1. **combine_date_time_num()**: It combines separate columns for date and time into a single datetime column. Here are a few points for what the function should be tested on:

- Valid inputs for date and time to ensure correct formatting.
- Edge cases such as leap years, boundary values, and unusual date/time formats.
- Invalid inputs, including missing or incorrect date/time data, to ensure proper error handling.
  
2. **safe_extract()**: Safely extracts elements from a list, dictionary, etc., and handles the exceptions. This function should be tested for:

- Valid inputs where the extraction is successful.
- Invalid inputs where extraction fails and the function handles the error properly.

3. **parse_scored_filenames()**: Parses filenames to extract information like ID, task number, date, and time. It uses the combine_date_time_num() function. This function should be tested for:

- List of filenames representing different scenarios (e.g., valid filenames, missing components in filenames).
- Empty filename list.
- Filenames containing different separators.
- Various lengths of task numbers.

4. **list_files_multipattern()**: Lists files in a directory matching multiple patterns. It filters files based on inclusion and exclusion patterns. This function should be tested for:

- Different patterns for file matching.
- Exclusion patterns.
- Directories containing files that match or don't match the patterns.
- Different search types ('basename' and 'dirname').
- full_names set to True and False.

5. **qc_s3_download_create_formatted()**: Performs various operations related to S3 download, and formatting of files. It internally uses **list_files_multipattern()**, **parse_scored_filenames()**, **get_usrid_from_specdirname()**, and **get_sesid_from_specdirname()**  functions. Here, we have to **mock data** for testing since the function interacts with external resources such as S3 and file system directories. By mocking data, we can simulate different scenarios and ensure that the function behaves as expected under various conditions without relying on real-world data, ensuring consistent and reliable test results. This function should be tested for:

- Different combinations of input parameters.
- Existing and non-existing directories/files to verify that the function creates required directories and files correctly for the existing ones and it raises an exception when provided with non-existing directories.
- With and without subject_list.
- With skip_copy set to True and False.
- With verbose set to True and False.

6. **study_export_to_id_list()**: Processes a CSV file containing metadata, extracts session and user IDs, and optionally checks file existence in a specified directory. It may raise a ValueError if the file format is not supported or if the specified columns are missing. It should be tested for:

- Valid CSV files containing different types of data.
- With and without checking file existence.
- With and without specifying additional fields.
- With empty file or missing required columns.

7. **get_sesid_from_specdirname()**: Extracts session IDs from strings in the format <user_id>_<session_id>. It should be tested for:

- Valid inputs representing different scenarios.
- Invalid inputs.

8. **get_usrid_from_specdirname()**: Extracts user IDs from strings in the format <user_id>_<session_id>. It should be tested for:

- Valid inputs representing different scenarios.
- Invalid inputs.

Now that I have a clear plan of what each function should be tested on following the bottom-up approach, I would write test suite for each of these functions, and make sure that it passes all the test cases. After making sure that all the test cases are passed, it is important to know and understand that my test covers all the functions, and that it does not miss any critical edge case. In order to ensure that, I will now check for code coverage. **Code coverage** is a metric that measures the percentage of code lines executed during the testing process. Ideally, the test suite should aim for a high code coverage, covering as much of the codebase as possible to ensure that all lines of code are executed and tested at least once. In this scenario, achieving **a code coverage of 90% or higher would be desirable**, indicating that the majority of the code paths have been exercised by the tests I created. 

In order to automate unit-tests, **I prefer tools such as Pytest**, which is widely used for testing Python applications. In the past, I have utilized **JUnit and Mockito** for unit testing in **Java applications**. However, since this is a Python application, Pytest is the preferred choice for writing and executing test cases. Additionally, Pytest seamlessly integrates with libraries such as **pytest-mock** for mocking data and dependencies, ensuring efficient and effective unit testing. To check for code coverage, I would use a code coverage tool such as **pytest-cov or coverage.py**, which provides detailed reports showing which lines of code were executed during testing and which lines were not. By analyzing these reports, I can identify any gaps in test coverage and write additional test cases to fill those gaps, ensuring comprehensive testing of the entire codebase.

Now that I have understood the code, developed the test suite for each of these functions, and checked the code coverage aiming for more than 90%, where all lines of code are executed and tested at least once. Let me discuss some of the **common challenges associated with unit tests** in general:

- Unit tests can sometimes be too tightly coupled to the implementation details, making them prone to breaking when the implementation changes.
- Writing comprehensive unit tests for complex functions or modules can be time-consuming, leading to potential gaps in test coverage.
- Maintaining a large number of unit tests can become challenging over time, especially when dealing with evolving codebases.
- In the specific case of this codebase, these challenges can be mitigated by following best practices such as writing clear, concise tests, using mocking to isolate dependencies, and regularly refactoring tests to keep them maintainable.

That concludes the discussion on how I would approach the testing of this codebase, write the test suite and test it, and ensure that it has a high code coverage. I have written tests for the same under the **tests folder** of this repo, feel free to look how I code the test cases discussed here. 

Thank you for reading! 
