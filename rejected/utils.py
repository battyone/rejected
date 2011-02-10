# -*- coding: utf-8 -*-
import grp
import logging
import os
import pwd
import signal
import socket
import sys
import yaml

children = []  # Global list of children to shutdown on shutdown
pidfiles = []  # Global list of pidfiles


def application_name():
    """
    Returns the currently running application name
    """
    return os.path.split(sys.argv[0])[1]


def hostname():
    """
    Returns the hostname for the machine we're running on
    """
    return socket.gethostname().split(".")[0]


def daemonize(pidfile=None, user=None, group=None):
    """
    Fork the Python app into the background and close the appropriate
    "files" to detach from console. Based off of code by Jürgen Hermann and
    http://code.activestate.com/recipes/66012/

    Parameters:

    * pidfile: Pass in a file to write the pid, defaults to
               /tmp/current_process_name-pid_number.pid
    * user: User to run as, defaults to current user
    * group: Group to run as, defaults to current group
    """

    # Flush stdout and stderr
    sys.stdout.flush()
    sys.stderr.flush()

    # Fork off from the process that called us
    pid = os.fork()
    if pid > 0:
        sys.exit(0)


    # Second fork to put into daemon mode
    pid = os.fork()
    if pid > 0:
        # exit from second parent, print eventual PID before
        sys.stdout.write('%s: started - PID # %d\n' % (application_name(),
                                                       pid))

        # Setup a pidfile if we weren't passed one
        pidfile = pidfile or \
                  os.path.normpath('/tmp/%s-%i.pid' % (application_name(),
                                                       pid))

        # Write a pidfile out
        with open(pidfile, 'w') as f:
          f.write('%i\n' % pid)

        # Append the pidfile to our global pidfile list
        global pidfiles
        pidfiles.append(pidfile)

        # Exit the parent process
        sys.exit(0)

    # Detach from parent environment
    os.chdir(os.path.normpath('/'))
    os.umask(0)
    os.setsid()

    # Redirect stdout, stderr, stdin
    si = file('/dev/null', 'r')
    so = file('/dev/null', 'a+')
    se = file('/dev/null', 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # Set the running user
    logging.debug("Changing the running user to %s:%s" % (user, group))

    if user:
        uid = pwd.getpwnam(user).pw_uid
        # Make sure we're not trying to switch to the same user
        if uid != os.geteuid():
            os.setuid(uid)

    # Set the running group
    if group:
        gid = grp.getgrnam(group).gr_gid
        # Make sure we're not already in the right group
        if gid != os.getegid():
            os.setgid(gid)

    return True


def load_configuration_file(config_file):
    """
    Load our YAML configuration file from disk or error out
    if not found or parsable
    """

    try:
        with file(config_file, 'r') as f:
            config = yaml.load(f)

    except IOError as err:
        sys.stderr.write('Configuration file not found "%s"\n' % config_file)
        sys.exit(1)

    except yaml.scanner.ScannerError as err:
        sys.stderr.write('Invalid configuration file "%s":\n%s\n' % \
                         (config_file, err))
        sys.exit(1)

    return config


def setup_logging(config, debug=False):
    """
    Setup the logging module to respect our configuration values.
    Expects a dictionary called config like:

    {'directory': '/log/path',       # Optional log file output directory
     'filename': 'application.log',  # Optional filename, not needed for syslog
     'format': "%(levelname) -10s %(asctime)s %(message)s", # Log format string
     'level': 'error'  # string value as defined in the logging_levels below
     'handler': 'syslog'  # Logging handler
     'syslog': { 'address': '/dev/log',  # syslog address to connect to
                 'facility': 'local6'} } # syslog facility to use

    Passing in debug=True will disable any log output to anything but stdout
    and will set the log level to debug regardless of the config.
    """
    # Set logging levels dictionary
    logging_levels = {'debug':    logging.DEBUG,
                      'info':     logging.INFO,
                      'warning':  logging.WARNING,
                      'error':    logging.ERROR,
                      'critical': logging.CRITICAL}

    # Get the logging value from the dictionary
    logging_level = config['level']

    if debug:

        # Override the logging level to use debug mode
        config['level'] = logging.DEBUG

        # If we have specified a file, remove it so logging info goes to stdout
        if 'filename' in config:
            del config['filename']

    else:

        # Use the configuration option for logging
        config['level'] = logging_levels.get(config['level'], logging.NOTSET)

    # Pass in our logging config
    logging.basicConfig(**config)
    logging.info('Log level set to %s' % logging_level)

    # If we have supported handler
    if 'handler' in config and not debug:

        # If we want to syslog
        if config['handler'] == 'syslog':

            facility = config['syslog']['facility']
            import logging.handlers as handlers

            # If we didn't type in the facility name
            if facility in handlers.SysLogHandler.facility_names:

                # Create the syslog handler
                address = config['syslog']['address']
                facility = handlers.SysLogHandler.facility_names[facility]
                syslog = handlers.SysLogHandler(address=address,
                                                facility=facility)

                # Get the default logger
                default_logger = logging.getLogger('')

                # Add the handler
                default_logger.addHandler(syslog)

                # Remove the default stream handler
                for handler in default_logger.handlers:
                    if isinstance(handler, logging.StreamHandler):
                        default_logger.removeHandler(handler)

            else:
                logging.error('%s:Invalid facility, syslog logging aborted',
                              application_name())


def shutdown():
    """
    Cleanly shutdown the application
    """
    # Tell all our children to terminate
    for child in children:
        child.terminate()

    # Remove our pidfiles
    for pidfile in pidfiles:
        if os.path.isfile(pidfile):
            os.unlink(pidfile)


def setup_signals():
    """
    Setup the signals we want to be notified on
    """
    signal.signal(signal.SIGTERM, _shutdown_signal_handler)
    signal.signal(signal.SIGHUP, _rehash_signal_handler)


def _shutdown_signal_handler(signum, frame):
    """
    Called on SIGTERM to shutdown the application
    """
    logging.info("SIGTERM received, shutting down")
    shutdown()

def _rehash_signal_handler(signum, frame):
    """
    Would be cool to handle this and effect changes in the config
    """
    logging.info("SIGHUP received, rehashing config")
