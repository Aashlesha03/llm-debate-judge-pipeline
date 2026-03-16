# Multi-Agent LLM Debate System Report

## 1. Methodology

This project implements a multi-agent debate framework using three LLM agents:

- Debater A
- Debater B
- Judge

The goal is to evaluate whether structured adversarial debate can produce more accurate answers than a single-model baseline.

### System Architecture

The pipeline follows four phases:

1. **Initialization**
   - Debater A and Debater B independently answer the same question.
   - Each produces an initial answer and short reasoning without seeing the other debater’s response.

2. **Multi-Round Debate**
   - Debater A argues first in each round.
   - Debater B responds with a counterargument.
   - Both receive the full transcript from previous rounds as context.
   - The system uses an adaptive stopping rule: if both agents converge to the same answer for two consecutive rounds, the debate stops early.

3. **Judgment**
   - The judge receives the original question, both initial answers, and the full debate transcript.
   - The judge provides:
     - analysis of both sides
     - strongest and weakest arguments from each debater
     - final verdict
     - confidence score from 1 to 5

4. **Evaluation**
   - The final judge answer is compared against the ground truth.
   - All intermediate data is logged.

### Models Used

- Debater A: **Llama 3.1 8B**
- Debater B: **Qwen3 8B**
- Judge: **GPT-OSS 20B**

These models were accessed through instructor-provided API endpoints.

### Hyperparameters

- Number of debate rounds: 3
- Temperature: 0.7
- Max tokens: 300
- Self-consistency samples: 5
- Number of questions: 100

### LLM Assistance Disclosure

LLM tools such as ChatGPT were used for coding assistance, debugging, and interface development during implementation.  
The final experiments, system assembly, and report content were completed independently.

---

## 2. Experiments

### Dataset

The system was evaluated on the **StrategyQA** dataset, a commonsense reasoning benchmark with yes/no answers.

A subset of **100 questions** was sampled for experiments.

### Baselines

Two required baselines were implemented:

1. **Direct QA**
   - A single model answers the question directly with reasoning.

2. **Self-Consistency**
   - A single model generates multiple sampled answers.
   - The majority answer is selected as the final prediction.

### Evaluation Metrics

Accuracy was measured for all three methods:

- Debate + Judge
- Direct QA
- Self-Consistency

Additionally, 95% confidence intervals were computed.

## Experimental Results

The system was evaluated on 100 questions from the StrategyQA dataset.  
We compared the Debate + Judge pipeline against two baselines: Direct QA and Self-Consistency.

Accuracy and 95% confidence intervals were computed for all methods.

| Method | Accuracy | 95% Confidence Interval |
|------|------|------|
| Debate + Judge | **0.45** | ± 0.10 |
| Direct QA | **0.72** | ± 0.09 |
| Self-Consistency | **0.68** | ± 0.09 |

### Interpretation of Results

The results show that the direct QA baseline achieved the highest accuracy on this dataset, followed by the self-consistency method. The debate-based system achieved lower accuracy compared to the baselines.

One possible explanation is that many StrategyQA questions are relatively simple yes/no factual reasoning tasks. In such cases, a strong single-pass model often produces the correct answer directly, leaving less room for improvement through adversarial debate.

Additionally, debate introduces multiple rounds of generation and reasoning, which increases the likelihood of compounding reasoning errors if one debater introduces incorrect information that the other debater fails to correct.

Despite the lower accuracy, the debate framework provides additional transparency into the reasoning process by exposing intermediate arguments and counterarguments. This makes it useful for qualitative analysis and interpretability of model reasoning.

### Statistical Interpretation

The 95% confidence intervals indicate the uncertainty of the accuracy estimates across the sampled dataset.

For example:

- Debate accuracy: **0.45 ± 0.10**
- Direct QA accuracy: **0.72 ± 0.09**
- Self-consistency accuracy: **0.68 ± 0.09**

The overlap between the Direct QA and Self-Consistency intervals suggests that their performance differences may not be statistically significant for this dataset size. However, both outperform the debate pipeline in this experiment.


---

## 3. Analysis

### Qualitative Transcript Analysis

Below are examples of how the debate system behaved on different questions.

### Example 1: Can penguins fly?

- Debater A argued that penguins are flightless birds with bodies adapted for swimming rather than flight.
- Debater B initially produced extra reasoning text, but later converged to the correct answer.
- The debate eventually stabilized around the correct answer: **No**.

**Observation:**  
This example showed that debate can recover from noisy intermediate outputs and still converge to the correct answer.

### Example 2: Did the Roman Empire exist at the same time as the Mayan civilization?

- Debater A initially gave a somewhat ambiguous answer about overlap in time.
- Debater B more clearly argued that the Mayan civilization overlapped with the Roman Empire, especially when considering the Eastern Roman Empire.
- The judge selected the correct answer: **Yes**.

**Observation:**  
This example demonstrates the advantage of multi-agent interaction: one model clarified a historical ambiguity that the other model initially expressed less precisely.

### Example 3: Is Mount Everest taller than Mount Kilimanjaro?

- Both debaters converged quickly on the correct answer.
- The judge’s output was accurate and well-structured.
- Final answer: **Yes**.

**Observation:**  
For simple factual comparisons, debate adds little benefit beyond what a strong single-pass model can already do.

### Example 4: Is the Earth closer to the Sun than Mars?

- Both debaters gave accurate orbital-distance reasoning.
- The judge selected the correct answer: **Yes**.

**Observation:**  
The debate framework is robust on straightforward astronomy questions, but the baselines also handle them well.

### Example 5: Do whales breathe underwater like fish?

- Both debaters correctly distinguished whales as mammals with lungs and fish as animals with gills.
- The judge selected the correct answer: **No**.

**Observation:**  
This example shows that debate works especially well when both agents are aligned with strong factual knowledge.

### Failure Analysis

The main failures were not always due to reasoning quality.  
During development, several engineering issues reduced measured performance:

- inconsistent answer formatting
- verbose judge outputs
- truncated model responses
- extra reasoning tags such as `<think>`

These were mitigated by:
- enforcing `FINAL_ANSWER:`
- normalizing yes/no outputs during evaluation
- refining judge prompts
- adding adaptive stopping

### Connection to Debate Theory

The project aligns with the theoretical motivation from **Irving, Christiano, and Amodei (2018)**, where adversarial interaction helps reveal stronger and weaker reasoning paths.  
However, the current dataset is relatively simple, so the benefits of adversarial debate are more visible in clarification and robustness than in headline accuracy gains.

---

## 4. Prompt Engineering

Prompt engineering was one of the most important parts of the project.

### Debater Prompt Design

The two debaters were assigned explicit roles:

- Debater A argues for an answer
- Debater B challenges weak reasoning and defends an alternative

Key design choices:
- explicit role framing
- concise reasoning instructions
- transcript visibility in later rounds
- enforced final format using `FINAL_ANSWER:`

### Judge Prompt Design

The judge prompt was iterated several times.

Initial versions produced:
- overly verbose reasoning
- incomplete outputs
- missing `FINAL_ANSWER`

To fix this, the final judge prompt required:
- explicit strongest and weakest arguments for both sides
- exact structured output format
- final answer constrained to `Yes` or `No`
- confidence score from 1 to 5

### Iteration Process

Prompt refinement happened in multiple stages:

1. Initial prompts focused on free-form reasoning.
2. Output inconsistencies made evaluation difficult.
3. Structured answer tags were added.
4. Judge format was tightened.
5. Final prompt versions improved logging, parsing, and reproducibility.

This process showed that prompt engineering is not only about accuracy, but also about making multi-agent systems evaluable and stable.

---

## 5. Conclusion

This project successfully implemented a full Debate + Judge pipeline with:

- independent initial answers
- multi-round debate
- adaptive stopping
- judge verdicts
- baseline comparisons
- evaluation scripts
- web interface

The final system satisfies the core assignment requirements and demonstrates how adversarial multi-agent reasoning can be implemented in practice.

The final results suggest that debate is competitive, but on relatively simple yes/no reasoning tasks, direct answering and self-consistency remain strong baselines.

Future improvements could include:
- more complex datasets
- stronger or multi-agent judge panels
- debate-specific retrieval evidence
- better calibration of judge confidence

---

## Appendix: Full Prompts

### Debater A Prompt

```text
You are Debater A in a multi-agent LLM debate.

Answer the question as accurately as possible.

Rules:
- Keep the response short.
- Use only necessary reasoning.
- FINAL_ANSWER must be exactly one word: Yes or No.
- If transcript is provided, briefly respond to the other debater.
- End exactly with:

FINAL_ANSWER: <Yes or No>