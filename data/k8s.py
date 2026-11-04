# 专项：K8s 与调度器。只引用实际读过的官方文档（2026-11-04 读取）。增删内容改这里，运行 publish.sh。
R = {
 "comp":("K8s 组件概览","https://kubernetes.io/docs/concepts/overview/components/"),
 "ctrl":("K8s 控制器（控制循环）","https://kubernetes.io/docs/concepts/architecture/controller/"),
 "api":("K8s API 概念（list/watch、resourceVersion）","https://kubernetes.io/docs/reference/using-api/api-concepts/"),
 "libs":("K8s 官方客户端库列表","https://kubernetes.io/docs/reference/using-api/client-libraries/"),
 "jc":("kubernetes-client/java（官方 Java 客户端）","https://github.com/kubernetes-client/java"),
 "jcex":("Java 客户端代码示例（Wiki）","https://github.com/kubernetes-client/java/wiki/3.-Code-Examples"),
 "jcwatch":("WatchExample.java","https://github.com/kubernetes-client/java/blob/master/examples/examples-release-latest/src/main/java/io/kubernetes/client/examples/WatchExample.java"),
 "kind":("kind 快速开始","https://kind.sigs.k8s.io/docs/user/quick-start/"),
 "tools":("kubectl 等工具安装","https://kubernetes.io/docs/tasks/tools/"),
 "ks":("kube-scheduler","https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/"),
 "fw":("调度框架（Scheduling Framework）","https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/"),
 "res":("容器资源管理（requests/limits）","https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/"),
 "aff":("把 Pod 分配到节点（亲和/反亲和）","https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/"),
 "taint":("污点与容忍","https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/"),
 "prio":("Pod 优先级与抢占","https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/"),
 "ns":("Namespace","https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/"),
 "quota":("ResourceQuota","https://kubernetes.io/docs/concepts/policy/resource-quotas/"),
 "lr":("LimitRange","https://kubernetes.io/docs/concepts/policy/limit-range/"),
 "rbac":("RBAC 鉴权","https://kubernetes.io/docs/reference/access-authn-authz/rbac/"),
 "mt":("K8s 多租户","https://kubernetes.io/docs/concepts/security/multi-tenancy/"),
 "job":("Job","https://kubernetes.io/docs/concepts/workloads/controllers/job/"),
 "cron":("CronJob","https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/"),
 "dp":("设备插件（Device Plugins）","https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/device-plugins/"),
 "gpu":("调度 GPU","https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/"),
 "extn":("给节点通告扩展资源","https://kubernetes.io/docs/tasks/administer-cluster/extended-resource-node/"),
 "extp":("给容器分配扩展资源","https://kubernetes.io/docs/tasks/configure-pod-container/extended-resource/"),
 "kq":("Kueue 概览","https://kueue.sigs.k8s.io/docs/overview/"),
 "kqi":("Kueue 安装","https://kueue.sigs.k8s.io/docs/getting-started/installation/"),
 "kqq":("Kueue：管理集群配额","https://kueue.sigs.k8s.io/docs/tasks/manage/administer_cluster_quotas/"),
 "kqj":("Kueue：运行 Job","https://kueue.sigs.k8s.io/docs/tasks/run/jobs/"),
 "vc":("Volcano 文档","https://volcano.sh/en/docs/"),
 "slurm":("Slurm 概览","https://slurm.schedmd.com/overview.html"),
}
def a(k): t,u=R[k]; return f'<a href="{u}" target="_blank" rel="noopener">{t} ↗</a>'
UV = lambda s: f'<p class="uv">未核实：{s}</p>'
def pre(s): import html; return '<pre class="cmp">'+html.escape(s.strip())+'</pre>'

M = [
{"id":"k8s-01","title":"K8s 核心与 API 交互","short":"核心与 API",
 "goal":"能不看资料讲清：一个 Pod 从 kubectl apply 到跑起来经过哪些组件；为什么 K8s 是“声明式 + 调谐循环”；list-watch 和 resourceVersion 怎么让客户端低成本追踪变化。能用 kubectl 和 Java 客户端列出、创建、监听 Pod。",
 "four":[
("是什么",f"""<p><b>控制平面</b>：kube-apiserver（暴露 K8s HTTP API，是唯一入口）、etcd（保存全部 API 数据的一致、高可用键值存储）、kube-scheduler（为还没绑定节点的 Pod 选节点）、kube-controller-manager（运行各类控制器）。<b>节点</b>上有 kubelet（保证 Pod 及其容器在跑）和容器运行时。{a('comp')}</p>
<p><b>Pod</b> 是最小调度单位；<b>Deployment</b> 声明“要几个副本、用什么模板”；<b>Service</b> 给一组 Pod 一个稳定访问入口。</p>
<p><b>控制器</b>是一个“控制循环”：盯住集群的当前状态，让它向期望状态靠近。{a('ctrl')}</p>"""),
("为什么这样设计",f"""<p>你只写期望状态（spec），由控制器不断对比实际状态（status）并修正，这就是<b>声明式 + 调谐</b>。好处：组件挂掉重启后再对比一次就能自愈，不依赖“某条命令一定执行成功”。{a('ctrl')}</p>
<p>所有组件都只和 API Server 交互、不直接改 etcd，API Server 统一做鉴权、准入和校验。</p>
<p><b>list-watch</b>：客户端先 list 拿到全量和集合的 resourceVersion，再从这个版本开始 watch 增量变化，避免反复轮询全量。每个对象都有 resourceVersion 字段。{a('api')} Java 客户端的 Informer 就是在 list-watch 之上加本地缓存。{a('jcex')}</p>"""),
("什么时候会出问题",f"""<ul><li><b>watch 版本过旧</b>：请求的 resourceVersion 已不可用时，API Server 返回 <b>410 Gone</b>，客户端必须重新 list 再 watch。{a('api')}自己写 watch 循环不处理它，就会丢事件或死循环。</li>
<li><b>直接轮询 list</b>：大集群里频繁全量 list 会压垮 API Server，所以要用 Informer 缓存读。</li>
<li><b>以为命令式改动会保留</b>：手动改了 Deployment 管的 Pod，控制器会按模板改回去。</li>
<li><b>etcd 是单一事实来源</b>：etcd 不可用时集群无法变更（已运行的 Pod 一般继续跑）。</li></ul>{UV('etcd 故障时已运行 Pod 的具体表现，按经验描述，未在官方文档逐条核对。')}"""),
("怎么验证过","<p>做完下面实验后自己填：① 删掉 Deployment 的一个 Pod，看它被重建（调谐）；② Java watch 程序打印 ADDED/MODIFIED/DELETED 的顺序；③ 用 <code>kubectl get pod -v=6</code> 看 kubectl 实际发出的 HTTP 请求。</p>"),
 ],
 "lab":"""<p class="uv">以下命令未在本机运行验证（本机没有 Docker），按官方文档整理。</p>
<h4>1. 装 kind 和 kubectl，建集群</h4><p>按 """+a('kind')+""" 和 """+a('tools')+""" 安装（macOS 可用 <code>brew install kind kubectl</code>；Windows/Linux 见文档）。需要先装好 Docker。</p>"""+pre("""
kind create cluster            # 默认集群名 kind
kubectl cluster-info --context kind-kind
kubectl get nodes""")+"""
<h4>2. kubectl 看声明式与调谐</h4>"""+pre("""
kubectl create deployment web --image=nginx --replicas=2
kubectl get pods -l app=web -w      # 另开一个终端保持观察
kubectl delete pod -l app=web --wait=false   # 看控制器把 Pod 补回 2 个
kubectl expose deployment web --port=80
kubectl get svc,endpoints web
kubectl get pod -v=6                # 看实际 HTTP 请求""")+"""
<h4>3. Java 客户端：列出 / 创建 / 监听 Pod</h4><p>选官方 """+a('jc')+"""（K8s 官方客户端库列表中的 Java 客户端）。Maven Central 当前最新版本 <b>28.0.0</b>。注意 README 说明：从 20.0.0 起 API 不向后兼容，可选参数合并为一个请求对象（调用以 <code>.execute()</code> 结尾），且不再支持 Java 8。</p>"""+pre("""
<!-- pom.xml -->
<dependency>
  <groupId>io.kubernetes</groupId>
  <artifactId>client-java</artifactId>
  <version>28.0.0</version>
</dependency>""")+pre("""
import io.kubernetes.client.openapi.*;
import io.kubernetes.client.openapi.apis.CoreV1Api;
import io.kubernetes.client.openapi.models.*;
import io.kubernetes.client.util.*;
import com.google.gson.reflect.TypeToken;
import java.util.concurrent.TimeUnit;

public class PodLab {
  public static void main(String[] a) throws Exception {
    ApiClient client = Config.defaultClient();          // 读 ~/.kube/config
    client.setHttpClient(client.getHttpClient().newBuilder()
        .readTimeout(0, TimeUnit.SECONDS).build());     // watch 需要无限读超时
    Configuration.setDefaultApiClient(client);
    CoreV1Api api = new CoreV1Api();

    // 1) 列出（与官方 Example.java 一致）
    for (V1Pod p : api.listPodForAllNamespaces().execute().getItems())
      System.out.println(p.getMetadata().getNamespace() + "/" + p.getMetadata().getName());

    // 2) 创建（未核实：createNamespacedPod 新式写法）
    V1Pod pod = new V1Pod().metadata(new V1ObjectMeta().name("java-demo"))
        .spec(new V1PodSpec().addContainersItem(
            new V1Container().name("c").image("nginx")));
    api.createNamespacedPod("default", pod).execute();

    // 3) 监听（仿照官方 WatchExample.java，把 Namespace 换成 Pod）
    try (Watch<V1Pod> w = Watch.createWatch(client,
        api.listNamespacedPod("default").watch(true).buildCall(null),
        new TypeToken<Watch.Response<V1Pod>>(){}.getType())) {
      for (Watch.Response<V1Pod> e : w)
        System.out.println(e.type + " " + e.object.getMetadata().getName()
            + " " + e.object.getStatus().getPhase());
    }
  }
}""")+UV("列出与 watch 写法来自官方 Example.java / WatchExample.java；createNamespacedPod 与 listNamespacedPod 的新式调用是照同一风格推断，未编译验证。")+"""
<p>运行后，另开终端执行 <code>kubectl delete pod java-demo</code>，看 watch 打印的事件序列。进阶：官方示例里的 <b>InformerExample</b>（需要 <code>client-java-extended</code> 模块）演示 list-watch + 本地缓存，见 """+a('jcex')+"""。</p>""",
 "lab_out":"Java 程序能列出/创建/监听 Pod，写一张“list-watch 与 410 Gone”卡片",
 "qa":[
("kubectl apply 一个 Deployment 后，到容器跑起来，依次经过哪些组件？","kubectl → kube-apiserver（鉴权/准入/校验，写入 etcd）→ Deployment 控制器创建 ReplicaSet → ReplicaSet 控制器创建 Pod → kube-scheduler 为未绑定 Pod 选节点并绑定 → 该节点 kubelet 通过容器运行时拉起容器并上报状态。"),
("什么是调谐循环？为什么比命令式更能自愈？","控制器反复比较期望状态和当前状态并采取动作使其靠近。即使中间失败或组件重启，下一轮对比仍会纠正，不依赖某条命令一次成功。"),
("list-watch 中 resourceVersion 起什么作用？","list 返回集合的 resourceVersion，watch 从该版本开始推送之后的增量变化；每个对象也带 resourceVersion，标识其存储版本。"),
("watch 收到 410 Gone 怎么办？","说明请求的版本已不可用（太旧），需要重新 list 拿新版本，再从新版本 watch。Informer 会自动处理。"),
("为什么推荐用 Informer 而不是定时 list？","Informer 只做一次 list 加持续 watch，读操作走本地缓存，显著减轻 API Server 压力，并能以事件回调方式响应变化。"),
 ],
 "refs":["comp","ctrl","api","libs","jc","jcex","jcwatch","kind","tools"]},

{"id":"k8s-02","title":"kube-scheduler 调度器","short":"调度器",
 "goal":"能讲清 kube-scheduler 的“过滤 → 打分 → 绑定”；知道 requests 而不是实际用量决定能否调度；会用 describe/events 定位 Pending 原因；理解亲和、污点容忍、优先级抢占和调度框架扩展点各解决什么问题。",
 "four":[
("是什么",f"""<p>kube-scheduler 监视新建且未分配节点的 Pod，为每个 Pod 找最合适的节点。满足要求的节点称为<b>可行节点（feasible nodes）</b>；没有可行节点时 Pod 保持未调度（Pending），直到能放下。选点分两步：<b>过滤（Filtering）</b>找可行节点，<b>打分（Scoring）</b>给可行节点排序，选最高分；然后把决定通知 API Server，这一步叫<b>绑定（binding）</b>。{a('ks')}</p>
<p><b>调度框架</b>把流程拆成扩展点：PreEnqueue、QueueSort、PreFilter、Filter、PostFilter、PreScore、Score、NormalizeScore、Reserve、Permit、PreBind、Bind、PostBind。每次调度分为<b>调度周期</b>（串行）和<b>绑定周期</b>（可并发）。{a('fw')}</p>"""),
("为什么这样设计",f"""<p><b>requests 决定调度</b>：调度器只看节点可分配量与已调度 Pod 的 requests 之和，不看实际用量；limits 由 kubelet/运行时在运行期限制。{a('res')}</p>
<p><b>约束分层</b>：nodeSelector/节点亲和描述“Pod 想去哪”，Pod 亲和/反亲和描述“和谁放一起/分开”；{a('aff')}<b>污点</b>反过来让节点“排斥”Pod，只有带匹配<b>容忍</b>的 Pod 才能上去，适合专用节点（如 GPU 节点）。{a('taint')}</p>
<p><b>优先级与抢占</b>：放不下时，抢占逻辑找一个节点，驱逐其上优先级更低的 Pod 来腾地方。{a('prio')}</p>
<p><b>扩展点</b>让你用插件定制，而不用 fork 整个调度器。{a('fw')}</p>"""),
("什么时候会出问题",f"""<ul><li><b>requests 写太大</b>：节点明明很闲，Pod 却 Pending；写太小则节点超卖、运行期争抢。{a('res')}</li>
<li><b>绕过调度器</b>：手动设 <code>spec.nodeName</code> 会绕过调度器，污点等检查都不生效。{a('taint')}</li>
<li><b>硬亲和/反亲和过严</b>：requiredDuringScheduling 规则找不到满足的节点就永远 Pending。{a('aff')}</li>
<li><b>NoExecute 污点</b>：会驱逐节点上已运行且不容忍的 Pod，不只是阻止新调度。{a('taint')}</li>
<li><b>抢占误伤</b>：高优先级 Pod 一多，低优先级批任务会被反复驱逐。{a('prio')}</li></ul>"""),
("怎么验证过","<p>实验后填写：① 把 Pending Pod 的 Events 原文抄下来，解释每个“0/N nodes are available”后面的原因；② 污点加上/去掉前后，Pod 状态如何变化；③ 打分阶段你观察不到，想一想怎么验证（提示：调高调度器日志级别，未核实具体方法）。</p>"),
 ],
 "lab":"""<p class="uv">以下命令未在本机运行验证。建议用多节点 kind 集群，方便观察调度。</p>"""+pre("""
# kind 多节点配置 kind-3.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker""")+pre("""
kind create cluster --name sched --config kind-3.yaml
kubectl get nodes        # 记下两个 worker 节点名，下面用 <w1> <w2> 代替""")+"""
<h4>1. 构造 Pending：requests 超过任何节点</h4>"""+pre("""
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata: {name: big}
spec:
  containers:
  - name: c
    image: nginx
    resources: {requests: {cpu: "100", memory: "1Gi"}}
EOF
kubectl get pod big            # STATUS 应为 Pending
kubectl describe pod big       # 看最底部 Events 的 FailedScheduling 原因
kubectl get events --field-selector involvedObject.name=big""")+"""
<h4>2. 污点与容忍</h4>"""+pre("""
kubectl taint nodes <w1> dedicated=gpu:NoSchedule
kubectl taint nodes <w2> dedicated=gpu:NoSchedule
kubectl run t1 --image=nginx           # 应 Pending（control-plane 默认也有污点）
kubectl describe pod t1 | tail -5
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata: {name: t2}
spec:
  tolerations:
  - {key: dedicated, operator: Equal, value: gpu, effect: NoSchedule}
  containers: [{name: c, image: nginx}]
EOF
kubectl get pod -o wide                # t2 能调度上去
kubectl taint nodes <w1> dedicated=gpu:NoSchedule-   # 去掉污点，观察 t1""")+UV("kind 的 control-plane 节点默认是否带 NoSchedule 污点，用 kubectl describe node 自查。")+"""
<h4>3. 节点亲和（硬性）</h4>"""+pre("""
kubectl label nodes <w2> disk=ssd
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata: {name: aff}
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - {key: disk, operator: In, values: [ssd]}
  containers: [{name: c, image: nginx}]
EOF
kubectl get pod aff -o wide   # 若 <w2> 仍有污点则 Pending，想想为什么""")+"""
<h4>4.（选做）优先级与抢占</h4><p>按 """+a('prio')+""" 创建两个 PriorityClass，先用低优先级 Pod 占满一个节点的 CPU requests，再提交高优先级 Pod，观察低优先级 Pod 被驱逐。</p>""",
 "lab_out":"抄下 3 种 FailedScheduling 原因并逐一解释",
 "qa":[
("kube-scheduler 选节点的两步是什么？选完之后叫什么？","过滤（找可行节点）和打分（给可行节点排序取最高分）；把结果通知 API Server 的步骤叫绑定。"),
("节点 CPU 实际使用率只有 10%，为什么 Pod 还是 Pending？","调度器按 requests 之和与节点可分配量比较，不看实际用量；已调度 Pod 的 requests 总和可能已占满。"),
("污点/容忍和节点亲和有什么区别？","亲和是 Pod 主动“想去”某些节点；污点是节点主动“排斥”不容忍的 Pod。容忍只表示“允许去”，不保证一定去，常和亲和配合实现专用节点。"),
("NoSchedule 和 NoExecute 区别？","NoSchedule 只阻止新的不容忍 Pod 调度上来；NoExecute 还会驱逐已在运行且不容忍的 Pod。"),
("如果想按自定义规则给节点打分，应该改哪？","写调度框架插件，实现 Score（必要时 PreScore/NormalizeScore）扩展点，通过调度器配置启用，而不是修改调度器源码主流程。"),
 ],
 "refs":["ks","fw","res","aff","taint","prio"]},

{"id":"k8s-03","title":"多租户与配额","short":"多租户与配额",
 "goal":"能讲清 Namespace、ResourceQuota、LimitRange、RBAC 各管什么、怎么配合；能触发并读懂一次配额超限；知道软隔离（命名空间）和更强隔离（虚拟集群等）的区别。",
 "four":[
("是什么",f"""<p><b>Namespace</b> 在一个集群内隔离一组资源的名字作用域，是多租户的基本单位。{a('ns')}</p>
<p><b>ResourceQuota</b> 限制一个命名空间的资源总量（如 requests.cpu、limits.memory、Pod 数量等）。{a('quota')}</p>
<p><b>LimitRange</b> 约束命名空间内单个 Pod/容器的资源最小值、最大值，并可给没写的容器注入默认 requests/limits。{a('lr')}</p>
<p><b>RBAC</b> 用 Role/ClusterRole 定义权限，用 RoleBinding/ClusterRoleBinding 授给用户、组或 ServiceAccount。{a('rbac')}</p>"""),
("为什么这样设计",f"""<p>配额在<b>准入阶段</b>拦截：创建或更新违反配额时，控制平面直接以 <b>HTTP 403 Forbidden</b> 拒绝，并给出违反了哪条约束。{a('quota')}这样超额请求根本不会进入调度队列。</p>
<p>如果命名空间对 cpu/memory 启用了配额，每个新 Pod 都必须写 requests 或 limits，否则可能被拒；所以官方建议配合 LimitRange 注入默认值。{a('quota')}</p>
<p>官方多租户文档把模型分为“多团队”和“多客户”，隔离手段从命名空间级的控制平面隔离，到每租户独立控制平面（虚拟控制平面）不等，隔离越强成本越高。{a('mt')}</p>"""),
("什么时候会出问题",f"""<ul><li><b>没写 requests 被拒</b>：开了 cpu/memory 配额却没有 LimitRange 默认值，用户的 Pod 创建失败。{a('quota')}</li>
<li><b>Deployment 看似成功</b>：Deployment 本身创建成功，但 ReplicaSet 创建 Pod 被配额拒绝，错误只出现在 ReplicaSet 的事件里，容易漏看。</li>
<li><b>配额不等于资源保证</b>：配额总和可以大于集群实际容量，配额只限上限不预留资源。</li>
<li><b>RBAC 过宽</b>：随手绑定 cluster-admin 会让命名空间隔离失效。{a('rbac')}</li></ul>{UV('“配额总和可以超过集群容量”按 ResourceQuota 文档的语义推断，未找到原句。')}"""),
("怎么验证过","<p>实验后填写：① 超限时的 403 错误原文；② Deployment 超限时去哪里看到错误；③ 用 <code>kubectl auth can-i</code> 验证 ServiceAccount 权限的结果。</p>"),
 ],
 "lab":"""<p class="uv">以下命令未在本机运行验证。</p>"""+pre("""
kubectl create namespace team-a
cat <<'EOF' | kubectl apply -n team-a -f -
apiVersion: v1
kind: ResourceQuota
metadata: {name: q}
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 1Gi
    limits.cpu: "2"
    limits.memory: 2Gi
    pods: "3"
---
apiVersion: v1
kind: LimitRange
metadata: {name: lr}
spec:
  limits:
  - type: Container
    default: {cpu: 500m, memory: 256Mi}
    defaultRequest: {cpu: 250m, memory: 128Mi}
EOF
kubectl describe quota q -n team-a""")+"""
<h4>1. 直接触发超限（单个 Pod）</h4>"""+pre("""
kubectl run huge -n team-a --image=nginx --overrides='{"spec":{"containers":[{"name":"huge","image":"nginx","resources":{"requests":{"cpu":"2"},"limits":{"cpu":"2"}}}]}}'
# 期望：Error from server (Forbidden): ... exceeded quota ...""")+"""
<h4>2. 通过 Deployment 触发（错误藏在 ReplicaSet）</h4>"""+pre("""
kubectl create deployment web -n team-a --image=nginx --replicas=5
kubectl get deploy,rs,pod -n team-a          # 只起来部分副本
kubectl describe rs -n team-a | grep -A3 Events
kubectl describe quota q -n team-a           # Used 与 Hard 对比""")+"""
<h4>3. RBAC：只读 ServiceAccount</h4>"""+pre("""
kubectl create serviceaccount viewer -n team-a
kubectl create role pod-reader -n team-a --verb=get,list,watch --resource=pods
kubectl create rolebinding viewer-rb -n team-a --role=pod-reader --serviceaccount=team-a:viewer
kubectl auth can-i list pods -n team-a --as=system:serviceaccount:team-a:viewer    # yes
kubectl auth can-i create pods -n team-a --as=system:serviceaccount:team-a:viewer  # no""")+"""
<p>简述（不做实验）：命名空间是软隔离；需要租户各自有独立控制平面时，可了解官方多租户文档中的虚拟控制平面方案。{0}</p>""".format(a('mt'))+UV("分层命名空间（HNC）、vcluster 等具体项目本次未读文档，不展开。"),
 "lab_out":"记下 403 超限原文和 Deployment 部分副本的排查路径",
 "qa":[
("ResourceQuota 和 LimitRange 分别管什么？","ResourceQuota 管命名空间的总量上限；LimitRange 管单个 Pod/容器的最小/最大值并可注入默认 requests/limits。"),
("超出配额时 API 返回什么？发生在哪个阶段？","HTTP 403 Forbidden，带违反约束的说明；发生在 API Server 的准入阶段，请求不会被持久化，也不会进入调度。"),
("为什么开了 cpu 配额后，没写 requests 的 Pod 会失败？如何解决？","启用 cpu/memory 配额后每个新 Pod 必须指定对应的 requests 或 limits；用 LimitRange 设置默认值即可。"),
("Deployment 副本没起够，但 kubectl apply 没报错，去哪查？","describe 对应的 ReplicaSet 看 Events，那里有创建 Pod 被配额拒绝的错误；再 describe quota 对比 Used/Hard。"),
("Role 与 ClusterRole、RoleBinding 与 ClusterRoleBinding 的区别？","Role 作用于单个命名空间，ClusterRole 是集群范围（也可以被 RoleBinding 引用、只在某命名空间生效）；RoleBinding 在命名空间内授权，ClusterRoleBinding 在整个集群授权。"),
 ],
 "refs":["ns","quota","lr","rbac","mt"]},

{"id":"k8s-04","title":"批任务与异构资源","short":"批任务与异构资源",
 "goal":"能讲清 Job/CronJob 语义；设备插件如何把 GPU 变成 nvidia.com/gpu 这类可调度扩展资源及其限制；为什么需要 Kueue/Volcano 这类队列与批调度；在 kind 上用 Kueue 让 Job 排队。",
 "four":[
("是什么",f"""<p><b>Job</b> 创建一个或多个 Pod 并重试直到指定数量成功完成；<b>CronJob</b> 按 cron 时间表周期性创建 Job。{a('job')} {a('cron')}</p>
<p><b>设备插件</b>：通过 kubelet 的 Registration gRPC 服务注册，向 kubelet 报告它管理的设备，kubelet 在节点状态里通告资源（如 2 个 <code>hardware-vendor.example/foo</code>），之后 Pod 可以像申请 CPU 一样申请。{a('dp')}装好厂商插件后集群就有 <code>nvidia.com/gpu</code>、<code>amd.com/gpu</code> 这类可调度资源。{a('gpu')}</p>
<p><b>Kueue</b>：K8s 原生的作业排队系统，管理配额以及作业如何消耗配额，决定作业何时等待、何时准入（允许创建 Pod）、何时被抢占；它装在原生集群上，不替换现有组件。{a('kq')}核心对象：ResourceFlavor（资源种类，可用 nodeLabels 对应不同节点）、ClusterQueue（定义配额）、LocalQueue（命名空间内的提交入口，用户不能直接提交到 ClusterQueue）。{a('kqq')}</p>
<p><b>Volcano</b>：CNCF 的容器批调度项目，支持 Spark、PyTorch、Ray 等框架，提供异构设备调度、拓扑感知、多集群调度等能力。{a('vc')}</p>"""),
("为什么这样设计",f"""<p>默认调度器按单个 Pod 调度，不懂“这个作业整体该不该开始”。Kueue 在 Pod 创建前决定准入：它通过 webhook 自动管理 Job 的 suspend 状态，配额够了才放行，所以你不用手动把 Job 建成挂起状态。{a('kqj')}</p>
<p>扩展资源只能是<b>整数</b>，不能超卖；GPU 只应写在 limits 里：只写 limits 时以 limits 作为 requests；两者都写必须相等；不能只写 requests。{a('extp')} {a('gpu')}</p>{UV('“容器之间不共享 GPU、不能申请小数”是常见说法，本次读的 GPU 页面未找到原句。')}
<p>一句话对比 Slurm：Slurm 是面向 Linux 集群的开源集群管理与作业调度系统，自带资源分配与排队；K8s + Kueue/Volcano 是在容器编排之上补齐批调度。{a('slurm')}</p>"""),
("什么时候会出问题",f"""<ul><li><b>Pod 逐个调度导致死锁</b>：分布式训练要 N 个 Pod 同时到位，默认调度器可能只放上一部分，占着 GPU 空等。Volcano 文档把这类需求列为批调度的动机。{a('vc')}</li>
{UV('“部分调度占资源空等”是批调度通识，Volcano 首页只列出了需求，未逐字核对 gang 调度说明。')}
<li><b>未写 requests</b>：Kueue 依赖 requests 计算配额；只写 limits 时把 limits 当 requests。{a('kqj')}</li>
<li><b>GPU 申请写法错误</b>：只写 requests 不写 limits，不符合限制。{a('gpu')}</li>
<li><b>Job 失败重试</b>：backoffLimit 用尽后 Job 失败，需要看 Pod 日志而不是只看 Job 状态。{a('job')}</li></ul>"""),
("怎么验证过","<p>实验后填写：① Kueue 下第二个 Job 等待时，Job 和 Workload 分别是什么状态；② 释放配额后它何时开始；③ 假 GPU 资源在 <code>kubectl describe node</code> 里怎么显示。</p>"),
 ],
 "lab":"""<p class="uv">以下命令未在本机运行验证。家里电脑一般没有 NVIDIA GPU 在 kind 中可用，所以用<b>假的扩展资源 example.com/gpu</b> 演示，它只是一个整数计数，没有真实设备。</p>
<h4>1. Job 与 CronJob</h4>"""+pre("""
kubectl create job pi --image=busybox -- sh -c 'echo hello; sleep 5'
kubectl get job,pod -w
kubectl create cronjob tick --image=busybox --schedule='*/1 * * * *' -- date
kubectl get cronjob,job -w      # 看几分钟后删掉：kubectl delete cronjob tick""")+"""
<h4>2. 给节点通告假 GPU（官方“扩展资源”任务的方法）</h4>"""+pre("""
kubectl get nodes                      # 选一个节点，下面记作 <node>
kubectl proxy &                        # 默认监听 127.0.0.1:8001
curl --header "Content-Type: application/json-patch+json" \\
  --request PATCH \\
  --data '[{"op": "add", "path": "/status/capacity/example.com~1gpu", "value": "2"}]' \\
  http://localhost:8001/api/v1/nodes/<node>/status
kubectl describe node <node> | grep -A8 Capacity   # 应出现 example.com/gpu: 2""")+"""
<h4>3. 安装 Kueue（官方文档当前版本 v0.20.4）</h4>"""+pre("""
kubectl apply --server-side -f https://github.com/kubernetes-sigs/kueue/releases/download/v0.20.4/manifests.yaml
kubectl wait deploy/kueue-controller-manager -nkueue-system --for=condition=available --timeout=5m""")+UV("Kueue 对 K8s 最低版本的要求，请以安装页为准；用最新 kind 默认节点镜像一般较新。")+"""
<h4>4. 配队列：总配额 1 个假 GPU</h4>"""+pre("""
cat <<'EOF' | kubectl apply -f -
apiVersion: kueue.x-k8s.io/v1beta2
kind: ResourceFlavor
metadata: {name: default-flavor}
---
apiVersion: kueue.x-k8s.io/v1beta2
kind: ClusterQueue
metadata: {name: cluster-queue}
spec:
  namespaceSelector: {}
  resourceGroups:
  - coveredResources: ["cpu", "memory", "example.com/gpu"]
    flavors:
    - name: default-flavor
      resources:
      - {name: cpu, nominalQuota: 4}
      - {name: memory, nominalQuota: 4Gi}
      - {name: example.com/gpu, nominalQuota: 1}
---
apiVersion: kueue.x-k8s.io/v1beta2
kind: LocalQueue
metadata: {namespace: default, name: user-queue}
spec: {clusterQueue: cluster-queue}
EOF""")+UV("把 example.com/gpu 放进 coveredResources 是按 Kueue 配额文档的通用写法推断，官方示例只用了 cpu/memory。")+"""
<h4>5. 提交两个各要 1 个假 GPU 的 Job，看第二个排队</h4>"""+pre("""
for i in 1 2; do cat <<'EOF' | kubectl create -f -
apiVersion: batch/v1
kind: Job
metadata:
  generateName: gpu-job-
  namespace: default
  labels: {kueue.x-k8s.io/queue-name: user-queue}
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: c
        image: busybox
        command: ["sh", "-c", "sleep 60"]
        resources:
          requests: {cpu: "100m", memory: 64Mi}
          limits: {example.com/gpu: 1}
EOF
done
kubectl get workloads,jobs,pods      # 一个 Job 运行，另一个挂起等待
kubectl describe clusterqueue cluster-queue""")+"""
<p>60 秒后第一个完成、释放配额，第二个应自动开始。对比：去掉 queue-name 标签直接提交，看只有节点调度器限制时会怎样。</p>""",
 "lab_out":"Kueue 排队成功截图 + 一张“准入 vs 调度”卡片",
 "qa":[
("设备插件怎样让 GPU 变成可调度资源？","设备插件通过 kubelet 的 Registration gRPC 注册并上报设备列表，kubelet 在节点状态里通告扩展资源（如 nvidia.com/gpu），调度器据此按数量调度，Pod 在 limits 中申请。"),
("扩展资源/GPU 的申请有哪些限制？","只能是整数、不能超卖；GPU 只在 limits 中指定（只写 limits 时以它为 requests；两者都写必须相等；不能只写 requests）。"),
("Kueue 和 kube-scheduler 的分工？","Kueue 决定作业是否准入（配额够才放行、可排队和抢占），通过管理 Job 的 suspend 实现；kube-scheduler 负责准入后每个 Pod 落到哪个节点。"),
("ResourceFlavor、ClusterQueue、LocalQueue 各是什么？","ResourceFlavor 描述一类资源（可用节点标签对应不同硬件）；ClusterQueue 定义各 flavor 的配额；LocalQueue 是命名空间里的提交入口，指向一个 ClusterQueue。"),
("一句话说 Slurm 与 K8s + Kueue/Volcano 的区别？","Slurm 是为 Linux 集群原生设计的集群管理与作业调度系统；K8s 本身面向容器编排，靠 Kueue/Volcano 在其上补充排队、配额和批调度。"),
 ],
 "refs":["job","cron","dp","gpu","extn","extp","kq","kqi","kqq","kqj","vc","slurm"]},
]
