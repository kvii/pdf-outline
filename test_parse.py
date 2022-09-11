
import unittest
from dataclasses import dataclass
from typing import List

from parse import OutlineItem, parse_str


class TestParse(unittest.TestCase):
    def test_parse(self):

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
                "	e e 5",
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
        ]

        for v in data:
            if v.isErr:
                with self.assertRaises(Exception):
                    parse_str(v.s)
            else:
                value = parse_str(v.s)
                self.assertEqual(v.want, value, v.name)
