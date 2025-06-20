import os
import argparse


def killBot():
    os.system("/usr/bin/tmux kill-session -t bot")
    print("Bot killed")


def startBot():
    os.system("/usr/bin/tmux kill-session -t bot")
    os.system("/usr/bin/tmux new-session -d -s bot 'python3 -u main.py'")
    print("Bot Started")


def updateBot():
    killBot()
    os.system('eval "$(ssh-agent -s)"')
    os.system("ssh-add github_ssh_key")
    os.system("git fetch origin")
    os.system("git pull origin main")
    print("Bot Updated")
    startBot()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control the bot")
    parser.add_argument("command", help="run/kill/update")

    args = parser.parse_args()

    match args.command:
        case "run":
            startBot()
        case "kill":
            killBot()
        case "update":
            updateBot()
        case _:
            print(f"Unknown command {args.command}")
