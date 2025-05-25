from PIL import Image
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

def convert_to_jpg(file_path):
    """
    将给定路径的图片转换为JPG格式。
    如果图片已经是JPG或JPEG格式，则直接返回原始路径。

    参数:
    file_path (str): 原始图片的完整路径。

    返回:
    str: 转换后的JPG图片的路径，或原始路径（如果已经是JPG/JPEG），如果转换失败则返回None。
    """
    try:
        # 获取文件扩展名并转为小写
        file_name, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        # 检查是否已经是JPG或JPEG
        if file_extension in ['.jpg', '.jpeg']:
            print(f"文件 {file_path} 已经是JPG/JPEG格式，无需转换。")
            return file_path

        img = Image.open(file_path)
        
        # 构建输出文件名，将扩展名更改为 .jpg
        output_path = file_name + ".jpg"
        
        # 如果图像有alpha通道（例如PNG的透明度），转换为RGB
        if img.mode == 'RGBA' or img.mode == 'LA' or (img.mode == 'P' and 'transparency' in img.info):
            # 创建一个白色背景的图像
            background = Image.new("RGB", img.size, (255, 255, 255))
            # 将原始图像粘贴到背景上（处理透明度）
            # 如果img是P模式且有透明度，先转为RGBA
            if img.mode == 'P' and 'transparency' in img.info:
                img = img.convert("RGBA")
            
            # 获取alpha通道作为mask
            if img.mode == 'RGBA':
                alpha_mask = img.split()[3]
            elif img.mode == 'LA': # LA模式，第二个通道是alpha
                 alpha_mask = img.split()[1]
            else: # 其他情况（如P模式转换后的RGBA）
                 alpha_mask = None # 或者根据具体情况处理

            background.paste(img, mask=alpha_mask)
            img_to_save = background
        else:
            # 如果已经是RGB或可以安全转换为RGB
            img_to_save = img.convert('RGB')
            
        img_to_save.save(output_path, "JPEG")
        print(f"图片已成功转换为JPG格式并保存到: {output_path}")
        return output_path
    except FileNotFoundError:
        print(f"错误: 文件未找到 {file_path}")
        return None
    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        return None

if __name__ == "__main__":
    print("--- 开始执行皮肤分析脚本 ---")
    # 调用封装后的函数
    # 可以选择传入图片路径，或者不传使用默认配置
    # 例如: analyze_skin_with_api("/path/to/your/specific/image.png")
    analysis_result = convert_to_jpg(R"D:\桌面\demo\skin_analysis_mcp_workflow\image\1.png")

    if analysis_result:
        print("\n--- 分析完成，成功获取响应 ---")
        # 可以在这里进一步处理 analysis_result
        # print(json.dumps(analysis_result, indent=4))
    else:
        print("\n--- 皮肤分析失败 ---")

