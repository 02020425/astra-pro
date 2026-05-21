import math
from typing import Union, Dict, Any


class CalculatorTool:
    name = "calculator"
    description = "用于进行数学计算，包括加减乘除、幂运算、三角函数等"
    
    def call(self, args: Dict[str, Any]) -> str:
        expression = args.get("expression", "")
        try:
            result = eval(expression, {"math": math, "__builtins__": {}})
            return f"计算结果：{result}"
        except Exception as e:
            return f"计算错误：{str(e)}"
    
    async def async_call(self, args: Dict[str, Any]) -> str:
        return self.call(args)
    
    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "要计算的数学表达式",
                        }
                    },
                    "required": ["expression"],
                },
            },
        }


calculator_tool = CalculatorTool()