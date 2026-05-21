import math
from typing import Union, Dict, Any


class CalculatorTool:
    name = "calculator"
    description = "用于进行数学计算，支持加减乘除、sqrt、sin、cos、log、pi、e 等数学函数"
    
    def call(self, args: Dict[str, Any]) -> str:
        expression = args.get("expression", "").strip().strip("`").strip()
        namespace = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        try:
            result = eval(expression, namespace, {})
            return f"计算结果：{result}"
        except Exception as e:
            return f"计算错误（表达式: {expression}）：{str(e)}"
    
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