from autogen_agentchat.teams import SelectorGroupChat
import inspect
import os

def main():
    source = inspect.getsource(SelectorGroupChat.__init__)
    filepath = os.path.join(os.getcwd(), 'selector_group_chat_init.txt')
    with open(filepath, 'w') as f:
        f.write(source)
    print(f'Source code written to {filepath}')

if __name__ == '__main__':
    main()