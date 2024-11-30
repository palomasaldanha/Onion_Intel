import re
import os
import pandas as pd
import argparse
from PIL import Image
import matplotlib.pyplot as plt
import webbrowser
import subprocess
import tempfile

# Display the Logo in Rammstein Style 
def display_logo():
    logo = r"""
    ########################################################################################################
        _____                                          _____                                                
    __|__   |__  ____   _  ____  _____  ____   _   __|_    |__  ____   _    __    ______  ____    ____     
    /     \     ||    \ | ||    |/     \|    \ | | |    |      ||    \ | | _|  |_ |   ___||    |  |    |    
    |     |     ||     \| ||    ||     ||     \| | |    |      ||     \| ||_    _||   ___||    |_ |    |_   
    \_____/   __||__/\____||____|\_____/|__/\____| |____|    __||__/\____|  |__|  |______||______||______|  
        |_____|                                        |_____|                                               
        _____                                                                                               
    __|___  |__  ______  ____    _____   ______  __   _                                                    
    |   ___|    ||   ___||    \  |     | |   ___||  |_| |                                                   
    `-.`-.     ||   ___||     \ |     \ |   |__ |   _  |                                                   
    |______|  __||______||__|\__\|__|\__\|______||__| |_|                                                   
        |_____|                                                                                              
                                                                                    by: Paloma_Saldanha       
                                                                                    
    ########################################################################################################                                                                                                                
    """
    print(logo)

# Function to extract matches and return relevant information
def extract_matches(df, matches):
    results = []
    for index in matches:
        row = df.loc[index]
        domain = row.get('Onion_Site', 'N/A')  
        url = row.get('url', 'N/A')  
        title = row.get('title', 'N/A')
        has_screenshot = 'Yes' if pd.notnull(row['screenshot_path_rel']) and os.path.exists(row['screenshot_path_rel']) else 'No'
        results.append({
            'DOMAIN': domain,
            'URL': url,
            'TITLE': title,
            'HAS_Screenshot': has_screenshot
        })
    return results

# Function to search for a specific term or pattern in the title using regex
def search_title(df, pattern, save_csv=None):
    regex = re.compile(pattern, re.IGNORECASE)  # Case-insensitive search
    matches = []

    print("\nMatches found:")
    for index, row in df.iterrows():
        if pd.notnull(row['title']) and regex.search(row['title']):
            matches.append(index)
            print(f"Index: {index}, Title: {row['title']}")

    if matches:
        print(f"\n########################################################################################################\nTotal Matches Found: {len(matches)}")
        ask_for_image(df, matches)  # Prompt to display image if available
        ask_for_http(df, matches)   # Prompt to display HTTP conversation if available

        if save_csv:
            results = extract_matches(df, matches)
            save_to_csv(results, save_csv)
    else:
        print("No matches found.")

# Function to search for a pattern in the stored response files using regex (using the relative path for responses)
def search_response(df, pattern, save_csv=None):
    regex = re.compile(pattern, re.IGNORECASE)  # Case-insensitive search
    matches = []

    # Define the base path for the responses
    base_response_path = './output/response/'

    print("\nMatches found:")
    for index, row in df.iterrows():
        response_file = row['stored_response_path_rel']  # Updated to use the correct column
        if pd.notnull(response_file) and os.path.exists(base_response_path + response_file):
            try:
                with open(base_response_path + response_file, 'r', encoding='ISO-8859-1') as file:
                    content = file.read()
                    if regex.search(content):
                        matches.append(index)
                        print(f"Index: {index}, Title: {row['title']}")
            except Exception as e:
                print(f"Error reading {response_file}: {e}")
        else:
            print(f"Response file {response_file} not found.")

    if matches:
        print(f"\n########################################################################################################\nTotal Matches Found: {len(matches)}")
        ask_for_image(df, matches)  # Prompt to display image if available
        ask_for_http(df, matches)   # Prompt to display HTTP conversation if available

        if save_csv:
            results = extract_matches(df, matches)
            save_to_csv(results, save_csv)
    else:
        print("No matches found.")

# Function to filter out HTTP headers and extract HTML content
def extract_html_content(http_content):
    # Split the content by new lines to separate headers and body
    lines = http_content.splitlines()

    # Initialize variables to hold the HTML content
    html_content = []
    in_html_section = False

    # Loop through each line
    for line in lines:
        # Identify the start of the HTML content (when headers end)
        if not in_html_section and line.strip() == '':
            in_html_section = True
            continue
        
        # Append the content after headers end (the HTML part)
        if in_html_section:
            # Ignore chunked encoding sizes (if present)
            if line.strip().isdigit():
                continue
            html_content.append(line)

    # Join the filtered lines to form the HTML content
    html_content_str = "\n".join(html_content)

    # Ensure proper HTML structure if it's missing
    if "<html" not in html_content_str.lower():
        html_content_str = f"<html><body>{html_content_str}</body></html>"

    return html_content_str

# Function to ask the user for the index and render the HTTP conversation (HTML only) in a web browser using subprocess
def ask_for_http(df, matches):
    # Define the base path for the responses
    base_response_path = './output/response/'

    # Check if any of the results have a valid HTTP conversation
    matches_with_http = [index for index in matches if pd.notnull(df.loc[index, 'stored_response_path_rel']) and os.path.exists(base_response_path + df.loc[index, 'stored_response_path_rel'])]

    if matches_with_http:
        # Ask the user if they want to view an HTTP conversation
        while True:
            view_http = input("\n########################################################################################################\nSome results have HTTP conversations. Would you like to view one? (yes/no): ").strip().lower()
            if view_http in ['yes', 'no']:
                break
            else:
                print("Please enter 'yes' or 'no'.")

        if view_http == 'yes':
            while True:
                try:
                    user_input = input("\n########################################################################################################\nEnter the index of the match you'd like to see the HTTP conversation for (or type 'exit' to quit): ").strip()
                    if user_input.lower() == 'exit':
                        break
                    elif int(user_input) in matches_with_http:
                        index = int(user_input)
                        response_path_rel = df.loc[index, 'stored_response_path_rel']
                        full_response_path = base_response_path + response_path_rel

                        if pd.notnull(response_path_rel) and os.path.exists(full_response_path):
                            try:
                                # Read the HTTP conversation content
                                with open(full_response_path, 'r', encoding='ISO-8859-1') as file:
                                    http_content = file.read()

                                # Extract only the HTML part, ignoring headers
                                html_content = extract_html_content(http_content)

                                # Create a temporary HTML file to store the content
                                with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as temp_file:
                                    temp_file.write(html_content)
                                    temp_html_path = os.path.abspath(temp_file.name)  # Convert to absolute path

                                # Print debug info
                                print(f"Opening HTML content: {temp_html_path}")

                                # Use subprocess to run the Firefox command
                                try:
                                    print(f"\nOpening the HTML content in Firefox using subprocess...")
                                    subprocess.run(['/Applications/Firefox.app/Contents/MacOS/firefox', temp_html_path])  # Run Firefox with the file
                                except Exception as e:
                                    print(f"\nError: Could not open Firefox. Trying default browser...")
                                    webbrowser.open_new_tab(temp_html_path)  # Fallback to the default browser

                            except Exception as e:
                                print(f"Error displaying HTML content: {e}")
                        else:
                            print("HTTP content not found or invalid. Please choose another index.")
                    else:
                        print("Invalid index. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a valid index or type 'exit'.")

# Function to display available ports and search for a specific port in the Port_Nmap column
def search_port(df):
    df['Port_Nmap'] = df['Port_Nmap'].astype(str)  # Ensure string comparison
    port_counts = df['Port_Nmap'].value_counts()

    # Display the available ports and their counts
    print("\nAvailable Ports:")
    for port, count in port_counts.items():
        print(f"Port: {port}, Count: {count}")

    # Ask the user to choose a port
    while True:
        chosen_port = input("\n########################################################################################################\nPlease enter a port from the list above: ").strip()
        if chosen_port in port_counts.index:
            break
        else:
            print("Invalid port. Please choose a valid port from the list.")

    # Search and display results for the chosen port
    matches = df[df['Port_Nmap'] == chosen_port]
    if not matches.empty:
        print(f"\nFound {len(matches)} results for port {chosen_port}:")
        for index, row in matches.iterrows():
            print(f"Index: {index}, Title: {row['title']}, Port: {row['Port_Nmap']}")

        ask_for_image(df, matches.index)  # Prompt to display image if available
        ask_for_http(df, matches.index)   # Prompt to display HTTP conversation if available
    else:
        print(f"No results found for port {chosen_port}.")


# Function to ask the user for the index and display the screenshot using the relative path
def ask_for_image(df, matches):
    # Define the base path for the screenshots
    base_screenshot_path = './output/screenshot/'

    # Ask the user if they want to filter to show only indexes with screenshots
    show_only_with_screenshot = input("\n########################################################################################################\nDo you want to see only matches with screenshots? (yes/no): ").strip().lower()

    if show_only_with_screenshot == 'yes':
        # Filter matches to only those with a valid screenshot path (using the relative path)
        matches_with_screenshot = [index for index in matches if pd.notnull(df.loc[index, 'screenshot_path_rel']) and os.path.exists(base_screenshot_path + df.loc[index, 'screenshot_path_rel'])]

        if matches_with_screenshot:
            print(f"\n########################################################################################################\nShowing {len(matches_with_screenshot)} results with valid screenshots:\n")
            for index in matches_with_screenshot:
                print(f"Index: {index}, Title: {df.loc[index, 'title']}")
            matches = matches_with_screenshot  # Update the matches to only those with screenshots
        else:
            print("No matches with valid screenshots found.")
            return

    while True:
        try:
            user_input = input("\n########################################################################################################\nEnter the index of the match you'd like to see the screenshot for (or type 'exit' to quit): ").strip()
            if user_input.lower() == 'exit':
                break
            elif int(user_input) in matches:
                index = int(user_input)
                screenshot_path_rel = df.loc[index, 'screenshot_path_rel']
                full_screenshot_path = base_screenshot_path + screenshot_path_rel

                if pd.notnull(screenshot_path_rel) and isinstance(screenshot_path_rel, str) and os.path.exists(full_screenshot_path):
                    try:
                        img = Image.open(full_screenshot_path)
                        plt.imshow(img)
                        plt.axis('off')  # Hide axes
                        plt.show()
                    except Exception as e:
                        print(f"Error displaying screenshot: {e}")
                else:
                    print("Screenshot not found or invalid. Please choose another index.")
            else:
                print("Invalid index. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid index or type 'exit'.")


# Function to save results to a CSV file
def save_to_csv(results, file_path):
    df_results = pd.DataFrame(results)
    df_results.to_csv(file_path, index=False)
    print(f"\n########################################################################################################\nResults saved to {file_path}")

# Function to search both in titles and text when -r is used
def unified_search(df, pattern, save_csv=None):
    regex = re.compile(pattern, re.IGNORECASE)  # Case-insensitive search
    matches = set()  # Use a set to avoid duplicate entries
    title_matches_count = 0
    text_matches_count = 0

    print(f"\n########################################################################################################\nSearching for pattern: {pattern}\n")

    # Search in titles
    for index, row in df.iterrows():
        if pd.notnull(row['title']) and regex.search(row['title']):
            matches.add(index)
            title_matches_count += 1
            print(f"Title Match - Index: {index}, Title: {row['title']}")

    # Search in stored responses (using the relative path column 'stored_response_path_rel')
    for index, row in df.iterrows():
        response_file = row['stored_response_path_rel']  # Updated to use the correct column
        if pd.notnull(response_file) and os.path.exists('./output/response/' + response_file):
            try:
                with open('./output/response/' + response_file, 'r', encoding='ISO-8859-1') as file:
                    content = file.read()
                    if regex.search(content):
                        matches.add(index)
                        text_matches_count += 1
                        print(f"Text Match - Index: {index}, Title: {row['title']}")
            except Exception as e:
                print(f"Error reading {response_file}: {e}")
        else:
            print(f"Response file {response_file} not found.")

    # If any matches were found
    if matches:
        total_matches_count = len(matches)
        print(f"\n########################################################################################################\nTotal Matches Found: {total_matches_count}")
        print(f"{title_matches_count} in Titles")
        print(f"{text_matches_count} in Text")

        matches_list = list(matches)
        ask_for_image(df, matches_list)  # Prompt to display image if available
        ask_for_http(df, matches_list)   # Prompt to display HTTP conversation if available

        if save_csv:
            results = extract_matches(df, matches_list)
            save_to_csv(results, save_csv)
    else:
        print("No matches found.")

# Main function to handle command-line arguments
def main():
    display_logo()

    parser = argparse.ArgumentParser(description="Search CSV files for patterns in titles or response files.")
    parser.add_argument('-f', '--csv_file_path', type=str, required=True, help='Path to the CSV file')
    parser.add_argument('-t', '--title_search', type=str, help='Regex pattern to search in titles')
    parser.add_argument('-s', '--text_search', type=str, help='Regex pattern to search in stored responses')
    parser.add_argument('-r', '--regex_input', type=str, help='Generic regex pattern for both title and response search')
    parser.add_argument('-p', '--port_search', action='store_true', help='List available ports and search for a specific port')
    parser.add_argument('--csv', type=str, help='Path to save results in CSV')

    args = parser.parse_args()

    # Load the CSV file
    df = pd.read_csv(args.csv_file_path)

    # Search in title if -t is provided
    if args.title_search:
        print(f"Searching in titles for pattern: {args.title_search}")
        search_title(df, args.title_search, save_csv=args.csv)

    # Search in stored responses if -s is provided
    if args.text_search:
        print(f"Searching in stored responses for pattern: {args.text_search}")
        search_response(df, args.text_search, save_csv=args.csv)

    # If -r is provided, search both in title and responses in a unified way
    if args.regex_input:
        unified_search(df, args.regex_input, save_csv=args.csv)

    # If -p is provided, list available ports and allow the user to search for a specific port
    if args.port_search:
        search_port(df)

if __name__ == '__main__':
    main()
