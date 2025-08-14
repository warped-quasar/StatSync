import os

# Folder structure for StatSync
folders = [
    "src",                # main Python source files
    "docs/technical",     # technical documentation
    "docs/high_level",    # high-level user documentation
    "config",             # configuration files
    "tests",              # unit/integration tests
    "data/raw",           # raw ingested data
    "data/processed",     # processed/cleaned data
    "logs"                # runtime logs
]

# Files to create
files = [
    "src/nba_sync.py",                # main ingestion script
    "src/__init__.py",                 # to make src a package
    "config/config.yaml",              # config placeholder
    "docs/technical/README.md",        # technical doc placeholder
    "docs/high_level/README.md",       # high-level doc placeholder
    "tests/test_nba_sync.py",          # test placeholder
    "requirements.txt",                # dependencies list
    ".gitignore",                      # git ignore rules
    "README.md"                        # project overview
]

def create_project_structure():
    # Create folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

    # Create files with placeholders
    for file in files:
        if not os.path.exists(file):
            with open(file, "w") as f:
                if file.endswith(".py"):
                    f.write("# Placeholder Python file\n")
                elif file.endswith(".md"):
                    f.write(f"# {file.split('/')[-1].replace('.md', '')}\n")
                elif file.endswith(".yaml"):
                    f.write("# Configuration placeholder\n")
                elif file == ".gitignore":
                    f.write("__pycache__/\n*.pyc\n.env\n")
                elif file == "requirements.txt":
                    f.write("# List your dependencies here\n")
            print(f"Created file: {file}")
        else:
            print(f"File already exists: {file}")

if __name__ == "__main__":
    create_project_structure()
