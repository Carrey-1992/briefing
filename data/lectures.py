BEA="https://www.anthropic.com/engineering/building-effective-agents"
MEM="https://docs.anthropic.com/en/docs/claude-code/memory"
ARCH="https://modelcontextprotocol.io/docs/learn/architecture"
JAVA="https://github.com/modelcontextprotocol/java-sdk"
def a(u,t="来源"): return f'<a href="{u}" target="_blank" rel="noopener">{t} ↗</a>'
LECT = {1: {
"goal":"能不看资料讲清：编码代理本质上是“LLM 在循环里使用工具、依据环境反馈推进”；知道规则文件（CLAUDE.md / AGENTS.md / Cursor rules）如何影响它；能说出代理在什么情况下会出错。",
"four":[
("是什么",f"""<p>Anthropic 把“代理式系统”分为两类：<b>工作流</b>（LLM 和工具按预先写好的代码路径编排）和<b>代理</b>（LLM 自己决定流程和工具使用）。{a(BEA)}</p>
<p>文中的说法：代理“通常只是在循环里、根据环境反馈使用工具的 LLM”，每一步都要从环境拿到“ground truth”（如工具调用结果、代码执行结果）来判断进展，并常设最大迭代次数等停止条件。{a(BEA)}</p>
<p>对编码代理来说，这个循环就是：读需求 → 读代码/搜索 → 改文件 → 跑测试或编译 → 看结果 → 再改，直到完成或需要人决策。</p>"""),
("为什么这样设计",f"""<p>文章建议<b>先用最简单的方案</b>，只在确有收益时增加复杂度；代理用延迟和成本换效果。{a(BEA)}</p>
<p>编码是代理的好场景，原因文中列了：代码可以用自动化测试验证、代理能用测试结果迭代、问题结构清晰、产出质量可客观衡量。{a(BEA)}</p>
<p>工具设计（文中称 ACI，代理-计算机接口）要像设计人机界面一样用心。例子：他们发现模型在切换目录后用相对路径容易出错，于是改成工具只接受绝对路径，问题消失。{a(BEA)}</p>
<p>规则文件的作用：Claude Code 每次会话都从全新上下文开始，CLAUDE.md 是你写下的持久指令，每次会话开头加载。{a(MEM)}</p>"""),
("什么时候会出问题",f"""<ul><li><b>错误累积</b>：自主性带来更高成本和“错误叠加”的风险，文章建议在沙箱里充分测试并加护栏。{a(BEA)}</li>
<li><b>规则不被遵守</b>：官方说明 CLAUDE.md 是“上下文，不是强制配置”，含糊或互相矛盾的指令可能被任选其一；要强制拦截某个操作应该用 hook（如 PreToolUse）。{a(MEM)}</li>
<li><b>规则文件太长</b>：官方建议每个 CLAUDE.md 控制在 200 行以内，越长越占上下文、遵守度越低。{a(MEM)}</li>
<li><b>框架遮蔽底层</b>：框架多一层抽象，会让底层 prompt 和响应难以调试；对“底层到底做了什么”的错误假设是常见错误来源。{a(BEA)}</li>
<li><b>上下文窗口与成本</b>：每轮循环都把历史、文件内容、工具结果放进上下文，任务越长越贵、越容易丢失早期信息。具体窗口大小和价格因模型而异，这里不写数字（未核实）。</li></ul>"""),
("怎么验证过","<p>完成本周实验后，在卡片里写下：有/无规则文件时，代理生成代码的 3 处具体差异；规则里哪一条没被遵守，你怎么改写后被遵守了。没做完实验之前，这一栏保持空白。</p>"),
],
"lab":f"""<ol><li>找一个小的 Java 项目（Spring Boot 或纯 Maven 均可），确保 <code>mvn test</code> 能跑通。</li>
<li><b>无规则基线</b>：不放任何规则文件，让 Claude Code（或 Cursor）完成一个小需求，例如“新增一个按名字查询用户的接口并写单测”。保存 diff。</li>
<li><b>加规则</b>：在项目根目录写 <code>CLAUDE.md</code>（或 Cursor 的规则文件），写 5–10 条可验证的规则，例如“构建命令是 mvn -q test”“Controller 放在 …/web 包”“禁止使用 field 注入，用构造器注入”“每个新接口必须有单测”。官方建议写成具体可检查的句子。{a(MEM)}</li>
<li>在 Claude Code 里运行 <code>/context</code>，确认 CLAUDE.md 出现在 Memory files 列表里。{a(MEM)}</li>
<li>新开会话，用同样的需求再跑一次，保存 diff。</li>
<li>对比两份 diff：包结构、注入方式、测试是否生成、是否自己跑了测试。记下哪条规则没被遵守，改写后再试一次。</li></ol>""",
"qa":[
("工作流和代理的区别是什么？","工作流：LLM 和工具按预先写好的代码路径编排；代理：LLM 自己动态决定流程和工具使用。"),
("为什么说编码是代理的好场景？","代码可用自动化测试验证，代理可以用测试结果迭代；问题结构清晰；质量可客观衡量。"),
("代理每一步为什么要拿“环境反馈”？","要靠工具结果或代码执行结果这类真实信息判断进展，否则错误会叠加；同时设最大迭代次数等停止条件。"),
("CLAUDE.md 写了规则，代理却没遵守，可能原因和对策？","CLAUDE.md 只是上下文不是强制配置；规则含糊、互相矛盾或文件过长都会降低遵守度。对策：写具体可验证的句子、保持短小、用 /context 确认已加载；必须拦截的操作用 hook。"),
("举一个“好的工具设计”的例子。","文中例子：模型在切换目录后用相对路径出错，把工具改成只接受绝对路径后就不再出错。思路是让工具更难被用错（poka-yoke）。"),
]},
2: {
"goal":"能不看资料画出 MCP 的 Host / Client / Server 关系和两层结构，说清 Tools / Resources / Prompts 的区别，知道 stdio 与 Streamable HTTP 的适用场景，并用 Java SDK 写出一个能被 AI 真实调用的最小 Server。",
"four":[
("是什么",f"""<p>MCP（Model Context Protocol）是 AI 应用与外部上下文/工具之间交换上下文的协议。它只管协议本身，不规定 AI 应用怎么用 LLM 或怎么管理拿到的上下文。{a(ARCH)}</p>
<p><b>参与者</b>：Host 是 AI 应用（如 Claude Code、VS Code）；Host 为每个 Server 创建一个 Client，每个 Client 与对应 Server 保持一条专用连接；Server 是提供上下文的程序，可以在本地或远程运行。{a(ARCH)}</p>
<p><b>两层</b>：数据层基于 JSON-RPC 2.0，定义发现、原语（tools / resources / prompts）和通知；传输层负责连接建立、消息分帧和鉴权。{a(ARCH)}</p>
<p><b>三类服务端原语</b>：Tools 是 AI 可调用的可执行函数（如查数据库）；Resources 是提供上下文的数据源（如文件内容、表结构）；Prompts 是可复用的交互模板（如 few-shot 示例）。每类都有 <code>*/list</code> 发现方法，Tool 用 <code>tools/call</code> 执行。{a(ARCH)}</p>"""),
("为什么这样设计",f"""<ul><li><b>一个 Server 一个 Client</b>：连接隔离，一个 Server 出问题不影响其他；Host 统一协调。{a(ARCH)}</li>
<li><b>数据层与传输层分离</b>：同一套 JSON-RPC 消息格式可以跑在 stdio 或 Streamable HTTP 上。{a(ARCH)}</li>
<li><b>两种传输</b>：stdio 用于同一台机器上的进程间通信，没有网络开销，本地 Server 通常只服务一个 Client；Streamable HTTP 用 HTTP POST 发客户端消息、可选 SSE 做流式，适合远程 Server，支持 bearer token、API key 等标准鉴权，官方推荐用 OAuth 获取令牌。{a(ARCH)}</li>
<li><b>无状态与按请求携带元数据</b>：当前官方架构页写明 MCP 是无状态协议，每个请求在 <code>_meta</code> 里带协议版本和能力，服务器不依赖之前的请求；Server 必须实现 <code>server/discover</code>，客户端可选在其他请求前调用。页面示例使用的协议版本是 <code>2026-07-28</code>。{a(ARCH)}（注意：旧版本规范使用 initialize 握手，你读到的旧教程可能与此不同，以官方当前文档为准。）</li>
<li><b>列表可动态变化</b>：先 <code>tools/list</code> 再调用，配合 <code>notifications/tools/list_changed</code> 通知，工具集可以运行时变化。{a(ARCH)}</li></ul>"""),
("什么时候会出问题",f"""<ul><li><b>通知可能丢</b>：官方说明通知是 best effort，跨传输重连时尤其不保证送达，客户端还应定期轮询保持新鲜。{a(ARCH)}</li>
<li><b>版本不匹配</b>：Server 不支持请求的协议版本时返回 <code>UnsupportedProtocolVersionError</code> 并列出支持的版本，客户端需重试。SDK 版本与规范版本对不上是常见坑。{a(ARCH)}</li>
<li><b>已弃用能力</b>：从协议版本 2026-07-28 起，客户端原语 Sampling 和 Logging 被标为弃用；新实现应直接对接 LLM 提供商 API，日志写 stderr（stdio）或用 OpenTelemetry。{a(ARCH)}</li>
<li><b>stdio 下乱打日志</b>：stdio 用标准输出传协议消息，往 stdout 打印日志会破坏消息流；应写 stderr（同上官方建议）。</li>
<li><b>工具描述写得差</b>：模型靠 name / description / inputSchema 决定是否和如何调用；名字含糊、参数不清会导致调错或不调。这与第 1 周的 ACI 原则一致。{a(BEA)}</li>
<li><b>远程 Server 的安全</b>：远程 Server 要做鉴权；工具能执行真实操作，权限要最小化。</li></ul>"""),
("怎么验证过","<p>完成实验后填写：你的 Server 暴露了哪几个 Tool，<code>tools/list</code> 的返回长什么样；AI 第一次是否调对了；你改了哪处描述后调用更准确。未做实验前保持空白。</p>"),
],
"lab":f"""<ol><li>打开 {a(JAVA,'MCP Java SDK 仓库')}，读 README 和示例，确认当前版本对应的 Maven 坐标与 Server 构建方式（SDK 的具体类名与版本号这里不写，未核实，以仓库为准）。</li>
<li>准备一个本地 CSV，例如 <code>users.csv</code>（id,name,city）。</li>
<li>用 SDK 写一个 <b>stdio</b> 传输的 Server，暴露 1 个 Tool：<code>users_find_by_city</code>，inputSchema 只有一个必填字符串参数 <code>city</code>，返回匹配行的文本。所有日志写 stderr。</li>
<li>可选：再暴露 1 个 Resource（CSV 的表头说明），体会 Tool 与 Resource 的区别。</li>
<li>打包成可执行 jar，在 Claude Code 里把它配置为 MCP Server（配置方法见 Claude Code 官方文档的 MCP 章节）。</li>
<li>问 AI“天津有哪些用户？”，观察它是否调用你的 Tool；故意把 description 写含糊再试一次，对比结果。</li>
<li>可选：用官方的 MCP Inspector 直接查看 <code>tools/list</code> 和 <code>tools/call</code> 的请求与响应。{a(ARCH)}</li></ol>""",
"qa":[
("Host、Client、Server 分别是什么，数量关系如何？","Host 是 AI 应用；Host 为每个 Server 创建一个 Client，Client 与 Server 一对一保持专用连接；一个 Host 可连多个 Server。"),
("MCP 的两层各负责什么？","数据层：基于 JSON-RPC 2.0 的消息结构与语义（发现、原语、通知）；传输层：连接建立、消息分帧、鉴权（stdio / Streamable HTTP）。"),
("Tools、Resources、Prompts 的区别？各举一例。","Tools：可执行操作，如查询数据库；Resources：只提供上下文数据，如表结构；Prompts：可复用交互模板，如 few-shot 示例。"),
("stdio 与 Streamable HTTP 怎么选？","本地同机进程、单客户端用 stdio，无网络开销；远程、多客户端用 Streamable HTTP，可用标准 HTTP 鉴权，官方推荐 OAuth。"),
("为什么 stdio Server 不能往 stdout 打日志？收到 list_changed 通知后客户端该做什么？","stdout 承载协议消息，日志会破坏消息流，应写 stderr。收到通知后重新调用 tools/list 刷新工具列表；通知是 best effort，还要定期轮询。"),
]}}
