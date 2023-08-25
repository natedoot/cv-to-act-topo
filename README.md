# CloudVision Topology Extractor

This project helps you to extract the topology from CloudVision and generate a YAML file for your virtual lab environment.

## Requirements

- [VS Code](https://code.visualstudio.com/)
- [Docker](https://www.docker.com/)
- [Remote Development extension pack for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)

## Usage

1. **Clone the Repository**:
```
   git clone https://github.com/natedoot/cv-to-act-topo.git
   cd cv-to-act-topo
```
1) Open the Project in VS Code:
Open the project folder in VS Code.

2) Reopen in Container:
Click on the "Reopen in Container" button in the lower left corner of the VS Code window.

3) Execute the Script Inside the Container:
Run the script with your CloudVision server details and any other required arguments. Here's an example:
```
python /app/main_script.py --apiserver apiserver.cv-staging.corp.arista.io:443 --auth=token,token.tok --pattern dc1-
```
Adjust the arguments according to your setup.
