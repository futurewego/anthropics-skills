# JDK 21升级问题排查指南

## 一、编译错误

### 1.1 Lombok编译失败

**错误信息**:
```
[ERROR] lombok.javac.apt.LombokProcessor could not be initialized
[ERROR] Caused by: java.lang.IllegalAccessError: class lombok.javac.apt.LombokProcessor
```

**原因**: Lombok版本不兼容JDK 21

**解决方案**:
```xml
<!-- 升级到1.18.30+版本 -->
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <version>1.18.36</version>
</dependency>
```

**检查**:
```bash
# 查看当前Lombok版本
mvn dependency:tree | grep lombok
```

### 1.2 MapStruct编译失败

**错误信息**:
```
[ERROR] Bad service configuration file, or exception thrown while constructing Processor object
```

**原因**: 缺少JDK 21的模块打开配置

**解决方案**:
在maven-compiler-plugin中添加:
```xml
<compilerArgs>
    <arg>--add-opens</arg>
    <arg>jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED</arg>
</compilerArgs>
```

### 1.3 javax/jakarta命名空间冲突

**错误信息**:
```
[ERROR] package javax.servlet does not exist
[ERROR] package javax.persistence does not exist
```

**原因**: 依赖中混用了javax和jakarta

**解决方案**:
1. 检查依赖树找出使用javax的依赖:
```bash
mvn dependency:tree | grep javax
```

2. 排除或升级这些依赖:
```xml
<dependency>
    <groupId>xxx</groupId>
    <artifactId>xxx</artifactId>
    <exclusions>
        <exclusion>
            <groupId>javax.servlet</groupId>
            <artifactId>javax.servlet-api</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

### 1.4 Spring Boot配置属性错误

**错误信息**:
```
[ERROR] Property 'xxx' is no longer supported
```

**原因**: Spring Boot 3.x移除或重命名了部分配置属性

**解决方案**:
查看Spring Boot 3.x迁移指南:
https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide

常见变更:
- `spring.mvc.static-path-pattern` → `spring.mvc.static-path-pattern`
- 移除了部分Actuator端点配置

## 二、运行时错误

### 2.1 ClassNotFoundException

**错误信息**:
```
java.lang.ClassNotFoundException: javax.servlet.http.HttpServlet
```

**原因**: 运行时类路径中缺少jakarta依赖

**解决方案**:
确保使用jakarta版本的依赖:
```xml
<dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>6.0.0</version>
</dependency>
```

### 2.2 NoSuchMethodError

**错误信息**:
```
java.lang.NoSuchMethodError: 'void xxx.method()'
```

**原因**: 依赖版本不匹配

**解决方案**:
1. 查看依赖冲突:
```bash
mvn dependency:tree -Dverbose
```

2. 使用BOM统一版本管理或显式指定版本

### 2.3 IllegalAccessError

**错误信息**:
```
java.lang.IllegalAccessError: class X (in unnamed module) cannot access class Y
```

**原因**: JDK 21强模块封装

**解决方案**:
在启动参数中添加:
```bash
java --add-opens java.base/java.lang=ALL-UNNAMED \
     --add-opens java.base/java.util=ALL-UNNAMED \
     -jar your-app.jar
```

或在pom.xml中配置:
```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <jvmArguments>
            --add-opens java.base/java.lang=ALL-UNNAMED
        </jvmArguments>
    </configuration>
</plugin>
```

### 2.4 连接池错误

**错误信息**:
```
Cannot load driver class: com.mysql.jdbc.Driver
```

**原因**: MySQL驱动类名变更

**解决方案**:
```yaml
# 旧配置
spring:
  datasource:
    driver-class-name: com.mysql.jdbc.Driver

# 新配置
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
```

## 三、测试问题

### 3.1 JUnit版本不兼容

**错误信息**:
```
org.junit.platform.commons.JUnitException
```

**原因**: JUnit 4与Spring Boot 3.x不兼容

**解决方案**:
迁移到JUnit 5:
```xml
<!-- 移除JUnit 4 -->
<!-- 添加JUnit 5 (Spring Boot 3.x默认包含) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

代码迁移:
```java
// JUnit 4
import org.junit.Test;
@Test
public void test() {}

// JUnit 5
import org.junit.jupiter.api.Test;
@Test
void test() {}
```

### 3.2 MockMvc测试失败

**错误信息**:
```
jakarta.servlet.ServletException: Request processing failed
```

**原因**: 测试配置需要更新

**解决方案**:
```java
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(UserController.class)
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void testGetUser() throws Exception {
        mockMvc.perform(get("/user/1"))
                .andExpect(status().isOk());
    }
}
```

## 四、性能问题

### 4.1 GC频率增加

**排查步骤**:
```bash
# 1. 启用GC日志
java -Xlog:gc*:file=gc.log:time,uptime,level,tags \
     -XX:+UseG1GC \
     -jar your-app.jar

# 2. 分析GC日志(使用GCEasy或GCViewer)

# 3. 调整GC参数
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -XX:G1HeapRegionSize=16m \
     -Xms4g -Xmx4g \
     -jar your-app.jar
```

### 4.2 内存占用增加

**排查步骤**:
```bash
# 1. 生成堆转储
jmap -dump:live,format=b,file=heap.hprof <pid>

# 2. 使用MAT分析内存泄漏

# 3. 启用Native Memory Tracking
java -XX:NativeMemoryTracking=detail -jar your-app.jar

# 4. 查看内存详情
jcmd <pid> VM.native_memory summary
```

### 4.3 启动时间变长

**优化方案**:
```bash
# 1. 使用CDS (Class Data Sharing)
java -Xshare:dump
java -Xshare:on -jar your-app.jar

# 2. 启用虚拟线程 (JDK 21特性)
spring.threads.virtual.enabled=true

# 3. 延迟加载
spring.main.lazy-initialization=true
```

## 五、依赖冲突

### 5.1 Jackson版本冲突

**错误信息**:
```
com.fasterxml.jackson.databind.JsonMappingException
```

**解决方案**:
```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.fasterxml.jackson</groupId>
            <artifactId>jackson-bom</artifactId>
            <version>2.16.1</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### 5.2 Netty版本冲突

**解决方案**:
```xml
<dependency>
    <groupId>io.netty</groupId>
    <artifactId>netty-bom</artifactId>
    <version>4.1.104.Final</version>
    <type>pom</type>
    <scope>import</scope>
</dependency>
```

## 六、配置文件问题

### 6.1 application.yml属性不生效

**检查清单**:
- [ ] 属性名是否正确(Spring Boot 3.x有变更)
- [ ] 缩进是否正确
- [ ] 是否有多个配置文件冲突
- [ ] Profile是否生效

### 6.2 数据源配置问题

**常见配置**:
```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/db?serverTimezone=Asia/Shanghai&useUnicode=true&characterEncoding=utf8&useSSL=false
    username: root
    password: root
    type: com.alibaba.druid.pool.DruidDataSource
```

## 七、IDE问题

### 7.1 IntelliJ IDEA

**问题**: IDE无法识别JDK 21

**解决方案**:
1. File → Project Structure → Project → SDK: 选择JDK 21
2. File → Settings → Build, Execution, Deployment → Compiler → Java Compiler: 设置Target bytecode version为21
3. 重新导入Maven项目

### 7.2 Eclipse

**问题**: Eclipse编译错误

**解决方案**:
1. 安装JDK 21支持插件
2. Project → Properties → Java Compiler: 设置Compiler compliance level为21
3. Maven → Update Project

## 八、快速诊断命令

```bash
# 检查JDK版本
java -version

# 检查Maven版本
mvn -version

# 查看有效POM
mvn help:effective-pom

# 查看依赖树
mvn dependency:tree

# 查看依赖冲突
mvn dependency:tree -Dverbose

# 强制更新快照
mvn clean install -U

# 跳过测试编译
mvn clean compile -DskipTests

# 查看插件版本
mvn help:effective-pom | grep -A 3 "maven-compiler-plugin"
```

## 九、回滚方案

如果升级后问题严重,使用备份快速回滚:
```bash
# 1. 恢复pom.xml
cp pom.xml.backup pom.xml

# 2. 恢复源代码(如果有修改)
git checkout <backup-branch>

# 3. 清理并重新编译
mvn clean compile
```

## 十、获取帮助

1. **查看官方文档**:
   - Spring Boot 3.x迁移指南
   - Jakarta EE迁移指南
   - JDK 21 Release Notes

2. **社区支持**:
   - Stack Overflow
   - Spring社区论坛
   - GitHub Issues

3. **企业内部**:
   - 联系架构组
   - 查看内部知识库
   - 提交GitLab Issue
