# CYSOC
Description of the CYSOC project.

To be defined...

## Working with the notebooks
Tbd... testing the changes that will

1. From the command line, check out this repo from Git (e.g. with ```git clone https://github.com/hommedal/CYSOC.git```).
1. Enter the ```CYSOC``` folder and open it in vscode (e.g. with ```code .```) and look around.
1. Especially look at the ```create_venv_*.*``` file and either run the appropriate one or create a Python virtual environment manually.
1. Once the environment is ready, open one of the playbooks (```*.ipynb```, e.g. ```Playbooks/Test/system_information.ipynb```) in vscode.
1. Select the appropriate virtual environment as the kernel (e.g. ```.venv_windows/Script/python.exe```).
1. Run the code cells in the notebook to see that everythiong is working as expected.

## Safely commiting notebooks
The notebooks code and documentation cells should not hold any NN sensitive data. Output cells might, thought. So to strip any output from notebooks before comitting them to the repo (in particular for Github) you can install the python package ```nbstripout``` by running ```pip install nbstripout``` at the repository level of your project folder, e.g. ```C:\Dev\CYSOC\```, where you have your (hidden) ```.git``` folder.

After installing it (which configures some settings of your Git repo) that will run before commits are made, specifically:

``` INI
[filter "nbstripout"]
	clean = \"C:/Dev/CYSOC/.venv_win/Scripts/python.exe\" -m nbstripout
	smudge = cat
```

As you can see it runs the ```nbstripout``` tool which clears the output of all notebooks before Git commits the file to the repo. This one specifically uses the Python executable in the environment that has been set up for Windows for this project, and if you are using both Windows and Linux you need to install the tool in both. Because of that it has been included in the ```python_requirements.txt``` file that is used to set up the environment.

You can read more about ```nbstripout``` [Git and nbstripout](Docs/doc_nbstripout-explained.md).

## Creating a Python virtual environment

### Linux
To create a Python virtual environment for the CYSOC project on Linux, use the following command:

```bash
source create_venv_linux.sh
```

**NB:** It is important that you use the source or . shorthand command to run the script; otherwise, you will not have the environment activated after it has been created.

#### Manual installation
You can also create it manually by following these steps:

1. Decide on the folder location and Python versions to use.
    - Make sure you're standing in the CYSOC folder.
    - Check available Python versions, and decide which one to use for the environment.
    - It is recommended to use the latest available, e.g. ```Python 3.12```.
    - If you are using a Linux distro like ```Ubuntu 22.04```, ```Python 3.12``` may not be available.
    - There are ways around this, but we will not cover that here. Use the latest available, like e.g ```Python 3.11```.
1. Install any necessary Python versions you need.
    - You can do this by running ```apt install python3.12-minimal```.
    - It is recommended that you install the minimal version to reduce bloat.
    - This is particularly important when you install Python in multiple virtual environments.
    - This will mean that you will have to install more of the packages you will need using the ```pip``` command.
1. You also need to install the virtual environment package, e.g. by running ```apt install python3.12-venv```.
    - You will need to sudo to root before running the command (```sudo -i```) or by prefixing the command with ```sudo```.
    - Obviously, you may need to change the version number too, depending on which Python version you want to use.
    - If you only run ```apt install python-venv``` you will install it for the default Python interpreter version, which may not be the one you want.
1. Once the correct Python version and virtual environment package is installed, you can create the environment.
    - Do this by running ```python3-12 -m venv .venv_name --promt CYSOC```.
    - Exchange the Python version, the venv folder name (```.venv_name```), and the virtual environment command line prompt prefix (```CYSOC```) to anything you prefer.

### Windows
To be defined...

### Brief explanation
A Python virtual environment is something that you want to create to be able to install packages for your project without bloating and potentially creating version conflicts between Python and package versions on your main system or userland install of Python. Ideally you keep your main Python install minimal and used as little as possible, and you use virtual environments for anything you need set up for development projects and production code.

The minimal installation you need to be able to create Python virtual environments on your system is:

- Python, in all versions that you need for your different projects.
- Either the venv (```python3-venv```) or virtualenv (```python3-virtualenv```) package will work.

**Multiple Python versions**

Remember that if you are installing multiple Python versions, you must install the virtual environment package for each of those versions.

If you want to know what the default installation of Python is on your Linux system you can run ```readlink -f /usr/bin/python3```.

This works because on most systems the main Python3 executable is a link to the default version, and the ```readlink``` command show you which of the versioned executables the ```python3``` link points to. It will typically look something like this: ```/usr/bin/python3.12```.

But if you run ```ls -lah /usr/bin/python3*``` you may get several Python binaries listed, if more than one version is installed.

This is why, when you are to create a virtual environment, that you want to be explicit on the version and make sure you have the ```venv``` package for the version you want in your virtual environment installed (e.g. the package ```python3.10-venv```).

**Activating the virtual environment**

You activate a virtual environment you have created by running ```.venv/bin/activate``` on Linux and ```.venv/Scripts/activate``` on Windows, if the environment you created was placed in ```.venv```.

What happens when you run the activation script is that a lot of environment variables are updated to point to the Python binaries and libraries in the virtual environment, so that when you run the command ```python``` or ```pip``` (python package manager) you run the ones in the virtual environment folder.

Also, if you install packages using ```pip install <package name>``` the package will be installed in the virtual environment and not your base Python installation on your system.

**Deactivating the environment**

One of the aliases installed by the activation script is ```deactivate```. This is the command you use to deactivate the environment. When you run that, the environment variables are reset to what they were before you activated the environment.

**Inside or outside the environment?**

One thing you will notice is that inside the environment you could run Python by running the command ```python```, while outside the environment you sometimes have to use either ```python3``` or the explicit version, like ```python3.12```. This is because the basic Python 3 install need to survive next to a Python 2 install, and it uses the ```python``` binary name.

Some distributions and operating systems and Python installations will still register the ```python``` alias to point to the default Python 3 installation.

But inside the environment you have full control, so here the alias is always set to ```python```. If you want to see which version is running you can run the command ```python --version```.

The easiest way to see which environment you are in is to look at the prompt on the command line in the shell you activated the environment. It will have gotten a prefix to its prompt that is either the folder name of the virtual environment or the explicit prompt you gave using the --prompt command line argument.

**Best practice**

The best practice for creating virtual environments for Python are:

1. Always use the latest Python version if it will work for you.
1. Always install the ```python3.xx-minimal``` package unless you know you will need all the extra packages that comes with the full installation.
1. Always install the ```venv``` package for the version of python you have chosen, like ```python3.xx-venv```.
1. It is a good idea to always call the virtual environment folder ```.venv```. This way you always know that there is a virtual environment inside a project folder when you enter it.
1. But since this makes it hard to use the prompt prefix to see which environment you are in, it is also necessary to specify the prompt prefix explicitly using the ```--promt``` argument:

```Bash
$ python3 -m venv .venv --prompt "ProjectX"
```

This way, when you enter your project folder you immediately see the precense of an environment since it has a folder called ```.venv```, and when you activate it by running ```.venv/bin/activate``` you will get a prompt that tells you which project's environment you have activate since it will say ```(ProjectX) C:\Dev\CYSOC> ▯```.

When you run the ```deactivate``` alias all temporary aliases and environmental variables will be reset, including the prompt, that will return to "normal".

**References:**
- https://docs.python.org/3/library/venv.html
- https://stackoverflow.com/questions/41573587/what-is-the-difference-between-venv-pyvenv-pyenv-virtualenv-virtualenvwrappe
- https://medium.com/@sukul.teradata/understanding-python-virtual-environments-using-venv-and-virtualenv-283f37d24b13
