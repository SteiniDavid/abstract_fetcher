---
layout: digest
title: "Covariate shift in imitation learning"
date: 2026-01-21
topic_key: covshift_imitation_learning
num_candidates: 200
num_unique: 171
num_novel: 141
num_selected: 10
num_downloaded: 9
num_abstracts: 10
---
## Summary

- **Papers selected:** 10
- **PDFs downloaded:** 9 (skipped: 1, failed: 0)
- **Abstracts available:** 10
- **Conclusions extracted:** 5

## 1) Efficient Imitation Learning with Conservative World Models (2024) — Conference on Learning for Dynamics & Control

**Authors:** Victor Kolev, Rafael Rafailov, K. Hatch, Jiajun Wu, Chelsea Finn

**Links:** [Paper](https://www.semanticscholar.org/paper/6534cd07cf88680dd38747597bb6990b6fa64eb0) | [DOI](https://doi.org/10.48550/arXiv.2405.13193) | [arXiv](https://arxiv.org/abs/2405.13193)

**Why selected:** matches: imitation learning, distribution shift, compounding errors

### Abstract

We tackle the problem of policy learning from expert demonstrations without a reward function. A central challenge in this space is that these policies fail upon deployment due to issues of distributional shift, environment stochasticity, or compounding errors. Adversarial imitation learning alleviates this issue but requires additional on-policy training samples for stability, which presents a challenge in realistic domains due to inefficient learning and high sample complexity. One approach to this issue is to learn a world model of the environment, and use synthetic data for policy training. While successful in prior works, we argue that this is sub-optimal due to additional distribution shifts between the learned model and the real environment. Instead, we re-frame imitation learning as a fine-tuning problem, rather than a pure reinforcement learning one. Drawing theoretical connections to offline RL and fine-tuning algorithms, we argue that standard online world model algorithms are not well suited to the imitation learning problem. We derive a principled conservative optimization bound and demonstrate empirically that it leads to improved performance on two very challenging manipulation environments from high-dimensional raw pixel observations. We set a new state-of-the-art performance on the Franka Kitchen environment from images, requiring only 10 demos on no reward labels, as well as solving a complex dexterity manipulation task.

*(Source: metadata)*

### Conclusion

In this work we argue that policy optimization algorithms designed for online RL are not well suited to the IRL/AIL setting as they carry out excessive exploration and induce additional distributional shifts. We focus on the model-based case, and argue that conservative models used for offline RL are better suited to the AIL setting. We pose imitation learning as a fine-tuning problem, rather than a purely RL one, and we draw theoretical connections to offline RL and conservative fine-tuning algorithms. We provide a conservative optimization bound, as well as a practical algorithm and evaluate it on challenging manipulation tasks. The proposed algorithm achieves faster and more stable performance as compared to previous imitation learning approaches. In future work we plan to evaluate our method on further domains. Acknowledgments Chelsea Finn is a CIFAR Fellow in the Learning in Machines and Brains program. This work was also supported by ONR grant N00014-22-1-2621 and the Volkswagen Group.

---

## 2) Adaptive Absolute-Relative Rating for Noise Rejection in Behavioral Cloning based on Tsallis Statistics (2025) — IEEE/SICE International Symposium on System Integration

**Authors:** Taisuke Kobayashi, T. Aoyama

**Links:** [Paper](https://www.semanticscholar.org/paper/ab5044cb120018b9d6f47c4532c1c199a3b35868) | [DOI](https://doi.org/10.1109/SII59315.2025.10871068)

**Why selected:** matches: imitation learning, behavioral cloning, offline imitation; recent publication

### Abstract

In robot control from demonstrations, a sufficient dataset cannot be collected for many of the tasks that require experts with qualifications to special skills. Unfortunately, insufficient expert dataset would manifest various types of noise hidden in it. Since adding data is difficult as well, offline imitation learning needs to be robust to such a noise. In the conventional work, a behavioral cloning method based on Tsallis statistics has been developed. However, it weights each data with absolute rating with a fixed threshold, which would fail to imitate coarse/diverse motions. Therefore, this paper improves the conventional method by adding the function of relative rating for each data, which should enable robots to imitate non-noisy data even from coarse/diverse motions. This function can be obtained from a different derivation way of the optimization problem with Tsallis statistics. By integrating it with the conventional derivation way, the proposed method can adjust between the absolute and relative ratings. Finally, for more convenience, we design optimization tricks for the hyperparameters to maximize the variance of weights with avoiding extremely large weights. In numerical simulations and real-robot experiments, we demonstrate the robustness of the proposed method.

*(Source: metadata)*

### Conclusion

*Conclusion not available (PDF not downloaded)*

---

## 3) Bridging Multicalibration and Out-of-distribution Generalization Beyond Covariate Shift (2024) — Neural Information Processing Systems

**Authors:** Jiayun Wu, Jiashuo Liu, Peng Cui, Zhiwei Steven Wu

**Links:** [Paper](https://www.semanticscholar.org/paper/03dd209a79b302cd7bc976c0bbe6761c152c05b3) | [DOI](https://doi.org/10.48550/arXiv.2406.00661) | [arXiv](https://arxiv.org/abs/2406.00661)

**Why selected:** matches: covariate shift, distribution shift; 11 citations

### Abstract

We establish a new model-agnostic optimization framework for out-of-distribution generalization via multicalibration, a criterion that ensures a predictor is calibrated across a family of overlapping groups. Multicalibration is shown to be associated with robustness of statistical inference under covariate shift. We further establish a link between multicalibration and robustness for prediction tasks both under and beyond covariate shift. We accomplish this by extending multicalibration to incorporate grouping functions that consider covariates and labels jointly. This leads to an equivalence of the extended multicalibration and invariance, an objective for robust learning in existence of concept shift. We show a linear structure of the grouping function class spanned by density ratios, resulting in a unifying framework for robust learning by designing specific grouping functions. We propose MC-Pseudolabel, a post-processing algorithm to achieve both extended multicalibration and out-of-distribution generalization. The algorithm, with lightweight hyperparameters and optimization through a series of supervised regression steps, achieves superior performance on real-world datasets with distribution shift.

*(Source: metadata)*

### Conclusion

To conclude, we establish a new optimization framework for out-of-distribution generalization through extended multicalibration with joint grouping functions. While the current algorithm focuses on regression, there is potential for future work to extend our approach to general forms of tasks, particularly in terms of classification. 10

---

## 4) Automatic Dataset Shift Identification to Support Safe Deployment of Medical Imaging AI (2024) — International Conference on Medical Image Computing and Computer-Assisted Intervention

**Authors:** Mélanie Roschewitz, Raghav Mehta, Charles Jones, Ben Glocker

**Links:** [Paper](https://www.semanticscholar.org/paper/6a683e8d8364ee57917e6ab1172562f7864f05fb) | [DOI](https://doi.org/10.1007/978-3-032-04981-0_7) | [arXiv](https://arxiv.org/abs/2411.07940)

**Why selected:** matches: covariate shift, dataset shift

### Abstract

Shifts in data distribution can substantially harm the performance of clinical AI models and lead to misdiagnosis. Hence, various methods have been developed to detect the presence of such shifts at deployment time. However, the root causes of dataset shifts are diverse, and the choice of shift mitigation strategies is highly dependent on the precise type of shift encountered at test time. As such, detecting test-time dataset shift is not sufficient: precisely identifying which type of shift has occurred is critical. In this work, we propose the first unsupervised dataset shift identification framework for imaging datasets, effectively distinguishing between prevalence shift (caused by a change in the label distribution), covariate shift (caused by a change in input characteristics) and mixed shifts (simultaneous prevalence and covariate shifts). We discuss the importance of self-supervised encoders for detecting subtle covariate shifts and propose a novel shift detector leveraging both self-supervised encoders and task model outputs for improved shift detection. We show the effectiveness of the proposed shift identification framework across three different imaging modalities (chest radiography, digital mammography, and retinal fundus images) on five types of real-world dataset shifts using five large publicly available datasets.

*(Source: metadata)*

### Conclusion

*Conclusion not found in PDF*

---

## 5) Robust Behavioral Cloning for Autonomous Vehicles using End-to-End Imitation Learning (2020) — SAE International Journal of Connected and Automated Vehicles

**Authors:** Tanmay Vilas Samak, Chinmay Vilas Samak, S. Kandhasamy

**Links:** [Paper](https://www.semanticscholar.org/paper/62b38624ce1029b602e8d3212ec7111503d527d3) | [DOI](https://doi.org/10.4271/12-04-03-0023) | [arXiv](https://arxiv.org/abs/2010.04767)

**Why selected:** matches: imitation learning, behavioral cloning; 40 citations

### Abstract

In this work, we present a robust pipeline for cloning driving behavior of a human using end-to-end imitation learning. The proposed pipeline was employed to train and deploy three distinct driving behavior models onto a simulated vehicle. The training phase comprised of data collection, balancing, augmentation, preprocessing and training a neural network, following which, the trained model was deployed onto the ego vehicle to predict steering commands based on the feed from an onboard camera. A novel coupled control law was formulated to generate longitudinal control commands on-the-go based on the predicted steering angle and other parameters such as actual speed of the ego vehicle and the prescribed constraints for speed and steering. We analyzed computational efficiency of the pipeline and evaluated robustness of the trained models through exhaustive experimentation. Even a relatively shallow convolutional neural network model was able to learn key driving behaviors from sparsely labelled datasets and was tolerant to environmental variations during deployment of the said driving behaviors.

*(Source: metadata)*

### Conclusion

This work presented a lightweight pipeline for training and deploying robust driving behavior models on autonomous vehicles using end-to-end imitation learning. The work also introduced a coupled control scheme so as to enhance the cooperative nature of lateral and longitudinal motion control commands. Additionally, a set of experiments and evaluation metrics for analyzing the efficiency and robustness of the proposed pipeline were formulated and presented as a part of this research. Three distinct driving behaviors were cloned using the proposed pipeline and exhaustive experimentation was carried out so as to test the bounds of the proposed system. Even a comparatively shallow neural network model was able to learn key driving behaviors from a sparsely labelled dataset and was tolerant to environmental variations during deployment of the said driving behaviors. Finally, the presented approach was validated by comparing it with NVIDIA’s state-of-the-art implementation. This work may be taken up to develop explicit hardware or sim2real implementations of end-to-end learning for autonomous driving. Additionally, the effect of collecting a diverse dataset from multiple human drivers and using substitute/multiple sensing modalities may be studied. Moreover, alternative approaches may be investigated to address the problem of generalization failure of end-to-end trained models in disparate scenarios. Furthermore, theoretical formulations for assessing reliability of autonomous systems trained using end-to-end learning may be researched exhaustively. Finally, this research may be pursued further in order to standardize the experiments and evaluation metrics for testing efficiency of an end-to-end learning pipeline and robustness of the trained models. 6. REFERENCES [1] Yurtsever E., Lambert J., Carballo A., and Takeda K., “A Survey of Autonomous Driving: Common Practices and Emerging Technologies,” IEEE Access, vol. 8, (2020): 58443-58469, doi: 10.1109/ACCESS.2020.2983149 [2] Rubio F., Valero F., and Llopis-Albert C., “A review of mobile robots: Concepts, methods, theoretical framework, and applications,” International Journal of Advanced Robotic Systems, vol. 16, no. 2, (2019): 1–22, doi: 10.1177/1729881419839596 [3] Alom M., Taha T., Yakopcic C., Westberg S., et. al., “The History Began from AlexNet: A Comprehensive Survey on Deep Learning Approaches,” (2018), arXiv:1803.01164 [4] Zhou F., Jin L., and Dong J., “Review of Convolutional Neural Network,” Jisuanji Xuebao/Chinese Journal of Computers 40, (2017): 1229-1251, doi: 10.11897/SP.J.1016.2017.01229 [5] Tampuu A., Semikin M., Muhammad N., Fishman D., and Matiisen, T., “A Survey of End-to-End Driving: Architectures and Training Methods,” (2020), arXiv:2003.06404 [6] K. Sivanathan, B. K. Vinayagam, T. Samak and C. Samak, "Decentralized Motion Planning for Multi-Robot Navigation using Deep Reinforcement Learning," 2020 3rd International Conference on Intelligent Sustainable Systems (ICISS), Thoothuku

---

## 6) Conformalized Interactive Imitation Learning: Handling Expert Shift and Intermittent Feedback (2024) — arXiv.org

**Authors:** Michelle D. Zhao, Reid G. Simmons, H. Admoni, Aaditya Ramdas, Andrea Bajcsy

**Links:** [Paper](https://www.semanticscholar.org/paper/e499fd0794ed7fe556a69b24300d3afec2b224eb) | [DOI](https://doi.org/10.48550/arXiv.2410.08852) | [arXiv](https://arxiv.org/abs/2410.08852)

**Why selected:** matches: imitation learning, distribution shift, DAgger

### Abstract

In interactive imitation learning (IL), uncertainty quantification offers a way for the learner (i.e. robot) to contend with distribution shifts encountered during deployment by actively seeking additional feedback from an expert (i.e. human) online. Prior works use mechanisms like ensemble disagreement or Monte Carlo dropout to quantify when black-box IL policies are uncertain; however, these approaches can lead to overconfident estimates when faced with deployment-time distribution shifts. Instead, we contend that we need uncertainty quantification algorithms that can leverage the expert human feedback received during deployment time to adapt the robot's uncertainty online. To tackle this, we draw upon online conformal prediction, a distribution-free method for constructing prediction intervals online given a stream of ground-truth labels. Human labels, however, are intermittent in the interactive IL setting. Thus, from the conformal prediction side, we introduce a novel uncertainty quantification algorithm called intermittent quantile tracking (IQT) that leverages a probabilistic model of intermittent labels, maintains asymptotic coverage guarantees, and empirically achieves desired coverage levels. From the interactive IL side, we develop ConformalDAgger, a new approach wherein the robot uses prediction intervals calibrated by IQT as a reliable measure of deployment-time uncertainty to actively query for more expert feedback. We compare ConformalDAgger to prior uncertainty-aware DAgger methods in scenarios where the distribution shift is (and isn't) present because of changes in the expert's policy. We find that in simulated and hardware deployments on a 7DOF robotic manipulator, ConformalDAgger detects high uncertainty when the expert shifts and increases the number of interventions compared to baselines, allowing the robot to more quickly learn the new behavior.

*(Source: metadata)*

### Conclusion

We first extend uncertainty quantification via online conformal prediction to handle intermittent labels, such as those observed in interactive imitation learning. We then propose ConformalDAgger, a unification of our online conformal prediction algorithm with interactive imitation learning. Our approach provides asymptotic coverage guarantees for deployed end-to-end policies, uses the calibrated 10 Published as a conference paper at ICLR 2025 uncertainty measure to detect expert distribution shifts and actively query for more feedback, and empirically enables the robot learner update its policy to better align with the expert. ACKNOWLEDGMENTS The authors would like to thank Gokul Swamy for insightful conversations and the detailed review, Yilin Wu for help with diffusion policy and robot hardware setup. MZ is supported by an NDSEG fellowship.

---

## 7) Generative Adversarial Imitation Learning (2016) — Neural Information Processing Systems

**Authors:** Jonathan Ho, Stefano Ermon

**Links:** [Paper](https://www.semanticscholar.org/paper/4ab53de69372ec2cd2d90c126b6a100165dc8ed1) | [arXiv](https://arxiv.org/abs/1606.03476)

**Why selected:** matches: imitation learning; 3467 citations

### Abstract

Consider learning a policy from example expert behavior, without interaction with the expert or access to reinforcement signal. One approach is to recover the expert's cost function with inverse reinforcement learning, then extract a policy from that cost function with reinforcement learning. This approach is indirect and can be slow. We propose a new general framework for directly extracting a policy from data, as if it were obtained by reinforcement learning following inverse reinforcement learning. We show that a certain instantiation of our framework draws an analogy between imitation learning and generative adversarial networks, from which we derive a model-free imitation learning algorithm that obtains significant performance gains over existing model-free methods in imitating complex behaviors in large, high-dimensional environments.

*(Source: metadata)*

### Conclusion

*Conclusion not found in PDF*

---

## 8) Diffusion Meets DAgger: Supercharging Eye-in-hand Imitation Learning (2024) — Robotics: Science and Systems

**Authors:** Xiaoyu Zhang, Matthew Chang, Pranav Kumar, Saurabh Gupta

**Links:** [Paper](https://www.semanticscholar.org/paper/0f6d341ffc366c42c4d741668cfa104dea354174) | [DOI](https://doi.org/10.48550/arXiv.2402.17768) | [arXiv](https://arxiv.org/abs/2402.17768)

**Why selected:** matches: imitation learning, DAgger; 28 citations

### Abstract

A common failure mode for policies trained with imitation is compounding execution errors at test time. When the learned policy encounters states that are not present in the expert demonstrations, the policy fails, leading to degenerate behavior. The Dataset Aggregation, or DAgger approach to this problem simply collects more data to cover these failure states. However, in practice, this is often prohibitively expensive. In this work, we propose Diffusion Meets DAgger (DMD), a method to reap the benefits of DAgger without the cost for eye-in-hand imitation learning problems. Instead of collecting new samples to cover out-of-distribution states, DMD uses recent advances in diffusion models to synthesize these samples. This leads to robust performance from few demonstrations. We compare DMD against behavior cloning baseline across four tasks: pushing, stacking, pouring, and shirt hanging. In pushing, DMD achieves 80% success rate with as few as 8 expert demonstrations, where naive behavior cloning reaches only 20%. In stacking, DMD succeeds on average 92% of the time across 5 cups, versus 40% for BC. When pouring coffee beans, DMD transfers to another cup successfully 80% of the time. Finally, DMD attains 90% success rate for hanging shirt on a clothing rack.

*(Source: metadata)*

### Conclusion

*Conclusion not found in PDF*

---

## 9) Dynamic Rank Adjustment in Diffusion Policies for Efficient and Flexible Training (2025) — Robotics

**Authors:** Xiatao Sun, Shuo Yang, Yinxing Chen, Francis Fan, Yiyan Liang et al. (6 authors)

**Links:** [Paper](https://www.semanticscholar.org/paper/d69c0e196c45b88203b672eec115a278dff31248) | [DOI](https://doi.org/10.48550/arXiv.2502.03822) | [arXiv](https://arxiv.org/abs/2502.03822)

**Why selected:** matches: imitation learning, DAgger, behavioral cloning; recent publication

### Abstract

Diffusion policies trained via offline behavioral cloning have recently gained traction in robotic motion generation. While effective, these policies typically require a large number of trainable parameters. This model size affords powerful representations but also incurs high computational cost during training. Ideally, it would be beneficial to dynamically adjust the trainable portion as needed, balancing representational power with computational efficiency. For example, while overparameterization enables diffusion policies to capture complex robotic behaviors via offline behavioral cloning, the increased computational demand makes online interactive imitation learning impractical due to longer training time. To address this challenge, we present a framework, called DRIFT, that uses the Singular Value Decomposition to enable dynamic rank adjustment during diffusion policy training. We implement and demonstrate the benefits of this framework in DRIFT-DAgger, an imitation learning algorithm that can seamlessly slide between an offline bootstrapping phase and an online interactive phase. We perform extensive experiments to better understand the proposed framework, and demonstrate that DRIFT-DAgger achieves improved sample efficiency and faster training with minimal impact on model performance. The project website is available at: https://apollo-lab-yale.github.io/25-RSS-DRIFT-website/.

*(Source: metadata)*

### Conclusion

*Conclusion not found in PDF*

---

## 10) SAIL: Faster-than-Demonstration Execution of Imitation Learning Policies (2025) — arXiv.org

**Authors:** N. R. Arachchige, Zhenyang Chen, Wonsuhk Jung, Woo-Chul Shin, Rohan Bansal et al. (11 authors)

**Links:** [Paper](https://www.semanticscholar.org/paper/af0b77f432078c217b821c898647933cddc1b79d) | [DOI](https://doi.org/10.48550/arXiv.2506.11948) | [arXiv](https://arxiv.org/abs/2506.11948)

**Why selected:** matches: imitation learning, distribution shift, offline imitation; recent publication

### Abstract

Offline Imitation Learning (IL) methods such as Behavior Cloning are effective at acquiring complex robotic manipulation skills. However, existing IL-trained policies are confined to executing the task at the same speed as shown in demonstration data. This limits the task throughput of a robotic system, a critical requirement for applications such as industrial automation. In this paper, we introduce and formalize the novel problem of enabling faster-than-demonstration execution of visuomotor policies and identify fundamental challenges in robot dynamics and state-action distribution shifts. We instantiate the key insights as SAIL (Speed Adaptation for Imitation Learning), a full-stack system integrating four tightly-connected components: (1) a consistency-preserving action inference algorithm for smooth motion at high speed, (2) high-fidelity tracking of controller-invariant motion targets, (3) adaptive speed modulation that dynamically adjusts execution speed based on motion complexity, and (4) action scheduling to handle real-world system latencies. Experiments on 12 tasks across simulation and two real, distinct robot platforms show that SAIL achieves up to a 4x speedup over demonstration speed in simulation and up to 3.2x speedup in the real world. Additional detail is available at https://nadunranawaka1.github.io/sail-policy

*(Source: metadata)*

### Conclusion

We formalized and identified challenges in the novel problem of faster-than-demonstration execution of visuomotor policies. Our framework, SAIL, tackles the full-stack problem by combining Error-Adaptive Guidance, controller-invariant targets, adaptive speed modulation, and latency-aware scheduling. Experiments show SAIL achieves up to 4× speedup in simulation and 3.2× speedup in real-world while maintaining high success rates across diverse tasks. 7 Limitations Through formalizing and proposing a solution for the novel problem of faster-than-demonstration execution, we have identified several fundamental challenges that open up new research directions for the robotics community. First, SAIL focuses on addressing the observation-action drift as a result of controller dynamics shift and does not explicitly tackle the dynamics shift of robot-object interaction. This manifests most clearly in manipulation tasks where object-robot dynamics be8 Plate Fruits 1 2 Pack Chicken 1 2 Bimanual Serve 1 2 3 Wiping Board Stacking Cups Baking Folding Cloth 1 2 2 1 1 2 3 Figure 7: Real-world task setup with two robot platforms (Franka and UR5). 7 8 Figure 8: Commonly-seen failure modes from real-world evaluation. Speeding up policy execution poses challenges unseen in normal speed execution, which include imprecise grasping (grasping two cups in 1, missing eraser in 5, and missing chicken in 7), low-fidelity tracking (colliding with other cups in 2 and 3, missing handle in 4, missing collar in 6), jerky motion (fruit drops in 8). SAIL effectively reduces such failures under speeding-up execution, leading to higher task throughput. come significantly more complex at higher speeds—for instance, we observed that in the simulated Can task, increased execution speed can cause the robot to inadvertently throw the can out of the workspace due to increased momentum. Relatedly, the finite-data nature of offline imitation learning makes it vulnerable to distributional shift that cannot be addressed solely by improving the policy learning algorithms. Future research could address this by developing methods to incorporate explicit dynamics modeling into policies, either by leveraging known dynamics models or learning from simulation-based data during training. As the field continues to advance learning-based manipulation in the wild, we believe a key focus should be to enable the robot learning system to co-optimize the low-level control and the anticipated dynamic effects of the predicted actions at different execution speeds. We hope this work can open new pathways and facilitate wider adoption of learned policies in real industrial applications. 9 Acknowledgments The authors would like to acknowledge the State of Georgia and the Agricultural Technology Research Program at Georgia Tech for supporting the work described in this paper. We also acknowledge funding from the AI Manufacturing Pilot Facility project under Georgia Artificial Intelligence in Manufacturing (Georgia 

---


---

*Generated by paper-digest*