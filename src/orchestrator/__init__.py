import os
import csv
import sys
import logging
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))

current_dir = os.path.dirname(os.path.abspath(__file__))
print(f'current directory: {current_dir}')

# Import all of the programs modules within the parent_dir
import scraper
import parser
import cleaner
import updater

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)

class Orchestrator:
    def __init__(self):
        #Sets our base parameters
        self.counties = []
        self.start_date = '2024-07-01'       #Update start date here
        self.end_date = '2024-07-01'         #Update start date here

    def file_reset(self, county):
        # Define the root folder and subfolders
        root_folder = os.path.join(os.path.dirname(__file__), "..", "..", "data", county)
        subfolders = ['case_html', 'case_json', 'case_json_cleaned']

        # Loop through each subfolder and remove all files
        for subfolder in subfolders:
            folder_path = os.path.join(root_folder, subfolder)
            
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                # Loop through all the files in the subfolder
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    
                    # Check if it's a file and remove it
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    # If it's a directory, remove the directory and all its contents
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        print(f'Removed directory and its contents: {file_path}')
            else:
                print(f"Folder not found: {folder_path}")
        print("Finished removing files.")

    def orchestrate(self):

        #This open the county data CSV to see which counties should be scraped, parsed, cleaned, and updated.
        with open(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "resources", "texas_county_data.csv"
            ),
            mode="r",
        ) as file_handle:
            csv_file = csv.DictReader(file_handle)
            for row in csv_file:
                #This only selects the counties from the csv that should be parsed.
                if row["scrape"].lower() == "yes":
                    self.counties.append(row["county"])

        #This runs the different modules in order
        #src/scraper
        for c in self.counties:
            print(f"Starting to scrape, parse, clean, and update this county: {c}")
            """scraper.Scraper().scrape(county = c,
                                    start_date = self.start_date,
                                    end_date = self.end_date,
                                    court_calendar_link_text = None,
                                    case_number = None,
                                    case_html_path = None,
                                    judicial_officers = None,
                                    ms_wait = None)"""
            #src/parser
            parser.Parser().parse(county = c,
                            case_number = None,
                            parse_single_file = False,
                            test=False)
            #src/cleaner
            cleaner.Cleaner().clean(county = c)
            #src/updater
            updater.Updater(c).update()
            self.file_reset(c)
            print(f"Completed with scraping, parsing, cleaning, and updating of this county: {c}")

if __name__ == '__main__':
    Orchestrator().orchestrate()
