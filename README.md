# OnionIntel

**OnionIntel** is a tool designed for exploring and analyzing hidden services on the Tor network. It automates the process of gathering information about `.onion` sites, using tools like Nmap and HTTPX. The goal is to provide actionable insights for cybersecurity research, monitoring dark web services and creating an offline Database.

## Onion Search Tool (`onion_search.py`)

**Onion Search** is a command-line tool that enables users to search through a local CSV database of `.onion` sites and analyze both titles and responses stored from web crawls. The tool uses regular expressions to search for keywords or patterns in the site titles or content, and it can display screenshots (if available) associated with the results. This makes it an essential tool for cybersecurity researchers who want to monitor or analyze specific keywords on the dark web.

### Features:
- Search `.onion` site titles using regex.
- Search stored response content for specific patterns.
- Option to display screenshots of `.onion` sites (if available).
- Flexible filtering for results with valid screenshots.

### Usage:
```bash
python onion_search.py -f /path/to/csv_file.csv -t "Hack"        # Search for 'Hack' in titles
python onion_search.py -f /path/to/csv_file.csv -s "security"     # Search for 'security' in stored responses
python onion_search.py -f /path/to/csv_file.csv -r "Bitcoin"      # Search for 'Bitcoin' in both titles and responses
```

## Features
- Scrapes `.onion` sites from sources like Ahmia.
- Uses HTTPX to get informations from the sites. 
- Uses Nmap to scan `.onion` domains for open ports and services.
- Merges scan results with additional data for comprehensive analysis.
- Runs in a Jupyter notebook environment, leveraging both Python and shell commands.

## Current Version
This version runs through a Jupyter notebook, combining Python and shell commands to perform its operations. Future versions will offer a more streamlined experience and additional features.

## Upcoming Improvements
We are actively working to improve OnionIntel with the following features:
1. **Fully Python-based**: Transitioning the entire tool to Python for better portability and flexibility.
2. **Database Integration**: Introducing a database (possibly MySQL) for storing scan results and enabling more advanced querying and historical tracking.
3. **User-friendly Frontend**: A modern and intuitive web interface to interact with the tool and visualize results.

## How to Use
1. Ensure you have **Tor**, **Nmap**, **PDTM** and **HTTPX** installed on your system.
2. Clone the repository and open the Jupyter notebook in your environment.
3. Follow the instructions in the notebook to run scans and analyze `.onion` services.

## Prerequisites
- Python 3.x
- Jupyter Notebook
- Tor (running and configured)
- Nmap
- PDTM and HTTPX
- Python libraries: `requests`, `beautifulsoup4`, `pandas`, `xml.etree.ElementTree`

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/OnionIntel.git
cd OnionIntel
```
## Stay Tunned

We have more exciting features planned. Stay tuned for future updates and improvements!



