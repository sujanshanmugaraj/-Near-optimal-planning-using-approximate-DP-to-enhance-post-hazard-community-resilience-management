**Near-optimal planning using approximate dynamic programming to enhance post-hazard community resilience management**

**ABSTRACT**

The lack of a comprehensive decision-making approach at the community level poses significant challenges, particularly in the context of recovery management following disasters. This research introduces a sequential discrete optimization approach, providing a robust decision-making framework to address recovery management in Energy Power Networks (EPN). We present a mathematical model that incorporates approximate dynamic programming alongside heuristic strategies to determine effective recovery actions while managing large-scale optimization problems under various uncertainties.

To demonstrate the applicability of our proposed framework, we developed a simulation model using Python, employing the NetworkX library for graph-based representations of the EPN. The simulation features a DamagedNode class, encapsulating vital attributes such as repair time, importance, and the population served, along with an EPNNetwork class that simulates stochastic damage propagation and recovery processes. The core of the methodology employs a rollout algorithm, which iteratively prioritizes the repair of damaged nodes based on their importance, available resources, and probabilistic repair outcomes. 

Through computational results, we illustrate that our approach not only incorporates the recovery policies of responsible public and private entities but also enhances their performance under resource constraints. The simulation effectively models the recovery process in a testbed community, coarsely modelled after Gilroy, California, enabling community decision-makers to identify near-optimal recovery strategies post-disaster, particularly following severe earthquakes. Our methodology supports risk-informed decision-making, improving resilience in chaotic post-hazard scenarios, ultimately contributing to the robustness and reliability of electrical power networks.

This abstract effectively synthesizes the concepts presented in the research paper with the details of the code, emphasizing the decision-making framework, methodology, and implications for community-level recovery management.

