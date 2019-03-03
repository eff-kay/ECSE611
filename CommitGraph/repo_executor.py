import subprocess
import os

HIVE_GIT_COMMAND = "git clone https://git-wip-us.apache.org/repos/asf/hive.git"
HBASE_GIT_COMMAND = "git clone https://gitbox.apache.org/repos/asf/hbase.git"

class RepoExecutor:
    CLONE_REPO = {
        'hbase': HBASE_GIT_COMMAND,
        'hive': HIVE_GIT_COMMAND,
    }

    SAVE_CURRENT_WORKING_DIRECTORY = 'CURR_DIR=$PWD'
    GO_BACK_TO_WORKING_DIRECTORY = 'cd $CURR_DIR'

    def __init__(self, repo_name):
        self.repo_name = repo_name

        if repo_name not in ['hbase', 'hive']:
            raise NotImplementedError(f'{self.repo_name} must be either "hive" or "hbase"')

        if not os.path.isdir(f'./Repo/{self.repo_name}'):
            subprocess.run(";".join([
                self.SAVE_CURRENT_WORKING_DIRECTORY,
                f'cd Repo/',
                self.CLONE_REPO[self.repo_name],
                self.GO_BACK_TO_WORKING_DIRECTORY,
            ]), shell=True)

        # print(f'{self.repo_name} exists in ./Repo/{self.repo_name}...')

    def execute(self, command):
        return subprocess.check_output(";".join([
            self.SAVE_CURRENT_WORKING_DIRECTORY,
            f'cd Repo/{self.repo_name}',
            command,
            self.GO_BACK_TO_WORKING_DIRECTORY,
        ]), shell=True).decode('utf-8')

    def execute_commands(self, commands):
        return subprocess.run(";".join([
            self.SAVE_CURRENT_WORKING_DIRECTORY,
            f'cd Repo/{self.repo_name}',
            *commands,
            self.GO_BACK_TO_WORKING_DIRECTORY,
        ]), shell=True, capture_output=True, check=True)
