from googlesearch import search

def refine_query(query):
    """
    Refine the query to improve search accuracy.
    """
    # Add "official website" to the query for better results
    if not any(word in query.lower() for word in ["website", "official", "site"]):
        query += " official website"
    return query

def find_website(query):
    try:
        # Refine the query
        refined_query = refine_query(query)
        # Perform a Google search and get the first result
        for url in search(refined_query, num_results=1):
            return url
    except Exception as e:
        return f"An error occurred: {e}"

# Sample test cases
test_cases = [
    "amity school",
    "apple china",
    "mod",
    "united colors of benetton",
    "flipkart india"
]

# Run the test cases
for query in test_cases:
    result = find_website(query)
    print(f"Query: {query} -> Website: {result}")