# Industrial API Editor
A Node editor prototype Python App developed with [DearPyGui](https://github.com/hoffstadt/DearPyGui/tree/master).

## Install and run
1. Python version 3.12
2. Create a virtual environment with venv or conda.
3. Activate the environment
4. Install dependencies

    `pip install -r ./requirements.txt`

5. then start the application

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

- Right Click to add a State Node

- Right Click on node label to Open Actions Dialog

- Ctrl+Click to remove a link

- Double Click on Transition Nodes to open the Attributes window

- Pressing the export button it's possible to save the current diagram into JSON file

- Pressing the import button it's possible to open back a diagram previously saved with the export functionality

- The Generate API Stub functionality uses the [Open API Generator](http://api.openapi-generator.tech/api/gen/servers) to generate an stub implementation of of the **Industrial 4.0 API** adding the information inferred from the current diagram

## Case Study 

The case study conducted on the Fischertechnik training factory 4.0 24V you can find, in the training_factory_case_study folder, all the files related. A controller Python file for each component of the factory and an node red API wrapper file that perform the requests to the IoT Gateway of the factory.

## User Study
To evaluate the usefulness and practicality in terms of use of the Industrial API Editor case tool, a user study in two phases was conducted.
Carried out by involving N possible users of the tool in question, they were asked
to solve, using our software prototype, a modeling exercise on some manufacturing asset and generate the related Industrial 4.0 APIs.
They were then asked to answer a questionnaire to receive feedback regarding
their level of satisfaction and ease of use experienced during the previous phase.
In the user_study folder, you can find both the modeling exercise document and the results of thr questionnaire.