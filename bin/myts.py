#!/bin/env python
import sys
import logging
import re
import os
import os.path
import stat
import tempfile
import pprint
from string     import Template
from subprocess import call, check_call, CalledProcessError

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
        ssh = check_call(["ssh", "-q", server, "echo"])
    except CalledProcessError as e:
        print "error: ssh to %s failed with reutrn code %d" % (server, e.returncode)
        return False
    return True

def check_servers(servers):
    for server in servers:
        if not ssh(server):
            sys.exit(1)

def get_session_servers(session):
    session_file=os.path.expanduser("~/.tmux/sessions.tmux")
    if not os.path.isfile(session_file):
        logging.critical("fatal: {} file not found".format(session_file))
        sys.exit("cannot proceed without sessions definition file")

    servers = None
    with open(session_file) as file:
        for line in file:
            if re.match(session, line):
                servers = line[line.rindex(":")+1:].strip().split(",")
    return servers

def start_session(session):
    servers = get_session_servers(session)
    if servers is None:
        sys.exit("no servers defined for session [{}]".format(session))
    check_servers(servers)
    script = tempfile.mkstemp()[1]
    with open(script, "w") as file:
        file.write(get_script_content(session, servers))

    os.chmod(script, os.stat(script).st_mode | stat.S_IEXEC)
    logging.info("running {}".format(script))
    call(["/bin/bash", script])
    os.remove(script)

if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    if len(sys.argv) < 2:
        sys.exit("usage: {} session_name".format(sys.argv[0]))
    start_session(sys.argv[1])
