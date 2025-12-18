import pandas as pd

class CrimeAnalyzer:
    def __init__(self, crime_data_path):
        self.crime_data_path = crime_data_path
        self.crime_data = self.load_crime_data()

    def load_crime_data(self):
        try:
            data = pd.read_csv(self.crime_data_path)
            print("[CrimeAnalyzer] âœ… Crime data loaded successfully.")
            return data
        except FileNotFoundError:
            print(f"[CrimeAnalyzer] âŒ File not found at: {self.crime_data_path}")
            return None
        except Exception as e:
            print(f"[CrimeAnalyzer] âŒ Error loading crime data: {e}")
            return None

    def get_summary(self):
        if self.crime_data is not None:
            return self.crime_data.describe(include='all')
        else:
            return "[CrimeAnalyzer] âš ï¸ No crime data to summarize."
    def get_crime_types(self):
        if self.crime_data is not None:
            return self.crime_data['Crime Type'].unique()
        else:
            return "[CrimeAnalyzer] âš ï¸ No crime data to analyze."
    def get_crime_by_type(self, crime_type):
        if self.crime_data is not None:
            filtered_data = self.crime_data[self.crime_data['Crime Type'] == crime_type]
            if not filtered_data.empty:
                return filtered_data
            else:
                return f"[CrimeAnalyzer] âš ï¸ No data found for crime type: {crime_type}"
        else:
            return "[CrimeAnalyzer] âš ï¸ No crime data to filter."
    def get_crime_statistics(self):
        if self.crime_data is not None:
            stats = {
                'total_crimes': len(self.crime_data),
                'crime_types': self.get_crime_types(),
                'most_common_type': self.crime_data['Crime Type'].mode()[0] if not self.crime_data['Crime Type'].mode().empty else None,
                'crime_counts': self.crime_data['Crime Type'].value_counts().to_dict()
            }
            return stats
        else:
            return "[CrimeAnalyzer] âš ï¸ No crime data to analyze." 
    def get_crime_trends(self, time_column='Date'):
        if self.crime_data is not None and time_column in self.crime_data.columns:
            self.crime_data[time_column] = pd.to_datetime(self.crime_data[time_column], errors='coerce')
            trends = self.crime_data.groupby(self.crime_data[time_column].dt.to_period('M')).size()
            return trends
        else:
            return "[CrimeAnalyzer] âš ï¸ No crime data or invalid time column."
    def get_crime_heatmap(self, lat_column='Latitude', lon_column='Longitude'):
        if self.crime_data is not None and lat_column in self.crime_data.columns and lon_column in self.crime_data.columns:
            heatmap_data = self.crime_data[[lat_column, lon_column]].dropna()
            return heatmap_data
        else:
            return "[CrimeAnalyzer] âš ï¸ No crime data or invalid latitude/longitude columns."
    def save_crime_data(self, output_path):
        if self.crime_data is not None:
            try:
                self.crime_data.to_csv(output_path, index=False)
                print(f"[CrimeAnalyzer] âœ… Crime data saved to {output_path}")
            except Exception as e:
                print(f"[CrimeAnalyzer] âŒ Error saving crime data: {e}")
        else:
            print("[CrimeAnalyzer] âš ï¸ No crime data to save.")
    def __str__(self):
        return f"CrimeAnalyzer(crime_data_path={self.crime_data_path})"
# Ensure the CrimeAnalyzer class runs correctly
# This class provides methods to analyze crime data, including loading data, summarizing it, filtering by location, and more. 
