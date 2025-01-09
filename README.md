# Node-Editor-ImPyGui
A Node editor Python App developed with [DearPyGui](https://github.com/hoffstadt/DearPyGui/tree/master).

## Install and run
1. Create a virtual environment with venv or conda.
2. Activate the environment
3. Install dependencies

    `pip install -r ./requirements.txt`

4. then start the application

    `python ./node_editor.py`

## Run with Vagrant

1. You need Vagrant, virtualbox and the virtualbox guest addition installed on the host machine

2. From the project directory run

    `vagrant up`

3. From inside the guest machine, open a terminal

    `source editor-venv/bin/activate`
    
    `cd /vagrant`

    `python ./node_editor.py`

## Editor usage

- Right Click to Add a State Node

- Right Click on a State Node to Open Actions Dialog

- Ctrl+Click to remove a link

- Pressing the export button it's possible to save the current diagram into JSON file

- Pressing the import button it's possible to open back a diagram previously saved with the export functionality

- The Generate API Stub functionality uses the [Open API Generator](http://api.openapi-generator.tech/api/gen/servers) to generate an stub implementation of of the **Industrial 4.0 API** adding the information inferred from the current diagram

## Case Study 

The case study conducted on the Fischertechnik training factory 4.0 24V you can find, in the training factory case study folder, all the files related. A controller Python file for each component of the factory and an node red API wrapper file that perform the requests to the IoT Gateway of the factory.
