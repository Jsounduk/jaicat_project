class Education:
    def __init__(self):
        self.knowledge_base = {
            "STEM": ["math", "science"],
            "humanities": ["history", "literature"],
            "study_skills": ["time management", "note-taking"]
        }
        self.resources = {
            "online_courses": ["Coursera", "edX"],
            "study_guides": ["Khan Academy", "SparkNotes"]
        }

    def provide_info(self, topic):
        if topic in self.knowledge_base:
            return f"Ah, {topic}! I can tell you all about that. {self.knowledge_base[topic][0]} is a great place to start."
        else:
            return "I'm not familiar with that topic, but I can try to learn more about it!"

    def provide_resources(self):
        return "If you're looking to learn more, there are many online resources available. You can take online courses on platforms like Coursera or edX, or use study guides like Khan Academy or SparkNotes to help you understand the material."

jaicat_education = Education()

# Example interaction
user_input = "What's the deal with STEM?"
response = jaicat_education.provide_info("STEM")
print(response)  # Output: Ah, STEM! I can tell you all about that. math is a great place to start.

user_input = "I need help with my studies. What resources are available?"
response = jaicat_education.provide_resources()
print(response)  # Output: If you're looking to learn more, there are many online resources available. You can take online courses on platforms like Coursera or edX, or use study guides like Khan Academy or SparkNotes to help you understand the material.
