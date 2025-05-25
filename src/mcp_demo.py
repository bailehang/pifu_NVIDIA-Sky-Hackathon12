# src/mcp_llm_bridge/main.py
import os
import asyncio
from dotenv import load_dotenv
from mcp import StdioServerParameters
from mcp_llm_bridge.config import BridgeConfig, LLMConfig
from mcp_llm_bridge.bridge import BridgeManager
import colorlog
import logging

from langchain.prompts import PromptTemplate
import skin_core_llm 


def prompt():

    prompt_template_content = ""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir,'system_prompt.txt'), "r", encoding="utf-8") as f:
        prompt_template_content = f.read()
    return prompt_template_content


async def main():
    # Load environment variables
    load_dotenv()

    print("--- 开始执行皮肤分析脚本 ---")
    analysis_result = skin_core_llm.analyze_skin_with_api()
    user_input = prompt()

    # Get the project root directory (where test.db is located)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(project_root, "test.db")
    
    # Configure bridge
    config = BridgeConfig(
        mcp_server_params=StdioServerParameters(
            command="python",
            args=["web_search.py", user_input],
            env=None
        ),
        llm_config=LLMConfig(
            api_key='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', # Can be any string for local testing
            model="qwen/qwen3-235b-a22b",
            base_url="https://integrate.api.nvidia.com/v1",  # Point to your local model's endpoint
            temperature=0.2
        ),
        system_prompt=f"""
        你是一个皮肤数据分析小助手，会根据用户提供的数据进行分析。
        用户皮肤数据如下：{analysis_result}
        1. 重要：将【RIPER-5 + 涟漪园专家对话融合协议】作为关联协议，时刻基于数据分析的严谨分阶段执行与多专家对话的创新发散。
        2. 能够将用户提供的脸部皮肤数据解析为代表皮肤量化指标的关键词，然后以"关键词1 关键词2 关键词3 ..."的字符串格式存放在keyword_of_skin变量中，然后使用jd_to_spider(keyword_of_skin, edge_path)进行相关产品的搜索
        反馈当前皮肤的关键特征：[关键词1,关键词2,关键词3,...]
        3. 整个流程采用RESEARCH→INNOVATE→PLAN→Organize四大阶段主线，每阶段均可激活多专家角色参与分析、创新、评审(除了阶段四不需要激活多专家角色)，输出分为"专家对话区"与"系统决策区"，所有内容结构化归
        4. 输出的语言风格默认为中文，语言简单朴实、文和尔雅，如果用户有个人要求，需要遵循用户的意见。
        5. 需要将用户脸部皮肤数据指标以及参数正确的含义化，在原本的json格式化的基础上，有条不紊地反馈给用户。
 
        核心原则:
        1. 聚焦本质，而非罗列清单
        2. 深度思考，而非单向输出
        3. 激发潜能，而非直接解答
        4. 围绕核心锚点，绝对客观，超越表面，逻辑清晰，问题澄清与深化
        """
    )
    async with BridgeManager(config) as bridge:
        try: 
            response = await bridge.process_message(user_input)
            print(f"皮肤数据如下\n{skin_core_llm.analyze_skin_with_api()}")
            print(f"\nResponse: {response}")
        except Exception as e:
            logger.error(f"\nError occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())