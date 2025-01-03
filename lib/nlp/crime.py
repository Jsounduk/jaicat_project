# lib/nlp/crime.py

import pandas as pd

class CrimeAnalyzer:
    def __init__(self, data_path):
        """
        Initialize the CrimeAnalyzer with a path to the crime data CSV file.
        Parameters:
        - data_path: Path to the CSV file containing crime data.
        """
        self.data_path = data_path
        self.crime_data = self.load_data()

    def load_data(self):
        """Load crime data from a CSV file."""
        try:
            data = pd.read_csv(self.data_path)
            return data
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def get_crime_statistics(self):
        """Get basic statistics about the crime data."""
        if self.crime_data is not None:
            return self.crime_data.describe()
        return None

    def analyze_crime_type(self, crime_type):
        """
        Analyze the occurrences of a specific crime type.
        Parameters:
        - crime_type: The type of crime to analyze.
        Returns:
        - The number of occurrences of the specified crime type.
        """
        if self.crime_data is not None:
            return self.crime_data[self.crime_data['crime_type'] == crime_type].shape[0]
        return 0

    def get_top_crime_types(self, n=5):
        """
        Get the top N crime types based on occurrences.
        Parameters:
        - n: The number of top crime types to return.
        Returns:
        - A list of top N crime types and their counts.
        """
        if self.crime_data is not None:
            return self.crime_data['crime_type'].value_counts().head(n)
        return None

    def filter_crimes_by_location(self, location):
        """
        Filter crime data by a specific location.
        Parameters:
        - location: The location to filter by.
        Returns:
        - Filtered DataFrame with crimes in the specified location.
        """
        if self.crime_data is not None:
            return self.crime_data[self.crime_data['location'] == location]
        return None
