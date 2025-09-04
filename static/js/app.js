// 应用主要JavaScript功能

let currentIcsFile = null;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
    initializeUploadArea();
    initializeFileInput();
});

// 初始化上传区域
function initializeUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // 拖拽事件
    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // 点击上传区域
    uploadArea.addEventListener('click', function () {
        fileInput.click();
    });
}

// 初始化文件输入
function initializeFileInput() {
    const fileInput = document.getElementById('fileInput');

    fileInput.addEventListener('change', function (e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });
}

// 处理文件上传
function handleFile(file) {
    // 验证文件类型
    if (!file.name.toLowerCase().match(/\.(html|htm)$/)) {
        showAlert('请选择HTML文件', 'danger');
        return;
    }

    // 验证文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showAlert('文件大小不能超过16MB', 'danger');
        return;
    }

    uploadFile(file);
}

// 上传文件
function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    // 显示进度条
    showProgress();

    // 发送请求
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            hideProgress();

            if (data.success) {
                currentIcsFile = data.ics_file;
                showResult(data.message, data.download_url);
            } else {
                showAlert(data.error || '上传失败', 'danger');
            }
        })
        .catch(error => {
            hideProgress();
            console.error('上传错误:', error);
            showAlert('上传失败: ' + error.message, 'danger');
        });
}

// 显示进度条
function showProgress() {
    document.getElementById('uploadProgress').style.display = 'block';
    document.getElementById('resultArea').style.display = 'none';
}

// 隐藏进度条
function hideProgress() {
    document.getElementById('uploadProgress').style.display = 'none';
}

// 显示结果
function showResult(message, downloadUrl) {
    document.getElementById('resultMessage').textContent = message;
    document.getElementById('resultArea').style.display = 'block';

    // 设置下载按钮
    const downloadBtn = document.getElementById('downloadBtn');
    downloadBtn.onclick = function () {
        window.open(downloadUrl, '_blank');
    };

    // 设置CalDAV按钮
    const caldavBtn = document.getElementById('caldavBtn');
    caldavBtn.onclick = function () {
        createCalDAVAccount();
    };
}

// 创建CalDAV账户
function createCalDAVAccount() {
    if (!currentIcsFile) {
        showAlert('请先上传并处理课表文件', 'warning');
        return;
    }

    fetch('/api/caldav/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            ics_file: currentIcsFile
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showCalDAVModal(data.caldav_account);
            } else {
                showAlert(data.error || '创建CalDAV账户失败', 'danger');
            }
        })
        .catch(error => {
            console.error('创建CalDAV账户错误:', error);
            showAlert('创建CalDAV账户失败: ' + error.message, 'danger');
        });
}

// 显示CalDAV设置模态框
function showCalDAVModal(accountInfo) {
    // 填充账户信息
    document.getElementById('serverUrl').value = accountInfo.server_url;
    document.getElementById('username').value = accountInfo.username;
    document.getElementById('password').value = accountInfo.password;
    document.getElementById('calendarUrl').value = accountInfo.calendar_url;

    // 填充iOS设置步骤
    const iosSteps = document.getElementById('iosSteps');
    iosSteps.innerHTML = '';
    accountInfo.setup_instructions.ios.forEach(step => {
        const li = document.createElement('li');
        li.textContent = step;
        iosSteps.appendChild(li);
    });

    // 填充Android设置步骤
    const androidSteps = document.getElementById('androidSteps');
    androidSteps.innerHTML = '';
    accountInfo.setup_instructions.android.forEach(step => {
        const li = document.createElement('li');
        li.textContent = step;
        androidSteps.appendChild(li);
    });

    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('caldavModal'));
    modal.show();
}

// 切换密码显示
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('passwordToggleIcon');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.className = 'bi bi-eye-slash';
    } else {
        passwordInput.type = 'password';
        toggleIcon.className = 'bi bi-eye';
    }
}

// 复制账户信息
function copyAccountInfo() {
    const accountInfo = {
        server: document.getElementById('serverUrl').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        calendarUrl: document.getElementById('calendarUrl').value
    };

    const text = `服务器: ${accountInfo.server}\n用户名: ${accountInfo.username}\n密码: ${accountInfo.password}\n日历URL: ${accountInfo.calendarUrl}`;

    navigator.clipboard.writeText(text).then(function () {
        showAlert('账户信息已复制到剪贴板', 'success');
    }).catch(function () {
        // 降级处理
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showAlert('账户信息已复制到剪贴板', 'success');
    });
}

// 显示警告信息
function showAlert(message, type) {
    // 移除现有的警告
    const existingAlert = document.querySelector('.alert-temp');
    if (existingAlert) {
        existingAlert.remove();
    }

    // 创建新的警告
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show alert-temp`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // 插入到页面顶部
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    // 自动隐藏
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}
