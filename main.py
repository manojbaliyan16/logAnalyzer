from json_file_creator import JSONFileCreator
from keyword_file_selector import KeywordFileSelector
from log_file_searcher import LogFileSearcher

def main():
    # Create instances of the three classes
    json_file_creator = JSONFileCreator()
    keyword_file_selector = KeywordFileSelector()
    log_file_searcher = LogFileSearcher()

    # Get the path to the log file
    log_file_path = log_file_searcher.get_log_file_path()
    if not log_file_path:
        return

    # Get the path to the keyword file
    keyword_file_path = log_file_searcher.get_keyword_file_path()
    if not keyword_file_path:
        return

    # Search the log file for keywords
    log_file_searcher.search_log_file(log_file_path, keyword_file_path)


if __name__ == '__main__':
    main()
