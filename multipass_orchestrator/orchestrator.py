import yaml
import tempfile
import os
import multiprocessing
from sys import platform
from multipass import MultipassClient


def execute(vm_name, script):
    client = MultipassClient()
    client.transfer(script, "%s:/home/ubuntu" % vm_name)
    vm = client.get_vm(vm_name)
    if platform == 'win32':
        script_filename = script.split('\\')[-1]
    else:
        script_filename = script.split('/')[-1]
    vm.exec("chmod +x %s" % script_filename)
    vm.exec("./%s" % script_filename)


class MultipassOrchestrator:
    def __init__(self, config_file):
        self.procs = []
        self.client = MultipassClient()
        with open(config_file, 'r') as fh:
            self.config = yaml.load(fh, yaml.CSafeLoader)

    def delete_environment(self):
        vm_list = self.client.list()
        del_list = self.config.keys()
        for i in range(len(vm_list['list'])):
            if vm_list['list'][i]['name'] in del_list:
                vm = self.client.get_vm(vm_list['list'][i]['name'])
                vm.delete()
        self.client.purge()

    def span_environment(self):
        for vm_name in self.config.keys():
            if 'cloud_init' in self.config[vm_name]:
                self.client.launch(vm_name=vm_name,
                                   cpu=self.config[vm_name]['cpu'],
                                   disk=self.config[vm_name]['disk'],
                                   mem=self.config[vm_name]['mem'],
                                   image=self.config[vm_name]['image'],
                                   cloud_init=self.config[vm_name]['cloud_init'])
            else:
                self.client.launch(vm_name=vm_name,
                                   cpu=self.config[vm_name]['cpu'],
                                   disk=self.config[vm_name]['disk'],
                                   mem=self.config[vm_name]['mem'],
                                   image=self.config[vm_name]['image'])

    def build_environment(self):
        if platform == "linux" or platform == "linux2":
            # Multipass installed with Snap can not access /tmp
            tmp_dir = os.path.join(os.path.expanduser("~"), 'mpo-tmp')
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            tempfile.tempdir = tmp_dir
        tmp_dir = tempfile.gettempdir()
        build = {}
        for vm_name in self.config:
            build[vm_name] = {}
            if 'git_repos' in self.config[vm_name]:
                build[vm_name]['git_repos'] = self.config[vm_name]['git_repos']
            if 'build_scripts' in self.config[vm_name]:
                build[vm_name]['build_scripts'] = self.config[vm_name]['build_scripts']
        for vm_name in build:
            if len(build[vm_name]) == 0:
                continue
            build_script = os.path.join(tmp_dir, "%s_build.sh" % vm_name)
            with open(build_script, 'w', newline="\n") as fh:
                fh.write("#!/bin/bash\n\n")
                if 'git_repos' in build[vm_name]:
                    for i in range(len(build[vm_name]['git_repos'])):
                        fh.write("git clone %s\n\n" % build[vm_name]['git_repos'][i])
                if 'build_scripts' in build[vm_name]:
                    for i in range(len(build[vm_name]['build_scripts'])):
                        fh.write("%s 2>> .build_err.log >> .build_out.log\n" % build[vm_name]['build_scripts'][i])
                proc = multiprocessing.Process(target=execute, args=(vm_name, build_script,))
                self.procs.append(proc)
                proc.start()

        for proc in self.procs:
            proc.join()

    def run_environment(self):
        if platform == "linux" or platform == "linux2":
            # Multipass installed with Snap can not access /tmp
            tmp_dir = os.path.join(os.path.expanduser("~"), 'mpo-tmp')
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            tempfile.tempdir = tmp_dir
        tmp_dir = tempfile.gettempdir()
        run = {}
        for vm_name in self.config:
            run[vm_name] = {}
            if 'run_scripts' in self.config[vm_name]:
                run[vm_name]['run_scripts'] = self.config[vm_name]['run_scripts']
        for vm_name in run:
            if len(run[vm_name]) == 0:
                continue
            run_script = os.path.join(tmp_dir, "%s_run.sh" % vm_name)
            with open(run_script, 'w', newline="\n") as fh:
                fh.write("#!/bin/bash\n\n")
                if 'run_scripts' in run[vm_name]:
                    for i in range(len(run[vm_name]['run_scripts'])):
                        fh.write("%s 2>> .run_err.log >> .run_out.log\n" % run[vm_name]['run_scripts'][i])
                proc = multiprocessing.Process(target=execute, args=(vm_name, run_script,))
                self.procs.append(proc)
                proc.start()

        for proc in self.procs:
            proc.join()
