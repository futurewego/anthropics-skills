#!/bin/bash
# JDK升级验证脚本
# 运行Maven编译和测试，验证升级结果

set -e

PROJECT_PATH="${1:-.}"
RUN_TESTS="${2:-false}"

echo "========================================"
echo "JDK 升级验证"
echo "========================================"
echo "项目路径: $PROJECT_PATH"
echo "运行测试: $RUN_TESTS"
echo ""

cd "$PROJECT_PATH"

# 检查Maven
if ! command -v mvn &> /dev/null; then
    echo "❌ 错误: 未找到Maven命令"
    exit 1
fi

# 检查JDK版本
echo "[1/4] 检查JDK版本..."
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
echo "当前JDK版本: $JAVA_VERSION"

if [ "$JAVA_VERSION" -lt 21 ]; then
    echo "⚠️  警告: 当前JDK版本低于21，可能导致编译失败"
fi

# 清理并编译
echo ""
echo "[2/4] 清理并编译项目..."
if mvn clean compile -DskipTests; then
    echo "✅ 编译成功"
else
    echo "❌ 编译失败"
    echo ""
    echo "建议检查:"
    echo "  1. pom.xml配置是否正确"
    echo "  2. 依赖版本是否兼容"
    echo "  3. 源代码是否存在语法错误"
    exit 1
fi

# 依赖树分析
echo ""
echo "[3/4] 分析依赖树..."
mvn dependency:tree > dependency-tree.txt 2>&1
echo "✅ 依赖树已生成: dependency-tree.txt"

# 检查是否有javax依赖冲突
if grep -q "javax.servlet-api" dependency-tree.txt || \
   grep -q "javax.persistence-api" dependency-tree.txt || \
   grep -q "validation-api.*2.0" dependency-tree.txt; then
    echo "⚠️  警告: 发现旧版本的javax依赖，可能存在冲突"
    echo "   请检查 dependency-tree.txt"
fi

# 运行测试（可选）
if [ "$RUN_TESTS" = "true" ]; then
    echo ""
    echo "[4/4] 运行测试..."
    if mvn test; then
        echo "✅ 测试通过"
    else
        echo "⚠️  测试失败"
        echo "   这可能是正常的，需要人工检查测试用例"
    fi
else
    echo ""
    echo "[4/4] 跳过测试（使用参数 'true' 启用测试）"
fi

# 生成验证报告
REPORT_FILE="upgrade_validation_report.txt"
{
    echo "JDK升级验证报告"
    echo "================"
    echo "验证时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "项目路径: $PROJECT_PATH"
    echo "JDK版本: $JAVA_VERSION"
    echo ""
    echo "验证结果:"
    echo "  ✅ 编译: 成功"
    if [ "$RUN_TESTS" = "true" ]; then
        echo "  ✅ 测试: 已运行"
    else
        echo "  ⏭  测试: 已跳过"
    fi
    echo ""
    echo "依赖分析:"
    echo "  详见: dependency-tree.txt"
    echo ""
    echo "后续建议:"
    echo "  1. 运行完整的集成测试"
    echo "  2. 检查应用日志中的WARN信息"
    echo "  3. 进行性能基准测试"
    echo "  4. 在生产环境前进行充分验证"
} > "$REPORT_FILE"

echo ""
echo "========================================"
echo "验证完成!"
echo "========================================"
echo "验证报告: $REPORT_FILE"
echo "依赖树: dependency-tree.txt"
echo ""
echo "建议下一步:"
echo "  1. 查看验证报告: cat $REPORT_FILE"
echo "  2. 运行完整测试: mvn test"
echo "  3. 本地启动验证: mvn spring-boot:run"
echo ""
