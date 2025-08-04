# Documentation/documentation.py

import os
import re

class DocumentationGenerator:
    def __init__(self, root_dir):
        """Initialize with the root directory of the project."""
        self.root_dir = root_dir
        self.docs = []

    def extract_docstrings(self, file_path):
        """Extracts docstrings from a Python file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Regular expression to find docstrings
        docstring_pattern = re.compile(r'(\"\"\"(.*?)\"\"\"|\'\'\'(.*?)\'\'\')', re.DOTALL)
        return docstring_pattern.findall(content)

    def generate_docs(self):
        """Generate documentation for all Python files in the specified directory."""
        for dirpath, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                if filename.endswith('.py'):
                    file_path = os.path.join(dirpath, filename)
                    docstrings = self.extract_docstrings(file_path)

                    if docstrings:
                        self.docs.append({
                            'file': file_path,
                            'docstrings': [d[0] for d in docstrings]  # Extracted docstrings
                        })

    def save_docs(self, output_file='documentation.md'):
        """Save the extracted documentation to a Markdown file."""
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('# Project Documentation\n\n')
            for entry in self.docs:
                file.write(f"## {entry['file']}\n")
                for docstring in entry['docstrings']:
                    file.write(f"\n```\n{docstring}\n```\n")
                file.write("\n---\n")

    def run(self):
        """Run the documentation generator."""
        self.generate_docs()
        self.save_docs()
        print("Documentation generated successfully!")

if __name__ == "__main__":
    # Change 'C:/Users/josh_/Desktop/jaicat_project' to your project's root directory
    doc_generator = DocumentationGenerator(root_dir='C:/Users/josh_/Desktop/jaicat_project')
    doc_generator.run()
