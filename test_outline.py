
import unittest
from dataclasses import dataclass
from typing import List

from outline import OutlineItem, format_str, parse_str


class TestParse(unittest.TestCase):
    def test_parse(self):
        """测试解析函数"""

        @dataclass
        class TestCase:
            name: str
            """测试项目"""
            s: str
            """输入参数"""
            isErr: bool
            """是否为异常"""
            want: List[OutlineItem]
            """期望的返回值"""

        data = [
            TestCase(
                name='正常情况',
                s="a a 1\n"
                "	b b 2\n"
                "		c c 3\n"
                "		d d 4\n"
                "	e e 5\n",
                isErr=False,
                want=[
                    {
                     'name': 'a a',
                     'page': 1,
                     'children': [
                         {
                             'name': 'b b',
                             'page': 2,
                             'children': [
                                 {
                                     'name': 'c c',
                                     'page': 3,
                                     'children': [],
                                 },
                                 {
                                     'name': 'd d',
                                     'page': 4,
                                     'children': [],
                                 },
                             ],
                         },
                         {
                             'name': 'e e',
                             'page': 5,
                             'children': [],
                         },
                     ],
                    },
                ],
            ),
            TestCase(
                name='首行目录包含缩进符',
                s="	b b 2\n",
                isErr=True,
                want=[],
            ),
            TestCase(
                name='目录缩进字符使用空格符',
                s="a 1\n"
                "  b 2\n",
                isErr=True,
                want=[],
            ),
            TestCase(
                name='负数',
                s="a -1\n",
                isErr=False,
                want=[OutlineItem(name='a', page=-1, children=[])],
            ),
        ]

        for v in data:
            if v.isErr:
                with self.assertRaises(Exception):
                    parse_str(v.s)
            else:
                value = parse_str(v.s)
                self.assertEqual(v.want, value, v.name)

    def test_format(self):
        """测试格式化函数"""

        @dataclass
        class TestCase:
            name: str
            """测试项目"""
            items: List[OutlineItem]
            """目录项目"""
            want: str
            """期望值"""

        data = [
            TestCase(
                name='正常情况',
                items=[
                    {
                        'name': 'a a',
                        'page': 1,
                        'children': [
                            {
                                'name': 'b b',
                                'page': 2,
                                'children': [
                                    {
                                        'name': 'c c',
                                        'page': 3,
                                        'children': [],
                                    },
                                    {
                                        'name': 'd d',
                                        'page': 4,
                                        'children': [],
                                    },
                                ],
                            },
                            {
                                'name': 'e e',
                                'page': 5,
                                'children': [],
                            },
                        ],
                    },
                ],
                want="a a 1\n"
                "	b b 2\n"
                "		c c 3\n"
                "		d d 4\n"
                "	e e 5\n",
            ),
            TestCase(
                name='单行',
                items=[
                    OutlineItem(
                        name='a',
                        page=1,
                        children=[],
                    ),
                ],
                want='a 1\n',
            ),
        ]
        for v in data:
            s = format_str(v.items)
            self.assertEqual(s, v.want, v.name)

    def test_cycle(self):
        """测试 parse 与 format 的结果是否可以相互转换"""

        @dataclass
        class TestCase:
            name: str
            """测试项目"""
            s: str
            """被解析项"""

        data = [
            TestCase(
                name='基础情况',
                s="a 1\n",
            ),
            TestCase(
                name="正常情况",
                s="a a 1\n"
                "	b b 2\n"
                "		c c 3\n"
                "		d d 4\n"
                "	e e 5\n",
            ),
        ]
        for v in data:
            items = parse_str(v.s)
            s = format_str(items)
            self.assertEqual(s, v.s, v.name)
