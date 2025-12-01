# JDK 8 升级至 JDK 21 改造方案

> 基于 Dorado 框架和 Serial 系统的实战经验编写
> 面向企业级 Java SDK 和 Spring Boot + Spring Cloud 微服务项目
> 版本：v1.0
> 日期：2025-11-28

---

## 一、方案概述

### 1.1 升级背景

- **JDK 8 生命周期**：Oracle JDK 8 已于 2022 年 3 月结束公开更新支持
- **性能提升**：JDK 21 相比 JDK 8 在性能、GC、语言特性等方面有显著提升
- **长期支持（LTS）**：JDK 21 是最新的 LTS 版本，支持周期至 2028 年 9 月
- **现代化技术栈**：Spring Boot 3.x、Spring Cloud 2023.x 要求最低 JDK 17

### 1.2 升级收益

| 方面       | 具体收益                                     |
| -------- | ---------------------------------------- |
| **性能**   | • GC 性能提升（ZGC、G1GC 优化）<br>• 应用启动速度提升 20%-30%<br>• 运行时性能提升 10%-15% |
| **语言特性** | • Record 类型<br>• Pattern Matching<br>• Switch 表达式<br>• Text Blocks<br>• Virtual Threads (Project Loom) |
| **安全性**  | • 更好的密码学支持<br>• 安全漏洞修复<br>• 更严格的模块化封装    |
| **工具链**  | • 更好的 IDE 支持<br>• 更完善的诊断工具<br>• 容器环境优化   |

### 1.3 升级挑战

- **框架兼容性**：Spring Boot 2.x → 3.x 需要大版本升级
- **命名空间变更**：Java EE → Jakarta EE（javax.* → jakarta.*）
- **依赖升级**：大量第三方库需要升级到兼容 JDK 21 的版本
- **代码调整**：部分 JDK 内部 API 访问受限
- **测试工作量**：需要全面回归测试

---

## 二、技术架构调整

### 2.1 核心框架版本升级

#### 2.1.1 Spring 生态版本对应关系

| 组件                   | JDK 8 版本          | JDK 21 版本 | 备注                   |
| -------------------- | ----------------- | --------- | -------------------- |
| **Spring Boot**      | 2.2.x - 2.7.x     | 3.2.4+    | 最低要求 JDK 17          |
| **Spring Cloud**     | Hoxton - 2021.0.x | 2023.0.1+ | 对应 Spring Boot 3.2.x |
| **Spring Framework** | 5.x               | 6.x       | 随 Spring Boot 3.x 升级 |

#### 2.1.2 Spring Boot 3.x 主要变更

```xml
<!-- JDK 8 时代的配置 -->
<spring-boot.version>2.2.2.RELEASE</spring-boot.version>
<spring-cloud.version>Hoxton.RELEASE</spring-cloud.version>

<!-- JDK 21 时代的配置 -->
<spring-boot.version>3.2.4</spring-boot.version>
<spring-cloud.version>2023.0.1</spring-cloud.version>
```

**核心变更点：**
1. **Jakarta EE 9+**：所有 `javax.*` 包名更改为 `jakarta.*`
2. **移除过时 API**：移除了大量 Spring Boot 2.x 中标记为 @Deprecated 的 API
3. **配置属性变更**：部分配置属性名称和行为发生变化
4. **原生镜像支持**：增强对 GraalVM Native Image 的支持
5. **观测性增强**：更好的 Micrometer 和 Observability 支持

### 2.2 依赖版本升级清单

#### 2.2.1 核心依赖版本矩阵

| 依赖组件                    | JDK 8 版本         | JDK 21 版本   | 升级原因                   |
| ----------------------- | ---------------- | ----------- | ---------------------- |
| **Lombok**              | 1.16.x - 1.18.12 | 1.18.30+    | JDK 21 兼容性             |
| **MapStruct**           | 1.3.x - 1.4.x    | 1.5.5.Final | 注解处理器兼容                |
| **Guava**               | 20.x - 30.x      | 33.2.1-jre  | JDK 21 优化              |
| **Hutool**              | 5.3.x - 5.7.x    | 5.8.35+     | JDK 21 兼容性             |
| **Jackson**             | 2.10.x - 2.13.x  | 2.16.1+     | Jakarta EE 支持          |
| **MyBatis-Plus**        | 3.3.2            | 3.5.3+      | JDK 17+ 支持             |
| **Redisson**            | 3.11.6           | 3.23.0+     | JDK 17+ 优化             |
| **Hibernate Validator** | 6.x              | 8.0.1.Final | Jakarta Validation 3.0 |

#### 2.2.2 Jakarta EE 依赖替换

```xml
<!-- ========== JDK 8 时代 ========== -->
<!-- Servlet API -->
<dependency>
    <groupId>javax.servlet</groupId>
    <artifactId>javax.servlet-api</artifactId>
    <version>4.0.1</version>
</dependency>

<!-- Bean Validation -->
<dependency>
    <groupId>javax.validation</groupId>
    <artifactId>validation-api</artifactId>
    <version>2.0.1.Final</version>
</dependency>

<!-- Persistence API -->
<dependency>
    <groupId>javax.persistence</groupId>
    <artifactId>javax.persistence-api</artifactId>
    <version>2.2</version>
</dependency>

<!-- ========== JDK 21 时代 ========== -->
<!-- Servlet API -->
<dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>6.0.0</version>
</dependency>

<!-- Bean Validation -->
<dependency>
    <groupId>jakarta.validation</groupId>
    <artifactId>jakarta.validation-api</artifactId>
    <version>3.0.2</version>
</dependency>

<!-- Persistence API (JPA) -->
<dependency>
    <groupId>jakarta.persistence</groupId>
    <artifactId>jakarta.persistence-api</artifactId>
    <version>3.1.0</version>
</dependency>

<!-- Activation -->
<dependency>
    <groupId>jakarta.activation</groupId>
    <artifactId>jakarta.activation-api</artifactId>
    <version>2.0.1</version>
</dependency>
```

---

## 三、依赖版本统一管理方案

### 3.1 依赖管理项目架构

#### 3.1.1 项目结构设计

```
ym-dependencies-parent/
├── pom.xml                          # 顶层父 POM
├── ym-dependencies-bom/        # BOM 项目
│   └── pom.xml                      # 统一版本管理
├── ym-build-parent/            # 构建配置父 POM
│   └── pom.xml                      # Maven 插件配置
└── README.md                        # 使用说明
```

#### 3.1.2 顶层父 POM 配置

**文件：`ym-dependencies-parent/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.company</groupId>
    <artifactId>company-dependencies-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>pom</packaging>

    <name>Company Dependencies Parent</name>
    <description>企业级依赖版本统一管理父项目</description>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>

        <!-- Java 版本 -->
        <java.version>21</java.version>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <maven.compiler.release>21</maven.compiler.release>

        <!-- Maven 插件版本 -->
        <maven-compiler-plugin.version>3.11.0</maven-compiler-plugin.version>
        <maven-surefire-plugin.version>3.2.5</maven-surefire-plugin.version>
        <maven-failsafe-plugin.version>3.2.5</maven-failsafe-plugin.version>
        <maven-source-plugin.version>3.3.0</maven-source-plugin.version>
        <maven-javadoc-plugin.version>3.6.3</maven-javadoc-plugin.version>
        <maven-deploy-plugin.version>3.1.1</maven-deploy-plugin.version>
        <maven-install-plugin.version>3.1.1</maven-install-plugin.version>
        <maven-resources-plugin.version>3.3.1</maven-resources-plugin.version>
        <maven-clean-plugin.version>3.3.2</maven-clean-plugin.version>
        <maven-jar-plugin.version>3.3.0</maven-jar-plugin.version>
        <maven-war-plugin.version>3.4.0</maven-war-plugin.version>
        <spring-boot-maven-plugin.version>3.2.4</spring-boot-maven-plugin.version>

        <!-- 注解处理器版本 -->
        <lombok.version>1.18.36</lombok.version>
        <mapstruct.version>1.5.5.Final</mapstruct.version>
    </properties>

    <modules>
        <module>company-dependencies-bom</module>
        <module>company-build-parent</module>
    </modules>

    <build>
        <pluginManagement>
            <plugins>
                <!-- Maven Compiler Plugin -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <version>${maven-compiler-plugin.version}</version>
                    <configuration>
                        <source>${maven.compiler.source}</source>
                        <target>${maven.compiler.target}</target>
                        <release>${maven.compiler.release}</release>
                        <encoding>${project.build.sourceEncoding}</encoding>
                        <fork>true</fork>
                        <annotationProcessorPaths>
                            <path>
                                <groupId>org.projectlombok</groupId>
                                <artifactId>lombok</artifactId>
                                <version>${lombok.version}</version>
                            </path>
                            <path>
                                <groupId>org.mapstruct</groupId>
                                <artifactId>mapstruct-processor</artifactId>
                                <version>${mapstruct.version}</version>
                            </path>
                        </annotationProcessorPaths>
                        <compilerArgs>
                            <!-- MapStruct 配置 -->
                            <arg>-Amapstruct.suppressGeneratorTimestamp=true</arg>
                            <arg>-Amapstruct.defaultComponentModel=spring</arg>
                            <!--
                                JDK 21 模块强封装：为注解处理器打开 javac 内部 API 访问权限
                                Lombok 和 MapStruct 需要访问编译器内部 API
                            -->
                            <arg>--add-opens</arg>
                            <arg>jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED</arg>
                        </compilerArgs>
                    </configuration>
                </plugin>

                <!-- Maven Surefire Plugin (单元测试) -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-surefire-plugin</artifactId>
                    <version>${maven-surefire-plugin.version}</version>
                </plugin>

                <!-- Maven Failsafe Plugin (集成测试) -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-failsafe-plugin</artifactId>
                    <version>${maven-failsafe-plugin.version}</version>
                </plugin>

                <!-- Spring Boot Maven Plugin -->
                <plugin>
                    <groupId>org.springframework.boot</groupId>
                    <artifactId>spring-boot-maven-plugin</artifactId>
                    <version>${spring-boot-maven-plugin.version}</version>
                    <executions>
                        <execution>
                            <goals>
                                <goal>repackage</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>
            </plugins>
        </pluginManagement>
    </build>
</project>
```

#### 3.1.3 BOM 项目配置

**文件：`ym-dependencies-parent/ym-dependencies-bom/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.company</groupId>
        <artifactId>company-dependencies-parent</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>

    <artifactId>company-dependencies-bom</artifactId>
    <packaging>pom</packaging>

    <name>Company Dependencies BOM</name>
    <description>企业级依赖版本 BOM (Bill of Materials)</description>

    <properties>
        <!-- ========== Spring 生态版本 ========== -->
        <spring-boot.version>3.2.4</spring-boot.version>
        <spring-cloud.version>2023.0.1</spring-cloud.version>
        <spring-cloud-alibaba.version>2023.0.1.0</spring-cloud-alibaba.version>

        <!-- ========== 持久层框架版本 ========== -->
        <mybatis-plus.version>3.5.5</mybatis-plus.version>
        <mybatis-spring-boot-starter.version>3.0.3</mybatis-spring-boot-starter.version>
        <tk-mapper.version>4.3.0</tk-mapper.version>
        <pagehelper.version>6.1.0</pagehelper.version>
        <pagehelper-spring-boot-starter.version>2.1.0</pagehelper-spring-boot-starter.version>
        <druid.version>1.2.21</druid.version>

        <!-- ========== 缓存和分布式锁 ========== -->
        <redisson.version>3.27.2</redisson.version>
        <jedis.version>5.1.3</jedis.version>

        <!-- ========== 消息队列 ========== -->
        <rocketmq-spring-boot-starter.version>2.3.0</rocketmq-spring-boot-starter.version>

        <!-- ========== 服务注册与配置中心 ========== -->
        <apollo.version>2.3.0</apollo.version>
        <consul-api.version>1.4.5</consul-api.version>

        <!-- ========== 分布式事务和任务调度 ========== -->
        <seata.version>1.8.0</seata.version>
        <elastic-job.version>3.0.4</elastic-job.version>

        <!-- ========== 工具类库 ========== -->
        <guava.version>33.2.1-jre</guava.version>
        <hutool.version>5.8.35</hutool.version>
        <commons-lang3.version>3.14.0</commons-lang3.version>
        <commons-io.version>2.15.1</commons-io.version>
        <commons-collections4.version>4.4</commons-collections4.version>

        <!-- ========== JSON 和序列化 ========== -->
        <jackson.version>2.16.1</jackson.version>
        <fastjson2.version>2.0.47</fastjson2.version>

        <!-- ========== 日志框架 ========== -->
        <logback.version>1.4.14</logback.version>
        <slf4j.version>2.0.12</slf4j.version>

        <!-- ========== Jakarta EE 规范 ========== -->
        <jakarta.servlet.version>6.0.0</jakarta.servlet.version>
        <jakarta.validation.version>3.0.2</jakarta.validation.version>
        <jakarta.persistence.version>3.1.0</jakarta.persistence.version>
        <jakarta.activation.version>2.0.1</jakarta.activation.version>
        <jakarta.annotation.version>2.1.1</jakarta.annotation.version>

        <!-- ========== Bean 映射和验证 ========== -->
        <mapstruct.version>1.5.5.Final</mapstruct.version>
        <lombok.version>1.18.36</lombok.version>
        <hibernate-validator.version>8.0.1.Final</hibernate-validator.version>

        <!-- ========== API 文档 ========== -->
        <springdoc-openapi.version>2.3.0</springdoc-openapi.version>
        <knife4j.version>4.4.0</knife4j.version>

        <!-- ========== 云服务 SDK ========== -->
        <aliyun-oss.version>3.17.4</aliyun-oss.version>

        <!-- ========== HTTP 客户端 ========== -->
        <httpclient5.version>5.3.1</httpclient5.version>
        <okhttp.version>4.12.0</okhttp.version>

        <!-- ========== 测试框架 ========== -->
        <junit-jupiter.version>5.10.2</junit-jupiter.version>
        <mockito.version>5.11.0</mockito.version>

        <!-- ========== 其他 ========== -->
        <mysql-connector.version>8.3.0</mysql-connector.version>
        <easyexcel.version>3.3.4</easyexcel.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <!-- ========== Spring Boot Dependencies ========== -->
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>${spring-boot.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <!-- ========== Spring Cloud Dependencies ========== -->
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <!-- ========== Spring Cloud Alibaba Dependencies ========== -->
            <dependency>
                <groupId>com.alibaba.cloud</groupId>
                <artifactId>spring-cloud-alibaba-dependencies</artifactId>
                <version>${spring-cloud-alibaba.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>

            <!-- ========== MyBatis Plus ========== -->
            <dependency>
                <groupId>com.baomidou</groupId>
                <artifactId>mybatis-plus-boot-starter</artifactId>
                <version>${mybatis-plus.version}</version>
            </dependency>
            <dependency>
                <groupId>com.baomidou</groupId>
                <artifactId>mybatis-plus-core</artifactId>
                <version>${mybatis-plus.version}</version>
            </dependency>

            <!-- ========== Redisson ========== -->
            <dependency>
                <groupId>org.redisson</groupId>
                <artifactId>redisson-spring-boot-starter</artifactId>
                <version>${redisson.version}</version>
            </dependency>

            <!-- ========== Guava ========== -->
            <dependency>
                <groupId>com.google.guava</groupId>
                <artifactId>guava</artifactId>
                <version>${guava.version}</version>
            </dependency>

            <!-- ========== Hutool ========== -->
            <dependency>
                <groupId>cn.hutool</groupId>
                <artifactId>hutool-all</artifactId>
                <version>${hutool.version}</version>
            </dependency>

            <!-- ========== Jakarta EE APIs ========== -->
            <dependency>
                <groupId>jakarta.servlet</groupId>
                <artifactId>jakarta.servlet-api</artifactId>
                <version>${jakarta.servlet.version}</version>
            </dependency>
            <dependency>
                <groupId>jakarta.validation</groupId>
                <artifactId>jakarta.validation-api</artifactId>
                <version>${jakarta.validation.version}</version>
            </dependency>
            <dependency>
                <groupId>jakarta.persistence</groupId>
                <artifactId>jakarta.persistence-api</artifactId>
                <version>${jakarta.persistence.version}</version>
            </dependency>
            <dependency>
                <groupId>jakarta.activation</groupId>
                <artifactId>jakarta.activation-api</artifactId>
                <version>${jakarta.activation.version}</version>
            </dependency>

            <!-- ========== Lombok and MapStruct ========== -->
            <dependency>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <version>${lombok.version}</version>
                <scope>provided</scope>
            </dependency>
            <dependency>
                <groupId>org.mapstruct</groupId>
                <artifactId>mapstruct</artifactId>
                <version>${mapstruct.version}</version>
            </dependency>

            <!-- ========== Hibernate Validator ========== -->
            <dependency>
                <groupId>org.hibernate.validator</groupId>
                <artifactId>hibernate-validator</artifactId>
                <version>${hibernate-validator.version}</version>
            </dependency>

            <!-- ========== MySQL Connector ========== -->
            <dependency>
                <groupId>com.mysql</groupId>
                <artifactId>mysql-connector-j</artifactId>
                <version>${mysql-connector.version}</version>
            </dependency>

            <!-- ========== Jackson ========== -->
            <dependency>
                <groupId>com.fasterxml.jackson.core</groupId>
                <artifactId>jackson-databind</artifactId>
                <version>${jackson.version}</version>
            </dependency>

            <!-- 其他依赖省略... -->
        </dependencies>
    </dependencyManagement>
</project>
```

#### 3.1.4 构建配置父 POM

**文件：`ym-dependencies-parent/ym-build-parent/pom.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.ym</groupId>
        <artifactId>ym-dependencies-parent</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>

    <artifactId>ym-build-parent</artifactId>
    <packaging>pom</packaging>

    <name>YM Build Parent</name>
    <description>企业级 Maven 构建配置父 POM，提供统一的插件配置</description>

    <properties>
        <!-- 继承自 ym-dependencies-parent 的属性 -->
        <!-- 这里可以覆盖或新增属性 -->
    </properties>

    <build>
        <pluginManagement>
            <plugins>
                <!-- ========== Maven Compiler Plugin ========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <version>${maven-compiler-plugin.version}</version>
                    <configuration>
                        <source>${maven.compiler.source}</source>
                        <target>${maven.compiler.target}</target>
                        <release>${maven.compiler.release}</release>
                        <encoding>${project.build.sourceEncoding}</encoding>
                        <fork>true</fork>
                        <annotationProcessorPaths>
                            <path>
                                <groupId>org.projectlombok</groupId>
                                <artifactId>lombok</artifactId>
                                <version>${lombok.version}</version>
                            </path>
                            <path>
                                <groupId>org.mapstruct</groupId>
                                <artifactId>mapstruct-processor</artifactId>
                                <version>${mapstruct.version}</version>
                            </path>
                        </annotationProcessorPaths>
                        <compilerArgs>
                            <!-- MapStruct 配置 -->
                            <arg>-Amapstruct.suppressGeneratorTimestamp=true</arg>
                            <arg>-Amapstruct.defaultComponentModel=spring</arg>
                            <!-- JDK 21 模块强封装：打开 javac 内部 API 访问权限 -->
                            <arg>--add-opens</arg>
                            <arg>jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED</arg>
                        </compilerArgs>
                    </configuration>
                </plugin>

                <!-- ========== Maven Surefire Plugin（单元测试）========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-surefire-plugin</artifactId>
                    <version>${maven-surefire-plugin.version}</version>
                    <configuration>
                        <argLine>-Dfile.encoding=UTF-8</argLine>
                        <skipTests>${maven.test.skip}</skipTests>
                    </configuration>
                </plugin>

                <!-- ========== Maven Failsafe Plugin（集成测试）========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-failsafe-plugin</artifactId>
                    <version>${maven-failsafe-plugin.version}</version>
                    <executions>
                        <execution>
                            <goals>
                                <goal>integration-test</goal>
                                <goal>verify</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>

                <!-- ========== Maven Source Plugin（源码打包）========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-source-plugin</artifactId>
                    <version>${maven-source-plugin.version}</version>
                    <executions>
                        <execution>
                            <id>attach-sources</id>
                            <phase>verify</phase>
                            <goals>
                                <goal>jar-no-fork</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>

                <!-- ========== Maven Javadoc Plugin（文档生成）========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-javadoc-plugin</artifactId>
                    <version>${maven-javadoc-plugin.version}</version>
                    <configuration>
                        <encoding>UTF-8</encoding>
                        <charset>UTF-8</charset>
                        <docencoding>UTF-8</docencoding>
                        <!-- JDK 21 兼容性配置 -->
                        <source>21</source>
                        <detectJavaApiLink>false</detectJavaApiLink>
                        <doclint>none</doclint>
                    </configuration>
                    <executions>
                        <execution>
                            <id>attach-javadocs</id>
                            <phase>verify</phase>
                            <goals>
                                <goal>jar</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>

                <!-- ========== Maven Resources Plugin（资源处理）========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-resources-plugin</artifactId>
                    <version>${maven-resources-plugin.version}</version>
                    <configuration>
                        <encoding>${project.build.sourceEncoding}</encoding>
                    </configuration>
                </plugin>

                <!-- ========== Maven JAR Plugin（JAR 打包）========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-jar-plugin</artifactId>
                    <version>${maven-jar-plugin.version}</version>
                    <configuration>
                        <archive>
                            <manifest>
                                <addDefaultImplementationEntries>true</addDefaultImplementationEntries>
                                <addDefaultSpecificationEntries>true</addDefaultSpecificationEntries>
                            </manifest>
                        </archive>
                    </configuration>
                </plugin>

                <!-- ========== Maven WAR Plugin（WAR 打包，Web 应用使用）========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-war-plugin</artifactId>
                    <version>${maven-war-plugin.version}</version>
                    <configuration>
                        <failOnMissingWebXml>false</failOnMissingWebXml>
                        <archive>
                            <manifest>
                                <addDefaultImplementationEntries>true</addDefaultImplementationEntries>
                            </manifest>
                        </archive>
                    </configuration>
                </plugin>

                <!-- ========== Spring Boot Maven Plugin（Spring Boot 应用）========== -->
                <plugin>
                    <groupId>org.springframework.boot</groupId>
                    <artifactId>spring-boot-maven-plugin</artifactId>
                    <version>${spring-boot-maven-plugin.version}</version>
                    <configuration>
                        <excludes>
                            <exclude>
                                <groupId>org.projectlombok</groupId>
                                <artifactId>lombok</artifactId>
                            </exclude>
                        </excludes>
                    </configuration>
                    <executions>
                        <execution>
                            <goals>
                                <goal>repackage</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>

                <!-- ========== Maven Deploy Plugin（部署到仓库）========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-deploy-plugin</artifactId>
                    <version>${maven-deploy-plugin.version}</version>
                </plugin>

                <!-- ========== Maven Install Plugin（安装到本地）========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-install-plugin</artifactId>
                    <version>${maven-install-plugin.version}</version>
                </plugin>

                <!-- ========== Maven Clean Plugin（清理）========== -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-clean-plugin</artifactId>
                    <version>${maven-clean-plugin.version}</version>
                </plugin>
            </plugins>
        </pluginManagement>

        <!-- 默认插件（所有子项目都会继承）-->
        <plugins>
            <!-- 编译插件：所有项目都需要 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
            </plugin>

            <!-- 资源插件：所有项目都需要 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-resources-plugin</artifactId>
            </plugin>

            <!-- 测试插件：所有项目都需要 -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

**ym-build-parent 的职责：**

1. **统一编译配置**：JDK 21、Lombok、MapStruct 注解处理器
2. **统一测试配置**：单元测试和集成测试插件
3. **统一打包配置**：JAR、WAR、Spring Boot 可执行 JAR
4. **统一文档配置**：源码和 JavaDoc 生成
5. **统一部署配置**：本地安装和远程部署

**使用建议：**
- **纯 Java SDK 项目**：继承 `ym-build-parent` + 导入 `ym-dependencies-bom`
- **Spring Boot 应用**：继承 `ym-build-parent` + 导入 `ym-dependencies-bom`
- **特殊需求项目**：仅导入 `ym-dependencies-bom`，自定义构建配置

---

### 3.2 业务项目使用方式

#### 3.2.1 SDK 项目使用示例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.ym.sdk</groupId>
    <artifactId>common-utils-sdk</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <!-- 继承构建配置父 POM -->
    <parent>
        <groupId>com.ym</groupId>
        <artifactId>ym-build-parent</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>

    <dependencyManagement>
        <dependencies>
            <!-- 引入统一版本管理 BOM -->
            <dependency>
                <groupId>com.ym</groupId>
                <artifactId>ym-dependencies-bom</artifactId>
                <version>1.0.0-SNAPSHOT</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <!-- 直接使用，无需指定版本 -->
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
        </dependency>
        <dependency>
            <groupId>cn.hutool</groupId>
            <artifactId>hutool-all</artifactId>
        </dependency>
    </dependencies>
</project>
```

#### 3.2.2 Spring Boot 微服务项目使用示例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.ym.microservice</groupId>
    <artifactId>order-service</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <!-- 继承构建配置父 POM -->
    <parent>
        <groupId>com.ym</groupId>
        <artifactId>ym-build-parent</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>

    <dependencyManagement>
        <dependencies>
            <!-- 引入统一版本管理 BOM -->
            <dependency>
                <groupId>com.ym</groupId>
                <artifactId>ym-dependencies-bom</artifactId>
                <version>1.0.0-SNAPSHOT</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <!-- Spring Boot Starter -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Spring Cloud 组件 -->
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-starter-openfeign</artifactId>
        </dependency>

        <!-- MyBatis Plus -->
        <dependency>
            <groupId>com.baomidou</groupId>
            <artifactId>mybatis-plus-boot-starter</artifactId>
        </dependency>

        <!-- Redisson -->
        <dependency>
            <groupId>org.redisson</groupId>
            <artifactId>redisson-spring-boot-starter</artifactId>
        </dependency>

        <!-- 所有版本都由 BOM 统一管理 -->
    </dependencies>

    <build>
        <plugins>
            <!-- Spring Boot Maven Plugin -->
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## 四、代码迁移指南

### 4.1 Jakarta EE 命名空间迁移

#### 4.1.1 自动化替换脚本

**方式一：使用 IDE 批量替换（推荐）**

在 IntelliJ IDEA 中：
1. `Ctrl/Cmd + Shift + R`（Replace in Path）
2. 勾选 "Regex"
3. 批量替换以下内容：

| 查找 (Find)                  | 替换 (Replace)                 |
| -------------------------- | ---------------------------- |
| `import javax.servlet`     | `import jakarta.servlet`     |
| `import javax.validation`  | `import jakarta.validation`  |
| `import javax.persistence` | `import jakarta.persistence` |
| `import javax.annotation`  | `import jakarta.annotation`  |
| `import javax.ws.rs`       | `import jakarta.ws.rs`       |
| `import javax.xml.bind`    | `import jakarta.xml.bind`    |
| `import javax.activation`  | `import jakarta.activation`  |

**方式二：使用 OpenRewrite 自动化迁移工具**

```xml
<!-- 在 pom.xml 中添加 OpenRewrite 插件 -->
<plugin>
    <groupId>org.openrewrite.maven</groupId>
    <artifactId>rewrite-maven-plugin</artifactId>
    <version>5.28.0</version>
    <configuration>
        <activeRecipes>
            <recipe>org.openrewrite.java.migrate.JavaxMigrationToJakarta</recipe>
        </activeRecipes>
    </configuration>
    <dependencies>
        <dependency>
            <groupId>org.openrewrite.recipe</groupId>
            <artifactId>rewrite-migrate-java</artifactId>
            <version>2.11.0</version>
        </dependency>
    </dependencies>
</plugin>
```

执行迁移命令：
```bash
# 1. 检测需要迁移的代码
mvn rewrite:dryRun

# 2. 执行自动迁移
mvn rewrite:run
```

#### 4.1.2 常见代码迁移示例

**示例 1：Servlet API**

```java
// ========== JDK 8 + Spring Boot 2.x ==========
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;

public class CustomFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {
        // 业务逻辑
    }
}

// ========== JDK 21 + Spring Boot 3.x ==========
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;

public class CustomFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {
        // 业务逻辑（无需修改）
    }
}
```

**示例 2：Bean Validation**

```java
// ========== JDK 8 + Spring Boot 2.x ==========
import javax.validation.constraints.NotNull;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
import javax.validation.Valid;

@Data
public class UserDTO {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 20, message = "用户名长度必须在2-20之间")
    private String username;

    @NotNull(message = "年龄不能为空")
    private Integer age;
}

// ========== JDK 21 + Spring Boot 3.x ==========
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import jakarta.validation.Valid;

@Data
public class UserDTO {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 20, message = "用户名长度必须在2-20之间")
    private String username;

    @NotNull(message = "年龄不能为空")
    private Integer age;
}
```

**示例 3：JPA Persistence**

```java
// ========== JDK 8 + Spring Boot 2.x ==========
import javax.persistence.Entity;
import javax.persistence.Table;
import javax.persistence.Id;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Column;

@Entity
@Table(name = "t_user")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "username", length = 50)
    private String username;
}

// ========== JDK 21 + Spring Boot 3.x ==========
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Column;

@Entity
@Table(name = "t_user")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "username", length = 50)
    private String username;
}
```

### 4.2 Spring Boot 配置属性迁移

#### 4.2.1 配置文件迁移工具

Spring Boot 提供了配置迁移帮助工具：

```xml
<!-- 添加到 pom.xml，运行时会输出配置迁移建议 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-properties-migrator</artifactId>
    <scope>runtime</scope>
</dependency>
```

启动应用后，控制台会输出如下提示：
```
The use of configuration keys that have been renamed was found in the environment:

Property source 'application.yml':
    Key: spring.redis.jedis.pool.max-active
        Reason: none
        Replacement: spring.data.redis.jedis.pool.max-active
```

#### 4.2.2 常见配置属性变更

| 旧配置 (Spring Boot 2.x)           | 新配置 (Spring Boot 3.x)           | 说明                      |
| ------------------------------- | ------------------------------- | ----------------------- |
| `spring.redis.*`                | `spring.data.redis.*`           | Redis 配置统一到 spring.data |
| `spring.datasource.type`        | `spring.datasource.type`        | 保持不变                    |
| `spring.jpa.hibernate.ddl-auto` | `spring.jpa.hibernate.ddl-auto` | 保持不变                    |
| `logging.pattern.console`       | `logging.pattern.console`       | 保持不变                    |
| `management.metrics.export.*`   | `management.metrics.export.*`   | 保持不变                    |

### 4.3 移除废弃 API 调整

#### 4.3.1 Spring Security 变更

```java
// ========== Spring Boot 2.x ==========
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .authorizeRequests()
                .antMatchers("/public/**").permitAll()
                .anyRequest().authenticated()
            .and()
            .formLogin();
    }
}

// ========== Spring Boot 3.x ==========
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(Customizer.withDefaults());

        return http.build();
    }
}
```

#### 4.3.2 Date/Time API 推荐使用

```java
// ========== 不推荐（旧 API） ==========
import java.util.Date;
import java.text.SimpleDateFormat;

Date now = new Date();
SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
String dateStr = sdf.format(now);

// ========== 推荐（Java 8+ API） ==========
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

LocalDateTime now = LocalDateTime.now();
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
String dateStr = now.format(formatter);
```

---

## 五、升级实施步骤

### 5.1 升级前准备

#### 5.1.1 环境准备

```bash
# 1. 安装 JDK 21
# 下载地址：https://adoptium.net/temurin/releases/
# 或者使用 SDKMAN 安装
sdk install java 21-tem

# 2. 验证 JDK 版本
java -version
# 预期输出：
# openjdk version "21.0.x" 2024-xx-xx LTS
# OpenJDK Runtime Environment Temurin-21+xx (build 21.0.x+xx-LTS)
# OpenJDK 64-Bit Server VM Temurin-21+xx (build 21.0.x+xx-LTS, mixed mode, sharing)

# 3. 配置 JAVA_HOME
export JAVA_HOME=/path/to/jdk-21
export PATH=$JAVA_HOME/bin:$PATH

# 4. 验证 Maven 版本（建议 3.8.1+）
mvn -version
```

#### 5.1.2 代码分支管理

```bash
# 1. 基于主分支创建升级分支
git checkout main
git pull origin main
git checkout -b feature/upgrade-jdk21

# 2. 创建备份标签
git tag backup-before-jdk21-upgrade
git push origin backup-before-jdk21-upgrade
```

#### 5.1.3 依赖兼容性检查

创建检查脚本 `check-dependencies.sh`：

```bash
#!/bin/bash

echo "========== 检查项目依赖兼容性 =========="

# 1. 查看依赖树
mvn dependency:tree > dependency-tree.txt
echo "依赖树已保存到 dependency-tree.txt"

# 2. 检查过时依赖
mvn versions:display-dependency-updates > dependency-updates.txt
echo "依赖更新建议已保存到 dependency-updates.txt"

# 3. 检查插件版本
mvn versions:display-plugin-updates > plugin-updates.txt
echo "插件更新建议已保存到 plugin-updates.txt"

# 4. 查找 javax 引用
echo "========== 检查 javax 包引用 =========="
grep -r "import javax\." --include="*.java" src/ | wc -l
echo "找到的 javax 引用数量（需要迁移到 jakarta）"

echo "检查完成！"
```

### 5.2 分步升级流程

#### 步骤 1：升级 Maven 配置

1. **更新父 POM 的 JDK 版本**

```xml
<!-- 修改 pom.xml -->
<properties>
    <maven.compiler.source>21</maven.compiler.source>
    <maven.compiler.target>21</maven.compiler.target>
    <maven.compiler.release>21</maven.compiler.release>
</properties>
```

2. **升级 Maven 编译插件**

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.11.0</version>
    <configuration>
        <source>21</source>
        <target>21</target>
        <release>21</release>
        <fork>true</fork>
        <compilerArgs>
            <arg>--add-opens</arg>
            <arg>jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED</arg>
        </compilerArgs>
    </configuration>
</plugin>
```

3. **升级测试插件**

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>3.2.5</version>
</plugin>
```

#### 步骤 2：升级 Spring Boot 和 Spring Cloud

1. **更新版本号**

```xml
<properties>
    <!-- 从 2.x 升级到 3.x -->
    <spring-boot.version>3.2.4</spring-boot.version>
    <spring-cloud.version>2023.0.1</spring-cloud.version>
</properties>
```

2. **清理 Maven 缓存并重新下载依赖**

```bash
# 清理本地仓库缓存
mvn dependency:purge-local-repository -DreResolve=false

# 重新下载
mvn clean install -U
```

#### 步骤 3：升级 Lombok 和 MapStruct

```xml
<properties>
    <lombok.version>1.18.36</lombok.version>
    <mapstruct.version>1.5.5.Final</mapstruct.version>
</properties>
```

**验证注解处理器配置：**

```bash
# 清理编译产物
mvn clean

# 重新编译，查看生成的代码
mvn compile

# 检查 MapStruct 生成的实现类
ls -la target/generated-sources/annotations/
```

#### 步骤 4：Jakarta EE 命名空间迁移

**方式 1：使用 OpenRewrite（推荐）**

```bash
# 1. 添加 OpenRewrite 插件到 pom.xml（参考 4.1.1）

# 2. 执行迁移
mvn rewrite:run

# 3. 查看变更
git diff
```

**方式 2：手动批量替换**

使用 IDE 的全局替换功能（参考 4.1.1）。

#### 步骤 5：升级其他依赖

按照第二章"依赖版本升级清单"逐个升级：

```bash
# 每升级一个依赖后进行编译验证
mvn clean compile

# 如有编译错误，查看错误信息并调整代码
```

#### 步骤 6：代码适配调整

根据编译错误提示，调整代码：

1. **修复 Jakarta EE 命名空间问题**
2. **修复 Spring API 变更**
3. **修复第三方库 API 变更**

```bash
# 编译并查看所有错误
mvn clean compile 2>&1 | tee compile-errors.log

# 逐个修复错误
```

#### 步骤 7：单元测试和集成测试

```bash
# 1. 运行单元测试
mvn clean test

# 2. 查看测试报告
cat target/surefire-reports/*.txt

# 3. 修复失败的测试

# 4. 运行集成测试
mvn clean verify
```

#### 步骤 8：本地启动验证

```bash
# 1. 打包
mvn clean package -DskipTests

# 2. 启动应用
java -jar target/your-app.jar

# 3. 验证启动日志
# 确认没有 WARNING 或 ERROR

# 4. 执行冒烟测试
# 调用关键业务接口验证功能正常
```

#### 步骤 9：性能基准测试

```bash
# 使用 JMeter 或 Gatling 进行压测
# 对比升级前后的性能指标：
# - QPS (每秒请求数)
# - 响应时间 (P50, P95, P99)
# - 内存使用
# - GC 频率和停顿时间
```

### 5.3 测试验证清单

#### 功能测试

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 接口功能测试通过
- [ ] 数据库操作正常
- [ ] 缓存操作正常
- [ ] 消息队列收发正常
- [ ] 定时任务执行正常
- [ ] Feign 调用正常
- [ ] 文件上传下载正常
- [ ] 登录鉴权正常

#### 性能测试

- [ ] 应用启动时间对比
- [ ] 接口响应时间对比
- [ ] 吞吐量对比
- [ ] 内存使用对比
- [ ] CPU 使用对比
- [ ] GC 表现对比

#### 兼容性测试

- [ ] 数据库兼容性（MySQL 5.7/8.0）
- [ ] 缓存兼容性（Redis 6.x/7.x）
- [ ] 消息队列兼容性（RocketMQ 4.x/5.x）
- [ ] 容器环境兼容性（Docker, Kubernetes）

---

## 六、常见问题与解决方案

### 6.1 编译问题

#### 问题 1：Lombok 注解处理器失败

**错误信息：**
```
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.11.0:compile
java.lang.IllegalAccessError: class lombok.javac.apt.LombokProcessor
cannot access class com.sun.tools.javac.processing.JavacProcessingEnvironment
```

**解决方案：**

```xml
<!-- 1. 确保 Lombok 版本 >= 1.18.30 -->
<lombok.version>1.18.36</lombok.version>

<!-- 2. 添加 JDK 模块打开参数 -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.11.0</version>
    <configuration>
        <fork>true</fork>
        <compilerArgs>
            <arg>--add-opens</arg>
            <arg>jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED</arg>
        </compilerArgs>
    </configuration>
</plugin>
```

#### 问题 2：MapStruct 生成代码失败

**错误信息：**
```
[ERROR] Bad service configuration file, or exception thrown while
constructing Processor object: javax.annotation.processing.Processor
```

**解决方案：**

```xml
<!-- 1. 升级 MapStruct 到 1.5.5.Final+ -->
<mapstruct.version>1.5.5.Final</mapstruct.version>

<!-- 2. 配置注解处理器路径 -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.11.0</version>
    <configuration>
        <annotationProcessorPaths>
            <path>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <version>${lombok.version}</version>
            </path>
            <path>
                <groupId>org.mapstruct</groupId>
                <artifactId>mapstruct-processor</artifactId>
                <version>${mapstruct.version}</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

### 6.2 运行时问题

#### 问题 3：NoClassDefFoundError: javax/servlet/*

**错误信息：**
```
java.lang.NoClassDefFoundError: javax/servlet/http/HttpServletRequest
```

**解决方案：**

```java
// 1. 全局替换所有 javax.servlet 为 jakarta.servlet
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

// 2. 确保依赖正确
<dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>6.0.0</version>
</dependency>
```

#### 问题 4：Spring Boot Admin 兼容性问题

**错误信息：**
```
Unsupported class file major version 65
```

**解决方案：**

```xml
<!-- 升级 Spring Boot Admin 到支持 JDK 21 的版本 -->
<dependency>
    <groupId>de.codecentric</groupId>
    <artifactId>spring-boot-admin-starter-client</artifactId>
    <version>3.2.3</version>
</dependency>

<dependency>
    <groupId>de.codecentric</groupId>
    <artifactId>spring-boot-admin-starter-server</artifactId>
    <version>3.2.3</version>
</dependency>
```

### 6.3 性能问题

#### 问题 5：GC 频率增加

**排查步骤：**

```bash
# 1. 启用 GC 日志
java -Xlog:gc*:file=gc.log:time,uptime,level,tags \
     -XX:+UseG1GC \
     -jar your-app.jar

# 2. 分析 GC 日志
# 使用 GCEasy 或 GCViewer 工具分析

# 3. 调整 GC 参数
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -XX:G1HeapRegionSize=16m \
     -Xms4g -Xmx4g \
     -jar your-app.jar
```

#### 问题 6：内存占用增加

**排查步骤：**

```bash
# 1. 生成堆转储
jmap -dump:live,format=b,file=heap.hprof <pid>

# 2. 使用 MAT (Memory Analyzer Tool) 分析
# 查找内存泄漏和大对象

# 3. 启用 Native Memory Tracking
java -XX:NativeMemoryTracking=detail -jar your-app.jar

# 4. 查看内存使用详情
jcmd <pid> VM.native_memory summary
```

---

## 七、回滚方案

### 7.1 回滚决策标准

在以下情况下考虑回滚：

- 核心业务功能无法正常运行
- 性能下降超过 30%
- 出现严重的内存泄漏或 OOM
- 生产环境出现大量异常且无法快速修复
- 第三方依赖存在不可解决的兼容性问题

### 7.2 快速回滚步骤

#### 方式 1：代码回滚

```bash
# 1. 切换回备份分支
git checkout main
git pull origin main

# 2. 重新编译和部署
mvn clean package -DskipTests
# 部署到目标环境

# 3. 验证服务恢复正常
```

#### 方式 2：使用备份标签

```bash
# 1. 回退到升级前的代码状态
git checkout backup-before-jdk21-upgrade

# 2. 创建临时分支
git checkout -b rollback-from-jdk21

# 3. 重新部署
```

### 7.3 回滚验证

- [ ] 应用正常启动
- [ ] 核心接口功能正常
- [ ] 数据完整性验证
- [ ] 监控指标恢复正常
- [ ] 日志无异常

---

## 八、最佳实践与建议

### 8.1 升级策略

1. **先升级框架项目，再升级业务项目**
   - 优先升级 Dorado 这样的基础框架
   - 验证稳定后再升级依赖该框架的业务项目（如 Serial）

2. **先升级 SDK，再升级微服务**
   - 工具类 SDK 通常依赖少，风险低
   - 微服务依赖多，需要更全面的测试

3. **小步快跑，分批升级**
   - 不要一次性升级所有项目
   - 按业务重要性分批次升级
   - 低流量服务 → 中流量服务 → 核心服务

4. **灰度发布**
   - 使用 A/B 测试或金丝雀发布
   - 先在部分节点验证，逐步扩大范围

### 8.2 协作

1. **知识分享**
   - 组织 JDK 21 新特性培训
   - 分享升级经验和踩坑记录
   - 建立升级问题知识库

2. **代码审查**
   - 强化代码 Review，确保迁移质量
   - 重点检查 Jakarta EE 命名空间替换
   - 验证废弃 API 的替换是否正确

3. **文档更新**
   - 更新开发手册和技术规范
   - 更新部署文档（JDK 版本要求）
   - 记录已知问题和解决方案

### 8.3 持续优化

升级完成后，利用 JDK 21 新特性进行优化：

1. **使用 Virtual Threads（虚拟线程）**

```java
// 适用于高并发 I/O 密集型场景
Executors.newVirtualThreadPerTaskExecutor()
```

2. **使用 Record 类简化数据对象**

```java
// 替代传统的 DTO
public record UserDTO(String username, Integer age) {}
```

3. **使用 Pattern Matching 简化代码**

```java
// 简化 instanceof 和类型转换
if (obj instanceof String str) {
    System.out.println(str.toUpperCase());
}
```

4. **使用 Sequenced Collections**

```java
// JDK 21 新增的有序集合 API
List<String> list = new ArrayList<>();
String first = list.getFirst();
String last = list.getLast();
```

---

## 九、附录

### 9.1 JDK 版本兼容性矩阵

| JDK 版本 | Spring Boot 版本 | Spring Cloud 版本      | 发布日期    | LTS 支持结束           |
| ------ | -------------- | -------------------- | ------- | ------------------ |
| JDK 8  | 2.0.x - 2.7.x  | Finchley - 2021.0.x  | 2014-03 | 2030-12 (Extended) |
| JDK 11 | 2.1.x - 2.7.x  | Greenwich - 2021.0.x | 2018-09 | 2026-09            |
| JDK 17 | 2.5.x - 3.2.x  | 2021.0.x - 2023.0.x  | 2021-09 | 2029-09            |
| JDK 21 | 3.2.x+         | 2023.0.x+            | 2023-09 | 2028-09            |

### 9.2 Maven 插件版本推荐

| 插件                       | 推荐版本    | JDK 21 兼容性 |
| ------------------------ | ------- | ---------- |
| maven-compiler-plugin    | 3.11.0+ | ✅ 完全兼容     |
| maven-surefire-plugin    | 3.2.5+  | ✅ 完全兼容     |
| maven-failsafe-plugin    | 3.2.5+  | ✅ 完全兼容     |
| maven-jar-plugin         | 3.3.0+  | ✅ 完全兼容     |
| maven-war-plugin         | 3.4.0+  | ✅ 完全兼容     |
| spring-boot-maven-plugin | 3.2.4+  | ✅ 完全兼容     |

### 9.3 参考资料

#### 官方文档

- [JDK 21 Release Notes](https://www.oracle.com/java/technologies/javase/21-relnote-issues.html)
- [Spring Boot 3.x Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)
- [Spring Cloud 2023.x Release Notes](https://github.com/spring-cloud/spring-cloud-release/wiki/Spring-Cloud-2023.0-Release-Notes)
- [Jakarta EE 9+ Migration](https://jakarta.ee/resources/migration-guide/)

#### 工具

- [OpenRewrite](https://docs.openrewrite.org/) - 自动化代码迁移工具
- [Spring Boot Migrator](https://github.com/spring-projects-experimental/spring-boot-migrator) - Spring Boot 升级工具
- [GCEasy](https://gceasy.io/) - GC 日志分析工具
- [JProfiler](https://www.ej-technologies.com/products/jprofiler/overview.html) - Java 性能分析工具

#### 社区资源

- [Baeldung - Java 21 Features](https://www.baeldung.com/java-21-new-features)
- [InfoQ - JDK 21 深度解析](https://www.infoq.cn/article/jdk21-deep-dive)
- [Spring Blog](https://spring.io/blog) - Spring 官方博客

### 9.4 升级检查清单

#### 升级前检查

- [ ] JDK 21 环境已安装配置
- [ ] Maven 版本 >= 3.8.1
- [ ] 代码已提交到版本控制系统
- [ ] 已创建备份分支/标签
- [ ] 已生成依赖分析报告
- [ ] 已识别所有需要升级的依赖
- [ ] 已准备回滚方案
- [ ] 已通知相关团队成员

#### 升级中检查

- [ ] Maven 配置已更新
- [ ] Spring Boot 版本已升级
- [ ] Spring Cloud 版本已升级
- [ ] Lombok 和 MapStruct 版本已升级
- [ ] Jakarta EE 命名空间已迁移
- [ ] 所有第三方依赖已升级
- [ ] 编译成功无错误
- [ ] 单元测试全部通过
- [ ] 集成测试全部通过

#### 升级后检查

- [ ] 应用正常启动
- [ ] 启动日志无 ERROR 和 WARNING
- [ ] 核心业务接口功能正常
- [ ] 性能基准测试通过
- [ ] 内存和 GC 表现正常
- [ ] 监控指标正常
- [ ] 日志采集正常
- [ ] 链路追踪正常
- [ ] 文档已更新
- [ ] 团队已完成知识转移

---

## 十、总结

### 10.1 关键要点

1. **充分准备**：升级前做好依赖分析、环境准备和团队培训
2. **分步实施**：遵循"先框架后业务、先 SDK 后微服务"的原则
3. **自动化工具**：使用 OpenRewrite 等工具减少手工操作
4. **全面测试**：功能测试、性能测试、兼容性测试缺一不可
5. **灰度发布**：降低风险，确保平稳过渡
6. **持续优化**：升级后利用 JDK 21 新特性进一步优化代码

### 10.2 预期

- **性能提升**：应用启动速度和运行性能提升 15%-30%
- **GC 优化**：GC 停顿时间减少 20%-40%
- **安全性增强**：获得最新的安全补丁和漏洞修复
- **长期支持**：LTS 版本支持至 2028 年 9 月
- **现代化技术栈**：与最新的 Spring 生态保持同步
- **开发体验**：利用 JDK 21 新语言特性提升代码质量

---

**文档维护者：架构组**
**最后更新时间：2025-11-28**
**版本：v1.0**
