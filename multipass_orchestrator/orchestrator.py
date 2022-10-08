import yaml
import multiprocessing
from multipass import MultipassClient


def execute(vm_name, script):
    client = MultipassClient()
    client.transfer(script, "%s:/home/ubuntu" % vm_name)
    vm = client.get_vm(vm_name)
    vm.exec("chmod +x %s" % script.split('/')[-1])
    vm.exec("./%s" % script.split('/')[-1])


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
        build = {}
        for vm_name in self.config:
            build[vm_name] = {}
            if 'git_repo' in self.config[vm_name]:
                build[vm_name]['git_repo'] = self.config[vm_name]['git_repo']
            if 'git_branch' in self.config[vm_name]:
                build[vm_name]['git_branch'] = self.config[vm_name]['git_branch']
            if 'build_script' in self.config[vm_name]:
                build[vm_name]['build_script'] = self.config[vm_name]['build_script']
        for vm_name in build:
            if len(build[vm_name]) == 0:
                continue
            build_script = "/tmp/%s_build.sh" % vm_name
            with open(build_script, 'w') as fh:
                fh.write("#!/bin/bash\n\n")
                if 'git_repo' in build[vm_name]:
                    branch = ''
                    if 'git_branch' in build[vm_name]:
                        branch = "-b %s" % build[vm_name]['git_branch']
                    fh.write("git clone %s %s\n\n" % (branch, build[vm_name]['git_repo']))
                if 'build_script' in build[vm_name]:
                    fh.write("%s 2> .build_err.log > .build_out.log\n" % build[vm_name]['build_script'])
                proc = multiprocessing.Process(target=execute, args=(vm_name, build_script,))
                self.procs.append(proc)
                proc.start()

        for proc in self.procs:
            proc.join()

    def run_environment(self):
        run = {}
        for vm_name in self.config:
            run[vm_name] = {}
            if 'run_script' in self.config[vm_name]:
                run[vm_name]['run_script'] = self.config[vm_name]['run_script']
        for vm_name in run:
            if len(run[vm_name]) == 0:
                continue
            run_script = "/tmp/%s_run.sh" % vm_name
            with open(run_script, 'w') as fh:
                fh.write("#!/bin/bash\n\n")
                if 'run_script' in run[vm_name]:
                    fh.write("%s 2> .run_err.log > .run_out.log\n" % run[vm_name]['run_script'])
                proc = multiprocessing.Process(target=execute, args=(vm_name, run_script,))
                self.procs.append(proc)
                proc.start()

        for proc in self.procs:
            proc.join()
