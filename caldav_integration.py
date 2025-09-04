#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import hashlib
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RadicaleIntegration:
    """Radicale CalDAV服务集成"""
    
    def __init__(self, radicale_config_path: str = "/config"):
        self.config_path = radicale_config_path
        self.users_file = os.path.join(radicale_config_path, "users")
        
    def create_user(self, username: str, password: str) -> bool:
        """创建Radicale用户"""
        try:
            # 生成bcrypt密码哈希
            hashed_password = self._hash_password_bcrypt(password)
            
            # 读取现有用户文件
            users = self._read_users_file()
            
            # 添加新用户
            users[username] = hashed_password
            
            # 写回用户文件
            self._write_users_file(users)
            
            logger.info(f"用户 {username} 创建成功")
            return True
            
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """删除Radicale用户"""
        try:
            users = self._read_users_file()
            if username in users:
                del users[username]
                self._write_users_file(users)
                logger.info(f"用户 {username} 删除成功")
                return True
            return False
            
        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            return False
    
    def upload_calendar(self, username: str, calendar_name: str, ics_content: str) -> bool:
        """上传日历到Radicale"""
        try:
            # 创建用户目录
            user_dir = os.path.join("/data", username)
            os.makedirs(user_dir, exist_ok=True)
            
            # 创建日历文件
            calendar_file = os.path.join(user_dir, f"{calendar_name}.ics")
            with open(calendar_file, 'w', encoding='utf-8') as f:
                f.write(ics_content)
            
            logger.info(f"日历 {calendar_name} 上传成功")
            return True
            
        except Exception as e:
            logger.error(f"上传日历失败: {str(e)}")
            return False
    
    def _hash_password_bcrypt(self, password: str) -> str:
        """使用bcrypt哈希密码"""
        try:
            import bcrypt
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except ImportError:
            # 如果没有bcrypt，使用htpasswd命令
            return self._hash_password_htpasswd(password)
    
    def _hash_password_htpasswd(self, password: str) -> str:
        """使用htpasswd命令哈希密码"""
        try:
            # 使用htpasswd命令生成bcrypt哈希
            result = subprocess.run([
                'htpasswd', '-nbB', 'temp_user', password
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # 提取哈希部分
                return result.stdout.split(':')[1].strip()
            else:
                raise Exception(f"htpasswd命令失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"密码哈希失败: {str(e)}")
            # 降级到简单的MD5哈希（不推荐用于生产环境）
            return hashlib.md5(password.encode()).hexdigest()
    
    def _read_users_file(self) -> Dict[str, str]:
        """读取用户文件"""
        users = {}
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        username, password_hash = line.split(':', 1)
                        users[username] = password_hash
        return users
    
    def _write_users_file(self, users: Dict[str, str]) -> None:
        """写入用户文件"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        with open(self.users_file, 'w', encoding='utf-8') as f:
            for username, password_hash in users.items():
                f.write(f"{username}:{password_hash}\n")

# 全局实例
radicale_integration = RadicaleIntegration()
