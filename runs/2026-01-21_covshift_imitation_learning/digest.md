# Daily Paper Digest — Covariate shift in imitation learning — 2026-01-21

## Summary

- **Papers selected:** 10
- **PDFs downloaded:** 10 (skipped: 0, failed: 0)
- **Abstracts available:** 10
- **Conclusions extracted:** 4

## 1) Robust Offline Imitation Learning from Diverse Auxiliary Data (2024) — arXiv:cs.LG

**Authors:** Udita Ghosh, Dripta S. Raychaudhuri, Jiachen Li, Konstantinos Karydis, Amit K. Roy-Chowdhury

**Links:** [Paper](https://arxiv.org/abs/2410.03626) | [arXiv](https://arxiv.org/abs/2410.03626)

**Why selected:** matches: imitation learning, distribution shift, behavioral cloning

**PDF:** `papers/Robust_Offline_Imitation_Learning_from_Diverse_Aux_2024_2410_03626.pdf`

### Abstract

Offline imitation learning enables learning a policy solely from a set of expert demonstrations, without any environment interaction. To alleviate the issue of distribution shift arising due to the small amount of expert data, recent works incorporate large numbers of auxiliary demonstrations alongside the expert data. However, the performance of these approaches rely on assumptions about the quality and composition of the auxiliary data, and they are rarely successful when those assumptions do not hold. To address this limitation, we propose Robust Offline Imitation from Diverse Auxiliary Data (ROIDA). ROIDA first identifies high-quality transitions from the entire auxiliary dataset using a learned reward function. These high-reward samples are combined with the expert demonstrations for weighted behavioral cloning. For lower-quality samples, ROIDA applies temporal difference learning to steer the policy towards high-reward states, improving long-term returns. This two-pronged approach enables our framework to effectively leverage both high and low-quality data without any assumptions. Extensive experiments validate that ROIDA achieves robust and consistent performance across multiple auxiliary datasets with diverse ratios of expert and non-expert demonstrations. ROIDA effectively leverages unlabeled auxiliary data, outperforming prior methods reliant on specific data assumptions. Our code is available at https://github.com/uditaghosh/roida.

*(Source: metadata)*

### Conclusion (extracted)

We propose ROIDA, a simple yet effective framework for offline imitation that can maximize utilization of an unlabeled auxiliary dataset of unknown quality alongside a small set of expert demonstrations. Unlike previous methods that make assumptions about auxiliary dataset quality, ROIDA can seamlessly leverage uncurated, unlabeled offline datasets without relying on any quality assumptions. We demonstrate ROIDA’s efficacy on multiple manipulation and locomotion tasks, encompassing a wide variety of auxiliary dataset quality settings. The consistent performance gains over baselines validate ROIDA’s ability to unlock the full potential of heterogeneous offline datasets without relying on quality assumptions. Limitations While ROIDA demonstrates strong performance across various environments, we believe there is still room for improvement in the reward estimation process. To investigate this, we conduct an experiment shown in Table 5, where we substitute the estimated reward with the ground-truth reward from the D4RL benchmark. The results indicate a performance gap between the estimated and ground-truth rewards. This finding suggests that our method could potentially achieve higher performance if the reward estimation process is further refined and improved. Table 5: Performance on the Hopper task with ground-truth rewards. Setting Method ROIDA ROIDA w/ GT rewards 5 / 0 84.63± 16.01 94.63± 20.76 5 / 3 86.66± 21.94 98.53± 11.70 5 / 5 88.45± 8.46 104.46± 5.42 Avg. 86.58± 16.42 99.21± 14.11 In our particular framework, the reward estimation can be improved by an accurate choice of the hyperparameter η by performing mixture proportion estimation (Zhu et al., 2023; Ramaswamy et al., 2016). However, this is beyond the scope of our work. In order to avoid any assumption about the auxiliary data in our work, we have chosen η = 0.5 which is an unbiased estimate. We also provide additional results with η = 0.3 and η = 0.7 in Table 6. Here, we obtain better results when η is closer (η = 0.3 is closer than η = 0.7) to the true ratio between expert and suboptimal demonstration in the auxiliary dataset (0.01 for setting 5/0, 0.12 for setting 5/3 and 0.19 for setting 5/5). Since this true ratio is unknown, estimating it would be a problem in its own right, which could then be combined with our method. Additionally, the current implementation of ROIDA is designed for a single-task setting. An interesting avenue for future work is to extend our framework to multi-task or goal-conditioned settings, where the model is trained on datasets from different tasks or goals. In such a scenario, ROIDA could be used to learn a new, 12 Published in Transactions on Machine Learning Research (04/2025) Table 6: Performance on the Hopper task with varying η. Setting Method η = 0.3 η = 0.5 η = 0.7 5 / 0 88.12± 14.93 84.63± 16.01 82.40± 20.76 5 / 3 90.42± 18.84 86.66± 21.94 84.85± 7.13 5 / 5 91.02± 7.97 88.45± 8.46 86.45± 18.61 Avg. 89.85± 14.62 86.58± 16.42 84.57± 14.39 unseen, bu

---

## 2) MEGA-DAgger: Imitation Learning with Multiple Imperfect Experts (2023) — arXiv:cs.LG

**Authors:** Xiatao Sun, Shuo Yang, Mingyan Zhou, Kunpeng Liu, Rahul Mangharam

**Links:** [Paper](https://arxiv.org/abs/2303.00638) | [arXiv](https://arxiv.org/abs/2303.00638)

**Why selected:** matches: imitation learning, covariate shift, compounding errors

**PDF:** `papers/MEGA-DAgger_Imitation_Learning_with_Multiple_Imper_2023_2303_00638.pdf`

### Abstract

Imitation learning has been widely applied to various autonomous systems thanks to recent development in interactive algorithms that address covariate shift and compounding errors induced by traditional approaches like behavior cloning. However, existing interactive imitation learning methods assume access to one perfect expert. Whereas in reality, it is more likely to have multiple imperfect experts instead. In this paper, we propose MEGA-DAgger, a new DAgger variant that is suitable for interactive learning with multiple imperfect experts. First, unsafe demonstrations are filtered while aggregating the training data, so the imperfect demonstrations have little influence when training the novice policy. Next, experts are evaluated and compared on scenarios-specific metrics to resolve the conflicted labels among experts. Through experiments in autonomous racing scenarios, we demonstrate that policy learned using MEGA-DAgger can outperform both experts and policies learned using the state-of-the-art interactive imitation learning algorithms such as Human-Gated DAgger. The supplementary video can be found at \url{https://youtu.be/wPCht31MHrw}.

*(Source: metadata)*

---

## 3) Model-based Offline Imitation Learning with Non-expert Data (2022) — arXiv:cs.LG

**Authors:** Jeongwon Park, Lin Yang

**Links:** [Paper](https://arxiv.org/abs/2206.05521) | [arXiv](https://arxiv.org/abs/2206.05521)

**Why selected:** matches: imitation learning, compounding errors, behavioral cloning

**PDF:** `papers/Model-based_Offline_Imitation_Learning_with_Non-ex_2022_2206_05521.pdf`

### Abstract

Although Behavioral Cloning (BC) in theory suffers compounding errors, its scalability and simplicity still makes it an attractive imitation learning algorithm. In contrast, imitation approaches with adversarial training typically does not share the same problem, but necessitates interactions with the environment. Meanwhile, most imitation learning methods only utilises optimal datasets, which could be significantly more expensive to obtain than its suboptimal counterpart. A question that arises is, can we utilise the suboptimal dataset in a principled manner, which otherwise would have been idle? We propose a scalable model-based offline imitation learning algorithmic framework that leverages datasets collected by both suboptimal and optimal policies, and show that its worst case suboptimality becomes linear in the time horizon with respect to the expert samples. We empirically validate our theoretical results and show that the proposed method \textit{always} outperforms BC in the low data regime on simulated continuous control domains

*(Source: metadata)*

### Conclusion (extracted)

Addressing sample efﬁciency and covariate shift has been a long standing challenge in IL. In our work, we present principled remedies by ﬁnding usage of suboptimal demonstrations. We show that training a model from a suboptimal dataset and adversarial training in the estimated MDP yields an algorithm that requires much lower amount of expert samples. As the algorithms we present are general and backed with theory, it could potentially have real world use cases. It shares the same promise with ofﬂine RL, but without requiring reward labels. It is also worthy to share some limitations in our work. Notably, our algorithm relies on the sufﬁcient coverage assumption of the behavior dataset along with less principled approaches to estimate uncertainty. In that perspective, our work shares the same obstacles as model based ofﬂine RL algorithms, and future works on these limitations could beneﬁt them both.

---

## 4) LUMOS: Language-Conditioned Imitation Learning with World Models (2025) — arXiv:cs.RO

**Authors:** Iman Nematollahi, Branton DeMoss, Akshay L Chandra, Nick Hawes, Wolfram Burgard et al. (6 authors)

**Links:** [Paper](https://arxiv.org/abs/2503.10370) | [arXiv](https://arxiv.org/abs/2503.10370)

**Why selected:** matches: imitation learning, covariate shift, distribution shift; recent publication

**PDF:** `papers/LUMOS_Language-Conditioned_Imitation_Learning_with_2025_2503_10370.pdf`

### Abstract

We introduce LUMOS, a language-conditioned multi-task imitation learning framework for robotics. LUMOS learns skills by practicing them over many long-horizon rollouts in the latent space of a learned world model and transfers these skills zero-shot to a real robot. By learning on-policy in the latent space of the learned world model, our algorithm mitigates policy-induced distribution shift which most offline imitation learning methods suffer from. LUMOS learns from unstructured play data with fewer than 1% hindsight language annotations but is steerable with language commands at test time. We achieve this coherent long-horizon performance by combining latent planning with both image- and language-based hindsight goal relabeling during training, and by optimizing an intrinsic reward defined in the latent space of the world model over multiple time steps, effectively reducing covariate shift. In experiments on the difficult long-horizon CALVIN benchmark, LUMOS outperforms prior learning-based methods with comparable approaches on chained multi-task evaluations. To the best of our knowledge, we are the first to learn a language-conditioned continuous visuomotor control for a real-world robot within an offline world model. Videos, dataset and code are available at http://lumos.cs.uni-freiburg.de.

*(Source: metadata)*

---

## 5) Imitation Learning for Multi-turn LM Agents via On-policy Expert Corrections (2025) — arXiv:cs.LG

**Authors:** Niklas Lauffer, Xiang Deng, Srivatsa Kundurthy, Brad Kenstler, Jeff Da

**Links:** [Paper](https://arxiv.org/abs/2512.14895) | [arXiv](https://arxiv.org/abs/2512.14895)

**Why selected:** matches: imitation learning, covariate shift, DAgger; recent publication

**PDF:** `papers/Imitation_Learning_for_Multi-turn_LM_Agents_via_On_2025_2512_14895.pdf`

### Abstract

A popular paradigm for training LM agents relies on imitation learning, fine-tuning on expert trajectories. However, we show that the off-policy nature of imitation learning for multi-turn LM agents suffers from the fundamental limitation known as covariate shift: as the student policy's behavior diverges from the expert's, it encounters states not present in the training data, reducing the effectiveness of fine-tuning. Taking inspiration from the classic DAgger algorithm, we propose a novel data generation methodology for addressing covariate shift for multi-turn LLM training. We introduce on-policy expert corrections (OECs), partially on-policy data generated by starting rollouts with a student model and then switching to an expert model part way through the trajectory. We explore the effectiveness of our data generation technique in the domain of software engineering (SWE) tasks, a multi-turn setting where LLM agents must interact with a development environment to fix software bugs. Our experiments compare OEC data against various other on-policy and imitation learning approaches on SWE agent problems and train models using a common rejection sampling (i.e., using environment reward) combined with supervised fine-tuning technique. Experiments find that OEC trajectories show a relative 14% and 13% improvement over traditional imitation learning in the 7b and 32b setting, respectively, on SWE-bench verified. Our results demonstrate the need for combining expert demonstrations with on-policy data for effective multi-turn LM agent training.

*(Source: metadata)*

### Conclusion (extracted)

We introduce a novel, partially on-policy data generation technique, called on-policy expert corrections (OECs) to address the problem of covariate shift in imitation learning for multi-turn LM agents. Our technique combines the strengths of several existing paradigms for LM agent training: the relevance of on-policy training from RL, expert data from imitation learning methods, and rejection sampling from training with verifiable rewards. Our experiments highlight the limitations of relying on either purely on-policy training or purely expert demonstrations. Moreover, our experiments highlight the importance of evaluating data quality beyond verifiable rewards, showing that a small proportion of low-quality, positive trajectories can greatly destabilize learning. Our experiments focus on the SWE agent setting, but it will be important for future work to test our findings in other multi-turn LM agent domains, especially as LM agents are used for more complex and long-horizon tasks (Kwa et al., 2025) and the problem of covariate shift becomes increasingly severe. 9 Limitations. Although they have their clear benefits, OECs are not known to benefit from the same no-regret learning guarantees as traditional DAgger. Also, as fine-tuning is performed on a set of OEC trajectories, the on-policy portions of the trajectories become increasingly off-policy, potentially limiting their benefit. This could be mitigated by doing multiple intermediate rounds of OEC generation or by generating new OEC trajectories in an online fashion. Like other imitation learning approaches, OEC trajectories require a source of the expert trajectories (unlike other approaches such RL). In this work, we explored the setting in which a stronger model provides the expert trajectories, whoever, our ideas could be extended to human expert data, using increased test-time compute (e.g., best-of-N Brown et al. (2020) or tree-of-thought Yao et al. (2023)), or privileged information (e.g., hints Nath et al. (2025)) to generate OEC trajectories. 6 REPRODUCIBILITY STATEMENT The source code (built on top of a fork of SWE-agent Yang et al. (2024a)) for generating OEC trajectories, computing the covariate shift between trajectories, and performing the LLM-as-judge qualitative analysis are attached as supplementary material and will be released as a public Github repository for publication. Upon publication, we will also open-source our models OEC-SWE-32B and OEC-SWE-7B and the OEC trajectories collected for our experiments. The problem instances we generated trajectories on come from SWE-smith Yang et al. (2025) and a description of how the distribution is gathered is given in Section 4.1. Section 3 as well as Algorithm 1 included details on how OEC trajectory generation is performed and how our models are trained. Appendix C includes all relevant hyperparameters used for supervised fine-tuning.

---

## 6) Simulation-Driven Railway Delay Prediction: An Imitation Learning Approach (2025) — arXiv:cs.LG

**Authors:** Clément Elliker, Jesse Read, Sonia Vanier, Albert Bifet

**Links:** [Paper](https://arxiv.org/abs/2512.19737) | [arXiv](https://arxiv.org/abs/2512.19737)

**Why selected:** matches: imitation learning, covariate shift, DAgger; recent publication

**PDF:** `papers/Simulation-Driven_Railway_Delay_Prediction_An_Imit_2025_2512_19737.pdf`

### Abstract

Reliable prediction of train delays is essential for enhancing the robustness and efficiency of railway transportation systems. In this work, we reframe delay forecasting as a stochastic simulation task, modeling state-transition dynamics through imitation learning. We introduce Drift-Corrected Imitation Learning (DCIL), a novel self-supervised algorithm that extends DAgger by incorporating distance-based drift correction, thereby mitigating covariate shift during rollouts without requiring access to an external oracle or adversarial schemes. Our approach synthesizes the dynamical fidelity of event-driven models with the representational capacity of data-driven methods, enabling uncertainty-aware forecasting via Monte Carlo simulation. We evaluate DCIL using a comprehensive real-world dataset from \textsc{Infrabel}, the Belgian railway infrastructure manager, which encompasses over three million train movements. Our results, focused on predictions up to 30 minutes ahead, demonstrate superior predictive performance of DCIL over traditional regression models and behavioral cloning on deep learning architectures, highlighting its effectiveness in capturing the sequential and uncertain nature of delay propagation in large-scale networks.

*(Source: metadata)*

---

## 7) RLIF: Interactive Imitation Learning as Reinforcement Learning (2023) — arXiv:cs.AI

**Authors:** Jianlan Luo, Perry Dong, Yuexiang Zhai, Yi Ma, Sergey Levine

**Links:** [Paper](https://arxiv.org/abs/2311.12996) | [arXiv](https://arxiv.org/abs/2311.12996)

**Why selected:** matches: imitation learning, DAgger, behavioral cloning

**PDF:** `papers/RLIF_Interactive_Imitation_Learning_as_Reinforceme_2023_2311_12996.pdf`

### Abstract

Although reinforcement learning methods offer a powerful framework for automatic skill acquisition, for practical learning-based control problems in domains such as robotics, imitation learning often provides a more convenient and accessible alternative. In particular, an interactive imitation learning method such as DAgger, which queries a near-optimal expert to intervene online to collect correction data for addressing the distributional shift challenges that afflict naïve behavioral cloning, can enjoy good performance both in theory and practice without requiring manually specified reward functions and other components of full reinforcement learning methods. In this paper, we explore how off-policy reinforcement learning can enable improved performance under assumptions that are similar but potentially even more practical than those of interactive imitation learning. Our proposed method uses reinforcement learning with user intervention signals themselves as rewards. This relaxes the assumption that intervening experts in interactive imitation learning should be near-optimal and enables the algorithm to learn behaviors that improve over the potential suboptimal human expert. We also provide a unified framework to analyze our RL method and DAgger; for which we present the asymptotic analysis of the suboptimal gap for both methods as well as the non-asymptotic sample complexity bound of our method. We then evaluate our method on challenging high-dimensional continuous control simulation benchmarks as well as real-world robotic vision-based manipulation tasks. The results show that it strongly outperforms DAgger-like approaches across the different tasks, especially when the intervening experts are suboptimal. Code and videos can be found on the project website: https://rlif-page.github.io

*(Source: metadata)*

---

## 8) Robust Offline Imitation Learning Through State-level Trajectory Stitching (2025) — arXiv:cs.RO

**Authors:** Shuze Wang, Yunpeng Mei, Hongjie Cao, Yetian Yuan, Gang Wang et al. (7 authors)

**Links:** [Paper](https://arxiv.org/abs/2503.22524) | [arXiv](https://arxiv.org/abs/2503.22524)

**Why selected:** matches: imitation learning, covariate shift, offline imitation; recent publication

**PDF:** `papers/Robust_Offline_Imitation_Learning_Through_State-le_2025_2503_22524.pdf`

### Abstract

Imitation learning (IL) has proven effective for enabling robots to acquire visuomotor skills through expert demonstrations. However, traditional IL methods are limited by their reliance on high-quality, often scarce, expert data, and suffer from covariate shift. To address these challenges, recent advances in offline IL have incorporated suboptimal, unlabeled datasets into the training. In this paper, we propose a novel approach to enhance policy learning from mixed-quality offline datasets by leveraging task-relevant trajectory fragments and rich environmental dynamics. Specifically, we introduce a state-based search framework that stitches state-action pairs from imperfect demonstrations, generating more diverse and informative training trajectories. Experimental results on standard IL benchmarks and real-world robotic tasks showcase that our proposed method significantly improves both generalization and performance.

*(Source: metadata)*

---

## 9) Offline Imitation Learning with Model-based Reverse Augmentation (2024) — arXiv:cs.LG

**Authors:** Jie-Jing Shao, Hao-Sen Shi, Lan-Zhe Guo, Yu-Feng Li

**Links:** [Paper](https://arxiv.org/abs/2406.12550) | [arXiv](https://arxiv.org/abs/2406.12550)

**Why selected:** matches: imitation learning, covariate shift, offline imitation

**PDF:** `papers/Offline_Imitation_Learning_with_Model-based_Revers_2024_2406_12550.pdf`

### Abstract

In offline Imitation Learning (IL), one of the main challenges is the \textit{covariate shift} between the expert observations and the actual distribution encountered by the agent, because it is difficult to determine what action an agent should take when outside the state distribution of the expert demonstrations. Recently, the model-free solutions introduce the supplementary data and identify the latent expert-similar samples to augment the reliable samples during learning. Model-based solutions build forward dynamic models with conservatism quantification and then generate additional trajectories in the neighborhood of expert demonstrations. However, without reward supervision, these methods are often over-conservative in the out-of-expert-support regions, because only in states close to expert-observed states can there be a preferred action enabling policy optimization. To encourage more exploration on expert-unobserved states, we propose a novel model-based framework, called offline Imitation Learning with Self-paced Reverse Augmentation (SRA). Specifically, we build a reverse dynamic model from the offline demonstrations, which can efficiently generate trajectories leading to the expert-observed states in a self-paced style. Then, we use the subsequent reinforcement learning method to learn from the augmented trajectories and transit from expert-unobserved states to expert-observed states. This framework not only explores the expert-unobserved states but also guides maximizing long-term returns on these states, ultimately enabling generalization beyond the expert data. Empirical results show that our proposal could effectively mitigate the covariate shift and achieve the state-of-the-art performance on the offline imitation learning benchmarks. Project website: \url{https://www.lamda.nju.edu.cn/shaojj/KDD24_SRA/}.

*(Source: metadata)*

### Conclusion (extracted)

In this paper, we study the covariate shift problem of offline imitation learning. The key difficulty is that it is challenging for the agent to obtain trustworthy behavior on expert-unobserved states for policy optimization. To overcome this issue, we present a novel framework, offline imitation learning with Self-paced Reverse Augmentation. This framework generates the trajectories from expertunobserved states to expert-observed states in a self-paced way. When the agent encounters these expert-unobserved states, it can follow the generated trajectory to reach the expert-observed states, thereby improving the long-term return. To the best of our knowledge, this is the first time to introduce the reverse data augmentation to the offline imitation learning. It is different from previous methods based on the forward model. That is, it allows the strategy to explore more diverse expert-unobserved states. In the empirical studies, the effectiveness of our Self-paced Reverse Augmentation has been verified in a series of benchmark tasks. Not only has it achieved state-of-the-art performance, but it has also offered behavioral guidance and enhanced capabilities in the expert-unobserved states, providing a promising way to mitigate the covariate shift of offline imitation learning. This work is inspired by the BCDP [38], which presents the idea of leading the agent from expert-unobserved states to expertobserved states. We propose a reverse-model-based solution to generate diverse trajectories from expert-unobserved states to the expert-observed states. This strategy has a significant advantage in mitigating covariate shifts compared to previous forward-modelbased methods. A concurrent work, ILID [51], presents a similar idea and proposes a model-free data selection method leading the agents to focus on the trajectories whose resultant states fall within the expert data manifold. Further exploration of model-free strategies and the unified solutions with our model-based framework is an interesting direction. Another potential future direction is to extend Self-paced Reverse Augmentation with advanced model learning methods, such as dynamic quantization, to further improve the quality of augmented trajectories. ACKNOWLEDGMENTS This research was supported by Leading-edge Technology Program of Jiangsu Science Foundation (BK20232003), National Science Foundation of China (62176118) and the Postgraduate Research & Practice Innovation Program of Jiangsu Province (KYCX24_0233).

---

## 10) Feedback in Imitation Learning: The Three Regimes of Covariate Shift (2021) — arXiv:cs.LG

**Authors:** Jonathan Spencer, Sanjiban Choudhury, Arun Venkatraman, Brian Ziebart, J. Andrew Bagnell

**Links:** [Paper](https://arxiv.org/abs/2102.02872) | [arXiv](https://arxiv.org/abs/2102.02872)

**Why selected:** matches: imitation learning, covariate shift, behavioral cloning

**PDF:** `papers/Feedback_in_Imitation_Learning_The_Three_Regimes_o_2021_2102_02872.pdf`

### Abstract

Imitation learning practitioners have often noted that conditioning policies on previous actions leads to a dramatic divergence between "held out" error and performance of the learner in situ. Interactive approaches can provably address this divergence but require repeated querying of a demonstrator. Recent work identifies this divergence as stemming from a "causal confound" in predicting the current action, and seek to ablate causal aspects of current state using tools from causal inference. In this work, we argue instead that this divergence is simply another manifestation of covariate shift, exacerbated particularly by settings of feedback between decisions and input features. The learner often comes to rely on features that are strongly predictive of decisions, but are subject to strong covariate shift. Our work demonstrates a broad class of problems where this shift can be mitigated, both theoretically and practically, by taking advantage of a simulator but without any further querying of expert demonstration. We analyze existing benchmarks used to test imitation learning approaches and find that these benchmarks are realizable and simple and thus insufficient for capturing the harder regimes of error compounding seen in real-world decision making problems. We find, in a surprising contrast with previous literature, but consistent with our theory, that naive behavioral cloning provides excellent results. We detail the need for new standardized benchmarks that capture the phenomena seen in robotics problems.

*(Source: metadata)*

---


---

*Generated by paper-digest*