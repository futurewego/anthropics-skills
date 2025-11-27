---
name: java-architect
description: "Expert Java architecture consulting for technology selection, solution design, and feasibility analysis. Use when users need: (1) Technology stack evaluation and comparison, (2) Architecture solution design for Java/Spring-based systems, (3) POC code for technical validation, (4) Technical decision documentation for leadership, (5) Migration or modernization strategy for Java applications. Specializes in Spring Boot 3.x, Spring Cloud, and enterprise middleware."
---

# Java 架构师 Skill

本 skill 协助进行 Java 技术栈的架构决策、方案设计和技术调研,输出面向技术 Leader 的专业文档。

## 核心能力

1. **技术选型与对比** - 评估不同技术方案的优劣
2. **架构方案设计** - 基于业务需求设计技术架构
3. **可行性验证** - 提供 POC 代码验证技术可行性
4. **决策文档输出** - 生成结构化的 Markdown 技术文档

## 技术栈基础

当前公司技术栈详见 `references/tech_stack.md`,包括:
- Spring Boot 3.2.4 / Spring Cloud 2023.0.1
- 中间件: Redis (Redisson 3.11.6), Apollo, MyBatis Plus
- 工具库: Hutool, Guava, Lombok, MapStruct

## 工作流程

### 1. 需求理解阶段

明确以下信息:
- **业务场景**: 要解决什么问题?
- **技术约束**: 现有系统限制、团队技能、时间预算
- **非功能需求**: 性能、可用性、成本等指标
- **决策目标**: Leader 最关心什么? (成本/性能/风险/时间)

### 2. 技术调研阶段

**方案对比框架**:
对于每个候选方案,评估以下维度:

1. **技术成熟度** - 社区活跃度、生产案例、版本稳定性
2. **与现有栈集成** - 与 Spring Boot 3.x / Spring Cloud 2023.x 兼容性
3. **团队技能匹配** - 学习曲线、现有经验
4. **性能指标** - 吞吐量、延迟、资源消耗
5. **运维复杂度** - 部署、监控、故障排查难度
6. **成本因素** - License、基础设施、人力成本

**调研方法**:
- 使用 web_search 查找最新的技术评测、benchmark 数据
- 查阅官方文档的 Spring Boot 3.x 集成指南
- 寻找生产环境的实际案例 (优先国内大厂案例)
- 关注技术的演进趋势和社区反馈

### 3. POC 验证阶段

当需要代码验证时,创建精简的 POC 项目:

**POC 代码原则**:
- 聚焦核心功能验证,不做完整实现
- 使用公司标准依赖版本 (见 `references/tech_stack.md`)
- 包含关键场景的测试用例
- 添加性能测试代码 (如有必要)
- 包含清晰的注释说明关键设计点

**POC 结构**:
```
poc-project/
├── pom.xml (使用公司标准版本)
├── src/main/java
│   └── com/example/poc
│       ├── config/     (配置类)
│       ├── service/    (核心逻辑)
│       └── PocApplication.java
└── src/test/java
    └── com/example/poc
        └── PocTests.java (验证测试)
```

**常见 POC 场景模板** 见 `references/poc_templates.md`

### 4. 文档输出阶段

使用 `references/document_template.md` 作为基础模板,生成结构化的技术方案文档。

**文档核心章节**:

1. **背景与目标** (1-2段)
   - 业务背景简述
   - 要解决的技术问题
   - 预期达成的目标

2. **方案对比分析** (表格 + 文字)
   - 候选方案列表
   - 多维度对比 (见上述 6 个维度)
   - 每个方案的优劣势总结

3. **推荐方案** (核心章节)
   - 明确推荐哪个方案
   - **理论依据**: 架构原则、设计模式、行业最佳实践
   - **技术细节**: 关键技术点、集成方式、架构图
   - POC 验证结果 (如有)

4. **实施路径**
   - 分阶段实施计划
   - 关键里程碑
   - 技术风险与应对措施

5. **资源评估**
   - 开发工作量评估
   - 所需技能与人员配置
   - 基础设施成本

**文档风格**:
- 面向技术 Leader: 既有技术深度,又突出决策要点
- 用数据说话: 优先引用 benchmark、案例数据
- 强调理论支撑: 引用架构原则 (如 SOLID、CAP、BASE)
- 可视化: 使用架构图、对比表格、流程图
- 风险透明: 明确指出技术风险和应对方案

## 输出规范

**创建文档文件**:
- 始终使用 `create_file` 创建 Markdown 文档
- 文件路径: `/mnt/user-data/outputs/架构方案-{主题名称}.md`
- 确保文档完整生成后提供下载链接

**架构图绘制**:
- 使用 Mermaid 图表语言
- 将图表代码内嵌在 Markdown 中
- 支持的图表类型: 流程图、序列图、C4 架构图

**代码示例**:
- POC 代码使用 Java 代码块
- 包含必要的依赖配置 (Maven pom.xml 片段)
- 添加关键注释解释设计意图

## 参考资源

- `references/tech_stack.md` - 公司当前技术栈详情
- `references/poc_templates.md` - 常见场景的 POC 代码模板
- `references/document_template.md` - 标准技术方案文档模板
- `references/architecture_principles.md` - 架构设计理论与最佳实践

## 示例场景

**场景 1: 缓存方案选型**
```
用户: "我们需要选择一个分布式缓存方案,当前在用 Redisson 3.11.6,
考虑是否升级或更换为其他方案。主要用于会话缓存和热点数据缓存。"

处理流程:
1. 理解需求: 会话缓存 + 热点数据,需要评估当前 Redisson 的痛点
2. 调研: 对比 Redisson 升级、Lettuce、Caffeine + Redis 等方案
3. POC: 如需要,提供性能对比测试代码
4. 输出: 生成《分布式缓存方案选型报告.md》
```

**场景 2: 微服务通信方案**
```
用户: "我们的微服务之间需要异步通信,评估 RabbitMQ vs Kafka"

处理流程:
1. 理解: 业务场景 (消息量、顺序性、可靠性要求)
2. 调研: 对比两者在 Spring Cloud 生态的集成度
3. 理论分析: 基于 CAP 理论分析适用场景
4. 输出: 架构方案文档 + 集成示例代码
```

## 注意事项

- **版本兼容性**: 始终检查组件与 Spring Boot 3.2.4 / JDK 21 的兼容性
- **Jakarta EE 迁移**: Spring Boot 3.x 使用 Jakarta EE,注意 javax.* 到 jakarta.* 的迁移
- **实战导向**: 优先参考国内互联网公司的实践案例
- **成本意识**: 评估方案时考虑 License 成本和运维成本
- **团队能力**: 方案选择要考虑团队的实际技术能力
