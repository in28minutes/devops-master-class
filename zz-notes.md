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


How about learning DevOps and the 6 Most Popular DevOps Tools (Docker, Kubernetes, Azure Devops, Jenkins, Terraform and Ansible) on three cloud platforms (AWS, Azure and Google Cloud)?

Sounds like a dream?

in28minutes makes it a reality with this amazing course containing 200+ step by step lectures and 21 hours of video.

This course expects ZERO experience with Cloud or DevOps or any of the DevOps tools. 


There are a number of use cases we would work on during the course. Here are a couple of examples.
USE CASE 1 : You want to be able to provision and make changes to kubernetes clusters in the cloud automatically. All that you want to do is to commit configuration changes to a git repository.
USE CASE 2 : You want to automatically deploy new versions of microservices to the kubernetes cluster. You commit your changes to git repository and the new version of microservices will be automatically deployed.

Here is how these use cases would work. Let's start with use case 1.
- You 
- 
-

In this course, you will be working on several such use cases to learn
- 6 Most Popular DevOps Tools (Docker, Kubernetes, Azure Devops, Jenkins, Terraform and Ansible)
- Three cloud platforms (AWS, Azure and Google Cloud) 
- Implement Continuous Integration, Continuous Deployment, Infrastructure as Code, Service Discovery, Load Balancing and Centralized Configuration for Microservices on Kubernetes in the Cloud

You will create and run Docker Images for simple Java, Python and JavaScript Applications and a few microservices. You will run the microservices with amazing features on Kubernetes. You will create 8 terraform projects to provision virtual servers, storage buckets, load balancers and kubernetes clusters. You will create 8 azure devops pipelines and learn to use azure devops to manage your agile sprints. You will learn to implement continuous integration with Jenkins. You will install and manage software on multiple cloud servers using Ansible.

For course video : In the next 10 minutes, we will get a quick introduction to how software development evolved from water fall to agile to devops. Once you get the overview, we will start getting our hands dirty with containers and Docker.

I will see you in the next step with a little bit of history. See you there.


I'm Ranga Karanam. I'm the founder of in28Minutes and creator of some of the world's most popular courses on Full Stack, Microservices and the Cloud. I've helped more than 300,000 learners around the world acquire new technology skills. We have almost 30,000 5-Star reviews on our courses. So, rest assured you are in good hands.

So, are your ready to join me and take this amazing journey into the world of DevOps with 6 tools and 3 clouds?

Are you ready to learn DevOps with Docker, Kubernetes, Terraform, Ansible, Jenkins and Azure DevOps in multiple clouds - AWS, Azure and Google Cloud?

Start learning DevOps and join me on this exciting journey now.

I'll see you in the course.

https://www.udemy.com/course/devops-with-docker-kubernetes-and-azure-devops/?couponCode=NEW-COURSE

https://links.in28minutes.com/DevOps-LinkedIn
https://links.in28minutes.com/DevOps-YouTube
https://links.in28minutes.com/DevOps-SBT
https://links.in28minutes.com/DevOps-Teachable


Are you excited to learn about DevOps? Let's get started.

What is DevOps? How do you define it?

As with most buzzwords around software development, there is no accepted definition for DevOps.

Definitions vary from simple ones, like these two, to complex definitions that last 3 slides.. 

Instead of trying define DevOps, let's understand how Software Development evolved to DevOps.

First few decades of software development was centered around the water fall model. Waterfall model approached software development the same way that you would approach building a real estate project - for example, building an amazing bridge. You will build software in multiple phases that can go on for a period any where between a few weeks to a few months  - Requirements, ..... In most waterfall projects, it would be months before the business sees a working version of an application. 

While working in the waterfall model for a few decades, we understood a few key elements around developing great software:
- Software Development is a multi disciplinary effort involving a variety of skills. Communication between people is essential for the success of a software project. In the waterfall model, we tried to enhance communication by trying to prepare 1000 page documents on Requirements, Design, Architecture and Deployment. But, over a period of time, we understood that the best way to enhance communication within the team, is to get the team together. Get a variety of skills in the same team. We understood that cross functional teams - with wide range of skills - work great.
- Getting Feedback Quickly is important. Building great software is all about getting quick feedback? Are we building an application which meets the business expections? You cannot wait for months to get feedback. You would want to know quickly. Will your application have problems if it is deployed to production? You don't want to know it after a few months. You want to find it out as early as possible.
The earlier we find a problem, the easier it is to fix it.
We found that the best software teams are structured to enable quick feedback. Anything I'm working on, I would like to know if I'm doing the right thing as early as possible . 
- Automation is critical. Software Development involves a wide range of activities. Doing things manually is slow and error prone. We understood that it's essential to always look for opportunities to introduce Automation.

So, having understood the key elements to develop great software, in the next steps, lets look at how we evolved to Agile and DevOps.

In the next step, let's look at the evolution towards Agile.

Welcome Back.  Agile was the first step in evolution towards implementing our learnings with enhanced communication between teams, getting feedback and bringing in automation.

Agile brought the business and development teams together into one team which works to build great software in small iterations called sprints. Instead of spending weeks or months on each phase of development, agile focuses on taking small requirements called user stories through the development cycle within a few days, sometimes within the same day.

How did Agile enhance communication between teams? 

Agile brought the business and development teams together. Business is responsible for defining what to build? What are the requirements? Development is responsible for building a product that meets the requirements. When I say Development, I include everybody that works on Design, Coding, Testing and Packaging your software. 

In Agile, a representative from Business, called a Product Owner, is always present with the team, the team understands the business objectives clearly. When the development team does not understand the requirements well and is going in a wrong path, Product Owner helps them do course correction and stay on the correct path. Result : The final product the team builds is something that the business wants.

Another important factor is that Agile Teams have cross functional skills - coding skills - front end, api and databases, testing skills and business skills. This enhances communication between people that have to work together to build great software.

What are the Automation areas where Agile Teams focused on? Software Products can have a variety of defects. Functional Defects mean the product does not work as expected. Technical Defects make the maintainence of the software difficult. For example, code quality problems. In general, agile teams were focused on using automation to find technical and functional defects as early as possible.

Agile teams focused on automation tests. Writing great unit tests to test your methods and classes. Writing great integration tests to test your modules and applications. Agile teams also focused extensively on code quality. Tools like SONAR were used to assess the code quality of applications. 

Is it sufficient if you have great automation tests and great code quality checks? You would want to run them as often as possible. Agile Teams focused on Continuous Integration. You make a commit to version control. Your Unit Tests, Automation Tests and Code Quality Checks were automatically executed in a Continuous Integration Pipeline. Most popular CI/CD tool during the early agile time period was Jenkins.

How did Agile promote immediate feedback? 

Most important factor is that Business does not need to wait for months to see the final product.  At the end of every sprint, the product is demoed to all stakeholders including Architecture and Business Teams. All feedback is taken in while prioritizing user stories for the next sprint. Result : The final product the team builds is something that the business wants. 

Another important factor that enables immediate feedback is continuous integration. Let's say I commit some code into version control. Within 30 minutes, I get feedback if my code causes a unit test failure or a integration test failure. I will get feedback if my code does not meet code quality standards or does not have enough code coverage in the unit tests.

Was agile successful? Yes. For sure. By focusing on improving the communication between business and development teams, and focusing on finding a variety of defects early, Agile took software development to the next level. 

I, personally, had a wonderful experience working with some amazing teams in the Agile model. Software Engineering, which for me represents all the efforts in building software from requirements to taking applications live, for the first time, was as enjoyable as programming.

But, does evolution stop? Nope.

New challenges emerged. We started moving towards a microservices architecture and we started building a number of small api's instead of building large monolith applications. What was the new challenge? Operations becomes more important. Instead of doing 1 monolith release a month, you are doing hundreds of small microservice releases every week. Debugging problems across microservices and getting visibility into what's happening with the microservices became important. 

It was time for a new buzzword in software development. DevOps.

Let's discuss DevOps in the next step.

Welcome Back. What was the focus of DevOps? Focus of DevOps was on enhancing the communication between the Development and the Operations Team. How do we make deployments easier? How do we make the work operations team does more visible to the development team?

How did DevOps enhance communication between teams? DevOps brought Operations Teams closer to the Development Teams. In more mature enterprises, Development and Operations Teams worked as one Team. They started sharing common goals and both teams started to understand the challenges the other team faces. In enterprises in the early stages of devops evolution, a representative from the operations team can be involved in the sprints - standups and retrospectives.

What are the Automation areas where DevOps Teams focused on? In addition to the focus areas of agile - Continuous Integration and Test Automation, the DevOps teams were focused on helping automate several of the Operation Teams Activities - Provisioning Servers, Configuring Software on Servers, Deploying Applications and Monitoring Production Environments. A few key terminology are Continuous Deployment, Continuous Delivery and Infrastructure as Code. 

Continuous Deployment is all about continuously deploying new version of software on Test Environments. In even more mature organizations like Google, Facebook, Continuous Delivery helps in continuously deploying software to production - maybe hundreds of production deployments per day. Infrastructure as Code is all about treating your Infrastructure like you treat your application code. You create your infrastructure - servers, load balancers and database - in an automated way using configuration. You would version control your infrastructure - so that you can track your infrastructure changes over a period of time. We would discuss Continuous Deployment, Continuous Delivery and Infrastructure as Code in depth in the next steps. 

How did DevOps promote immediate feedback? 

DevOps brings Operations and Development Teams Together. Because Operations and Development are part of the same team, the entire team understands the challenges associated with Operations and Development. Any operational problems get quick attention of the developers. Any challenges in taking software live get early attention of operations team.

DevOps encouraged Continuous Integration, Continuous Delivery and Infrastructure as Code.

Because of Continous Delivery, If I make a code change or a configuration change that might break a test or a staging environment, I would know it within a few hours.

Because of Infrastructure As Code, Developers can self provision environments, deploy code and find problems on their own, without any help from operations team. 

While we talk as if agile and devops are two different things to make things simple, in reality, there is no accepted definition for what devops means. 

I see agile and devops as two phases that helped us improve how build great software. They don't compete against each other but together they help us build amazing software products.

As far as iam concerned the objective of Agile and DevOps together is to do things that 
- Promote Communication and Feedback between Business, Development and Operations Teams
- Ease the painpoints with Automation. We will discuss about Unit Tests, Integration Tests, Code Quality Checks, Continuous Integration, Continuous Delivery, Infrastructure as Code and Standardization through Containerization during this amazing journey in this course.

In the next steps, let's focus on some of the most important aspects of DevOps - Enhancing communication between Dev and Ops, Enhancing quick feedback through Continuous Delivery and Automating Infrastructure using IAAC.

Bring Down the Wall

As we discussed in the previous steps, DevOps is a Natural Evolution of Software Development. DevOps is NOT JUST a tool, a framework or just automation. It is a combination of all these. 

DevOps focuses on People, Process and Products. People aspects of DevOps are all about Culture and Create a Great Mindset. A culture which promotes open communication and values quick feedback. A culture that value high quality software. 

Agile helped in bridging the gap between the business and development teams. Development Teams understood the priorities of the business and worked with the business to deliver the stories providing most value first. However, the Dev and Ops teams were not aligned.

They had different goals.

The goal of Dev team is to take as many new features to production as possible.

The goal of Ops team was to keep the production environment as stable as possible.

As you can see, if taking things to production is difficult, dev and ops are unaligned.

DevOps aims to align the Dev and Ops teams with shared goals. 

Dev team works with the Ops team to understand and solve operational challenges. Ops team is part of the scrum team and understands the features under development.

How can we make this possible?

Break down the wall between Dev and Ops! 

In matured Dev Ops enterprises, Dev and Ops work as part of the same scrum team and share each other responsibilities. However, if you are in the early stages of devops evolution, how can you get Dev and Ops have common objectives and work together?

Here are some of the things you can do:

One of the things you can start with is to have the development team share some of the responsibilities of the operation team. For example, the dev team can take the responsibility of new release for the first week after production deployment. This helps the development team understand the challenges faced by operations in taking new releases live and help them come together and find better solutions.

Other thing you can do is to involve a representative of the operations team in the Scrum activities. Involve them in Standups and Retrospectives of the team.

The next thing you can do is to make the challenges faced by Operations team more visible to the Development team. When you face any challenges in operations, make development teams part of the teams working on solutions.

Which way you take, find ways of breaking the wall and get the Development and Operations team together.

Another interesting option emerges because of automation. By using Infrastructure as Code and enabling Self Provisioning for Developers, You can create common language that operations and development teams understand - code. More about this in the next couple of steps.

Pipelines, Continuous Integration, Continuous Deployment, Continuous Delivery
- Commit -> Unit Tests >  Code Quality Checks > Integration Tests > Package > Deploy App > Manual Testing > Approval > Next Environment
- Tools - Azure DevOps and Jenkins
- Build - Building a deployable version of application. Tools - Maven, Gradle, Docker, WASM, What is used for Python?, Anything else for JavaScript?
- Deployment - Putting new applications or new versions of application live. Tools - CI/CD Tools. Application Deployable - ear, war, container image


IAAC
- Done Manually - Provision Server, Install Java, Install Tomcat, Deploy Application
	- Everytime you create a server, this needs to be done manually. What if Java version needs to be updated? A security patch needs to be applied?
	- 
- Code Your Infra - Treat Infrastructure the same way as application code
	- Infra team focuses on value added work (instead of routine work)
	- Less Errors and Quick Recovery from Failures
	- Servers are Consistent (Avoids Configuration Drift)
- Tools - Ansible and Terraform
- Create Template, Provision Servers(Enabled by Cloud), Install Software, Configure Software, Deploy Application
- Provisioning Tools - Get new server ready with networking capabilities - CloudFormation and Terraform - Designed to provision the servers themselves (as well as the rest of your infrastructure, like load balancers, databases, networking configuration, etc). You can use precreated images created using Packer and AMI (Amazon Machine Image).
- Configuration management tools - Chef, Puppet, Ansible, and SaltStack - Designed to install and manage software on existing servers.


Standardization
