# lib/nlp/fitness.py

class FitnessNLP:
    def __init__(self):
        pass

    def analyze_fitness_data(self, data):
        """
        Analyze the input fitness data and provide insights.

        Parameters:
        - data: A dictionary containing fitness data such as steps, calories burned, and workout duration.

        Returns:
        - A string summary of the fitness data analysis.
        """
        steps = data.get('steps', 0)
        calories_burned = data.get('calories_burned', 0)
        workout_duration = data.get('workout_duration', 0)  # in minutes

        analysis = f"You have taken {steps} steps, burned {calories_burned} calories, and worked out for {workout_duration} minutes."
        return analysis

    def recommend_workout(self, fitness_level):
        """
        Recommend a workout based on the user's fitness level.

        Parameters:
        - fitness_level: The fitness level of the user (e.g., beginner, intermediate, advanced).

        Returns:
        - A workout recommendation.
        """
        workouts = {
            "beginner": "Try a 20-minute brisk walk or light yoga.",
            "intermediate": "Consider a 30-minute jog or a strength training session.",
            "advanced": "Challenge yourself with a 45-minute HIIT workout or heavy weightlifting."
        }

        return workouts.get(fitness_level.lower(), "No workout recommendations available.")

    def set_fitness_goal(self, goal):
        """
        Set a fitness goal for the user.

        Parameters:
        - goal: A string indicating the fitness goal (e.g., "lose weight", "gain muscle", "run a marathon").

        Returns:
        - A message confirming the goal has been set.
        """
        return f"Your fitness goal has been set to: {goal}"

