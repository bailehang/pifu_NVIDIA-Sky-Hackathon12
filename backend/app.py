import os
import uuid
import subprocess
import json
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import base64
from io import BytesIO

app = Flask(__name__, static_folder='../frontend')

# 配置上传文件夹和允许的文件类型
UPLOAD_FOLDER = 'image'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 皮肤类型列表
SKIN_TYPES = ["干性皮肤", "油性皮肤", "中性皮肤", "混合型皮肤", "敏感性皮肤"]

# 建议列表库
RECOMMENDATIONS = {
    "dry": [
        "保持皮肤充分保湿，使用含有透明质酸、甘油等保湿成分的护肤品",
        "减少去角质频率，避免使用刺激性强的清洁产品",
        "注意环境湿度，可使用加湿器增加空气湿度",
        "选择温和的洁面产品，避免过度清洁"
    ],
    "oily": [
        "保持皮肤清洁，使用控油型洁面产品",
        "注意T区控油，可使用含有水杨酸的护肤品",
        "避免使用过于油腻的护肤品，选择清爽型产品",
        "饮食尽量清淡，减少高油高糖食物摄入"
    ],
    "normal": [
        "保持良好的生活习惯，均衡饮食，充足睡眠",
        "定期护理皮肤，保持皮肤健康状态",
        "注意防晒，预防皮肤老化",
        "使用适合自己肤质的基础护肤品"
    ],
    "combination": [
        "分区护理，T区注意控油，两颊注意保湿",
        "选择适合混合型皮肤的护肤品，避免过于油腻或过于干燥",
        "保持皮肤清洁，但不要过度清洁",
        "定期去角质，保持毛孔通畅"
    ],
    "sensitive": [
        "使用温和、无刺激的护肤品，避免含有酒精、香料等刺激性成分的产品",
        "注意防晒，选择物理防晒产品",
        "避免频繁更换护肤品，减少皮肤过敏风险",
        "保持皮肤屏障健康，可使用含有神经酰胺的护肤品"
    ]
}

def analyze_skin(image_path):
    """
    分析皮肤图像并返回分析结果
    
    在实际应用中，这里应该包含真正的皮肤分析算法
    例如使用计算机视觉技术分析皮肤纹理、颜色等特征
    
    参数:
        image_path: 图像文件路径
    
    返回:
        包含分析结果的字典
    """
    # 模拟分析过程
    print(f"开始分析图像: {image_path}")
    
    # 随机生成分析结果
    import random
    from datetime import datetime
    random.seed(datetime.now().timestamp())  # 使用当前时间作为随机种子，确保每次结果不同
    
    # 随机选择皮肤类型
    skin_type = random.choice(SKIN_TYPES)
    
    # 随机生成各项指标 (0-100)
    moisture_level = random.randint(20, 90)
    oil_level = random.randint(20, 90)
    pigmentation_level = random.randint(5, 40)
    sensitivity_level = random.randint(10, 70)
    
    # 根据皮肤类型选择建议
    if skin_type == "干性皮肤":
        recommendations = RECOMMENDATIONS["dry"]
    elif skin_type == "油性皮肤":
        recommendations = RECOMMENDATIONS["oily"]
    elif skin_type == "中性皮肤":
        recommendations = RECOMMENDATIONS["normal"]
    elif skin_type == "混合型皮肤":
        recommendations = RECOMMENDATIONS["combination"]
    else:  # 敏感性皮肤
        recommendations = RECOMMENDATIONS["sensitive"]
    
    # 添加一些通用建议
    general_recommendations = [
        "保持良好的生活习惯，饮食均衡，充足睡眠",
        "注意防晒，减少紫外线对皮肤的伤害",
        "定期清洁皮肤，保持毛孔通畅"
    ]
    
    # 从通用建议中随机选择1-2条添加到特定建议中
    recommendations += random.sample(general_recommendations, random.randint(1, 2))
    
    # 构建结果字典
    results = {
        "skin_type": skin_type,
        "moisture_level": moisture_level,
        "oil_level": oil_level,
        "pigmentation_level": pigmentation_level,
        "sensitivity_level": sensitivity_level,
        "recommendations": recommendations
    }
    
    return results

# 提供前端静态文件
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# 执行分析
@app.route('/analyze', methods=['POST'])
def analyze():
    # 检查请求中是否有文件
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': '没有文件部分'}), 400
    
    file = request.files['image']
    
    # 如果用户没有选择文件，浏览器可能会提交一个空文件
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    # 检查文件是否有效
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        filename = secure_filename(f"{uuid.uuid4()}.{file.filename.rsplit('.', 1)[1].lower()}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 保存文件
        file.save(file_path)
        
        try:
            # 分析皮肤
            results = analyze_skin(file_path)
            
            return jsonify({
                'success': True,
                'results': results
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'分析过程出错: {str(e)}'
            }), 500
    else:
        return jsonify({'success': False, 'message': '不支持的文件类型'}), 400

# 运行应用
if __name__ == '__main__':
    app.run(debug=True)    