import io

a = """第一章 函数与极限 1
\t第一节 映射与函数 1
\t\t一、映射 1
\t\t二、函数 3
\t\t习题 1-1 16"""


with io.StringIO(a) as f:
    for s in f:
        print(s)
