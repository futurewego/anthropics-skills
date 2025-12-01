---
name: jdk8-to-jdk21-upgrade
description: Automated JDK 8 to JDK 21 upgrade assistant for Java projects. Use this skill when users request to upgrade Java projects from JDK 8 to JDK 21, migrate Spring Boot 2.x to 3.x, convert javax.* to jakarta.*, update Maven dependencies, or modernize Java enterprise applications. Handles pom.xml modification, source code migration, dependency version upgrades, and compilation validation.
---

# JDK 8 to JDK 21 Upgrade Assistant

自动化Java项目从JDK 8升级到JDK 21的完整流程，包括Spring Boot 3.x迁移、Jakarta EE命名空间转换、依赖升级和代码兼容性修复。

## 快速开始

当用户请求升级项目时，执行以下流程：

### 阶段1: 项目分析

```bash
python scripts/analyze_project.py <project_path>
```

分析项目结构、依赖版本、代码使用情况，生成升级评估报告。

### 阶段2: 依赖配置升级

```bash
python scripts/upgrade_pom.py <project_path>/pom.xml
```

升级Maven配置到JDK 21兼容版本，使用企业统一的ym-build-parent。

### 阶段3: 源代码迁移

```bash
python scripts/migrate_imports.py <project_path>/src
```

批量转换javax.*到jakarta.*，修复过时的API调用。

### 阶段4: 编译验证

```bash
bash scripts/validate_upgrade.sh <project_path>
```

运行Maven编译和测试，验证升级结果。

### 阶段5: 生成报告

输出升级报告，包含：
- 已完成的自动化修改
- 需要人工检查的问题
- 回滚方案
- 后续优化建议

## 核心工作流程

### 升级决策树

```
用户请求升级项目
    ↓
检查项目类型
    ├─ Spring Boot项目 → 执行完整升级流程
    ├─ 普通Maven项目 → 执行基础升级流程
    └─ 多模块项目 → 逐模块升级
    ↓
分析当前状态
    ├─ 识别JDK版本
    ├─ 识别Spring版本
    ├─ 分析依赖树
    └─ 扫描代码使用
    ↓
生成升级计划
    ├─ 依赖升级清单
    ├─ 代码修改清单
    └─ 风险评估
    ↓
执行自动化升级
    ├─ 备份原始文件
    ├─ 修改pom.xml
    ├─ 迁移源代码
    └─ 运行编译测试
    ↓
生成升级报告
    ├─ 成功项清单
    ├─ 需人工处理项
    └─ 回滚指南
```

## 关键配置说明

### Maven Parent选择

根据项目情况选择合适的parent配置：

**方式1: 继承ym-build-parent（推荐）**
- 适用于新项目或完全升级的项目
- 自动获得JDK 21配置和依赖管理
- 参考: `assets/ym-build-parent-template.xml`

**方式2: 仅引入BOM**
- 适用于已有parent的项目
- 仅引入依赖版本管理
- 需手动配置compiler plugin

### 命名空间迁移规则

详见: `references/javax_jakarta_mapping.json`

核心映射：
- javax.servlet → jakarta.servlet
- javax.persistence → jakarta.persistence
- javax.validation → jakarta.validation
- javax.annotation → jakarta.annotation
- javax.transaction → jakarta.transaction

### 依赖版本策略

详见: `references/dependency_versions.json`

核心依赖升级：
- Spring Boot: 2.x → 3.2.4+
- Spring Cloud: Hoxton/2021.0.x → 2023.0.1+
- Lombok: 1.18.12- → 1.18.36+
- MyBatis-Plus: 3.3.x → 3.5.5+
- Redisson: 3.11.x → 3.27.2+

## 脚本使用说明

### scripts/analyze_project.py

**功能**: 全面分析项目，生成升级评估报告

**用法**:
```bash
python scripts/analyze_project.py /path/to/project
```

**输出**:
- 项目结构分析
- 当前版本信息
- javax使用统计
- 风险评估
- 预估工作量

### scripts/upgrade_pom.py

**功能**: 自动升级pom.xml配置

**用法**:
```bash
python scripts/upgrade_pom.py /path/to/pom.xml [--use-parent] [--backup]
```

**选项**:
- `--use-parent`: 使用ym-build-parent继承方式
- `--backup`: 备份原文件（默认启用）

**操作**:
- 修改parent为ym-build-parent或添加BOM
- 升级Spring Boot/Cloud版本
- 更新所有依赖版本
- 添加compiler plugin配置（如需要）

### scripts/migrate_imports.py

**功能**: 批量迁移Java源代码的import语句

**用法**:
```bash
python scripts/migrate_imports.py /path/to/src [--dry-run]
```

**选项**:
- `--dry-run`: 预览修改但不实际执行

**操作**:
- javax.* → jakarta.*
- 处理import冲突
- 生成修改报告

### scripts/fix_deprecated_apis.py

**功能**: 检测和修复过时的API调用

**用法**:
```bash
python scripts/fix_deprecated_apis.py /path/to/src
```

**检测项**:
- sun.misc.Unsafe使用
- com.sun.* 内部API
- 过时的Spring API
- 其他不兼容代码

**输出**:
- 可自动修复的项
- 需人工处理的项
- 修复建议

### scripts/validate_upgrade.sh

**功能**: 编译和测试验证

**用法**:
```bash
bash scripts/validate_upgrade.sh /path/to/project
```

**执行**:
- mvn clean compile
- mvn dependency:tree (分析依赖冲突)
- mvn test (可选)
- 生成验证报告

## 参考文档

### references/upgrade_guide.md

完整的升级指南，包含：
- 升级背景和收益
- 技术架构调整
- 分步骤执行指南
- 常见问题解决方案
- 回滚方案

### references/dependency_versions.json

依赖版本映射表，包含：
- JDK 8版本 → JDK 21版本映射
- 升级原因说明
- 特殊注意事项

### references/javax_jakarta_mapping.json

Jakarta EE命名空间映射表，包含：
- 完整的包名映射
- 注解映射
- 类名变更

### references/troubleshooting.md

问题排查指南，包含：
- 编译错误解决方案
- 运行时问题处理
- 性能问题排查
- 兼容性问题处理

## 企业级资源

### assets/ym-build-parent-template.xml

企业统一的Maven parent配置模板，包含：
- JDK 21编译配置
- Lombok + MapStruct注解处理器配置
- Spring Boot插件配置
- 标准的pluginManagement

### assets/ym-dependencies-bom-template.xml

企业BOM配置模板，用于已有parent的项目。

### assets/compiler-config-template.xml

独立的compiler plugin配置，用于不继承parent的场景。

## 执行注意事项

### 自动备份

所有修改操作都会自动创建备份：
- `pom.xml.backup-{timestamp}`
- `src.backup-{timestamp}/`

### 渐进式升级

对于大型项目，建议分阶段执行：
1. 先升级pom.xml，验证编译
2. 再迁移源代码，验证功能
3. 最后优化和测试

### 多模块项目处理

自动识别多模块项目，提供两种模式：
- 一次性全部升级
- 逐模块升级（推荐）

### 回滚机制

升级失败时，提供快速回滚：
```bash
python scripts/rollback.py /path/to/project
```

## 输出格式

升级完成后，生成结构化报告：

```markdown
# 升级报告 - {project_name}

## 执行摘要
- 升级状态: ✅ 成功 / ⚠️ 部分成功 / ❌ 失败
- 开始时间: {timestamp}
- 完成时间: {timestamp}
- 总耗时: {duration}

## 已完成的修改
✅ pom.xml升级 (1个文件)
✅ 源代码迁移 (23个文件)
✅ 编译验证 (成功)

## 需要人工检查
⚠️ UserService.java:45 - 使用了sun.misc.Unsafe
⚠️ 集成测试需要手动验证
⚠️ Redis配置可能需要调整

## 回滚方案
备份位置: {backup_path}
回滚命令: python scripts/rollback.py {project_path}

## 后续建议
1. 运行完整的集成测试
2. 检查日志中的WARN信息
3. 考虑使用JDK 21新特性优化代码
```

## 高级特性

### 批量升级

支持一次性升级多个项目：
```bash
python scripts/batch_upgrade.py --projects project1,project2,project3
```

### 自定义规则

支持通过配置文件自定义升级规则：
- `config/custom_mappings.json` - 自定义命名空间映射
- `config/custom_versions.json` - 自定义依赖版本
- `config/exclude_patterns.txt` - 排除特定文件

### CI/CD集成

提供Jenkins/GitLab CI配置示例：
- `assets/Jenkinsfile.upgrade`
- `assets/.gitlab-ci-upgrade.yml`

## 限制和约束

### 不支持的场景

- Gradle项目（仅支持Maven）
- JDK 8以下版本的升级
- 非标准项目结构

### 需要人工处理的情况

- 自定义框架的兼容性
- 复杂的反射代码
- JNI调用
- 字节码操作相关代码

## 版本历史

- v1.0.0 (2025-11-28) - 初始版本，支持基本升级流程
