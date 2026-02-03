import wikipedia
import pyjokes

def get_joke():
    return pyjokes.get_joke()

def search_wikipedia(query):
    try:
        # Search for the query and get the summary of the first result
        results = wikipedia.summary(query, sentences=2)
        return results
    except wikipedia.exceptions.DisambiguationError as e:
        return "There are multiple results for this. Please be more specific."
    except wikipedia.exceptions.PageError:
        return "I couldn't find any Wikipedia page for that."
    except Exception as e:
        return f"An error occurred: {str(e)}"
