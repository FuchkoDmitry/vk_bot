# def func():
#     newlst = input('введи значения').split(',')
#     return newlst
#
#
# # lst = [1,2,3,4]
# # iter = iter(lst)
# def func2(lst):
#     iterator = iter(lst)
#     while True:
#         e = input('input:')
#         if e == 'next':
#             try:
#                 print(next(iterator))
#             except StopIteration:
#                 print('список закончился')
#                 func2(func())
#             # break
#
# func2([1,2,3,4])
def input_func():
    return input('input')

def func():
    print('exit in gen func')

def genfunc(lst):
    for el in lst:
        message = input_func()
        yield el
        message = input_func()
        if message != 'exit':
            yield from genfunc(lst)

print(next(genfunc([1,2,4])))


