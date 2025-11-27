# 公司技术栈详情

本文档记录公司当前使用的 Java 技术栈版本和配置,作为架构决策的基础参考。

## 核心框架

### Spring 生态
- **Spring Boot**: 3.2.4
- **Spring Cloud**: 2023.0.1
- **Spring Data Redis**: 2.2.2.RELEASE (需确认与 Spring Boot 3.2.4 兼容性)

### JDK 版本
- **JDK**: 21 (已升级,注意 Jakarta EE 命名空间迁移)

## 持久化层

### ORM 框架
- **MyBatis Plus**: 3.3.2
- **TK Mapper**: 2.1.0
- **PageHelper**: 5.1.7

### 数据库驱动
- **javax.persistence**: 1.0 (Spring Boot 3.x 需迁移到 jakarta.persistence)

## 缓存与分布式

### 缓存
- **Redisson**: 3.11.6 (Redis 客户端,支持分布式锁、分布式集合)
- **Jedis**: 5.1.3 (备选 Redis 客户端)

### 配置中心
- **Apollo Client**: 2.2.0
- **Apollo Core**: 2.2.0

### 任务调度
- **Elastic Job**: 2.1.5

### 分布式协调
- **Apache Curator**: 2.10.0 (ZooKeeper 客户端)

## 工具类库

### 核心工具
- **Lombok**: 1.18.36 (代码生成)
- **Guava**: 33.2.1-jre (Google 通用工具库)
- **Hutool**: 5.8.35 (国产工具库,推荐用于常见场景)
- **Apache Commons Lang**: 3.4
- **MapStruct**: 1.5.5.Final (对象映射)
- **CGLIB**: 3.2.4 (动态代理)

### HTTP 客户端
- **Apache HttpClient**: 4.5.6

### 文件处理
- **Aliyun OSS SDK**: 2.8.3

### 微信集成
- **WxJava**: 3.3.0

## API 文档

### Swagger/OpenAPI
- **SpringFox**: 3.0.0-SNAPSHOT (注意: Spring Boot 3.x 推荐使用 springdoc-openapi)

## 验证与校验

### Bean Validation
- **Jakarta Validation**: 3.0.2 (JDK 21 + Spring Boot 3.x 标准)
- **Glassfish EL**: 3.0.0 (表达式语言实现)

## 序列化

### JSON
- **Jackson**: 2.16.1

### 其他
- **Jakarta Activation**: 2.0.1

## Web 容器

### Servlet
- **Jakarta Servlet**: 6.0.0 (Spring Boot 3.x 使用 Jakarta EE 9+)

## 监控与度量

### Metrics
- **Micrometer**: 1.4.2 (可能需要升级以匹配 Spring Boot 3.2.4)

## 日志

### Logging
- **Logback**: 1.4.14

## 代码质量

### 静态分析
- **P3C PMD**: 1.3.0 (阿里巴巴 Java 编码规约检查)

## 版本兼容性注意事项

### JDK 21 迁移影响

1. **Jakarta EE 命名空间**
   - `javax.*` → `jakarta.*`
   - 影响包: servlet, persistence, validation, activation
   - 需要检查所有依赖是否支持 Jakarta EE 9+

2. **Spring Boot 3.x 变更**
   - 最低要求 JDK 17
   - 默认使用 Jakarta EE 9+
   - 部分 Spring Cloud 组件版本要求更新

3. **可能需要升级的组件**
   - Spring Data Redis (当前 2.2.2.RELEASE 可能过旧)
   - Micrometer (当前 1.4.2 可能过旧)
   - MyBatis Plus (当前 3.3.2,建议升级到 3.5.x)
   - SpringFox (推荐迁移到 springdoc-openapi)

### 依赖版本建议

在进行技术选型时,优先选择:
- 明确支持 Spring Boot 3.2.x 的版本
- 官方文档中提到 JDK 21 兼容性的版本
- 使用 Jakarta EE 命名空间的版本

## Maven 依赖管理示例

```xml
<properties>
    <spring-boot.version>3.2.4</spring-boot.version>
    <spring-cloud.version>2023.0.1</spring-cloud.version>
    <java.version>21</java.version>
    <maven.compiler.source>21</maven.compiler.source>
    <maven.compiler.target>21</maven.compiler.target>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>${spring-boot.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>${spring-cloud.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

## 技术债务清单

基于当前技术栈,以下组件可能存在技术债务:

1. **Spring Data Redis 2.2.2** - 与 Spring Boot 3.2.4 版本差距较大
2. **MyBatis Plus 3.3.2** - 较旧版本,建议升级到 3.5.x
3. **Elastic Job 2.1.5** - 考虑迁移到 ElasticJob Lite 3.x
4. **SpringFox** - 长期未更新,建议迁移到 springdoc-openapi
5. **Apache Commons Lang 3.4** - 过旧,建议升级到 3.12+

这些债务应在后续架构方案中逐步解决。
