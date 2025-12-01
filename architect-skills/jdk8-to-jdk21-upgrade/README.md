# JDK 8 to JDK 21 Upgrade Skill

自动化Java项目从JDK 8升级到JDK 21的完整解决方案。

## 📋 功能概述

这个skill提供了完整的JDK升级自动化工具链，包括:

- ✅ 项目分析和评估
- ✅ Maven配置自动升级
- ✅ 源代码自动迁移(javax → jakarta)
- ✅ 编译和测试验证
- ✅ 问题排查指南

## 🚀 快速开始

在项目根目录执行:

```bash
# 1. 分析项目
python scripts/analyze_project.py .

# 2. 升级pom.xml
python scripts/upgrade_pom.py pom.xml --use-parent --backup

# 3. 迁移源代码
python scripts/migrate_imports.py src

# 4. 验证升级
bash scripts/validate_upgrade.sh .
```

## 📁 目录结构

```
jdk8-to-jdk21-upgrade/
├── SKILL.md                          # Skill核心文档
├── scripts/                          # 自动化脚本
│   ├── analyze_project.py            # 项目分析
│   ├── upgrade_pom.py                # POM升级
│   ├── migrate_imports.py            # import迁移
│   └── validate_upgrade.sh           # 验证脚本
├── references/                       # 参考文档
│   ├── upgrade_guide.md              # 完整升级指南
│   ├── dependency_versions.json      # 依赖版本映射
│   ├── javax_jakarta_mapping.json    # 命名空间映射
│   └── troubleshooting.md            # 问题排查指南
└── assets/                           # 模板资源
    ├── ym-build-parent-template.xml  # 企业Parent模板
    └── ym-dependencies-bom-template.xml  # 企业BOM模板
```

## 💡 使用场景

### 场景1: 单模块Spring Boot项目

```bash
cd /path/to/your-project
python /path/to/skill/scripts/analyze_project.py .
python /path/to/skill/scripts/upgrade_pom.py pom.xml --use-parent
python /path/to/skill/scripts/migrate_imports.py src
bash /path/to/skill/scripts/validate_upgrade.sh .
```

### 场景2: 多模块Maven项目

```bash
# 先升级父POM
python scripts/upgrade_pom.py pom.xml --use-parent

# 然后逐个模块升级
for module in module1 module2 module3; do
    python scripts/migrate_imports.py $module/src
done

# 统一验证
bash scripts/validate_upgrade.sh .
```

### 场景3: 已有parent的项目

```bash
# 使用BOM方式(不改变parent)
python scripts/upgrade_pom.py pom.xml --backup

# 其他步骤相同
python scripts/migrate_imports.py src
bash scripts/validate_upgrade.sh .
```

## 📊 脚本详解

### analyze_project.py

**功能**: 全面分析项目,生成升级评估报告

**输出**:
- `upgrade_analysis_report.md` - Markdown格式报告
- `upgrade_analysis.json` - JSON格式数据

**报告内容**:
- 项目结构分析
- 当前版本信息
- javax使用统计
- 风险评估
- 工作量估算

### upgrade_pom.py

**功能**: 自动升级pom.xml配置

**选项**:
- `--use-parent`: 使用ym-build-parent继承方式(推荐)
- `--no-backup`: 不创建备份文件

**操作**:
- 修改parent或添加BOM
- 升级Spring Boot/Cloud版本
- 更新所有依赖版本
- 配置compiler plugin

### migrate_imports.py

**功能**: 批量迁移Java源代码的import语句

**选项**:
- `--dry-run`: 预览模式,不实际修改文件

**操作**:
- javax.* → jakarta.*
- 处理import冲突
- 生成修改统计

### validate_upgrade.sh

**功能**: 编译和测试验证

**参数**:
- 参数1: 项目路径(默认当前目录)
- 参数2: 是否运行测试(true/false,默认false)

**执行**:
- 检查JDK版本
- Maven编译
- 依赖树分析
- 可选的测试运行

## 🎯 核心特性

### 1. 智能分析

自动识别:
- 项目类型(单模块/多模块)
- 框架版本(Spring Boot/Cloud)
- javax命名空间使用情况
- 过时API调用
- 升级风险点

### 2. 安全备份

所有修改前自动备份:
- `pom.xml.backup-{timestamp}`
- 备份记录在验证报告中

### 3. 渐进式升级

支持分阶段执行:
1. 先升级配置,验证编译
2. 再迁移代码,验证功能
3. 最后优化和测试

### 4. 详细报告

生成多份报告:
- 项目分析报告
- 迁移统计报告
- 验证结果报告
- 依赖树分析

## ⚠️ 注意事项

### 升级前准备

- [ ] 确保代码已提交
- [ ] 创建备份分支
- [ ] 确认JDK 21已安装
- [ ] Maven版本 >= 3.8.1

### 不支持场景

- ❌ Gradle项目
- ❌ JDK 8以下版本
- ❌ 非标准项目结构

### 需要人工处理

- 自定义框架兼容性
- 复杂反射代码
- JNI调用
- 字节码操作

## 📚 参考资源

### 内置文档

- `references/upgrade_guide.md` - 完整升级指南
- `references/troubleshooting.md` - 问题排查
- `references/dependency_versions.json` - 版本映射
- `references/javax_jakarta_mapping.json` - 命名空间映射

### 外部资源

- [Spring Boot 3.x Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)
- [Jakarta EE Migration](https://jakarta.ee/resources/migration-guide/)
- [JDK 21 Release Notes](https://www.oracle.com/java/technologies/javase/21-relnote-issues.html)

## 🐛 问题反馈

遇到问题时:

1. 查看 `references/troubleshooting.md`
2. 检查生成的报告文件
3. 联系架构组支持

## 📝 更新日志

### v1.0.0 (2025-11-28)

- ✅ 初始版本发布
- ✅ 支持项目分析
- ✅ 支持POM自动升级
- ✅ 支持源代码迁移
- ✅ 支持编译验证

---

**维护者**: 架构组
**最后更新**: 2025-11-28
