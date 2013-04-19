#!/bin/env python
import sys
import logging
import re
import os
import os.path
import stat
import tempfile
import pprint
import subprocess
from string     import Template

sessions_data_file = os.path.expanduser("~/.tmux/sessions.tmux")

def get_header_lines(session_name):
    header = Template("""#!/bin/bash

SESSION_NAME=${name}

if ! tmux has-session -t ${SESSION_NAME} > /dev/null
then
    tmux new-session -s "${SESSION_NAME}" -d
""")
    return header.safe_substitute(name=session_name)

def get_first_host_lines(host):
    first_server = Template("""
    tmux rename-window "${server}"
    tmux send-keys -t "${SESSION_NAME}:${window}" "ssh ${server}" C-m
    tmux split-window -v -p 50 "ssh ${server}"
""")
    # we start the window count with 1, this is set within your ~/.tmux.conf
    return first_server.safe_substitute(window=1, server=host)

def get_other_host_lines(hosts):
    each_server = Template("""
    tmux new-window -kn "${server}"
    tmux send-keys -t "${SESSION_NAME}:${window}" "ssh ${server}" C-m
    tmux split-window -v -p 50 "ssh ${server}"
""")
    content = ""
    count = 2
    for host in hosts:
        content += each_server.safe_substitute(window=count, server=host)
        count += 1
    return content

def get_footer_lines():
    return """
    tmux select-window -t "${SESSION_NAME}:1"
    tmux select-pane -U
fi

tmux attach-session -t $SESSION_NAME"""

def get_script_content(session_name, servers):
    file_content = get_header_lines(session_name)
    file_content += get_first_host_lines(servers[0])
    file_content += get_other_host_lines(servers[1:])
    file_content += get_footer_lines()
    return file_content

def ssh(server):
    logging.info("checking server: %s" % server)
    try:
        ssh = subprocess.check_call(["ssh", "-q", server, "echo"])
    except subprocess.CalledProcessError as e:
        print "error: ssh to %s failed with reutrn code %d" % (server, e.returncode)
        return False
    return True

def check_servers(servers):
    for server in servers:
        if not ssh(server):
            sys.exit(1)

def get_all_sessions():
    return sorted(set(get_defined_sessions() + get_active_sessions()))

def get_active_sessions():
    proc = subprocess.Popen(["tmux", "list-sessions"], stdout=subprocess.PIPE)
    sessions = []
    for line in proc.stdout:
        if re.search(":", line):
            sessions.append(line[0:line.index(":")])
    return sessions

def get_defined_sessions():
    if not os.path.isfile(sessions_data_file):
        logging.critical("fatal: {} file not found".format(sessions_data_file))
        sys.exit("cannot proceed without sessions definition file")

    sessions = []
    with open(sessions_data_file) as file:
        for line in file:
            if re.match("#",line) is None and re.search(":", line):
                sessions.append(line[0:line.index(":")].strip())
    return sessions

def get_session_servers(session):
    if not os.path.isfile(sessions_data_file):
        logging.critical("fatal: {} file not found".format(sessions_data_file))
        sys.exit("cannot proceed without sessions definition file")

    servers = None
    with open(sessions_data_file) as file:
        for line in file:
            if re.match(session, line):
                servers = [srv.strip() for srv in line[line.rindex(":")+1:].split(",")]
    return servers

def attach_session(session):
    cmd = ["tmux", "attach-session", "-t", session]
    if session is None:
        print "quitting..."
    else:
        subprocess.call(cmd)

def new_session(session):
    servers = get_session_servers(session)
    if servers is None:
        sys.exit("no servers defined for session [{}]".format(session))
    check_servers(servers)
    script = tempfile.mkstemp()[1]
    with open(script, "w") as file:
        file.write(get_script_content(session, servers))

    os.chmod(script, os.stat(script).st_mode | stat.S_IEXEC)
    logging.info("running {}".format(script))
    subprocess.call(["/bin/bash", script])
    os.remove(script)

def prompt_for_active_sessions():
    sessions = get_active_sessions()
    print "Choose one of the following sessions by number (or n)\n"
    choice = {'n': None}
    for item, value in enumerate(sessions):
        print "%2d: %s" % (item+1, value)
        choice[str(item+1)] = value
    while True:
        ans = raw_input("your choice: ")
        if (ans in choice.keys()):
            break
        else:
            print "error: invalid choice"
    return choice[ans]

def start_session(session):
    if session in get_active_sessions():
        attach_session(session)
    else:
        new_session(session)

if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    if len(sys.argv) < 2:
        attach_session(prompt_for_active_sessions())
    else:
        start_session(sys.argv[1])
