from autogen import GroupChatManager
import inspect
import os

def main():
    source = inspect.getsource(GroupChatManager.__init__)
    filepath = os.path.join(os.getcwd(), 'group_chat_manager_init.txt')
    with open(filepath, 'w') as f:
        f.write(source)
    print(f'Source code written to {filepath}')

if __name__ == '__main__':
    main()