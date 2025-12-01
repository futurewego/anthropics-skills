# POC 代码模板集

本文档提供常见技术场景的 POC 验证代码模板,帮助快速验证技术可行性。

## 模板目录

1. [Redis 分布式锁验证](#1-redis-分布式锁验证)
2. [消息队列集成验证](#2-消息队列集成验证)
3. [分布式事务验证](#3-分布式事务验证)
4. [API 网关集成验证](#4-api-网关集成验证)
5. [缓存性能对比](#5-缓存性能对比)

---

## 1. Redis 分布式锁验证

### 场景
验证 Redisson 分布式锁在高并发场景下的正确性和性能。

### pom.xml 依赖
```xml
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <version>3.11.6</version>
</dependency>
```

### 配置类
```java
import org.redisson.Redisson;
import org.redisson.api.RedissonClient;
import org.redisson.config.Config;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RedissonConfig {
    
    @Bean
    public RedissonClient redissonClient() {
        Config config = new Config();
        config.useSingleServer()
              .setAddress("redis://127.0.0.1:6379")
              .setConnectionPoolSize(50)
              .setConnectionMinimumIdleSize(10);
        return Redisson.create(config);
    }
}
```

### 核心验证代码
```java
import cn.hutool.core.util.IdUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RLock;
import org.redisson.api.RedissonClient;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 分布式锁 POC 验证
 * 目标: 验证在高并发场景下,分布式锁能否保证资源访问的互斥性
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DistributedLockPocService {
    
    private final RedissonClient redissonClient;
    
    // 模拟共享资源 (库存)
    private final AtomicInteger stock = new AtomicInteger(100);
    
    /**
     * 无锁扣减库存 (用于对比)
     */
    public boolean deductStockWithoutLock(String orderId) {
        if (stock.get() <= 0) {
            log.warn("库存不足,订单: {}", orderId);
            return false;
        }
        
        // 模拟业务处理耗时
        try {
            Thread.sleep(10);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        int remaining = stock.decrementAndGet();
        log.info("订单: {} 扣减成功,剩余库存: {}", orderId, remaining);
        return true;
    }
    
    /**
     * 使用分布式锁扣减库存
     */
    public boolean deductStockWithLock(String orderId) {
        String lockKey = "stock:lock";
        RLock lock = redissonClient.getLock(lockKey);
        
        try {
            // 尝试获取锁,最多等待 5 秒,锁自动释放时间 10 秒
            boolean acquired = lock.tryLock(5, 10, TimeUnit.SECONDS);
            
            if (!acquired) {
                log.warn("获取锁失败,订单: {}", orderId);
                return false;
            }
            
            // 获取锁成功,执行业务逻辑
            if (stock.get() <= 0) {
                log.warn("库存不足,订单: {}", orderId);
                return false;
            }
            
            // 模拟业务处理耗时
            Thread.sleep(10);
            
            int remaining = stock.decrementAndGet();
            log.info("订单: {} 扣减成功,剩余库存: {}", orderId, remaining);
            return true;
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            log.error("扣减库存异常,订单: {}", orderId, e);
            return false;
        } finally {
            // 释放锁
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
}
```

### 测试代码
```java
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 分布式锁性能与正确性测试
 */
@Slf4j
@SpringBootTest
class DistributedLockPocTest {
    
    @Autowired
    private DistributedLockPocService lockService;
    
    /**
     * 测试: 1000 个并发请求,验证是否会出现超卖
     */
    @Test
    void testConcurrentDeductWithoutLock() throws InterruptedException {
        int threadCount = 1000;
        ExecutorService executor = Executors.newFixedThreadPool(50);
        CountDownLatch latch = new CountDownLatch(threadCount);
        
        AtomicInteger successCount = new AtomicInteger(0);
        
        long startTime = System.currentTimeMillis();
        
        for (int i = 0; i < threadCount; i++) {
            final int orderId = i;
            executor.submit(() -> {
                try {
                    boolean result = lockService.deductStockWithoutLock("ORDER-" + orderId);
                    if (result) {
                        successCount.incrementAndGet();
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await();
        executor.shutdown();
        
        long duration = System.currentTimeMillis() - startTime;
        
        log.info("========== 无锁测试结果 ==========");
        log.info("总请求数: {}", threadCount);
        log.info("成功数: {}", successCount.get());
        log.info("耗时: {} ms", duration);
        log.info("预期成功数: 100 (初始库存)");
        log.info("是否超卖: {}", successCount.get() > 100);
    }
    
    /**
     * 测试: 1000 个并发请求,使用分布式锁
     */
    @Test
    void testConcurrentDeductWithLock() throws InterruptedException {
        int threadCount = 1000;
        ExecutorService executor = Executors.newFixedThreadPool(50);
        CountDownLatch latch = new CountDownLatch(threadCount);
        
        AtomicInteger successCount = new AtomicInteger(0);
        
        long startTime = System.currentTimeMillis();
        
        for (int i = 0; i < threadCount; i++) {
            final int orderId = i;
            executor.submit(() -> {
                try {
                    boolean result = lockService.deductStockWithLock("ORDER-" + orderId);
                    if (result) {
                        successCount.incrementAndGet();
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await();
        executor.shutdown();
        
        long duration = System.currentTimeMillis() - startTime;
        
        log.info("========== 分布式锁测试结果 ==========");
        log.info("总请求数: {}", threadCount);
        log.info("成功数: {}", successCount.get());
        log.info("耗时: {} ms", duration);
        log.info("预期成功数: 100 (初始库存)");
        log.info("是否准确: {}", successCount.get() == 100);
    }
}
```

### 验证指标
- **正确性**: 是否出现超卖 (成功数应 <= 初始库存)
- **性能**: TPS (总请求数 / 耗时秒数)
- **可用性**: 获取锁失败率

---

## 2. 消息队列集成验证

### 场景
验证 RabbitMQ 与 Spring Boot 3.x 的集成,测试消息可靠性。

### pom.xml 依赖
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-amqp</artifactId>
</dependency>
```

### 配置
```yaml
spring:
  rabbitmq:
    host: localhost
    port: 5672
    username: guest
    password: guest
    # 开启消息确认
    publisher-confirm-type: correlated
    publisher-returns: true
    template:
      mandatory: true
```

### 生产者
```java
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class OrderMessageProducer {
    
    private final RabbitTemplate rabbitTemplate;
    
    private static final String EXCHANGE = "order.exchange";
    private static final String ROUTING_KEY = "order.created";
    
    public void sendOrderCreatedMessage(String orderId) {
        String message = "订单创建: " + orderId;
        
        rabbitTemplate.convertAndSend(EXCHANGE, ROUTING_KEY, message, msg -> {
            // 设置消息持久化
            msg.getMessageProperties().setDeliveryMode(MessageDeliveryMode.PERSISTENT);
            return msg;
        });
        
        log.info("发送消息: {}", message);
    }
}
```

### 消费者
```java
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class OrderMessageConsumer {
    
    @RabbitListener(queues = "order.queue")
    public void handleOrderCreated(String message) {
        log.info("收到消息: {}", message);
        
        // 模拟业务处理
        try {
            Thread.sleep(100);
            log.info("消息处理完成: {}", message);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            log.error("消息处理失败: {}", message, e);
        }
    }
}
```

### 测试代码
```java
@Test
void testMessageReliability() throws InterruptedException {
    int messageCount = 1000;
    
    for (int i = 0; i < messageCount; i++) {
        producer.sendOrderCreatedMessage("ORDER-" + i);
    }
    
    // 等待消费完成
    Thread.sleep(30000);
    
    // 验证: 检查消费日志,确认消息无丢失
}
```

---

## 3. 分布式事务验证

### 场景
使用 Seata AT 模式验证分布式事务的一致性。

### pom.xml 依赖
```xml
<dependency>
    <groupId>io.seata</groupId>
    <artifactId>seata-spring-boot-starter</artifactId>
    <version>1.6.1</version>
</dependency>
```

### 配置
```yaml
seata:
  enabled: true
  application-id: order-service
  tx-service-group: default_tx_group
  registry:
    type: nacos
    nacos:
      server-addr: localhost:8848
```

### 业务代码
```java
import io.seata.spring.annotation.GlobalTransactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class OrderService {
    
    private final OrderMapper orderMapper;
    private final StockFeignClient stockClient;
    private final AccountFeignClient accountClient;
    
    /**
     * 全局事务: 创建订单 + 扣减库存 + 扣减账户余额
     */
    @GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
    public void createOrder(String orderId, int productId, int amount) {
        // 1. 创建订单
        Order order = new Order();
        order.setOrderId(orderId);
        order.setProductId(productId);
        order.setAmount(amount);
        orderMapper.insert(order);
        
        // 2. 远程调用: 扣减库存
        stockClient.deduct(productId, 1);
        
        // 3. 远程调用: 扣减账户余额
        accountClient.deduct("USER123", amount);
        
        // 模拟异常: 验证是否回滚
        if (amount > 1000) {
            throw new RuntimeException("金额超限,触发回滚");
        }
    }
}
```

### 验证要点
- 正常流程: 订单、库存、账户数据一致
- 异常回滚: 触发异常后,三方数据全部回滚
- 性能影响: 对比无事务场景的性能损耗

---

## 4. API 网关集成验证

### 场景
验证 Spring Cloud Gateway 与后端服务的集成。

### pom.xml 依赖
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-gateway</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-loadbalancer</artifactId>
</dependency>
```

### 配置
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100
                redis-rate-limiter.burstCapacity: 200
```

### 自定义过滤器
```java
import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Slf4j
@Component
public class LoggingFilter implements GlobalFilter, Ordered {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        long startTime = System.currentTimeMillis();
        String path = exchange.getRequest().getURI().getPath();
        
        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            long duration = System.currentTimeMillis() - startTime;
            log.info("请求路径: {}, 耗时: {} ms", path, duration);
        }));
    }
    
    @Override
    public int getOrder() {
        return -1;
    }
}
```

### 压力测试
使用 JMeter 或 wrk 进行压测:
```bash
wrk -t 10 -c 100 -d 30s http://localhost:8080/api/orders/1
```

验证指标:
- 吞吐量 (RPS)
- 延迟 (P95, P99)
- 限流效果

---

## 5. 缓存性能对比

### 场景
对比 Caffeine (本地缓存) + Redis (分布式缓存) 的性能差异。

### pom.xml 依赖
```xml
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <version>3.11.6</version>
</dependency>
```

### 配置
```java
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

@Configuration
public class CacheConfig {
    
    @Bean
    public Cache<String, Object> caffeineCache() {
        return Caffeine.newBuilder()
                .maximumSize(10000)
                .expireAfterWrite(10, TimeUnit.MINUTES)
                .recordStats()
                .build();
    }
}
```

### 性能测试
```java
@Test
void testCachePerformance() {
    int iterations = 100000;
    
    // 测试 Caffeine
    long caffeineStart = System.currentTimeMillis();
    for (int i = 0; i < iterations; i++) {
        String key = "key-" + (i % 1000);
        caffeineCache.get(key, k -> "value-" + k);
    }
    long caffeineDuration = System.currentTimeMillis() - caffeineStart;
    
    // 测试 Redis
    long redisStart = System.currentTimeMillis();
    for (int i = 0; i < iterations; i++) {
        String key = "key-" + (i % 1000);
        redissonClient.getBucket(key).get();
    }
    long redisDuration = System.currentTimeMillis() - redisStart;
    
    log.info("Caffeine 耗时: {} ms, TPS: {}", caffeineDuration, iterations * 1000 / caffeineDuration);
    log.info("Redis 耗时: {} ms, TPS: {}", redisDuration, iterations * 1000 / redisDuration);
}
```

---

## POC 最佳实践

1. **明确验证目标**: 每个 POC 聚焦 1-2 个核心指标
2. **真实场景模拟**: 使用生产环境的数据量和并发量
3. **可视化结果**: 使用图表展示性能数据
4. **文档化**: 记录验证过程、环境配置、结论
5. **可复现**: 提供完整的代码和配置,便于他人复现

## 注意事项

- POC 代码不是生产代码,重点在于快速验证,不需要完善的异常处理
- 性能测试应在独立环境进行,避免干扰
- 记录详细的测试环境信息 (机器配置、网络延迟等)
- 对比测试时保持环境一致性
