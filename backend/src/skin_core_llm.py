# skin_analysis/skin_core_llm.py
import requests
import sys,os,json

from to_jpg import convert_to_jpg
from config_loader import get_app_config # 导入新的统一入口函数

sys.stdout.reconfigure(encoding="utf-8")

# --- 1. 将核心逻辑封装到函数中 ---
def analyze_skin_with_api(image_path=None):
    """
    加载配置，处理图片，向API发送皮肤分析请求，并返回JSON响应。

    Args:
        image_path (str, optional): 输入图片的路径。如果为None，则使用配置文件中的默认路径。

    Returns:
        dict or None: 如果请求成功并解析到JSON，则返回JSON响应字典；否则返回None。
    """
    # --- 1. 加载应用配置 ---
    app_cfg = get_app_config()

    # --- 2. 获取并处理输入图片路径 ---
    if image_path is None:
        file_path = app_cfg.default_image_path
    else:
        file_path = image_path

    print(f"使用的图片路径: {file_path}")
    to_jpg_path = convert_to_jpg(file_path)

    if not to_jpg_path:
        print("图片转换失败或文件不存在，程序将退出。")
        return None # 或者 sys.exit(1) 如果希望失败时终止程序

    # --- 4. 准备API请求 ---
    payload={}
    files=[
      (app_cfg.file_form_field_name,
       (app_cfg.file_sent_filename_placeholder, open(to_jpg_path,'rb'), app_cfg.file_content_type)
      )
    ]
    headers = {
      app_cfg.api_key_header_name: app_cfg.api_key
    }

    response_json = None # 初始化响应变量

    try:
        print(f"向URL {app_cfg.api_url} 发送请求...")
        response = requests.request("POST",
                                    app_cfg.api_url,
                                    headers=headers,
                                    data=payload,
                                    files=files,
                                    timeout=app_cfg.request_timeout_seconds)
        response.raise_for_status() # 如果HTTP请求返回了失败的状态码 (4xx or 5xx)，则抛出HTTPError异常

        response_json = response.json()['result']
        # 将JSON对象格式化输出
        formatted_json = json.dumps(response_json,
                                    indent=app_cfg.json_indent,
                                    ensure_ascii=app_cfg.json_ensure_ascii)
        print("\n--- API 响应 ---")
        # print(formatted_json)
        return formatted_json

    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误: {e}")
        if 'response' in locals() and response is not None: # 确保response对象存在
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误: {e}")
    except requests.exceptions.Timeout:
        print(f"请求超时（超过 {app_cfg.request_timeout_seconds} 秒）。")
    except requests.exceptions.RequestException as e: # 其他requests相关的错误
        print(f"请求发生错误: {e}")
    except json.JSONDecodeError:
        print("无法解析响应为JSON。")
        if 'response' in locals() and response is not None: # 确保response对象存在
            print(f"原始响应内容 (状态码 {response.status_code}):\n{response.text}")
    except Exception as e: # 捕获其他意外错误
        print(f"在API请求或处理过程中发生未知错误: {e}")
    finally:

        for _, (_, file_obj, _) in files:
             pass

        if to_jpg_path and to_jpg_path != file_path and os.path.exists(to_jpg_path):
            try:
                # 确保在关闭文件后再删除 (requests handles closing for files in the 'files' parameter)
                print(f"尝试删除临时转换文件: {to_jpg_path}")
                os.remove(to_jpg_path)
                print(f"已删除临时转换文件: {to_jpg_path}")
            except Exception as e_remove:
                print(f"删除临时文件 {to_jpg_path} 失败: {e_remove}")

    # 返回API响应（如果成功）
    return response_json

def response_to_json(analysis_result):
    # 保存结果为JSON文件
        output_path = os.path.join(os.path.dirname(__file__), "skin_core_llm.json")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=4)
            print(f"分析结果已保存到: {output_path}")
        except Exception as e:
            print(f"保存分析结果到JSON文件失败: {e}")

# --- 7. 示例用法（如何在脚本执行时调用函数） ---
if __name__ == "__main__":
    print("--- 开始执行皮肤分析脚本 ---")
    analysis_result = analyze_skin_with_api()

    if analysis_result:
        print("\n--- 分析完成，成功获取响应 ---")
        
        response_to_json(analysis_result)
    else:
        print("\n--- 皮肤分析失败 ---")


print("脚本执行完毕。")