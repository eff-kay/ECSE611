There are 4 steps to the pipeline

### 1. BaseLineIpCommits

This gets the ground truth from the commit logs via two methods

1. Get issueAndCommitData from the commit logs
2. Get issueAndCommitData from the website via parsing 


### 2. CommitGraph

This step creates a graph from the commit patches identified in the first step.

### 3. LikelihoodOfIPCommits

This step calculates the likelihood of whether two graphs calculated in the previous step are Inappropriately partitioned or not. 

### 4. CreateFinalResults

This step will create the final resutls for documentation. 