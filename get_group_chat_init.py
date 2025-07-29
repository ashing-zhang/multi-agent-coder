import inspect
from autogen import GroupChat

# 获取GroupChat类的__init__方法源码
source = inspect.getsource(GroupChat.__init__)

# 将源码写入文件
with open('group_chat_init.txt', 'w', encoding='utf-8') as f:
    f.write(source)

print('GroupChat.__init__ source code has been written to group_chat_init.txt')