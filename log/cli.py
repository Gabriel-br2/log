import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Utility to filter formatted logs.")
    
    parser.add_argument("file", help="Path to the log file (e.g., my_log.log)")
    
    parser.add_argument("-l", "--level",     help="Filter by log level (e.g., DEBUG, ERROR, CRITICAL)")
    parser.add_argument("-d", "--date",      help="Filter by date/time (e.g., '2026-04-06')")
    parser.add_argument("-t", "--traceback", action="store_true", help="Extract only error/traceback blocks")

    args = parser.parse_args()

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            printing_traceback = False
          
            for line in f:
                if args.traceback:
                    if "Traceback (most recent call last):" in line:
                        printing_traceback = True
                    
                    if printing_traceback:
                        print(line, end="")
                        if not line.startswith(" ") and not line.startswith("╭") and ":" in line and "Traceback" not in line:
                            printing_traceback = False
                    continue

                if args.level and f"{args.level}" not in line:
                    continue
                
                if args.date and not line.startswith(args.date):
                    continue

                print(line, end="")

    except FileNotFoundError:
        print(f"Error: The file '{args.file}' was not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()