DevOps is all about People, Process and Tools. In this course, you will learn to do DevOps using Docker, Kubernetes, Ansible, Terraform, Azure DevOps and Jenkins. You will play with 3 different clouds - AWS, Azure and Google Cloud.

Agile
- Individuals and interactions over processes and tools,  Working software over comprehensive documentation, Customer collaboration over contract negotiation,  Responding to change over following a plan
- Faster Feedback
	- Short Iterations (Vision -> Iteration 1 -> Iteration 2 -> .. -> Iteration n -> Product)
	- Code, Build, Test, Release, Deploy, Plan
	- more frequent deployments, higher-quality products and happier customers
- More Automation
	- CI, UT, AT, TDD, Visualization
- Enhanced Communication 
	- Business, Architecture, Development (Cross Functional), Testing
	- No need to wait for 6 months how something looks

Architectures Moved towards Microservices which increased deployments exponentially. Operations became the bottleneck.

DevOps
- Natural Evolution of Software Development. 
- DevOps is NOT JUST a tool, framework or just automation. It is a combination. Its more of a culture and a mindset. (Faster Feedback (TTM), High Quality Software. )
- People (Culture), Process, Products (Tools) - Culture is very important
- Business, Architecture, Development, Testing, Operations (Security)
- More Automation - Continuous Deployment, Continuous Delivery, IAAC, Monitoring
- Borrows from Agile and Lean
- Code, Build, Test, Release, Deploy, Operate, Monitor, Plan
- Values or Principles
- Practices
- Tools

7C's 
- Continuous Planning, Development, Integration, Deployment, Testing (Shift Left in Testing), Delivery, Monitoring, Feedback - Do Often

Breakdown the wall
- Working towards a common goal
- Bringing Ops and Dev Together - Automated Platforms and Services - (DH Chapter 8)
- Dev Shares OPs Responsiblities
- Dev maintains releases for first week
- Self Provisioning
- Integrate OPS Engineers into Scrum Teams
- OPS Liason for Every Scrum Team
- Involve Ops in Standups and Retros
- Make Ops work visible

Attitude
- DevOps is still evolving
- Do you know the complexity in aiming for something big like DevOps in multiple clouds (AWS, Azure and GCP) with multiple tools (Docker, K8S, Terraform, Ansible)? You will get confused. So, don't worry if you get confused by the terminology. You can re-watch this course 1000 times if you would want. 
- Tools are not important. Concepts and your thought process is important. Tomorrow, Docker might not be around. But if you understand the problem Docker solved, you can use another tool to solve the problem.
- Is there a perfect tool set or a perfect approach for DevOps? Is there an Utopian World for DevOps? Unfortunately, the answer is no! With evolution of Cloud and Microservices, DevOps Toolset is also evolving everyday. 

Pipelines, CI, Continuous Deployment, Continuous Delivery
Commit -> Unit Tests >  Run Integration Tests > Package > Deploy App > Manual Testing > Approval > Next Environment

IAAC
- Done Manually - Provision Server, Install Java, Install Tomcat, Deploy Application
	- Everytime you create a server, this needs to be done manually. What if Java version needs to be updated? A security patch needs to be applied?
	- 
- Code Your Infra - Treat Infrastructure the same way as application code
	- Infra team focuses on value added work (instead of routine work)
	- Less Errors and Quick Recovery from Failures
	- Servers are Consistent (Avoids Configuration Drift)
- Best Practices
	- Self Provisioning
	- Treat Servers as Disposable
	- Do not do anything manually
	- Version Your Infra
	- Incremental Changes
	- Zero Downtime Deployments
- Create Template, Provision Servers(Enabled by Cloud), Install Software, Configure Software, Deploy Application
- Provisioning Tools - Get new server ready with networking capabilities - CloudFormation and Terraform - Designed to provision the servers themselves (as well as the rest of your infrastructure, like load balancers, databases, networking configuration, etc). You can use precreated images created using Packer and AMI (Amazon Machine Image).
- Configuration management tools - Chef, Puppet, Ansible, and SaltStack - Designed to install and manage software on existing servers.
- Build - Building a deployable version of application. Tools - Maven, Gradle, Docker, WASM, What is used for Python?, Anything else for JavaScript?
- Deployment - Putting new applications or new versions of application live. Tools - CI/CD Tools. Application Deployable - ear, war, container image

DevOps Transformation
- Journey to adopt the right tools, maturing the teams, maturing the managers, etc etc
- Challenges in implementing devops - the real challenge in implementing devops is not about tools
- Organizational challenges in implementing DevOps
- How low and medium maturity organizations do this complete cycle..(develop, test, deploy and monitor)

DevOps Metrics
- Improve deployment frequency
- Achieve faster time to market
- Lower failure rate of new releases
- Shorten lead time between fixes
- Improve mean time to recovery

Best Practices
- Standardization - Get all teams aligned - Tools/Processes - Containers
- Limit Work In Progress, Limit Batch Size, Constraints - Manual Env Setup > Manual Deployment > Manual Testing 
	- Reduce Lead Time and Process Time - Business Idea, Work Started, Work Complete
- Version Control Everything - App Code, DB Schemas, Infrastructure
- Self Provisioning - On demand creation of Dev, Test and Prod Environments
- Enable Quick Feedback - Shift Left - Keep Pushing Quality Close To Source and Fast Feedback - Drive towards TDD and Pair Programming!
- Have the right mix of I Shaped, T Shaped and E Shaped Teams Scott Prugh
- Automate As Much As Possible
  - NFR Tests - Performance and Load Tests
- Immutable Infra
- Enable Low Risk Releases
- Culture

Culture
- What would you do if something is very difficult? DO IT OFTEN?
- Culture of Learning and Calculated Risk Taking
- Continuous Improvements
- Local Discoveries > Global Improvements
- A/B Testing

Enable Low Risk Releases
- Small
- Canaries
- Feature Toggles
- A/B Testing
- Dev Prod Parity
- Automated Testing
- IAAC
	- Dev Prod Parity - Options > Copy from Machine Image, Create from Bare Metal EAch time, IAAC, Containerization, Using Cloud 

Immutability
- Server Template, Provision Server, Tweak1 (Script 0), Tweak2(Script 1), Tweak3(Script 2), Current State. Tweaks - Security Patch, Version Upgrade
- How do we replicate?
- You want to create a new server. Will you have the confidence to execute scripts in order?

ITS NEVER DONE DONE!!! STORY OF DEVOPS

### Story

Here's an amazing story:

You are the star developer in a team and you would need to make a quick fix. You go to a github repository! 

You quickly checkout the project. 

You quickly create your local environment. 

You make a change. You test it. You update the unit and automation tests.

You commit it.

You get an email saying it is deployed to QA. 

A few integration tests are automatically run.

Your QA team gets an email asking for approval. They do a manual test and approve.

Your code is live in production in a few minutes.

You might think this is an ideal scenario. But, do you know that this is what is happening in innovative enterprises like Netflix, Amazon and Google day in and day out!

This is the story of DevOps. 

In this course, you will learn to make this possible for complex microservices architectures in multiple clouds using some amazing tools - Docker, Kubernetes, Azure DevOps, Jenkins, Terraform and Ansible.

Are you ready to get start with this amazing course?

### What is DevOps

Show a variety of definitions!

As you can see it is not easy to get people to agree on a definition of devops. 

However there are a few things that every body agrees on!

Break down the wall between Dev and Ops! 

Agile helped in bridging the gap between the business and development teams. Development Teams understood the priorities of the business and worked with the business to deliver the stories providing most value first. However, the Dev and Ops teams were not aligned.

They had different goals.

The goal of Dev team is to take as many new features to production as possible.

The goal of Ops team was to keep the production environment as stable as possible.

As you can see, if taking things to production is difficult, dev and ops are unaligned.

DevOps aims to align the Dev and Ops teams with shared goals. 

Dev team works with the Ops team to understand and solve operational challenges. Ops team is part of the scrum team and understands the features under development.

How can we make this possible?

Devops Values CAMS
- There are four core values in the DevOps movement: Culture, Automation, Measurement, and Sharing (sometimes abbreviated as the acronym CAMS). The goal is to automate as much of the software delivery process as possible.