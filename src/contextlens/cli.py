import argparse
from .mcp.server import start_server

def main():
    parser = argparse.ArgumentParser(description="ContextLens CLI")
    parser.add_argument('command', choices=['mcp'], help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == 'mcp':
        start_server()

if __name__ == "__main__":
    main()
