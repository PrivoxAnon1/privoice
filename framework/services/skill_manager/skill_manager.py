import os, json, asyncio
import subprocess
from skills.pvx_base import PriVoice
from framework.services.skill_manager.skill import Skill
from bus.Message import Message
from threading import Event
from bus.MsgBusClient import MsgBusClient
import time
from framework.message_types import (
        MSG_UTTERANCE,
        MSG_SPEAK,
        MSG_REGISTER_INTENT,
        MSG_MEDIA,
        MSG_SYSTEM,
        MSG_RAW,
        MSG_SKILL
        )
MY_BASE_DIR = os.getcwd()
SYS_BASE_DIR = os.getenv('PVX_BASE_DIR')
cancel_words = ['stop', 'forget it', 'cancel', 'quit', 'never mind', 'terminate']

"""a skill repo is a repository which contains one or more skills
 skills are identified by the directory name with the first 
 9 characters being 'privoice_' so in the root of the repo, 
 any directories beginning with 'privoice_' are assumed to be
 privoice skills. if there is a skill.json file in this directory
 as well as an __init__.py file then the skill will be recognized"""

def get_skill_repos():
    fh = open(os.getcwd() + "/framework/services/skill_manager/" + "repositories.json")
    skill_repos = json.loads(fh.read())
    fh.close()
    return skill_repos

def get_pid(skill_identifier):
    p = subprocess.Popen(["ps", "auxww"], stdout=subprocess.PIPE) 
    out, err = p.communicate()
    out = out.decode('utf-8')
    lines = out.split("\n")
    skill_identifier = "privoice_" + skill_identifier
    for line in lines:
        if line.find(skill_identifier) > -1:
            line_as_array = line.split(" ")
            line = [i for i in line_as_array if i]
            return line[1]
    return 0

class SkillManager(PriVoice):
    def __init__(self, bus=None, timeout=5):
        self.skill_id = 'skill_manager'
        super().__init__(skill_id=self.skill_id, skill_category='system', sync=True)

        self.state = 'Idle'
        self.last_op = ''

        ## TODO convert to two method calls, get repos and register intents
        self.get_skills_from_repos()
        self.register_intents()


    def register_intents(self):
        ## register intents ##
        # register subject is skill
        for verb in ['list', 'show', 'display']:
            self.register_intent('C', verb, 'skills', self.handle_list_skills)

        # register subject is all skills
        for verb in ['list', 'show', 'display']:
            self.register_intent('C', verb, 'all skills', self.handle_list_skills)

        # register list installed skills
        for verb in ['list', 'show', 'display']:
            self.register_intent('C', verb, 'installed skills', self.handle_list_installed_skills)

        # register list available skills
        for verb in ['list', 'show', 'display']:
            self.register_intent('C', verb, 'available skills', self.handle_list_available_skills)

        # register list active skills
        for verb in ['list', 'show', 'display']:
            self.register_intent('C', verb, 'active skills', self.handle_list_active_skills)

        # register install skill
        for verb in ['add', 'install', 'download', 'create']:
            self.register_intent('C', verb, 'skill', self.handle_install_skill)

        # register delete skill
        for verb in ['delete', 'remove', 'terminate', 'uninstall', 'cancel', 'kill', 'unload']:
            self.register_intent('C', verb, 'skill', self.handle_delete_skill)

        # add custom intents based on available skills
        for skill_id in self.available_skills:
            skill = self.get_skill_for_id(skill_id)
            for verb in ['add', 'install', 'download', 'create']:
                self.register_intent('C', verb, skill.name, self.handle_install_skill)

        # add custom intents based on available skills
        for skill_id in self.available_skills:
            skill = self.get_skill_for_id(skill_id)
            for verb in ['delete', 'remove', 'terminate', 'cancel', 'kill', 'unload']:
                self.register_intent('C', verb, skill.name, self.handle_install_skill)

        # start/run/restart skill name
        for skill_id in self.available_skills:
            skill = self.get_skill_for_id(skill_id)
            for verb in ['start', 'restart', 'run', 'execute']:
                self.register_intent('C', verb, skill.name, self.handle_start_skill)

        # stop/etc 
        for verb in ['stop', 'cancel', 'terminate', 'shut down', 'halt', 'kill']:
            self.register_intent('C', verb, 'skill', self.handle_stop_skill)

        # start/run/restart skill name
        for skill_id in self.available_skills:
            skill = self.get_skill_for_id(skill_id)
            for verb in ['stop', 'cancel', 'terminate', 'shut down', 'halt', 'kill']:
                self.register_intent('C', verb, skill.name, self.handle_stop_skill)

        self.register_intent('C', 'help', 'skill', self.help)
        self.register_intent('C', 'help', 'skills', self.help)
        self.register_intent('C', 'help', 'skill manager', self.help)
        self.register_intent('C', 'skill', 'help', self.help)
        self.register_intent('C', 'skills', 'help', self.help)


    def get_skill_for_id(self, skill_id):
        for skill in self.all_skills:
            if skill.skill_id == skill_id:
                return skill

    def handle_timeout(self):
        print("Timed out?")
        self.speak("Nevermind!")
        """
        print("State=%s, timed out !" % (self.state,))
        self.state = 'idle'
        self.play_media(self.skill_base_dir + '/assets/fail.mp3')
        """

    def start_skill(self, skill_id):
        print("XXXXXXXXXXXXXXXXxxx do nothing start skill hit !!!!!!!!!!!!!!!!!")
        self.speak("Incomplete! start skill not working yet!")

    def uninstall_skill(self, skill_id):
        print("XXXXXXXXXXXXXXXXxxx do nothing remove skill hit !!!!!!!!!!!!!!!!!")
        self.speak("Incomplete! uninstall not working yet!")


    def stop_skill(self, skill_id):
        print("XXXXXXXXXXXXXXXXxxx stop skill hit !!!!!!!!!!!!!!!!!")
        pid = get_pid(skill_id)
        if pid and pid!= '' or pid != '0':
            cmd = "kill %s" % (pid,)
            os.system(cmd)

    def install_skill(self, skill_id):
        print("XXXXXXXXXXXXXXXXxxx install skill hit !!!!!!!!!!!!!!!!!")
        will_speak = "Installing the " + skill_id
        self.speak(will_speak)
        for skill in self.all_skills:
            if skill.name == skill_id:
                print("Found skill and would have installed it ")
                skill_dir_name = skill.base_dir.split("/")
                skill_dir_name = skill_dir_name[len(skill_dir_name)-1]
                dest_dir = SYS_BASE_DIR + "/skills/user_skills/" + skill_dir_name 
                cmd = "%s/scripts/install_skill.sh %s %s" % (SYS_BASE_DIR, skill.base_dir, dest_dir)
                print("Found skill!, src=%s, dest=%s, cmd=%s" % (skill.base_dir, dest_dir, cmd))
                os.system(cmd)
                will_speak = skill_id + " Installation complete."
                self.speak(will_speak)


    def handle_user_which_skill_response(self, user_input):
        print("user response to which skill is %s" % (user_input,))
        user_input = user_input.lower()
        if user_input in cancel_words:
            # user wants to bail
            print("User exit phrase detected %s" % (ujser_input,))
            return

        for skill in self.all_skills:
            if skill.name == user_input:
                print("Found skill %s last op is %s" % (user_input,self.last_op))

                if self.last_op == 'stop':
                    self.last_op = ''
                    self.stop_skill(skill.name)
                    self.speak("The %s skill has been stopped." % (skill.name,))

                if self.last_op == 'start':
                    self.last_op = ''
                    self.start_skill(skill.name)
                    self.speak("The %s skill has been started." % (skill.name,))

        # skill not found!
        print("Skill not found %s --- %s" % (user_input,self.last_op))
        self.speak("Sorry I can't find the %s skill." % (user_input,))

    def handle_stop_skill(self, msg):
        print(msg)
        print(msg['data'])
        sentence_info = msg['data']['utt']
        sentence_info = msg['data']['utt']
        subject = sentence_info['subject']
        if subject and subject != '' and subject != 'skill':
            subject = subject.replace(" skill","")
            self.stop_skill(subject)
            self.speak("The %s skill has been stopped" % (subject,))
        else:
            self.last_op = 'stop'
            prompt = "Stop which skill?"
            self.get_user_input(self.handle_user_which_skill_response, prompt, self.handle_timeout)

    def handle_start_skill(self, msg):
        print(msg)
        print(msg['data'])
        sentence_info = msg['data']['utt']
        sentence_info = msg['data']['utt']
        subject = sentence_info['subject']
        if subject and subject != '' and subject != 'skill':
            print("XXXXXXXXXXXX run skill %s" % (subject,))
            self.start_skill(subject)
            #self.handle_user_which_skill_response(subject)
        else:
            self.last_op = 'start'
            prompt = "Start which skill?"
            self.get_user_input(self.handle_user_which_skill_response, prompt, self.handle_timeout)

    def handle_list_skills(self, msg):
        say = ""
        if len(self.available_skills) > 0:
            say = "The following skills are available to be installed."
            for skill in self.available_skills:
                skill = skill.replace("_"," ")
                speak_skill = " The " + skill + " skill."
                say += speak_skill

        if len(self.already_installed) > 0:
            say += " The following skills are already installed."
            for skill in self.already_installed:
                skill = skill.replace("_"," ")
                speak_skill = " The " + skill + " skill."
                say += speak_skill

        self.speak(say)

    def handle_list_installed_skills(self, msg):
        print(self.already_installed)
        say = ''
        for skill in self.already_installed:
            skill_name = skill
            say += "the %s skill" % (skill_name,)
        self.speak(say)

    def handle_list_available_skills(self, msg):
        print(self.available_skills)
        say = ''
        for skill in self.available_skills:
            say += "the %s skill" % (skill,)
        self.speak(say)

    def handle_list_active_skills(self, msg):
        output = os.popen("ps auxww | grep privoice").read()
        output = output.split("\n")
        say = 'The following skills are currently running.'
        for line in output:
            line = line.split("/")
            line = line[ len(line) - 1 ]
            line = line.strip()
            if line and len(line) > 0: 
                line = line[9:]
                print("XXXXXXXXXXXXXXXXXXXXX %s" % (line,))
                tmp = "The %s skill." % (line,)
                say += tmp

        self.speak(say)


    def handle_install_skill(self, msg):
        print(msg)
        print(msg['data'])
        sentence_info = msg['data']['utt']
        subject = sentence_info['subject']
        if subject and subject != '' and subject != 'skill':
            self.install_skill(subject)
        else:
            prompt = "Which skill?"
            self.get_user_input(self.handle_user_which_skill_response, prompt, self.handle_timeout)

    def handle_delete_skill(self, msg):
        self.speak("you asked to delete skill")
        # TODO delete is a stop fillowed by an rm
        self.uninstall_skill(msg)


    def get_skills_from_repos(self):
        skill_repos = get_skill_repos()

        # clear out previous run results
        os.chdir("tmp/skills")
        os.system("rm -Rf *")

        # build directory of skills 
        self.available_skills = []
        self.already_installed = []
        directory = '.'
        self.all_skills = []
        skill_ids = []
        for repo in skill_repos:
            repo_name = repo['repo_name']
            if not repo['repo_uri'].startswith("https"):
                # if local files
                try:
                    os.chdir(repo['repo_uri'])
                except:
                    print("Error! invalid local repo dir %s" % (repo['repo_uri'],))
                    pass
            else:
                # else checkout repository
                old_subdirs = set( next(os.walk('.'))[1] )
                print("\nProcessing Repo %s" % (repo_name,))
                cmd = "git clone %s" % (repo['repo_uri'],)
                try:
                    os.system(cmd)
                except:
                    print("Error! caught exception on git clone of repo %s" % (repo_name,))
                    pass
                new_subdirs = set( next(os.walk('.'))[1] ) - old_subdirs
                if new_subdirs:
                    new_subdirs = list( new_subdirs )
                    #print(new_subdirs)
                    os.chdir(new_subdirs[0])

            #print("Moved to directory %s" % (os.getcwd(),))
            subdirs = set( next(os.walk('.'))[1] )
            repo_skill_ctr = 0
            for subdir in subdirs:
                if subdir.startswith("privoice_"):
                    #print("Maybe Found skill %s" % (subdir,))
                    skill_base_dir = os.getcwd() + "/" + subdir
                    err_flag = True
                    # we require a skill.json file be present
                    try:
                        fh = open(subdir + "/skill.json")
                        skill_data = json.loads(fh.read())
                        err_flag = False
                    except:
                        print("Error, no skill.json file found!")

                    if err_flag:
                        continue

                    # we also require an __init__.py file be present
                    try:
                        fh = open(subdir + "/__init__.py")
                    except:
                        print("Error, no __init__.py file found!")
                        err_flag = True

                    if err_flag:
                        continue

                    skill_ids.append(skill_data['skill_id'])
                    self.all_skills.append(Skill(
                                skill_id=skill_data['skill_id'],
                                name=skill_data['name'],
                                description=skill_data['description'],
                                search_terms=skill_data['search_terms'],
                                repo=repo_name,
                                base_dir=skill_base_dir
                               ))
                    repo_skill_ctr += 1

            os.chdir("../")
            print("Found %s skills in this repo" % (repo_skill_ctr,))

        os.chdir(MY_BASE_DIR)
        #print("Ended up in %s" % (os.getcwd(),))

        # at this point, all_skills[] array holds all known skills
        # from all known repositories. Now determine any user skills
        # which are already installed
        os.chdir("skills/user_skills")
        cleaned_list = []
        self.already_installed = set( next(os.walk('.'))[1] )
        for skill in self.already_installed:
            cleaned_list.append( skill[9:] )

        self.already_installed = set(cleaned_list)
        print("Already installed", self.already_installed)

        self.available_skills = set( skill_ids ) - self.already_installed
        print("Available, not already installed ", self.available_skills)

        os.chdir("../../")

    # normal skill type stuff
    def stop(self, msg):
        print("\n*** Skill Manager - stop() hit ***\n")
        """the protocol is set state to your value
        and run until it changes. this will change it
        to 'Idle'"""
        self.state = 'Idle'

    def run_skill(self):
        # only do this if you want some 
        # sort of background timer
        while True:
            #print("tic")
            time.sleep(10)

    def help(self, msg):
        say = """The skill manager is used to install and remove skills.
        Basic commands are install skill, remove skill and show skills.
        You may also start and stop skills.
        For example, stop the weather skill.
        Or, show active skills."""
        self.speak(say)


if __name__ == '__main__':
    sm = SkillManager()
    sm.run_skill()
    Event().wait()  # should never get here

