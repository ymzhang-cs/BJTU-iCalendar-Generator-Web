#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的测试脚本，用于验证应用功能
"""

import os
import tempfile
from calendar_generator import BJTUCalendarGenerator

def test_calendar_generator():
    """测试日历生成器"""
    print("测试日历生成器...")
    
    # 创建测试HTML内容（使用BJTU教务系统格式）
    test_html = """
    <html>
    <body>
        <table class="table table-bordered">
            <tr>
                <th>时间</th>
                <th>星期一</th>
                <th>星期二</th>
                <th>星期三</th>
                <th>星期四</th>
                <th>星期五</th>
            </tr>
            <tr>
                <td>第1节</td>
                <td>
                    <div>
                        <span>
                            M402004B [03] <br />
                            软件工程<br />
                        </span>
                        <div style="max-width:120px;">
                            第01-16周
                            <i>魏名元</i>
                        </div>
                        <span class="text-muted">海淀西校区, 逸夫教学楼, YF415</span>
                    </div>
                </td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td>第2节</td>
                <td></td>
                <td>
                    <div>
                        <span>
                            C108005B [02] <br />
                            概率论与数理统计(B)<br />
                        </span>
                        <div style="max-width:120px;">
                            第02, 04, 06, 08, 10, 12, 14, 16周
                            <i>刘玉婷</i>
                        </div>
                        <span class="text-muted">海淀西校区, 思源楼, SY207</span>
                    </div>
                </td>
                <td></td>
                <td></td>
                <td></td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(test_html)
        temp_file = f.name
    
    try:
        # 测试生成器
        generator = BJTUCalendarGenerator()
        ics_content = generator.generate_from_html(temp_file)
        
        print("✅ 日历生成器测试通过")
        print(f"生成的ICS内容长度: {len(ics_content)} 字符")
        
        # 保存测试输出
        with open('test_output.ics', 'w', encoding='utf-8') as f:
            f.write(ics_content)
        print("✅ 测试输出已保存到 test_output.ics")
        
    except Exception as e:
        print(f"❌ 日历生成器测试失败: {str(e)}")
    finally:
        # 清理临时文件
        os.unlink(temp_file)

def test_flask_app():
    """测试Flask应用"""
    print("\n测试Flask应用...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # 测试健康检查
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ 健康检查测试通过")
            else:
                print(f"❌ 健康检查测试失败: {response.status_code}")
            
            # 测试主页
            response = client.get('/')
            if response.status_code == 200:
                print("✅ 主页测试通过")
            else:
                print(f"❌ 主页测试失败: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Flask应用测试失败: {str(e)}")

if __name__ == '__main__':
    print("开始测试...")
    test_calendar_generator()
    test_flask_app()
    print("\n测试完成！")
