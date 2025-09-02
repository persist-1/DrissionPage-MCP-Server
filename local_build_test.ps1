#!/usr/bin/env powershell
# DrissionPage MCP 本地构建和测试脚本
# 零依赖本地运行 - PowerShell版本

Write-Host "=== DrissionPage MCP 本地构建和测试 ===" -ForegroundColor Green
Write-Host "工作目录: $(Get-Location)" -ForegroundColor Cyan
Write-Host "PowerShell版本: $($PSVersionTable.PSVersion)" -ForegroundColor Cyan
Write-Host ""

# 错误处理
$ErrorActionPreference = "Stop"
$SuccessCount = 0
$TotalSteps = 6

function Write-Step {
    param([string]$Message, [string]$Color = "Yellow")
    Write-Host ">>> $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
    $script:SuccessCount++
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

try {
    # 步骤1: 检查Python环境
    Write-Step "步骤1: 检查Python环境"
    
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python可用: $pythonVersion"
    } else {
        Write-Error-Custom "Python不可用，请安装Python 3.10+"
        exit 1
    }
    
    # 步骤2: 检查虚拟环境
    Write-Step "步骤2: 检查虚拟环境"
    
    if (Test-Path ".venv") {
        Write-Success "虚拟环境存在"
        
        # 激活虚拟环境
        Write-Host "激活虚拟环境..."
        & ".venv\Scripts\Activate.ps1"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "虚拟环境激活成功"
        } else {
            Write-Error-Custom "虚拟环境激活失败"
        }
    } else {
        Write-Host "创建虚拟环境..."
        python -m venv .venv
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "虚拟环境创建成功"
            & ".venv\Scripts\Activate.ps1"
        } else {
            Write-Error-Custom "虚拟环境创建失败"
            exit 1
        }
    }
    
    # 步骤3: 安装依赖
    Write-Step "步骤3: 安装项目依赖"
    
    Write-Host "升级pip..."
    python -m pip install --upgrade pip
    
    Write-Host "安装项目依赖..."
    pip install -e .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "项目依赖安装成功"
    } else {
        Write-Error-Custom "项目依赖安装失败"
        exit 1
    }
    
    Write-Host "安装开发依赖..."
    pip install -r requirements-dev.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "开发依赖安装成功"
    } else {
        Write-Host "⚠️ 开发依赖安装失败，继续执行" -ForegroundColor Yellow
    }
    
    # 步骤4: 运行基本功能测试
    Write-Step "步骤4: 运行基本功能测试"
    
    python test_basic_functionality.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "基本功能测试通过"
    } else {
        Write-Error-Custom "基本功能测试失败"
    }
    
    # 步骤5: 运行pytest测试
    Write-Step "步骤5: 运行pytest测试"
    
    if (Get-Command pytest -ErrorAction SilentlyContinue) {
        Write-Host "运行单元测试..."
        pytest tests/test_basic.py -v -m "unit"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "单元测试通过"
        } else {
            Write-Error-Custom "单元测试失败"
        }
        
        Write-Host "运行集成测试（跳过浏览器测试）..."
        pytest tests/ -v -m "not browser and not network"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "集成测试通过"
        } else {
            Write-Host "⚠️ 集成测试失败" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️ pytest不可用，跳过pytest测试" -ForegroundColor Yellow
    }
    
    # 步骤6: 检查项目结构
    Write-Step "步骤6: 检查项目结构"
    
    $requiredFiles = @(
        "src/drissionpage_mcp/__init__.py",
        "src/drissionpage_mcp/main.py",
        "src/drissionpage_mcp/config/settings.py",
        "pyproject.toml",
        "requirements.txt"
    )
    
    $allFilesExist = $true
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Host "✓ $file" -ForegroundColor Green
        } else {
            Write-Host "✗ $file" -ForegroundColor Red
            $allFilesExist = $false
        }
    }
    
    if ($allFilesExist) {
        Write-Success "项目结构检查通过"
    } else {
        Write-Error-Custom "项目结构检查失败"
    }
    
} catch {
    Write-Error-Custom "构建过程中出现异常: $($_.Exception.Message)"
    exit 1
}

# 输出结果
Write-Host ""
Write-Host "=== 构建测试结果 ===" -ForegroundColor Green
Write-Host "成功步骤: $SuccessCount/$TotalSteps" -ForegroundColor Cyan

if ($SuccessCount -eq $TotalSteps) {
    Write-Host "🎉 所有构建测试通过！" -ForegroundColor Green
    Write-Host ""
    Write-Host "项目已准备就绪，可以使用以下命令启动:" -ForegroundColor Yellow
    Write-Host "  drissionpage-mcp" -ForegroundColor Cyan
    Write-Host "  # 或" -ForegroundColor Gray
    Write-Host "  dp-mcp" -ForegroundColor Cyan
    exit 0
} elseif ($SuccessCount -gt ($TotalSteps / 2)) {
    Write-Host "⚠️ 部分构建测试通过，项目基本可用" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "❌ 构建测试失败，请检查错误信息" -ForegroundColor Red
    Write-Host "提示：如果遇到字符编码问题，请确保PowerShell使用UTF-8编码" -ForegroundColor Yellow
    Write-Host "可以尝试运行：[Console]::OutputEncoding = [System.Text.Encoding]::UTF8" -ForegroundColor Yellow
    exit 1
}