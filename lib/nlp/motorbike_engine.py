import wikipedia
 
 # Define a function to retrieve information on motorbikes
def    get_motorbike_info(query):
     results = wikipedia.search(query)
     if results:
         page = wikipedia.page(results[0])
         return page.content
     else:
         return "I couldn't find any information on that motorbike."
 
# Define a function to retrieve information on engines
def    get_engine_info(query):
     results = wikipedia.search(query)
     if results:
         page = wikipedia.page(results[0])
         return page.content
     else:
         return "I couldn't find any information on that engine."
 
# Define a function to provide motorbike and engine information to the user
def    provide_motorbike_engine_info(query):
     if "motorbike" in query:
         return get_motorbike_info(query)
     elif "engine" in query:
         return get_engine_info(query)
     else:
        return "I'm not sure what you're looking for. Can you be more specific?"
 
# Example usage:
query = "What is a Harley-Davidson?"
print(provide_motorbike_engine_info(query))

query = "How does a V8 engine work?"
print(provide_motorbike_engine_info(query))
  
def get_motorbike_info(query):
    results = wikipedia.search(query)
    if results:
        page = wikipedia.page(results[0])
        return page.content

def main():
    while True:
        query = input("Enter your query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        print(provide_motorbike_engine_info(query))

if __name__ == "__main__":
    main()
