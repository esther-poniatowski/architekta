
## Installation

> [!IMPORTANT]
> **Prerequisites**  
> Ensure that the following tools are available on the local machine:
> - git
> - conda
> - Visual Studio Code (recommended)

To set up this project on a local machine, follow the steps below:

### Initialize a local copy of the repository

1. Navigate to the local directory where the root folder of the repository should reside.
  
2. Clone the repository:
```bash
git clone git@github.com:esther-poniatowski/multitask-context-dependent-behavior.git
```

> [!NOTE]
> The repository files are installed into a new directory named `multitask-context-dependent-behavior`.


### Create a virtual environment

1. Create an dedicated conda environment including all the dependencies for using the project:
```
conda env create -f environment.yml
```

> [!NOTE]
> The new conda environment is named `mtcdb`. 

2. Register the current packages in the environment:

a. Check and copy the path to the site-packages directory of the environment:
```bash
conda activate mtcdb
python -c "import site; print(site.getsitepackages()[0])"
```
Usually: `∼/miniconda3/envs/mtcdb/lib/pythonX.Y/site-packages`

b. Register the source directory of the project in a `mtcdb.pth` file:
```bash
echo "/path/to/mtcdb/src" > "path/to/conda/site-packages/mtcbd.pth"
```
Replace `"/path/to/mtcdb"` and `"path/to/conda/site-packages"` by the actual paths.

## Usage

...


## Contributing

> [!IMPORTANT]
> To contribute effectively, please conform to those guidelines and use the provided templates.  
> To suggest improvements, use **issues**.
> To actively implement improvements, **commit** in the local version and **push** changes to the remote branches. 

### Submitting Issues

To submit an issue on the GitHub page of the repository:

1. Navigate to the "Issues" tab and click on "New Issue".
2. Select and fill the issue template.
3. Add relevant labels, assignees, and milestone if applicable.

### Committing changes

#### Configure the repository

1. Navigate to the root directory of the local repository.
  
2. Specify the user profile (recorded in commits' metadata):
```bash
git config user.name "Example Name"
git config user.email "exampleemail@domain.com"
```
Replace `"Example Name"` and `"exampleemail@domain.com"` by the actual name and email corresponding to the GitHub user.

3. Configure the commit template (`.gitmessage` file):
```
git config commit.template .gitmessage
```

> [!TIP]
> **Format of the Commit Message**
> - Limit the subject line to 50 characters and the body at 72 characters per line, indicated by the delimiters in the template (`####`).
> - Separate the subject from the body with a blank line.
> 
> **Contents**
> - Subject: Indicate a prefix (see the options in the comments of the template), a scope (in parentheses) and a title after a colon (`:` character).
> - Title: Use the imperative mood and capitablize.
> - Body: Explain what and why (not how).
> - References: Mention issues or other commits using [GitHub keywords](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/using-keywords-in-issues-and-pull-requests)

#### Set up credentials

1. Ask the author to share the Personal Access Token of the repository.

2. Create a plaintext file located at `.git/credentials`:

3. Add authentication data in this file under the form of a URL address:
```plaintext
https://<username>:<personal-access-token>@github.com
```
Replace `<username>` and `<personal-access-token>` by the actual user name indicated before for the Git repository and the personal access token provided by the author.

4. Configure the credential helper to use the credentials file:
```bash
git config credential.helper 'store --file=.git/credentials'
```
