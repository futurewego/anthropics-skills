# Architect Skills

Java 架构师技术选型与方案设计 Skill。

## 概述

本 skill 专为 Java 架构师设计,协助进行:
- 技术选型与方案对比
- 架构方案设计
- POC 可行性验证
- 技术决策文档输出

## 技术栈

基于以下技术栈:
- Spring Boot 3.2.4
- Spring Cloud 2023.0.1
- JDK 21
- Redis (Redisson 3.11.6)
- Apollo 2.2.0
- MyBatis Plus 3.3.2

## 使用方式

1. 在 Claude 中上传 `java-architect.skill` 文件
2. 启用 skill
3. 向 Claude 描述技术需求,如:
   - "评估 RabbitMQ vs Kafka 消息队列方案"
   - "设计微服务拆分方案"
   - "选择分布式缓存方案"

## 目录结构

```
architect-skills/
├── SKILL.md                          # Skill 主文件
└── references/                       # 参考文档
    ├── tech_stack.md                 # 技术栈详情
    ├── document_template.md          # 方案文档模板
    ├── poc_templates.md              # POC 代码模板
    └── architecture_principles.md    # 架构设计理论
```

## 输出示例

Claude 会生成包含以下内容的技术方案文档:
- 背景与目标
- 方案对比分析(多维度表格)
- 推荐方案(含理论依据、架构图)
- POC 验证结果
- 实施路径与风险评估
- 资源评估(工作量、成本)

## 版本

- v1.0 - 初始版本
- 支持 Spring Boot 3.x / JDK 21
