# 练习待办数据。增删待办只改这里，然后运行 publish.sh。
# 每个待办：id（唯一，勾选状态按 id 存储）、title、goal、week（对应周）、steps[(id, 标题, HTML 说明)]、compose（可选）、refs[(标题, url)]
TODOS = [
 {"id": "grafana-home", "title": "Grafana 家里电脑练习", "week": 11,
  "goal": "用 Docker Compose 起 Grafana + Prometheus + Redis + RabbitMQ + Kafka，学会用 Grafana 看这三个中间件。",
  "steps": [
   ("s1", "Compose 起 Grafana 和 Prometheus",
    "<p>Grafana 镜像 <code>grafana/grafana</code>（开源版；官方说明从 12.4.0 起 <code>grafana/grafana-oss</code> 不再更新），端口 <b>3000</b>。Prometheus 镜像 <code>prom/prometheus</code>，端口 <b>9090</b>。在 Grafana 里添加 Prometheus 数据源，地址填 <code>http://prometheus:9090</code>（同一 Compose 网络内用服务名）。</p>"),
   ("s2", "Redis：数据源插件 + redis_exporter",
    "<p>① 官方 Redis 数据源插件 ID 为 <code>redis-datasource</code>，安装命令 <code>grafana-cli plugins install redis-datasource</code>（在 Grafana 容器内执行后重启容器），连 Redis 查键值和 INFO。② 再试 <code>oliver006/redis_exporter</code>，默认端口 <b>9121</b>，用环境变量 <code>REDIS_ADDR</code> 指定 Redis 地址，Prometheus 抓 <code>redis-exporter:9121</code>。</p><p class='uv'>未核实：插件在 Grafana 中的具体查询界面和支持的命令列表。</p>"),
   ("s3", "RabbitMQ：rabbitmq_prometheus",
    "<p>启用自带插件 <code>rabbitmq-plugins enable rabbitmq_prometheus</code>，指标在 <b>15692</b> 端口 <code>/metrics</code>。管理界面镜像 <code>rabbitmq:4-management</code>，管理端口 <b>15672</b>。Prometheus 抓 <code>rabbitmq:15692</code>，Grafana 画队列堆积和消费速率。</p><p class='uv'>未核实：官方镜像是否默认已启用 rabbitmq_prometheus（启动后 curl 15692 看一下即知）；具体指标名请以 /metrics 输出为准。</p>"),
   ("s4", "Kafka：Exporter 看消费组 lag，命令行/Kafka UI 看消息",
    "<p>Kafka 官方镜像 <code>apache/kafka</code>，端口 <b>9092</b>（官网示例用的是 4.4.0 标签）。Kafka Exporter 镜像 <code>danielqsj/kafka-exporter</code>，端口 <b>9308</b>，参数 <code>--kafka.server=kafka:9092</code>，Prometheus 抓它看消费组 lag。也可用 JMX Exporter（prometheus/jmx_exporter）。看消息内容：<code>bin/kafka-console-consumer.sh --topic 主题 --from-beginning --bootstrap-server localhost:9092</code>，或 Kafka UI（<code>ghcr.io/kafbat/kafka-ui</code>，端口 8080）。</p><p class='uv'>未核实：apache/kafka 默认对外通告地址是否让其他容器（exporter、Kafka UI）用 <code>kafka:9092</code> 连上；很可能需要配置 listeners/advertised.listeners 环境变量，请对照 Docker Hub 页面说明。JMX Exporter 的具体配置未核实。</p>"),
   ("s5", "记一张四栏卡片",
    "<p>是什么 / 为什么这样设计 / 什么时候会出问题 / 怎么验证过。重点：Grafana 不存数据；指标（Prometheus）和数据内容（数据源插件、命令行）是两种看法。</p>"),
  ],
  "compose": """# 未在本机运行验证；只含官方文档能确认的镜像和端口
services:
  grafana:
    image: grafana/grafana
    ports: ["3000:3000"]
  prometheus:
    image: prom/prometheus
    ports: ["9090:9090"]
    volumes: ["./prometheus.yml:/etc/prometheus/prometheus.yml"]
  redis:
    image: redis
    ports: ["6379:6379"]
  redis-exporter:
    image: oliver006/redis_exporter
    environment: ["REDIS_ADDR=redis://redis:6379"]
    ports: ["9121:9121"]
  rabbitmq:
    image: rabbitmq:4-management
    ports: ["5672:5672", "15672:15672", "15692:15692"]
  kafka:
    image: apache/kafka:4.4.0
    ports: ["9092:9092"]
    # 未核实：容器间访问需要的 listeners 配置
  kafka-exporter:
    image: danielqsj/kafka-exporter
    command: ["--kafka.server=kafka:9092"]
    ports: ["9308:9308"]

# prometheus.yml（同目录）
# scrape_configs:
#   - job_name: redis
#     static_configs: [{targets: ["redis-exporter:9121"]}]
#   - job_name: rabbitmq
#     static_configs: [{targets: ["rabbitmq:15692"]}]
#   - job_name: kafka
#     static_configs: [{targets: ["kafka-exporter:9308"]}]""",
  "refs": [
   ("Grafana Docker 安装", "https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/"),
   ("Grafana Redis 数据源插件", "https://grafana.com/grafana/plugins/redis-datasource/"),
   ("Prometheus 安装（Docker）", "https://prometheus.io/docs/prometheus/latest/installation/"),
   ("redis_exporter", "https://github.com/oliver006/redis_exporter"),
   ("RabbitMQ Prometheus 监控", "https://www.rabbitmq.com/docs/prometheus"),
   ("RabbitMQ 下载与 Docker 镜像", "https://www.rabbitmq.com/docs/download"),
   ("Kafka 快速入门", "https://kafka.apache.org/quickstart"),
   ("apache/kafka Docker 镜像", "https://hub.docker.com/r/apache/kafka"),
   ("Kafka Exporter", "https://github.com/danielqsj/kafka_exporter"),
   ("JMX Exporter", "https://github.com/prometheus/jmx_exporter"),
   ("Kafka UI（kafbat）", "https://github.com/kafbat/kafka-ui"),
  ]},
]
