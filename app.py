#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

# 导入日历生成器模块
from calendar_generator import BJTUCalendarGenerator
from caldav_integration import radicale_integration

app = Flask(__name__)
CORS(app)

# 配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# 确保上传和输出目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'html', 'htm'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传课表HTML文件并生成ICS文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '只支持HTML文件'}), 400
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        logger.info(f"文件已上传: {file_path}")
        
        # 生成ICS文件
        try:
            generator = BJTUCalendarGenerator()
            ics_content = generator.generate_from_html(file_path)
            
            # 保存ICS文件
            ics_filename = f"{uuid.uuid4()}.ics"
            ics_path = os.path.join(app.config['OUTPUT_FOLDER'], ics_filename)
            
            with open(ics_path, 'w', encoding='utf-8') as f:
                f.write(ics_content)
            
            logger.info(f"ICS文件已生成: {ics_path}")
            
            # 清理上传的HTML文件
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'message': '课表解析成功',
                'ics_file': ics_filename,
                'download_url': f'/api/download/{ics_filename}'
            })
            
        except Exception as e:
            logger.error(f"生成ICS文件时出错: {str(e)}")
            # 清理上传的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': f'解析课表失败: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"上传文件时出错: {str(e)}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """下载ICS文件"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name='课表.ics',
            mimetype='text/calendar'
        )
    except Exception as e:
        logger.error(f"下载文件时出错: {str(e)}")
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/api/caldav/create', methods=['POST'])
def create_caldav_account():
    """创建CalDAV账户"""
    try:
        data = request.get_json()
        if not data or 'ics_file' not in data:
            return jsonify({'error': '缺少ICS文件参数'}), 400
        
        ics_filename = data['ics_file']
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], ics_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'ICS文件不存在'}), 404
        
        # 生成CalDAV账户信息
        account_id = str(uuid.uuid4())
        username = f"user_{account_id[:8]}"
        password = str(uuid.uuid4())[:12]
        
        # 读取ICS文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            ics_content = f.read()
        
        # 创建Radicale用户
        if not radicale_integration.create_user(username, password):
            return jsonify({'error': '创建CalDAV用户失败'}), 500
        
        # 上传日历到Radicale
        calendar_name = '课表'
        if not radicale_integration.upload_calendar(username, calendar_name, ics_content):
            return jsonify({'error': '上传日历失败'}), 500
        
        # 获取服务器URL（从环境变量或使用默认值）
        server_url = os.environ.get('RADICALE_SERVER_URL', 'http://localhost:5232')
        
        caldav_info = {
            'account_id': account_id,
            'username': username,
            'password': password,
            'server_url': server_url,
            'calendar_url': f'{server_url}/{username}/',
            'setup_instructions': {
                'ios': [
                    '打开"设置" > "日历" > "账户" > "添加账户"',
                    '选择"其他" > "CalDAV账户"',
                    f'服务器: {server_url.replace("http://", "").replace("https://", "")}',
                    f'用户名: {username}',
                    f'密码: {password}',
                    '点击"下一步"完成设置'
                ],
                'android': [
                    '打开日历应用',
                    '添加账户 > CalDAV',
                    f'服务器: {server_url.replace("http://", "").replace("https://", "")}',
                    f'用户名: {username}',
                    f'密码: {password}',
                    '保存设置'
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'caldav_account': caldav_info
        })
        
    except Exception as e:
        logger.error(f"创建CalDAV账户时出错: {str(e)}")
        return jsonify({'error': f'创建账户失败: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
