class MentalHealth:
    def __init__(self):
        self.knowledge_base = {
            "anxiety": ["symptoms", "treatment options"],
            "depression": ["signs", "therapy"],
            "trauma": ["PTSD", "coping mechanisms"]
        }
        self.resources = {
            "hotlines": ["National Suicide Prevention Lifeline", "Crisis Text Line"],
            "online_resources": ["Mental Health America", "The Trevor Project"]
        }

    def provide_info(self, topic):
        if topic in self.knowledge_base:
            return f"Ah, {topic}! I can tell you all about that. {self.knowledge_base[topic][0]} is a great place to start."
        else:
            return "I'm not familiar with that topic, but I can try to learn more about it!"

    def provide_resources(self):
        return "If you're struggling with your mental health, there are resources available to help. You can call a hotline like the National Suicide Prevention Lifeline or text the Crisis Text Line. There are also online resources like Mental Health America and The Trevor Project that can provide support and information."

jaicat_mental_health = MentalHealth()

# Example interaction
user_input = "What's the deal with anxiety?"
response = jaicat_mental_health.provide_info("anxiety")
print(response)  # Output: Ah, anxiety! I can tell you all about that. symptoms is a great place to start.

user_input = "I need help with my mental health. What resources are available?"
response = jaicat_mental_health.provide_resources()
print(response)  # Output: If you're struggling with your mental health, there are resources available to help. You can call a hotline like the National Suicide Prevention Lifeline or text the Crisis Text Line. There are also online resources like Mental Health America and The Trevor Project that can provide support and information.
