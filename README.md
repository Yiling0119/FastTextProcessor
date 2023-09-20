# FastTextProcessor
A Python library designed to simplify two fundamental data processing tasks: querying by string and calculating mean values. It offers data querying mechanism that liberates users from the hassles of populating data like existing NoSQL databases

You may refer to the examples below to run your code to get mean value or to query by string:

# Example usage of queryByString:
options = {
    "case_insensitive": True, 
    "output_format": "json",  # Choose "json" or "txt"
    "log_file": "search.log",
}
queryByString("/path/to/your/directory", "search_keyword", options)

# Example usage of calculateMean:
