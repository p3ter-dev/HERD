<div align="center">
  <img src="/home/peter/HERD/herd.png">
  <h1>HERD</h1>
  <p><strong>Move as one. Think as one. Distribute as many.</strong></p>
</div>

HERD (Heterogeneous Edge Resource Distribution) is an AI-powered task orchestration system. Clients submit tasks via a REST API, and a dispatcher holds those tasks in a priority queue. An AI scheduler (using Q-learning) intelligently decides which worker node should handle each task based on live metrics like CPU usage, memory, and historical success rates. Over time, the scheduler learns and improves its routing policy to route the right task to the right node.
