import signal
import time
import logging
import datetime
import argparse
import sys
import os

exit_flag = False
file_dict = {}

logger = logging.getLogger(__name__)

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger.setLevel(logging.DEBUG)


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name
    global exit_flag
    logger.debug('Received ' + signal.Signals(sig_num).name)
    exit_flag = True


def dirwatch(args):
    """Watch a given directory added magic string."""
    file_names = os.listdir(args.path)
    for file_ in file_names:
        if file_.endswith(args.ext) and file_ not in file_dict:
            file_dict[file_] = 0
            logger.info(f'New file was added ({file_})')
    for keys in list(file_dict):
        if keys not in file_names:
            logger.info(f'A file was removed ({keys})')
            del file_dict[keys]
    for file_ in file_dict:
        file_dict[file_] = magic_word(os.path.join(args.path,file_),file_dict[file_], args.magic)

def magic_word(file_name,starting_line,word):
    counter = starting_line
    with open(file_name) as f:
        for counter, line in enumerate(f):
            if counter >= starting_line:
                if word in line:
                    logger.info(f'{word} found on line {counter + 1}')
            counter += 1
    return counter


def create_parser():
    """Create a command line parser object with some arguments."""
    parser = argparse.ArgumentParser(
        description="Watches a directory of text files for a magic string.")
    parser.add_argument(
        'path', help='Directory to watch')
    parser.add_argument(
        'magic', help='String to watch for')
    parser.add_argument(
        '-e', '--ext', default='.txt', help='Text file extension to watch e.g .txt, .log')
    parser.add_argument(
        '-i', '--interval', default=2.0, help='Number of seconds between polling')
    return parser


def main(args):
    parser = create_parser()
    # Run the parser to collect command line arguments into a
    # NAMESPACE called 'ns'
    ns = parser.parse_args()

    if not ns:
        parser.print_usage()
        sys.exit(1)
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    app_start_time = datetime.datetime.now()

    logger.info(
        '\n'
        '-----------------------------------------------------------------\n'
        f'    Running {__file__}\n'
        f'    Started on {app_start_time.isoformat()}\n'
        '-----------------------------------------------------------------\n'
    )

    directory = ns.path
    time_polling = ns.interval
    

    while not exit_flag:
        try:
            # call my directory watching function
            dirwatch(ns)
        except FileNotFoundError:
            logger.error('Directory does not exist')
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            print(e)

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(int(time_polling))
    
    uptime = datetime.datetime.now() - app_start_time
    logger.info(
        '\n'
        '-----------------------------------------------------------------\n'
        f'    Stopped {__file__}\n'
        f'    Uptime was {str(uptime)}\n'
        '-----------------------------------------------------------------\n'
    )

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start

if __name__ == "__main__":
    main(sys.argv[1:])